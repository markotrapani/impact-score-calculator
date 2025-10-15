#!/usr/bin/env python3
"""
Intelligent Jira Impact Score Estimator

Analyzes Jira ticket exports and automatically estimates impact score components
based on ticket fields, description, labels, and other metadata.

Usage:
    python intelligent_estimator.py <jira_export.xlsx>
    python intelligent_estimator.py <jira_export.xlsx> --output scores.json
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd


class IntelligentImpactEstimator:
    """Analyzes Jira tickets and estimates impact score components intelligently."""
    
    # Priority to severity mapping
    PRIORITY_TO_SEVERITY = {
        'blocker': 38,
        'critical': 38,
        'highest': 38,
        'high': 30,
        'medium': 22,
        'low': 16,
        'lowest': 8,
        'trivial': 8,
    }
    
    # Severity field mappings
    SEVERITY_MAPPINGS = {
        '1 - critical': 38,
        '1 - high': 38,
        'sev 1': 38,
        'p1': 38,
        '2 - high': 30,
        '2 - medium': 30,
        'sev 2': 30,
        'p2': 30,
        '3 - medium': 22,
        '3 - low': 22,
        'sev 3': 22,
        'p3': 22,
        '4 - low': 16,
        'p4': 16,
        '5 - trivial': 8,
        'p5': 8,
    }
    
    # Known high-value customers (examples - would be customized)
    VIP_CUSTOMERS = [
        'monday.com', 'monday', 'salesforce', 'twilio', 'stripe', 
        'shopify', 'zoom', 'slack', 'datadog', 'hashicorp'
    ]
    
    # Keywords indicating workaround availability
    WORKAROUND_KEYWORDS = {
        'simple': ['workaround', 'can use', 'alternative', 'use instead', 'run command'],
        'complex': ['manual', 'multiple steps', 'requires', 'need to'],
        'with_impact': [
            'performance', 'slower', 'degraded', 'limited',
            'inconvenient', 'operational overhead', 'manual intervention',
            'hard-coded', 'hardcoded', 'manual update', 'manually update',
            'reduced capability', 'reduced effectiveness', 'not as designed',
            'operational impact', 'requires updating', 'human error',
            'reduced confidence', 'less effective', 'workaround impact'
        ],
        'none': ['no workaround', 'cannot', 'impossible', 'requires fix', 'needs patch'],
    }
    
    # SLA breach indicators
    SLA_KEYWORDS = ['sla breach', 'sla violated', 'exceeded sla', 'manual recovery', 'downtime']
    
    # Frequency indicators
    FREQUENCY_KEYWORDS = {
        'multiple': ['multiple', 'several', 'recurring', 'repeated', 'again', 'reoccur'],
        'single': ['first time', 'one time', 'single', 'once'],
    }
    
    # RCA indicators
    RCA_KEYWORDS = ['rca', 'root cause', 'action item', 'post mortem', 'postmortem']
    
    def __init__(self, excel_path: str):
        """Initialize with path to Jira Excel export."""
        self.excel_path = Path(excel_path)
        self.df = None
        self.ticket_data = {}
        
    def load_data(self) -> pd.DataFrame:
        """Load Jira export data."""
        try:
            # Try to read the file
            xl_file = pd.ExcelFile(self.excel_path)
            sheet_name = xl_file.sheet_names[0]
            self.df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            print(f"✓ Loaded ticket data from {self.excel_path}")
            print(f"  Sheet: {sheet_name}")
            print(f"  Columns: {len(self.df.columns)}")
            
            return self.df
        except Exception as e:
            raise Exception(f"Error loading Excel file: {e}")
    
    def extract_ticket_info(self) -> Dict:
        """Extract key information from the ticket."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        row = self.df.iloc[0]
        
        # Extract key fields
        self.ticket_data = {
            'issue_key': self._get_field(row, ['Issue key', 'Jira', 'Key']),
            'summary': self._get_field(row, ['Summary']),
            'description': self._get_field(row, ['Description']),
            'priority': self._get_field(row, ['Priority']),
            'issue_type': self._get_field(row, ['Issue Type']),
            'status': self._get_field(row, ['Status']),
            'severity': self._get_field(row, ['Custom field (Severity)', 'Severity']),
            'labels': self._get_labels(row),
            'customer_name': self._get_field(row, [
                'Custom field (Customer Name)',
                'Custom field (Account Name)',
                'Custom field (CSQ Customer Name)'
            ]),
            'workaround': self._get_field(row, ['Custom field (Workaround)']),
            'rca': self._get_field(row, ['Custom field (RCA)']),
            'zendesk': self._get_field(row, [
                'Custom field (Zendesk Link)',
                'Custom field (Zendesk)',
                'Custom field (Zendesk ID/s)'
            ]),
        }
        
        return self.ticket_data
    
    def _get_field(self, row, field_names: List[str]) -> Optional[str]:
        """Get field value from row, trying multiple possible field names."""
        for field in field_names:
            if field in row.index and pd.notna(row[field]):
                return str(row[field])
        return None
    
    def _get_labels(self, row) -> List[str]:
        """Extract all labels from the ticket."""
        labels = []
        for col in row.index:
            if col.startswith('Labels') and pd.notna(row[col]):
                labels.append(str(row[col]))
        return labels
    
    def estimate_impact_severity(self) -> Tuple[int, str]:
        """Estimate Impact & Severity score (0-38 points)."""
        reasons = []
        
        # Get description and summary for context analysis
        desc = ((self.ticket_data.get('description') or '') + ' ' + 
                (self.ticket_data.get('summary') or '')).lower()
        
        # First, check for P4 indicators (monitoring/reporting issues, not service degradation)
        p4_indicators = [
            'metric', 'metrics', 'monitoring', 'prometheus', 'grafana',
            'alert', 'alerting', 'false alert', 'reporting',
            'dashboard', 'visualization', 'observability'
        ]
        
        # Check if this is a monitoring/metrics issue (P4) vs actual service issue
        is_monitoring_issue = any(indicator in desc for indicator in p4_indicators)
        
        # Check for actual service degradation keywords
        service_ok_indicators = [
            'service is fine', 'service working', 'db is working',
            'fully functional', 'no actual', 'appears to be',
            'reporting issue', 'calculation artifact', 'metrics artifact'
        ]
        service_is_ok = any(indicator in desc for indicator in service_ok_indicators)
        
        # If it's a monitoring issue AND service is OK, likely P4
        if is_monitoring_issue and service_is_ok:
            reasons.append("Monitoring/metrics issue with service functioning normally (P4)")
            return 16, '; '.join(reasons)
        
        # Check priority field
        priority = (self.ticket_data.get('priority') or '').lower()
        if priority in self.PRIORITY_TO_SEVERITY:
            score = self.PRIORITY_TO_SEVERITY[priority]
            # But adjust if it's clearly a monitoring issue
            if is_monitoring_issue and service_is_ok and score > 16:
                reasons.append(f"Priority '{priority}' indicates {score} points, but adjusted to 16 for monitoring-only issue")
                return 16, '; '.join(reasons)
            reasons.append(f"Priority '{priority}' indicates {score} points")
            return score, '; '.join(reasons)
        
        # Check severity field
        severity = (self.ticket_data.get('severity') or '').lower()
        for key, score in self.SEVERITY_MAPPINGS.items():
            if key in severity:
                # If severity field explicitly says P4/Low AND it's a monitoring issue
                if ('4' in key or 'low' in severity) and is_monitoring_issue:
                    reasons.append(f"Severity field '{severity}' maps to {score} points (monitoring issue)")
                    return 16, '; '.join(reasons)
                reasons.append(f"Severity field '{severity}' maps to {score} points")
                return score, '; '.join(reasons)
        
        # Check description for actual severity indicators
        if any(word in desc for word in ['critical', 'down', 'outage', 'stopped', 'crash', 'data loss']):
            # But if service is actually OK (just reporting issue), it's not critical
            if service_is_ok:
                reasons.append("Critical keywords found but service is functioning (P4)")
                return 16, '; '.join(reasons)
            reasons.append("Critical keywords found in description")
            return 38, '; '.join(reasons)
        elif any(word in desc for word in ['degraded', 'slow', 'performance']):
            # Check if it's actual degradation or just monitoring
            if is_monitoring_issue and service_is_ok:
                reasons.append("Performance keywords found but service OK (monitoring issue, P4)")
                return 16, '; '.join(reasons)
            reasons.append("Performance degradation keywords found")
            return 30, '; '.join(reasons)
        elif any(word in desc for word in ['error', 'bug', 'issue', 'problem']):
            # For monitoring/metrics issues with no service impact
            if is_monitoring_issue and service_is_ok:
                reasons.append("Issue keywords found but monitoring-only (P4)")
                return 16, '; '.join(reasons)
            reasons.append("General issue keywords found")
            return 22, '; '.join(reasons)
        
        # Default to medium
        reasons.append("No clear severity indicators, defaulting to P3")
        return 22, '; '.join(reasons)
    
    def estimate_customer_arr(self) -> Tuple[int, str]:
        """Estimate Customer ARR score (0-15 points)."""
        reasons = []
        
        # Check for customer name (handle None values)
        customer = (self.ticket_data.get('customer_name') or '').lower()
        desc = ((self.ticket_data.get('description') or '') + ' ' + 
                (self.ticket_data.get('summary') or '')).lower()
        
        # Check if VIP customer
        for vip in self.VIP_CUSTOMERS:
            if vip.lower() in customer or vip.lower() in desc:
                reasons.append(f"VIP customer '{vip}' identified")
                return 15, '; '.join(reasons)
        
        # Check for multiple customers in description
        if 'multiple customers' in desc or 'several customers' in desc:
            reasons.append("Multiple customers mentioned")
            return 8, '; '.join(reasons)
        
        # Check labels for customer indicators
        labels_str = ' '.join(self.ticket_data.get('labels', [])).lower()
        if 'enterprise' in labels_str or 'premium' in labels_str:
            reasons.append("Enterprise/Premium labels found")
            return 13, '; '.join(reasons)
        
        # Check for subscription level
        if 'essentials' in desc or 'standard' in desc:
            reasons.append("Standard subscription tier mentioned")
            return 10, '; '.join(reasons)
        
        # Check if customer is mentioned at all
        if customer or 'customer' in desc:
            reasons.append("Customer mentioned but ARR unknown")
            return 10, '; '.join(reasons)
        
        # Default
        reasons.append("No customer information found, assuming single low ARR")
        return 0, '; '.join(reasons)
    
    def estimate_sla_breach(self) -> Tuple[int, str]:
        """Estimate SLA Breach score (0 or 8 points)."""
        reasons = []
        
        desc = ((self.ticket_data.get('description') or '') + ' ' + 
                (self.ticket_data.get('summary') or '') + ' ' +
                (self.ticket_data.get('rca') or '')).lower()
        
        # Check for explicit "no SLA breach" or "no downtime" statements first
        no_breach_indicators = [
            'no sla breach', 'no downtime', 'no shard downtime',
            'no actual', 'shards stable', 'service is fine',
            'fully functional', 'no service impact'
        ]
        
        if any(indicator in desc for indicator in no_breach_indicators):
            reasons.append("No SLA breach (service confirmed stable/functional)")
            return 0, '; '.join(reasons)
        
        # Check for SLA breach keywords
        for keyword in self.SLA_KEYWORDS:
            if keyword in desc:
                reasons.append(f"SLA breach keyword '{keyword}' found")
                return 8, '; '.join(reasons)
        
        # Check for downtime duration (but not if it's in a negative context)
        if re.search(r'(\d+)\s*(hour|hr|minute|min).*down', desc) and 'no' not in desc[:desc.find('down')] if 'down' in desc else False:
            reasons.append("Downtime duration mentioned, potential SLA impact")
            return 8, '; '.join(reasons)
        
        # Check status/labels for severity
        if self.ticket_data.get('priority', '').lower() in ['blocker', 'critical', 'highest']:
            reasons.append("Critical priority suggests potential SLA breach")
            return 8, '; '.join(reasons)
        
        reasons.append("No SLA breach indicators found")
        return 0, '; '.join(reasons)
    
    def estimate_frequency(self) -> Tuple[int, str]:
        """Estimate Frequency score (0-16 points)."""
        reasons = []
        
        desc = ((self.ticket_data.get('description') or '') + ' ' + 
                (self.ticket_data.get('summary') or '')).lower()
        
        # Check for explicit frequency mentions
        if re.search(r'(\d+)\s*times', desc) or re.search(r'(\d+)\s*occurrences', desc):
            match = re.search(r'(\d+)\s*(times|occurrences)', desc)
            if match:
                count = int(match.group(1))
                if count > 4:
                    reasons.append(f"{count} occurrences mentioned")
                    return 16, '; '.join(reasons)
                elif count >= 2:
                    reasons.append(f"{count} occurrences mentioned")
                    return 8, '; '.join(reasons)
        
        # Check for frequency keywords
        for keyword in self.FREQUENCY_KEYWORDS['multiple']:
            if keyword in desc:
                reasons.append(f"Multiple occurrence keyword '{keyword}' found")
                return 16, '; '.join(reasons)
        
        for keyword in self.FREQUENCY_KEYWORDS['single']:
            if keyword in desc:
                reasons.append(f"Single occurrence keyword '{keyword}' found")
                return 0, '; '.join(reasons)
        
        # Check for "similar to" or references to other tickets
        if 'similar to' in desc or 'same as' in desc or re.search(r'RED-\d+', desc):
            reasons.append("References to similar issues found")
            return 8, '; '.join(reasons)
        
        reasons.append("No clear frequency indicators, assuming single occurrence")
        return 0, '; '.join(reasons)
    
    def estimate_workaround(self) -> Tuple[int, str]:
        """Estimate Workaround score (5-15 points)."""
        reasons = []
        
        workaround_text = self.ticket_data.get('workaround') or ''
        desc = (self.ticket_data.get('description') or '') + ' ' + (self.ticket_data.get('summary') or '')
        combined = (workaround_text + ' ' + desc).lower()
        
        # Check for no workaround first
        if any(kw in combined for kw in self.WORKAROUND_KEYWORDS['none']):
            reasons.append("No workaround available, fix required")
            return 15, '; '.join(reasons)
        
        # Check if fix/patch is the only solution
        if 'fix' in combined or 'patch' in combined or 'requires version' in combined:
            if 'workaround' not in combined:
                reasons.append("Fix/patch required, no workaround")
                return 15, '; '.join(reasons)
        
        # If workaround is explicitly mentioned, analyze it
        has_workaround = 'workaround' in combined or 'use instead' in combined or 'alternative' in combined
        
        if has_workaround:
            # Check for performance/operational impact
            if any(kw in combined for kw in self.WORKAROUND_KEYWORDS['with_impact']):
                reasons.append("Workaround with performance/operational impact detected")
                return 12, '; '.join(reasons)
            
            # Check for complexity
            elif any(kw in combined for kw in self.WORKAROUND_KEYWORDS['complex']):
                reasons.append("Complex workaround found")
                return 10, '; '.join(reasons)
            
            # Simple workaround
            else:
                reasons.append("Simple workaround found")
                return 5, '; '.join(reasons)
        
        # Check if workaround field is explicitly filled (but keyword not in description)
        if workaround_text and workaround_text.strip() and workaround_text.lower() not in ['nan', 'none', 'n/a']:
            # Analyze workaround field content
            if any(kw in workaround_text.lower() for kw in self.WORKAROUND_KEYWORDS['with_impact']):
                reasons.append("Workaround field shows performance/operational impact")
                return 12, '; '.join(reasons)
            elif any(kw in workaround_text.lower() for kw in self.WORKAROUND_KEYWORDS['complex']):
                reasons.append("Workaround field shows complex workaround")
                return 10, '; '.join(reasons)
            else:
                reasons.append("Workaround field populated")
                return 10, '; '.join(reasons)
        
        # Default: unclear if workaround exists
        reasons.append("No clear workaround information, assuming complex workaround needed")
        return 10, '; '.join(reasons)
    
    def estimate_rca_action_item(self) -> Tuple[int, str]:
        """Estimate RCA Action Item score (0 or 8 points)."""
        reasons = []
        
        rca_text = self.ticket_data.get('rca') or ''
        desc = (self.ticket_data.get('description') or '') + ' ' + (self.ticket_data.get('summary') or '')
        combined = (rca_text + ' ' + desc).lower()
        
        # Check if RCA field is filled
        if rca_text and rca_text.strip() and len(rca_text.strip()) > 50:
            reasons.append("RCA field contains substantial content")
            return 8, '; '.join(reasons)
        
        # Check for RCA keywords
        for keyword in self.RCA_KEYWORDS:
            if keyword in combined:
                reasons.append(f"RCA keyword '{keyword}' found")
                return 8, '; '.join(reasons)
        
        # Check labels
        labels_str = ' '.join(self.ticket_data.get('labels', [])).lower()
        if 'rca' in labels_str or 'postmortem' in labels_str:
            reasons.append("RCA label found")
            return 8, '; '.join(reasons)
        
        reasons.append("No RCA indicators found")
        return 0, '; '.join(reasons)
    
    def estimate_all_components(self) -> Dict:
        """Estimate all impact score components."""
        impact_severity, severity_reason = self.estimate_impact_severity()
        customer_arr, arr_reason = self.estimate_customer_arr()
        sla_breach, sla_reason = self.estimate_sla_breach()
        frequency, freq_reason = self.estimate_frequency()
        workaround, work_reason = self.estimate_workaround()
        rca_action_item, rca_reason = self.estimate_rca_action_item()
        
        # For now, multipliers are 0 (could be enhanced with more analysis)
        support_multiplier = 0.0
        account_multiplier = 0.0
        
        components = {
            'impact_severity': {
                'score': impact_severity,
                'reason': severity_reason
            },
            'customer_arr': {
                'score': customer_arr,
                'reason': arr_reason
            },
            'sla_breach': {
                'score': sla_breach,
                'reason': sla_reason
            },
            'frequency': {
                'score': frequency,
                'reason': freq_reason
            },
            'workaround': {
                'score': workaround,
                'reason': work_reason
            },
            'rca_action_item': {
                'score': rca_action_item,
                'reason': rca_reason
            },
            'support_multiplier': support_multiplier,
            'account_multiplier': account_multiplier
        }
        
        return components
    
    def calculate_impact_score(self, components: Dict) -> Tuple[float, float, str]:
        """Calculate final impact score from components."""
        base_score = (
            components['impact_severity']['score'] +
            components['customer_arr']['score'] +
            components['sla_breach']['score'] +
            components['frequency']['score'] +
            components['workaround']['score'] +
            components['rca_action_item']['score']
        )
        
        total_multiplier = 1 + components['support_multiplier'] + components['account_multiplier']
        final_score = base_score * total_multiplier
        
        # Classify priority
        if final_score >= 90:
            priority = 'CRITICAL'
        elif final_score >= 70:
            priority = 'HIGH'
        elif final_score >= 50:
            priority = 'MEDIUM'
        elif final_score >= 30:
            priority = 'LOW'
        else:
            priority = 'MINIMAL'
        
        return base_score, round(final_score, 1), priority
    
    def display_results(self, components: Dict, base_score: float, final_score: float, priority: str):
        """Display estimation results."""
        print("\n" + "="*80)
        print("INTELLIGENT IMPACT SCORE ESTIMATION")
        print("="*80)
        
        issue_key = self.ticket_data.get('issue_key', 'Unknown')
        summary = self.ticket_data.get('summary', '')
        
        print(f"\nTicket: {issue_key}")
        print(f"Summary: {summary[:70]}..." if len(summary) > 70 else f"Summary: {summary}")
        
        print("\n" + "-"*80)
        print("COMPONENT BREAKDOWN")
        print("-"*80)
        
        print(f"\n1. Impact & Severity: {components['impact_severity']['score']:2d} points")
        print(f"   → {components['impact_severity']['reason']}")
        
        print(f"\n2. Customer ARR: {components['customer_arr']['score']:2d} points")
        print(f"   → {components['customer_arr']['reason']}")
        
        print(f"\n3. SLA Breach: {components['sla_breach']['score']:2d} points")
        print(f"   → {components['sla_breach']['reason']}")
        
        print(f"\n4. Frequency: {components['frequency']['score']:2d} points")
        print(f"   → {components['frequency']['reason']}")
        
        print(f"\n5. Workaround: {components['workaround']['score']:2d} points")
        print(f"   → {components['workaround']['reason']}")
        
        print(f"\n6. RCA Action Item: {components['rca_action_item']['score']:2d} points")
        print(f"   → {components['rca_action_item']['reason']}")
        
        print("\n" + "-"*80)
        print(f"BASE SCORE: {base_score:.0f} points")
        
        if components['support_multiplier'] > 0 or components['account_multiplier'] > 0:
            print(f"\nMultipliers:")
            print(f"  Support: {components['support_multiplier']:.0%}")
            print(f"  Account: {components['account_multiplier']:.0%}")
        
        print("\n" + "="*80)
        print(f"FINAL IMPACT SCORE: {final_score} points")
        print(f"PRIORITY LEVEL: {priority}")
        print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Intelligently estimate Jira ticket impact scores from Excel export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        'file',
        help='Path to Jira Excel export'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file for results',
        default=None
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed ticket information'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    print("="*80)
    print("INTELLIGENT JIRA IMPACT SCORE ESTIMATOR")
    print("="*80)
    print(f"\nAnalyzing: {args.file}\n")
    
    try:
        # Initialize estimator
        estimator = IntelligentImpactEstimator(args.file)
        
        # Load data
        estimator.load_data()
        
        # Extract ticket info
        print("\nExtracting ticket information...")
        ticket_info = estimator.extract_ticket_info()
        
        if args.verbose:
            print("\nTicket Data:")
            for key, value in ticket_info.items():
                if value:
                    display_val = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"  {key}: {display_val}")
        
        # Estimate components
        print("\nEstimating impact score components...")
        components = estimator.estimate_all_components()
        
        # Calculate final score
        base_score, final_score, priority = estimator.calculate_impact_score(components)
        
        # Display results
        estimator.display_results(components, base_score, final_score, priority)
        
        # Save to JSON if requested
        if args.output:
            result_data = {
                'ticket': ticket_info.get('issue_key', 'Unknown'),
                'summary': ticket_info.get('summary', ''),
                'components': {
                    'impact_severity': components['impact_severity']['score'],
                    'customer_arr': components['customer_arr']['score'],
                    'sla_breach': components['sla_breach']['score'],
                    'frequency': components['frequency']['score'],
                    'workaround': components['workaround']['score'],
                    'rca_action_item': components['rca_action_item']['score'],
                    'support_multiplier': components['support_multiplier'],
                    'account_multiplier': components['account_multiplier'],
                },
                'reasoning': {
                    'impact_severity': components['impact_severity']['reason'],
                    'customer_arr': components['customer_arr']['reason'],
                    'sla_breach': components['sla_breach']['reason'],
                    'frequency': components['frequency']['reason'],
                    'workaround': components['workaround']['reason'],
                    'rca_action_item': components['rca_action_item']['reason'],
                },
                'scores': {
                    'base_score': base_score,
                    'final_score': final_score,
                    'priority': priority
                }
            }
            
            with open(args.output, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            print(f"\n✓ Results saved to {args.output}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
