#!/usr/bin/env python3
"""
Generate Complete RCA with Auto-Generated Summary

This tool combines PDF analysis with cluster information to create
a comprehensive RCA with auto-generated summary, timeline, and action items.

Usage:
    python generate_complete_rca.py --customer "Azure" --date "10/24/25" \
      --zendesk-pdfs ticket1.pdf ticket2.pdf ticket3.pdf \
      --jira-pdfs bug1.pdf bug2.pdf \
      --clusters "cluster1" "cluster2" "cluster3" "cluster4" \
      --regions "region1" "region2" "region3" "region4"
"""

import sys
import argparse
import json
from pathlib import Path
from generate_rca_summary import RCASummaryGenerator
from create_multi_cluster_rca import create_multi_cluster_description


def main():
    parser = argparse.ArgumentParser(
        description='Generate complete RCA with auto-generated summary and cluster info',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --customer "Azure" --date "10/24/25" \
    --zendesk-pdfs ticket1.pdf ticket2.pdf ticket3.pdf \
    --jira-pdfs bug1.pdf bug2.pdf \
    --clusters "cluster1" "cluster2" "cluster3" "cluster4" \
    --regions "region1" "region2" "region3" "region4"
        """
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
        '--clusters',
        nargs='+',
        help='All affected cluster names'
    )
    
    parser.add_argument(
        '--regions',
        nargs='+',
        help='All affected regions'
    )
    
    parser.add_argument(
        '--components',
        nargs='+',
        help='All affected components'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for complete RCA (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("COMPLETE RCA GENERATOR")
    print("="*80)
    print(f"Customer: {args.customer}")
    print(f"Date: {args.date}")
    if args.zendesk_pdfs:
        print(f"Zendesk PDFs: {', '.join(args.zendesk_pdfs)}")
    if args.jira_pdfs:
        print(f"Jira PDFs: {', '.join(args.jira_pdfs)}")
    if args.clusters:
        print(f"Affected Clusters: {', '.join(args.clusters)}")
    if args.regions:
        print(f"Affected Regions: {', '.join(args.regions)}")
    print()
    
    try:
        # Step 1: Generate summary from PDFs
        print("Step 1: Analyzing PDFs to generate summary...")
        summary_generator = RCASummaryGenerator()
        pdf_analysis = summary_generator.analyze_tickets(
            zendesk_pdfs=args.zendesk_pdfs or [],
            jira_pdfs=args.jira_pdfs or []
        )
        
        # Step 2: Create enhanced description with cluster info
        print("Step 2: Creating comprehensive RCA description...")
        enhanced_description = create_enhanced_rca_description(
            customer_name=args.customer,
            date=args.date,
            clusters=args.clusters or [],
            regions=args.regions or [],
            components=args.components or [],
            pdf_analysis=pdf_analysis
        )
        
        # Step 3: Create complete RCA data
        print("Step 3: Generating complete RCA data...")
        complete_rca = {
            'project': 'Root Cause Analysis',
            'issue_type': 'RCA',
            'summary': f"{args.customer} - RCA {args.date}",
            'priority': 'Medium',
            'severity': 'Medium',
            'labels': [args.customer],
            'description': enhanced_description,
            'custom_fields': {
                'zendesk_tickets': [t.get('ticket_id', 'Unknown') for t in pdf_analysis['analyzed_tickets'] if 'error' not in t and t.get('ticket_id')],
                'jira_bugs': [b.get('ticket_id', 'Unknown') for b in pdf_analysis['analyzed_bugs'] if 'error' not in b and b.get('ticket_id')],
                'slack_channel': f"#prod-{args.date.replace('/', '')}-{args.customer.lower()}",
                'affected_clusters': args.clusters or [],
                'affected_regions': args.regions or [],
                'affected_components': args.components or [],
                'incident_scope': 'Multi-cluster' if args.clusters and len(args.clusters) > 1 else 'Single-cluster',
                'total_affected_clusters': len(args.clusters) if args.clusters else 0,
                'total_support_tickets': len(pdf_analysis['analyzed_tickets']),
                'total_bug_jiras': len(pdf_analysis['analyzed_bugs']),
                'average_impact_score': sum(pdf_analysis['impact_scores']) / len(pdf_analysis['impact_scores']) if pdf_analysis['impact_scores'] else 0
            },
            'linked_issues': [b.get('ticket_id', 'Unknown') for b in pdf_analysis['analyzed_bugs'] if 'error' not in b and b.get('ticket_id')],
            'auto_generated_summary': pdf_analysis['incident_summary'],
            'auto_generated_timeline': pdf_analysis['incident_timeline'],
            'auto_generated_root_cause': pdf_analysis['root_cause_analysis'],
            'auto_generated_action_items': pdf_analysis['action_items']
        }
        
        print("\n" + "-"*80)
        print("COMPLETE RCA DATA")
        print("-"*80)
        print(f"Project: {complete_rca['project']}")
        print(f"Issue Type: {complete_rca['issue_type']}")
        print(f"Summary: {complete_rca['summary']}")
        print(f"Priority: {complete_rca['priority']}")
        print(f"Severity: {complete_rca['severity']}")
        print(f"Labels: {', '.join(complete_rca['labels'])}")
        
        print(f"\nAuto-Generated Summary:")
        print(complete_rca['auto_generated_summary'])
        
        print(f"\nAuto-Generated Root Cause Analysis:")
        print(complete_rca['auto_generated_root_cause'])
        
        print(f"\nAuto-Generated Action Items:")
        for i, item in enumerate(complete_rca['auto_generated_action_items'], 1):
            print(f"{i}. {item['description']} ({item['type']}) - {item['priority']} Priority")
        
        if args.verbose:
            print(f"\nDetailed Analysis:")
            print(f"Affected Clusters: {', '.join(args.clusters or [])}")
            print(f"Affected Regions: {', '.join(args.regions or [])}")
            print(f"Affected Components: {', '.join(args.components or [])}")
            print(f"Total Support Tickets: {complete_rca['custom_fields']['total_support_tickets']}")
            print(f"Total Bug Jiras: {complete_rca['custom_fields']['total_bug_jiras']}")
            print(f"Average Impact Score: {complete_rca['custom_fields']['average_impact_score']:.1f}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(complete_rca, f, indent=2)
            print(f"\n✓ Complete RCA saved to {args.output}")
        
        print("\n" + "="*80)
        print("COMPLETE RCA GENERATION FINISHED!")
        print("="*80)
        print("Your RCA now includes:")
        print("✅ Auto-generated summary from PDF analysis")
        print("✅ Complete cluster information")
        print("✅ Auto-generated root cause analysis")
        print("✅ Auto-generated action items")
        print("✅ Timeline structure")
        print("✅ All ticket and bug information")
        print("✅ Ready for Jira form filling!")
    
    except Exception as e:
        print(f"\nError generating complete RCA: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def create_enhanced_rca_description(customer_name: str, date: str, 
                                  clusters: list, regions: list, components: list,
                                  pdf_analysis: dict) -> str:
    """Create enhanced RCA description combining PDF analysis with cluster info."""
    
    # Start with auto-generated summary
    description = f"**Summary:** {pdf_analysis['incident_summary']}\n\n"
    
    # Add cluster information
    if clusters:
        description += f"**Affected Clusters:** {', '.join(clusters)}\n"
    if regions:
        description += f"**Affected Regions:** {', '.join(regions)}\n"
    if components:
        description += f"**Affected Components:** {', '.join(components)}\n"
    
    description += f"\n**Date and Time (UTC)**\n"
    description += f"**Activity**\n"
    description += f"MMM-DD-YYYY, HH:MM <What happened/what has been done>\n\n"
    
    # Add ticket information
    zendesk_tickets = [t.get('ticket_id', 'Unknown') for t in pdf_analysis['analyzed_tickets'] if 'error' not in t and t.get('ticket_id')]
    jira_bugs = [b.get('ticket_id', 'Unknown') for b in pdf_analysis['analyzed_bugs'] if 'error' not in b and b.get('ticket_id')]
    
    if zendesk_tickets:
        description += f"**Related Zendesk Tickets:** {', '.join(zendesk_tickets)}\n"
    if jira_bugs:
        description += f"**Related Bug Jiras:** {', '.join(jira_bugs)}\n"
    
    # Add auto-generated root cause analysis
    description += f"\n**Initial Root Cause:** {pdf_analysis['root_cause_analysis']}\n\n"
    description += f"**Final Root Cause & Conclusions:** <Add your final RCA and Conclusions here>\n\n"
    
    # Add auto-generated action items
    action_items = pdf_analysis['action_items']
    if action_items:
        description += f"**Action item(s):**\n"
        description += f"After updating the table below, ensure the tickets are linked with the `relates to` type.\n\n"
        description += f"| Description | Type | Owner | Ticket | Priority |\n"
        description += f"|-------------|------|-------|--------|----------|\n"
        for item in action_items:
            description += f"| {item['description']} | {item['type']} | {item['owner']} | {item['ticket']} | {item['priority']} |\n"
    else:
        description += f"**Action item(s):**\n"
        description += f"After updating the table below, ensure the tickets are linked with the `relates to` type.\n\n"
        description += f"| Description | Type | Owner | Ticket | Priority |\n"
        description += f"|-------------|------|-------|--------|----------|\n"
        description += f"| <What is the AI about?> | Investigate or Prevent or Mitigate | @name | <jira-ticket> | <priority> |\n"
    
    return description


if __name__ == "__main__":
    main()
