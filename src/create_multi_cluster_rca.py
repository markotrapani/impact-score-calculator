#!/usr/bin/env python3
"""
Create Multi-Cluster RCA Ticket - Enhanced CLI Tool

This tool creates RCA tickets for incidents affecting multiple clusters,
with comprehensive linking to all related support tickets and bug Jiras.

Usage:
    python create_multi_cluster_rca.py --customer "Azure" --date "10/25/25" \
      --zendesk-tickets 146173 146983 146984 \
      --related-bugs RED-172012 RED-172013 \
      --clusters "rediscluster-ktcsproda11" "rediscluster-ktcsproda12" "rediscluster-ktcsproda13"
"""

import sys
import argparse
import json
from pathlib import Path
from jira_creator import JiraCreator


def main():
    parser = argparse.ArgumentParser(
        description='Create multi-cluster RCA tickets with comprehensive linking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --customer "Azure" --date "10/25/25" --zendesk-tickets 146173 146983 146984 --related-bugs RED-172012 RED-172013
  %(prog)s --customer "Customer Name" --date "10/25/25" --clusters "cluster1" "cluster2" "cluster3" --output multi_rca.json
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
        help='All Zendesk ticket IDs to link to RCA'
    )
    
    parser.add_argument(
        '--related-bugs',
        nargs='+',
        help='All related bug Jira keys to link to RCA'
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
        help='All affected components (e.g., DMC, Redis, Cluster)'
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
    
    args = parser.parse_args()
    
    print("="*80)
    print("MULTI-CLUSTER RCA TICKET CREATOR")
    print("="*80)
    print(f"Customer: {args.customer}")
    print(f"Date: {args.date}")
    if args.zendesk_tickets:
        print(f"Zendesk Tickets: {', '.join(args.zendesk_tickets)}")
    if args.related_bugs:
        print(f"Related Bugs: {', '.join(args.related_bugs)}")
    if args.clusters:
        print(f"Affected Clusters: {', '.join(args.clusters)}")
    if args.regions:
        print(f"Affected Regions: {', '.join(args.regions)}")
    if args.components:
        print(f"Affected Components: {', '.join(args.components)}")
    print()
    
    # Initialize creator
    creator = JiraCreator()
    
    try:
        print("Creating multi-cluster RCA ticket...")
        
        # Create enhanced RCA description for multi-cluster scenario
        description = create_multi_cluster_description(
            customer_name=args.customer,
            date=args.date,
            zendesk_tickets=args.zendesk_tickets,
            related_bugs=args.related_bugs,
            clusters=args.clusters,
            regions=args.regions,
            components=args.components
        )
        
        # Create RCA ticket data
        rca_data = creator.create_rca_ticket(
            customer_name=args.customer,
            date=args.date,
            zendesk_tickets=args.zendesk_tickets,
            related_bugs=args.related_bugs
        )
        
        # Override description with multi-cluster version
        rca_data.description = description
        
        # Add multi-cluster custom fields
        rca_data.custom_fields.update({
            'affected_clusters': args.clusters or [],
            'affected_regions': args.regions or [],
            'affected_components': args.components or [],
            'incident_scope': 'Multi-cluster' if args.clusters and len(args.clusters) > 1 else 'Single-cluster',
            'total_affected_clusters': len(args.clusters) if args.clusters else 0,
            'total_support_tickets': len(args.zendesk_tickets) if args.zendesk_tickets else 0,
            'total_bug_jiras': len(args.related_bugs) if args.related_bugs else 0
        })
        
        # Override slack channel if provided
        if args.slack_channel:
            rca_data.custom_fields['slack_channel'] = args.slack_channel
        
        print("\n" + "-"*80)
        print("MULTI-CLUSTER RCA TICKET DATA")
        print("-"*80)
        print(f"Project: {rca_data.project}")
        print(f"Issue Type: {rca_data.issue_type}")
        print(f"Summary: {rca_data.summary}")
        print(f"Priority: {rca_data.priority}")
        print(f"Severity: {rca_data.severity}")
        print(f"Labels: {', '.join(rca_data.labels)}")
        
        print("\nMulti-Cluster Information:")
        if args.clusters:
            print(f"  Affected Clusters: {', '.join(args.clusters)}")
        if args.regions:
            print(f"  Affected Regions: {', '.join(args.regions)}")
        if args.components:
            print(f"  Affected Components: {', '.join(args.components)}")
        
        print(f"\nLinked Tickets:")
        if args.zendesk_tickets:
            print(f"  Zendesk Tickets: {', '.join(args.zendesk_tickets)}")
        if args.related_bugs:
            print(f"  Bug Jiras: {', '.join(args.related_bugs)}")
        
        print("\nCustom Fields:")
        for field, value in rca_data.custom_fields.items():
            if value:
                if isinstance(value, list):
                    print(f"  {field}: {', '.join(map(str, value))}")
                else:
                    print(f"  {field}: {value}")
        
        if args.verbose:
            print(f"\nDescription Preview:")
            print(f"{rca_data.description[:1000]}...")
        
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
            print(f"\n✓ Multi-cluster RCA ticket data saved to {args.output}")
        
        print("\n" + "-"*80)
        print("MULTI-CLUSTER RCA TEMPLATE FIELDS TO FILL")
        print("-"*80)
        print("1. Summary: Add comprehensive incident summary covering all clusters")
        print("2. Initial Root Cause: Add preliminary understanding of multi-cluster impact")
        print("3. Final Root Cause: Add detailed analysis of root cause")
        print("4. Action Items: Add table with action items for each cluster/component")
        print("5. Timeline: Add detailed incident timeline across all clusters")
        print("6. Contributors: Add all incident participants")
        print("7. Cluster Details: Add specific information for each affected cluster")
        print("8. Account Details: Add customer account information")
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("1. Create the RCA ticket in Jira with the above fields")
        print("2. Fill in the multi-cluster template sections in the description")
        print("3. Link ALL related Zendesk tickets and bug Jiras")
        print("4. Add contributors and assign appropriate team members")
        print("5. Update status to 'Root Cause and Action Items' when ready")
        if args.output:
            print(f"6. Use the JSON data in {args.output} for automation")
    
    except Exception as e:
        print(f"\nError creating multi-cluster RCA ticket: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*80)
    print("Multi-Cluster RCA Ticket Creation Complete!")
    print("="*80)


def create_multi_cluster_description(customer_name: str, date: str, 
                                    zendesk_tickets: list, related_bugs: list,
                                    clusters: list, regions: list, components: list) -> str:
    """Create enhanced RCA description for multi-cluster scenarios."""
    
    description = f"**Summary:** <Add comprehensive incident summary covering all affected clusters>\n\n"
    
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
    if zendesk_tickets:
        description += f"**Related Zendesk Tickets:** {', '.join(zendesk_tickets)}\n"
    if related_bugs:
        description += f"**Related Bug Jiras:** {', '.join(related_bugs)}\n"
    
    description += f"\n**Initial Root Cause:** <Add preliminary understanding of multi-cluster impact>\n\n"
    description += f"**Final Root Cause & Conclusions:** <Add detailed analysis of root cause>\n\n"
    
    # Enhanced action items for multi-cluster
    description += f"**Action item(s):**\n"
    description += f"After updating the table below, ensure the tickets are linked with the `relates to` type.\n\n"
    description += f"| Description | Type | Owner | Ticket | Cluster |\n"
    description += f"|-------------|------|-------|--------|----------|\n"
    
    # Generate action items for each cluster/component
    if clusters:
        for cluster in clusters:
            description += f"| Investigate {cluster} cluster impact | Investigate | @name | <jira-ticket> | {cluster} |\n"
    
    if components:
        for component in components:
            description += f"| Review {component} component across all clusters | Investigate | @name | <jira-ticket> | All |\n"
    
    # Default action items
    description += f"| Implement preventive measures across all clusters | Prevent | @name | <jira-ticket> | All |\n"
    description += f"| Document multi-cluster incident response | Mitigate | @name | <jira-ticket> | All |\n"
    
    return description


if __name__ == "__main__":
    main()
