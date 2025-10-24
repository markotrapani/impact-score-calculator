#!/usr/bin/env python3
"""
Generate RCA Summary from Multiple PDFs

This tool analyzes multiple Zendesk and Jira PDFs to automatically generate
a comprehensive RCA summary with timeline, root cause analysis, and action items.

Usage:
    python generate_rca_summary.py --zendesk-pdfs ticket1.pdf ticket2.pdf ticket3.pdf \
      --jira-pdfs bug1.pdf bug2.pdf --customer "Azure" --date "10/24/25"
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict
from jira_creator import JiraCreator
from intelligent_estimator import IntelligentImpactEstimator
from universal_ticket_parser import UniversalTicketParser


class RCASummaryGenerator:
    """Generate comprehensive RCA summaries from multiple PDFs."""
    
    def __init__(self):
        self.creator = JiraCreator()
        self.analyzed_tickets = []
        self.analyzed_bugs = []
    
    def analyze_tickets(self, zendesk_pdfs: List[str], jira_pdfs: List[str]) -> Dict:
        """Analyze all PDFs and extract key information."""
        print("Analyzing all tickets and bugs...")
        
        # Analyze Zendesk tickets
        for pdf in zendesk_pdfs:
            if Path(pdf).exists():
                print(f"  Analyzing Zendesk ticket: {pdf}")
                ticket_info = self._analyze_zendesk_ticket(pdf)
                self.analyzed_tickets.append(ticket_info)
            else:
                print(f"  Warning: File not found: {pdf}")
        
        # Analyze Jira bugs
        for pdf in jira_pdfs:
            if Path(pdf).exists():
                print(f"  Analyzing Jira bug: {pdf}")
                bug_info = self._analyze_jira_bug(pdf)
                self.analyzed_bugs.append(bug_info)
            else:
                print(f"  Warning: File not found: {pdf}")
        
        return self._generate_comprehensive_summary()
    
    def _analyze_zendesk_ticket(self, pdf_path: str) -> Dict:
        """Analyze a single Zendesk ticket PDF."""
        try:
            # Parse the ticket
            parser = UniversalTicketParser(pdf_path)
            ticket_data = parser.parse()
            
            # Calculate impact score
            estimator = IntelligentImpactEstimator(pdf_path)
            estimator.load_data()
            ticket_info = estimator.extract_ticket_info()
            components = estimator.estimate_all_components()
            base_score, final_score, priority = estimator.calculate_impact_score(components)
            
            # Extract key information
            return {
                'type': 'zendesk',
                'file': pdf_path,
                'ticket_id': ticket_data.get('ticket_id', 'Unknown'),
                'summary': ticket_data.get('summary', 'No summary'),
                'description': ticket_data.get('description', ''),
                'impact_score': final_score,
                'priority': priority,
                'components': components,
                'cache_info': self._extract_cache_info(ticket_data.get('description', '')),
                'component': self._detect_component(ticket_data.get('description', '')),
                'environment': self._detect_organization(ticket_data.get('description', ''))
            }
        except Exception as e:
            print(f"    Error analyzing {pdf_path}: {e}")
            return {
                'type': 'zendesk',
                'file': pdf_path,
                'error': str(e)
            }
    
    def _analyze_jira_bug(self, pdf_path: str) -> Dict:
        """Analyze a single Jira bug PDF."""
        try:
            # Parse the bug
            parser = UniversalTicketParser(pdf_path)
            bug_data = parser.parse()
            
            # Extract key information
            return {
                'type': 'jira',
                'file': pdf_path,
                'ticket_id': bug_data.get('ticket_id', 'Unknown'),
                'summary': bug_data.get('summary', 'No summary'),
                'description': bug_data.get('description', ''),
                'priority': bug_data.get('priority', 'Unknown'),
                'severity': bug_data.get('severity', 'Unknown'),
                'component': self._detect_component(bug_data.get('description', '')),
                'environment': self._detect_organization(bug_data.get('description', '')),
                'cache_info': self._extract_cache_info(bug_data.get('description', ''))
            }
        except Exception as e:
            print(f"    Error analyzing {pdf_path}: {e}")
            return {
                'type': 'jira',
                'file': pdf_path,
                'error': str(e)
            }
    
    def _extract_cache_info(self, description: str) -> Dict:
        """Extract cache information from description."""
        import re
        cache_info = {}
        
        # Look for cache name patterns
        cache_match = re.search(r'cache name[:\s]+([^\s,]+)', description, re.IGNORECASE)
        if cache_match:
            cache_info['cache_name'] = cache_match.group(1)
        
        # Look for region patterns
        region_match = re.search(r'region[:\s]+([^\s,]+)', description, re.IGNORECASE)
        if region_match:
            cache_info['region'] = region_match.group(1)
        
        return cache_info
    
    def _detect_component(self, description: str) -> str:
        """Detect component from description."""
        description_lower = description.lower()
        
        if 'dmc' in description_lower:
            return 'DMC'
        elif 'redis' in description_lower:
            return 'Redis'
        elif 'cluster' in description_lower:
            return 'Cluster'
        else:
            return 'Unknown'
    
    def _detect_organization(self, description: str) -> str:
        """Detect affected organization."""
        description_lower = description.lower()
        
        if 'azure' in description_lower:
            return 'Azure'
        elif 'aws' in description_lower:
            return 'AWS'
        elif 'gcp' in description_lower:
            return 'GCP'
        else:
            return 'Unknown'
    
    def _generate_comprehensive_summary(self) -> Dict:
        """Generate comprehensive RCA summary from all analyzed tickets."""
        
        # Extract common patterns
        all_components = set()
        all_environments = set()
        all_cache_info = []
        impact_scores = []
        
        for ticket in self.analyzed_tickets + self.analyzed_bugs:
            if 'error' not in ticket:
                if ticket.get('component'):
                    all_components.add(ticket['component'])
                if ticket.get('environment'):
                    all_environments.add(ticket['environment'])
                if ticket.get('cache_info'):
                    all_cache_info.append(ticket['cache_info'])
                if ticket.get('impact_score'):
                    impact_scores.append(ticket['impact_score'])
        
        # Generate summary
        summary = self._create_incident_summary()
        timeline = self._create_incident_timeline()
        root_cause = self._create_root_cause_analysis()
        action_items = self._create_action_items()
        
        return {
            'incident_summary': summary,
            'incident_timeline': timeline,
            'root_cause_analysis': root_cause,
            'action_items': action_items,
            'affected_components': list(all_components),
            'affected_environments': list(all_environments),
            'cache_information': all_cache_info,
            'impact_scores': impact_scores,
            'analyzed_tickets': self.analyzed_tickets,
            'analyzed_bugs': self.analyzed_bugs
        }
    
    def _create_incident_summary(self) -> str:
        """Create comprehensive incident summary."""
        summary_parts = []
        
        # Count affected systems
        total_tickets = len(self.analyzed_tickets)
        total_bugs = len(self.analyzed_bugs)
        
        summary_parts.append(f"**Incident Overview:**")
        summary_parts.append(f"This incident affected multiple Azure clusters and resulted in {total_tickets} support tickets and {total_bugs} bug Jiras.")
        
        # Component analysis
        components = set()
        for ticket in self.analyzed_tickets + self.analyzed_bugs:
            if 'error' not in ticket and ticket.get('component'):
                components.add(ticket['component'])
        
        if components:
            summary_parts.append(f"**Primary Component:** {', '.join(components)}")
        
        # Cache information
        cache_names = []
        regions = []
        for ticket in self.analyzed_tickets + self.analyzed_bugs:
            if 'error' not in ticket and ticket.get('cache_info'):
                cache_info = ticket['cache_info']
                if cache_info.get('cache_name'):
                    cache_names.append(cache_info['cache_name'])
                if cache_info.get('region'):
                    regions.append(cache_info['region'])
        
        if cache_names:
            summary_parts.append(f"**Affected Caches:** {', '.join(set(cache_names))}")
        if regions:
            summary_parts.append(f"**Affected Regions:** {', '.join(set(regions))}")
        
        # Impact analysis
        if self.analyzed_tickets:
            avg_impact = sum(t.get('impact_score', 0) for t in self.analyzed_tickets if 'error' not in t) / len([t for t in self.analyzed_tickets if 'error' not in t and t.get('impact_score')])
            summary_parts.append(f"**Average Impact Score:** {avg_impact:.1f}")
        
        return '\n'.join(summary_parts)
    
    def _create_incident_timeline(self) -> str:
        """Create incident timeline."""
        timeline_parts = []
        
        timeline_parts.append("**Incident Timeline:**")
        timeline_parts.append("MMM-DD-YYYY, HH:MM - Initial reports received")
        timeline_parts.append("MMM-DD-YYYY, HH:MM - Multiple clusters affected")
        timeline_parts.append("MMM-DD-YYYY, HH:MM - Root cause identified")
        timeline_parts.append("MMM-DD-YYYY, HH:MM - Mitigation implemented")
        timeline_parts.append("MMM-DD-YYYY, HH:MM - Incident resolved")
        
        return '\n'.join(timeline_parts)
    
    def _create_root_cause_analysis(self) -> str:
        """Create root cause analysis."""
        rca_parts = []
        
        rca_parts.append("**Initial Root Cause Analysis:**")
        
        # Analyze common patterns
        cpu_issues = 0
        audit_issues = 0
        connection_issues = 0
        
        for ticket in self.analyzed_tickets + self.analyzed_bugs:
            if 'error' not in ticket:
                description = ticket.get('description', '').lower()
                if 'cpu' in description:
                    cpu_issues += 1
                if 'audit' in description:
                    audit_issues += 1
                if 'connection' in description:
                    connection_issues += 1
        
        if cpu_issues > 0:
            rca_parts.append(f"- High CPU utilization detected in {cpu_issues} tickets")
        if audit_issues > 0:
            rca_parts.append(f"- Audit logging issues identified in {audit_issues} tickets")
        if connection_issues > 0:
            rca_parts.append(f"- Connection problems reported in {connection_issues} tickets")
        
        rca_parts.append("\n**Preliminary Analysis:**")
        rca_parts.append("The incident appears to be related to DMC component issues affecting multiple Azure clusters. ")
        rca_parts.append("Common symptoms include high CPU utilization, audit logging problems, and connection issues.")
        rca_parts.append("Further investigation is needed to determine the root cause and implement preventive measures.")
        
        return '\n'.join(rca_parts)
    
    def _create_action_items(self) -> List[Dict]:
        """Create action items based on analysis."""
        action_items = []
        
        # Component-specific actions
        components = set()
        for ticket in self.analyzed_tickets + self.analyzed_bugs:
            if 'error' not in ticket and ticket.get('component'):
                components.add(ticket['component'])
        
        for component in components:
            action_items.append({
                'description': f'Investigate {component} component issues across all affected clusters',
                'type': 'Investigate',
                'owner': '@name',
                'ticket': '<jira-ticket>',
                'priority': 'High'
            })
        
        # Common action items
        action_items.extend([
            {
                'description': 'Review audit logging configuration and performance',
                'type': 'Investigate',
                'owner': '@name',
                'ticket': '<jira-ticket>',
                'priority': 'High'
            },
            {
                'description': 'Implement CPU monitoring and alerting improvements',
                'type': 'Prevent',
                'owner': '@name',
                'ticket': '<jira-ticket>',
                'priority': 'Medium'
            },
            {
                'description': 'Document incident response procedures for multi-cluster issues',
                'type': 'Mitigate',
                'owner': '@name',
                'ticket': '<jira-ticket>',
                'priority': 'Medium'
            }
        ])
        
        return action_items


def main():
    parser = argparse.ArgumentParser(
        description='Generate RCA summary from multiple PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --zendesk-pdfs ticket1.pdf ticket2.pdf --jira-pdfs bug1.pdf --customer "Azure" --date "10/24/25"
  %(prog)s --zendesk-pdfs *.pdf --customer "Customer" --date "10/24/25" --output summary.json
        """
    )
    
    parser.add_argument(
        '--zendesk-pdfs',
        nargs='+',
        help='Zendesk ticket PDF files to analyze'
    )
    
    parser.add_argument(
        '--jira-pdfs',
        nargs='+',
        help='Jira bug PDF files to analyze'
    )
    
    parser.add_argument(
        '--customer',
        required=True,
        help='Customer name'
    )
    
    parser.add_argument(
        '--date',
        required=True,
        help='Incident date (MM/DD/YY format)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for generated summary (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis'
    )
    
    args = parser.parse_args()
    
    if not args.zendesk_pdfs and not args.jira_pdfs:
        print("Error: Must provide at least one PDF file")
        sys.exit(1)
    
    print("="*80)
    print("RCA SUMMARY GENERATOR")
    print("="*80)
    print(f"Customer: {args.customer}")
    print(f"Date: {args.date}")
    if args.zendesk_pdfs:
        print(f"Zendesk PDFs: {', '.join(args.zendesk_pdfs)}")
    if args.jira_pdfs:
        print(f"Jira PDFs: {', '.join(args.jira_pdfs)}")
    print()
    
    try:
        generator = RCASummaryGenerator()
        summary_data = generator.analyze_tickets(
            zendesk_pdfs=args.zendesk_pdfs or [],
            jira_pdfs=args.jira_pdfs or []
        )
        
        print("\n" + "-"*80)
        print("GENERATED RCA SUMMARY")
        print("-"*80)
        print(summary_data['incident_summary'])
        
        print("\n" + "-"*80)
        print("INCIDENT TIMELINE")
        print("-"*80)
        print(summary_data['incident_timeline'])
        
        print("\n" + "-"*80)
        print("ROOT CAUSE ANALYSIS")
        print("-"*80)
        print(summary_data['root_cause_analysis'])
        
        print("\n" + "-"*80)
        print("ACTION ITEMS")
        print("-"*80)
        for i, item in enumerate(summary_data['action_items'], 1):
            print(f"{i}. {item['description']} ({item['type']}) - {item['priority']} Priority")
        
        if args.verbose:
            print("\n" + "-"*80)
            print("DETAILED ANALYSIS")
            print("-"*80)
            print(f"Affected Components: {', '.join(summary_data['affected_components'])}")
            print(f"Affected Environments: {', '.join(summary_data['affected_environments'])}")
            print(f"Impact Scores: {summary_data['impact_scores']}")
            
            print("\nAnalyzed Tickets:")
            for ticket in summary_data['analyzed_tickets']:
                if 'error' not in ticket:
                    print(f"  - {ticket['ticket_id']}: {ticket['summary']} (Score: {ticket.get('impact_score', 'N/A')})")
            
            print("\nAnalyzed Bugs:")
            for bug in summary_data['analyzed_bugs']:
                if 'error' not in bug:
                    print(f"  - {bug['ticket_id']}: {bug['summary']}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(summary_data, f, indent=2)
            print(f"\n✓ Summary saved to {args.output}")
    
    except Exception as e:
        print(f"\nError generating summary: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*80)
    print("RCA Summary Generation Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
