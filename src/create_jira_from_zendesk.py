#!/usr/bin/env python3
"""
Create Jira from Zendesk - CLI Tool

This tool analyzes Zendesk ticket PDFs and creates Jira tickets with proper
field mapping and impact score calculation.

Usage:
    python create_jira_from_zendesk.py zendesk_ticket.pdf
    python create_jira_from_zendesk.py zendesk_ticket.pdf --suggest-only
    python create_jira_from_zendesk.py zendesk_ticket.pdf --project MOD --output ticket_data.json
"""

import sys
import argparse
import json
from pathlib import Path
from jira_creator import JiraCreator


def main():
    parser = argparse.ArgumentParser(
        description='Create Jira tickets from Zendesk PDFs with impact scores',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s customer_issue.pdf
  %(prog)s zendesk_ticket.pdf --suggest-only
  %(prog)s ticket.pdf --project MOD --output ticket_data.json
  %(prog)s ticket.pdf --project RED --assignee john.doe
        """
    )
    
    parser.add_argument(
        'zendesk_file',
        help='Path to Zendesk PDF file'
    )
    
    parser.add_argument(
        '--suggest-only',
        action='store_true',
        help='Only suggest Jira fields, do not create ticket'
    )
    
    parser.add_argument(
        '--project',
        choices=['RED', 'MOD', 'DOC', 'RDSC'],
        default='RED',
        help='Jira project for the ticket (default: RED)'
    )
    
    parser.add_argument(
        '--assignee',
        help='Assignee for the ticket'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for ticket data (JSON format)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.zendesk_file).exists():
        print(f"Error: File not found: {args.zendesk_file}")
        sys.exit(1)
    
    print("="*80)
    print("ZENDESK TO JIRA TICKET CREATOR")
    print("="*80)
    print(f"Input File: {args.zendesk_file}")
    print(f"Project: {args.project}")
    print()
    
    # Initialize creator
    creator = JiraCreator()
    
    try:
        if args.suggest_only:
            print("Analyzing Zendesk ticket for Jira field suggestions...")
            suggestions = creator.suggest_jira_fields(args.zendesk_file)
            
            print("\n" + "-"*80)
            print("ZENDESK TICKET ANALYSIS")
            print("-"*80)
            print(f"Zendesk ID: {suggestions['ticket_info']['zendesk_id']}")
            print(f"Summary: {suggestions['ticket_info']['summary']}")
            print(f"Description: {suggestions['ticket_info']['description']}")
            
            print("\n" + "-"*80)
            print("IMPACT SCORE ANALYSIS")
            print("-"*80)
            print(f"Final Score: {suggestions['impact_analysis']['final_score']}")
            print(f"Base Score: {suggestions['impact_analysis']['base_score']}")
            print(f"Priority Level: {suggestions['impact_analysis']['priority']}")
            
            print("\nComponent Breakdown:")
            for component, data in suggestions['impact_analysis']['components'].items():
                print(f"  {component.replace('_', ' ').title()}: {data['score']} points")
                if args.verbose:
                    print(f"    → {data['reason']}")
            
            print("\n" + "-"*80)
            print("SUGGESTED JIRA FIELDS")
            print("-"*80)
            jira_fields = suggestions['suggested_jira_fields']
            print(f"Project: {jira_fields['project']}")
            print(f"Issue Type: {jira_fields['issue_type']}")
            print(f"Priority: {jira_fields['priority']}")
            print(f"Severity: {jira_fields['severity']}")
            print(f"Labels: {', '.join(jira_fields['labels'])}")
            print(f"Component: {jira_fields['component']}")
            print(f"Environment: {jira_fields['environment']}")
            
            print("\nCustom Fields:")
            for field, value in jira_fields['custom_fields'].items():
                if value is not None:
                    print(f"  {field}: {value}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(suggestions, f, indent=2)
                print(f"\n✓ Suggestions saved to {args.output}")
        
        else:
            print("Creating Jira ticket from Zendesk...")
            bug_data = creator.create_bug_from_zendesk(args.zendesk_file, args.project)
            
            # Override assignee if provided
            if args.assignee:
                bug_data.assignee = args.assignee
            
            print("\n" + "-"*80)
            print("JIRA TICKET DATA")
            print("-"*80)
            print(f"Project: {bug_data.project}")
            print(f"Issue Type: {bug_data.issue_type}")
            print(f"Summary: {bug_data.summary}")
            print(f"Priority: {bug_data.priority}")
            print(f"Severity: {bug_data.severity}")
            if bug_data.assignee:
                print(f"Assignee: {bug_data.assignee}")
            print(f"Labels: {', '.join(bug_data.labels)}")
            
            print("\nCustom Fields:")
            for field, value in bug_data.custom_fields.items():
                if value is not None:
                    print(f"  {field}: {value}")
            
            if args.verbose:
                print(f"\nDescription Preview:")
                print(f"{bug_data.description[:500]}...")
            
            if args.output:
                ticket_data = {
                    'project': bug_data.project,
                    'issue_type': bug_data.issue_type,
                    'summary': bug_data.summary,
                    'description': bug_data.description,
                    'priority': bug_data.priority,
                    'severity': bug_data.severity,
                    'assignee': bug_data.assignee,
                    'labels': bug_data.labels,
                    'custom_fields': bug_data.custom_fields,
                    'linked_issues': bug_data.linked_issues
                }
                
                with open(args.output, 'w') as f:
                    json.dump(ticket_data, f, indent=2)
                print(f"\n✓ Ticket data saved to {args.output}")
            
            print("\n" + "="*80)
            print("NEXT STEPS")
            print("="*80)
            print("1. Review the suggested Jira fields above")
            print("2. Create the ticket in Jira with these fields")
            print("3. Link the Zendesk ticket in the description")
            print("4. Update the Impact Score custom field with the calculated value")
            if args.output:
                print(f"5. Use the JSON data in {args.output} for automation")
    
    except Exception as e:
        print(f"\nError processing file: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*80)
    print("Processing Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
