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
        help='Output file for ticket data (default: auto-generated .md file in output/)'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'both'],
        default='markdown',
        help='Output format (default: markdown)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis'
    )

    parser.add_argument(
        '--use-claude',
        action='store_true',
        help='Use Claude AI for intelligent summary and description generation (requires ANTHROPIC_API_KEY)'
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
    if args.use_claude:
        print(f"AI Mode: Claude-powered description generation")
    print()

    # Initialize creator with optional Claude analyzer
    claude_analyzer = None
    if args.use_claude:
        try:
            from claude_analyzer import ClaudeAnalyzer
            import os
            if not os.environ.get('ANTHROPIC_API_KEY'):
                print("⚠ Error: ANTHROPIC_API_KEY environment variable not set")
                print("Please export your API key: export ANTHROPIC_API_KEY='your-key-here'")
                sys.exit(1)
            claude_analyzer = ClaudeAnalyzer()
            print("✓ Claude AI analyzer initialized")
        except ImportError:
            print("⚠ Error: anthropic package not installed. Run: pip install anthropic>=0.39.0")
            sys.exit(1)
        except Exception as e:
            print(f"⚠ Error initializing Claude analyzer: {e}")
            sys.exit(1)

    creator = JiraCreator(claude_analyzer=claude_analyzer)
    
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

            # Parse ticket to get components and scores
            from intelligent_estimator import IntelligentImpactEstimator
            estimator = IntelligentImpactEstimator(args.zendesk_file)
            estimator.load_data()
            ticket_info = estimator.extract_ticket_info()
            components = estimator.estimate_all_components()
            base_score, final_score, priority = estimator.calculate_impact_score(components)

            # Create bug data
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

            # Generate output files
            zendesk_id = bug_data.custom_fields.get('zendesk_id', 'Unknown')

            # Auto-generate output filename if not provided
            if not args.output:
                # Create output directory if it doesn't exist
                output_dir = Path('output')
                output_dir.mkdir(exist_ok=True)

                if args.format in ['markdown', 'both']:
                    output_file = output_dir / f"JIRA-{zendesk_id}.md"
                else:
                    output_file = output_dir / f"JIRA-{zendesk_id}.json"
            else:
                output_file = Path(args.output)

            # Save markdown format
            if args.format in ['markdown', 'both']:
                markdown_content = creator.generate_markdown(
                    jira_data=bug_data,
                    components=components,
                    zendesk_id=zendesk_id,
                    impact_score=final_score,
                    ticket_type='bug'
                )

                markdown_file = output_file if args.format == 'markdown' else output_file.with_suffix('.md')
                with open(markdown_file, 'w') as f:
                    f.write(markdown_content)
                print(f"\n✓ Markdown file saved to {markdown_file}")

            # Save JSON format
            if args.format in ['json', 'both']:
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
                    'linked_issues': bug_data.linked_issues,
                    'impact_score': final_score,
                    'components': components
                }

                json_file = output_file if args.format == 'json' else output_file.with_suffix('.json')
                with open(json_file, 'w') as f:
                    json.dump(ticket_data, f, indent=2)
                print(f"✓ JSON data saved to {json_file}")

            print("\n" + "="*80)
            print("NEXT STEPS")
            print("="*80)
            print("1. Review the generated markdown file")
            print("2. Copy and paste the markdown content into Jira")
            print("3. Verify all fields are correctly populated")
            print("4. Link any related tickets as needed")
            if args.format in ['markdown', 'both']:
                print(f"5. Markdown file: {markdown_file if args.format != 'json' else output_file.with_suffix('.md')}")
    
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
