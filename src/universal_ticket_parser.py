#!/usr/bin/env python3
"""
Universal Ticket Parser - Multi-Format Support

Handles Jira and Zendesk ticket exports in multiple formats:
- Jira: PDF, Excel (.xlsx), XML, Word (.docx)
- Zendesk: PDF

Extracts ticket data and normalizes it into a standard dictionary format
for use by the intelligent estimator.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

# PDF support
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Word document support
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# XML support
try:
    from lxml import etree
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False


class UniversalTicketParser:
    """Parse ticket exports from multiple formats (Jira/Zendesk)."""

    SUPPORTED_FORMATS = {
        'jira': ['.pdf', '.xlsx', '.xml', '.docx'],
        'zendesk': ['.pdf']
    }

    def __init__(self, file_path: Union[str, Path]):
        """Initialize parser with file path."""
        self.file_path = Path(file_path)
        self.file_ext = self.file_path.suffix.lower()
        self.source_type = None  # 'jira' or 'zendesk'
        self.raw_text = ""
        self.ticket_data = {}

    def parse(self) -> Dict:
        """Parse the ticket file and return normalized data."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Route to appropriate parser based on extension
        if self.file_ext == '.pdf':
            self.ticket_data = self._parse_pdf()
        elif self.file_ext == '.xlsx':
            self.ticket_data = self._parse_excel()
        elif self.file_ext == '.xml':
            self.ticket_data = self._parse_xml()
        elif self.file_ext == '.docx':
            self.ticket_data = self._parse_docx()
        else:
            raise ValueError(f"Unsupported file format: {self.file_ext}")

        return self.ticket_data

    def _parse_pdf(self) -> Dict:
        """Parse PDF export (Jira or Zendesk)."""
        if not PDF_AVAILABLE:
            raise ImportError("PyMuPDF (pymupdf) required for PDF support. Install: pip install pymupdf")

        # Extract text from PDF
        doc = fitz.open(self.file_path)
        self.raw_text = ""

        for page in doc:
            self.raw_text += page.get_text()

        doc.close()

        # Detect source type (Jira vs Zendesk)
        if self._is_zendesk_pdf():
            return self._parse_zendesk_pdf()
        else:
            return self._parse_jira_pdf()

    def _is_zendesk_pdf(self) -> bool:
        """Detect if PDF is from Zendesk."""
        zendesk_indicators = [
            'Ticket #', 'Requester:', 'Zendesk', 'Status:', 'Priority:',
            'Assignee:', 'Created:', 'Updated:'
        ]

        text_lower = self.raw_text.lower()
        matches = sum(1 for indicator in zendesk_indicators if indicator.lower() in text_lower)

        # If 4+ indicators match, likely Zendesk
        return matches >= 4

    def _parse_zendesk_pdf(self) -> Dict:
        """Parse Zendesk PDF export."""
        self.source_type = 'zendesk'
        data = {
            'source': 'zendesk',
            'ticket_id': self._extract_zendesk_field(r'Ticket #(\d+)'),
            'summary': self._extract_zendesk_field(r'Subject:\s*(.+)'),
            'description': self._extract_zendesk_description(),
            'priority': self._extract_zendesk_field(r'Priority:\s*(\w+)'),
            'status': self._extract_zendesk_field(r'Status:\s*(\w+)'),
            'requester': self._extract_zendesk_field(r'Requester:\s*(.+)'),
            'assignee': self._extract_zendesk_field(r'Assignee:\s*(.+)'),
            'created': self._extract_zendesk_field(r'Created:\s*(.+)'),
            'updated': self._extract_zendesk_field(r'Updated:\s*(.+)'),
            'labels': self._extract_zendesk_tags(),
            'raw_text': self.raw_text
        }

        return data

    def _extract_zendesk_field(self, pattern: str) -> Optional[str]:
        """Extract a field from Zendesk PDF using regex."""
        match = re.search(pattern, self.raw_text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_zendesk_description(self) -> str:
        """Extract ticket description from Zendesk PDF."""
        # Look for description section (usually after "Description:" or before "Comments:")
        desc_match = re.search(r'Description:\s*(.+?)(?=Comments:|$)', self.raw_text, re.DOTALL | re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()

        # Fallback: extract first large text block
        lines = self.raw_text.split('\n')
        description_lines = []
        in_description = False

        for line in lines:
            if line.strip() and len(line) > 50:
                in_description = True
                description_lines.append(line.strip())
            elif in_description and not line.strip():
                break

        return ' '.join(description_lines) if description_lines else self.raw_text[:500]

    def _extract_zendesk_tags(self) -> List[str]:
        """Extract tags/labels from Zendesk PDF."""
        tags_match = re.search(r'Tags:\s*(.+)', self.raw_text, re.IGNORECASE)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            return [tag.strip() for tag in tags_str.split(',')]
        return []

    def _parse_jira_pdf(self) -> Dict:
        """Parse Jira PDF export."""
        self.source_type = 'jira'
        data = {
            'source': 'jira',
            'issue_key': self._extract_jira_field(r'Issue Key:\s*([A-Z]+-\d+)'),
            'summary': self._extract_jira_field(r'Summary:\s*(.+)'),
            'description': self._extract_jira_description(),
            'priority': self._extract_jira_field(r'Priority:\s*(\w+)'),
            'severity': self._extract_jira_field(r'Severity:\s*(.+)'),
            'status': self._extract_jira_field(r'Status:\s*(\w+)'),
            'assignee': self._extract_jira_field(r'Assignee:\s*(.+)'),
            'reporter': self._extract_jira_field(r'Reporter:\s*(.+)'),
            'labels': self._extract_jira_labels(),
            'rca': self._extract_jira_field(r'RCA:\s*(.+)'),
            'customer': self._extract_jira_customer(),
            'raw_text': self.raw_text
        }

        return data

    def _extract_jira_field(self, pattern: str) -> Optional[str]:
        """Extract a field from Jira PDF using regex."""
        match = re.search(pattern, self.raw_text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_jira_description(self) -> str:
        """Extract description from Jira PDF."""
        desc_match = re.search(r'Description:\s*(.+?)(?=\n[A-Z][a-z]+:|$)', self.raw_text, re.DOTALL | re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()

        return self.raw_text[:1000]  # Fallback

    def _extract_jira_labels(self) -> List[str]:
        """Extract labels from Jira PDF."""
        labels_match = re.search(r'Labels:\s*(.+)', self.raw_text, re.IGNORECASE)
        if labels_match:
            labels_str = labels_match.group(1).strip()
            return [label.strip() for label in labels_str.split(',')]
        return []

    def _extract_jira_customer(self) -> Optional[str]:
        """Extract customer name from Jira PDF."""
        # Common customer field names in Jira
        patterns = [
            r'Customer:\s*(.+)',
            r'Account:\s*(.+)',
            r'Organization:\s*(.+)',
            r'Company:\s*(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _parse_excel(self) -> Dict:
        """Parse Excel export (Jira batch or single ticket)."""
        df = pd.read_excel(self.file_path)

        # Check if single ticket or batch
        if len(df) == 1:
            # Single ticket export - convert to dict
            row = df.iloc[0]
            return self._normalize_excel_row(row)
        else:
            # Batch export - return first ticket (or raise error)
            raise ValueError("Batch Excel exports not supported by this parser. Use calculate_jira_scores.py instead.")

    def _normalize_excel_row(self, row: pd.Series) -> Dict:
        """Normalize Excel row to standard format."""
        # Common Jira Excel column names (case-insensitive)
        data = {
            'source': 'jira',
            'issue_key': self._get_field(row, ['Issue key', 'Key', 'Jira']),
            'summary': self._get_field(row, ['Summary', 'Title']),
            'description': self._get_field(row, ['Description']),
            'priority': self._get_field(row, ['Priority']),
            'severity': self._get_field(row, ['Severity', 'Custom field (Severity)']),
            'status': self._get_field(row, ['Status']),
            'assignee': self._get_field(row, ['Assignee']),
            'labels': self._get_field(row, ['Labels'], as_list=True),
            'rca': self._get_field(row, ['RCA', 'Custom field (RCA)', 'Root Cause Analysis']),
            'customer': self._get_field(row, ['Customer', 'Account', 'Organization']),
        }

        return data

    def _get_field(self, row: pd.Series, field_names: List[str], as_list: bool = False) -> Optional[Union[str, List[str]]]:
        """Get field value from Excel row (case-insensitive)."""
        for field in field_names:
            for col in row.index:
                if field.lower() in col.lower():
                    value = row[col]
                    if pd.notna(value):
                        if as_list:
                            return str(value).split(',') if isinstance(value, str) else [str(value)]
                        return str(value)

        return [] if as_list else None

    def _parse_xml(self) -> Dict:
        """Parse Jira XML export."""
        if not XML_AVAILABLE:
            raise ImportError("lxml required for XML support. Install: pip install lxml")

        tree = etree.parse(str(self.file_path))
        root = tree.getroot()

        # Jira XML structure
        data = {
            'source': 'jira',
            'issue_key': self._get_xml_field(root, 'key'),
            'summary': self._get_xml_field(root, 'summary'),
            'description': self._get_xml_field(root, 'description'),
            'priority': self._get_xml_field(root, 'priority'),
            'status': self._get_xml_field(root, 'status'),
            'assignee': self._get_xml_field(root, 'assignee'),
            'labels': self._get_xml_field(root, 'labels', as_list=True),
        }

        return data

    def _get_xml_field(self, root, field_name: str, as_list: bool = False) -> Optional[Union[str, List[str]]]:
        """Extract field from XML."""
        elem = root.find(f'.//{field_name}')
        if elem is not None and elem.text:
            if as_list:
                return elem.text.split(',')
            return elem.text.strip()
        return [] if as_list else None

    def _parse_docx(self) -> Dict:
        """Parse Jira Word document export."""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx required for Word support. Install: pip install python-docx")

        doc = docx.Document(self.file_path)

        # Extract all text
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)

        self.raw_text = '\n'.join(full_text)

        # Parse similar to PDF (look for field patterns)
        data = {
            'source': 'jira',
            'issue_key': self._extract_jira_field(r'Issue Key:\s*([A-Z]+-\d+)'),
            'summary': self._extract_jira_field(r'Summary:\s*(.+)'),
            'description': self._extract_jira_description(),
            'priority': self._extract_jira_field(r'Priority:\s*(\w+)'),
            'status': self._extract_jira_field(r'Status:\s*(\w+)'),
            'labels': self._extract_jira_labels(),
            'raw_text': self.raw_text
        }

        return data


def parse_ticket_file(file_path: Union[str, Path]) -> Dict:
    """
    Convenience function to parse any supported ticket file.

    Args:
        file_path: Path to ticket export (PDF/Excel/XML/Word)

    Returns:
        Dictionary with normalized ticket data

    Examples:
        >>> data = parse_ticket_file('RED-12345.pdf')
        >>> data = parse_ticket_file('zendesk_ticket_789.pdf')
        >>> data = parse_ticket_file('jira_export.xlsx')
    """
    parser = UniversalTicketParser(file_path)
    return parser.parse()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python universal_ticket_parser.py <ticket_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        data = parse_ticket_file(file_path)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)
