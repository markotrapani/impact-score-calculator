#!/usr/bin/env python3
"""
Create RCA Ticket - CLI Tool

This tool creates RCA (Root Cause Analysis) tickets based on the template
from your Confluence documentation.

Usage:
    python create_rca_ticket.py --customer "Customer Name" --date "10/25/25"
    python create_rca_ticket.py --customer "Azure" --date "10/25/25" --zendesk-tickets 131142 131143
"""

import sys
import argparse
import json
from pathlib import Path
from jira_creator import JiraCreator


def main():
    parser = argparse.ArgumentParser(
        description='Create RCA tickets based on template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --customer "Customer Name" --date "10/25/25"
  %(prog)s --customer "Azure" --date "10/25/25" --zendesk-tickets 131142 131143
  %(prog)s --customer "Biocatch" --date "10/25/25" --related-bugs RED-172012 MOD-12345
        """
    )
    
    parser.add_argument(
        '--customer',
        required=True,
        help='Customer name for the RCA ticket'
    )
    
    parser.add_argument(
        '--date',
        required=True,
        help='Date for RCA ticket (MM/DD/YY format)'
    )
    
    parser.add_argument(
        '--zendesk-tickets',
        nargs='+',
        help='Zendesk ticket IDs to link to RCA'
    )
    
    parser.add_argument(
        '--related-bugs',
        nargs='+',
        help='Related bug Jira keys to link to RCA'
    )
    
    parser.add_argument(
        '--slack-channel',
        help='Slack channel name (auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for RCA ticket data (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed RCA ticket information'
    )
    
    parser.add_argument(
        '--bug-jira-file',
        help='Path to bug Jira PDF for auto-population'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("RCA TICKET CREATOR")
    print("="*80)
    print(f"Customer: {args.customer}")
    print(f"Date: {args.date}")
    if args.zendesk_tickets:
        print(f"Zendesk Tickets: {', '.join(args.zendesk_tickets)}")
    if args.related_bugs:
        print(f"Related Bugs: {', '.join(args.related_bugs)}")
    print()
    
    # Initialize creator
    creator = JiraCreator()
    
    try:
        print("Creating RCA ticket...")
        rca_data = creator.create_rca_ticket(
            customer_name=args.customer,
            date=args.date,
            zendesk_tickets=args.zendesk_tickets,
            related_bugs=args.related_bugs,
            bug_jira_file=args.bug_jira_file
        )
        
        # Override slack channel if provided
        if args.slack_channel:
            rca_data.custom_fields['slack_channel'] = args.slack_channel
        
        print("\n" + "-"*80)
        print("RCA TICKET DATA")
        print("-"*80)
        print(f"Project: {rca_data.project}")
        print(f"Issue Type: {rca_data.issue_type}")
        print(f"Summary: {rca_data.summary}")
        print(f"Priority: {rca_data.priority}")
        print(f"Severity: {rca_data.severity}")
        print(f"Labels: {', '.join(rca_data.labels)}")
        
        print("\nCustom Fields:")
        for field, value in rca_data.custom_fields.items():
            if value:
                if isinstance(value, list):
                    print(f"  {field}: {', '.join(map(str, value))}")
                else:
                    print(f"  {field}: {value}")
        
        if args.related_bugs:
            print(f"\nLinked Issues: {', '.join(rca_data.linked_issues)}")
        
        if args.verbose:
            print(f"\nDescription Preview:")
            print(f"{rca_data.description[:800]}...")
        
        if args.output:
            ticket_data = {
                'project': rca_data.project,
                'issue_type': rca_data.issue_type,
                'summary': rca_data.summary,
                'description': rca_data.description,
                'priority': rca_data.priority,
                'severity': rca_data.severity,
                'labels': rca_data.labels,
                'custom_fields': rca_data.custom_fields,
                'linked_issues': rca_data.linked_issues
            }
            
            with open(args.output, 'w') as f:
                json.dump(ticket_data, f, indent=2)
            print(f"\n✓ RCA ticket data saved to {args.output}")
        
        print("\n" + "-"*80)
        print("RCA TEMPLATE FIELDS TO FILL")
        print("-"*80)
        print("1. Summary: Add incident summary")
        print("2. Initial Root Cause: Add preliminary understanding")
        print("3. Final Root Cause: Add detailed analysis")
        print("4. Action Items: Add table with action items")
        print("5. Timeline: Add detailed incident timeline")
        print("6. Contributors: Add all incident participants")
        print("7. Cluster ID: Add affected cluster information")
        print("8. Account ID: Add customer account details")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Create the RCA ticket in Jira with the above fields")
        print("2. Fill in the template sections in the description")
        print("3. Link all related Zendesk tickets and bug Jiras")
        print("4. Add contributors and assign appropriate team members")
        print("5. Update status to 'Root Cause and Action Items' when ready")
        if args.output:
            print(f"6. Use the JSON data in {args.output} for automation")
    
    except Exception as e:
        print(f"\nError creating RCA ticket: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*80)
    print("RCA Ticket Creation Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
