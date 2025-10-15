#!/usr/bin/env python3
"""
Jira Impact Score Calculator - Command Line Tool

Simple command-line interface for processing Jira Excel exports and calculating impact scores.

Usage:
    python calculate_jira_scores.py <input_excel_file> [options]
    
Examples:
    python calculate_jira_scores.py jira_export.xlsx
    python calculate_jira_scores.py jira_export.xlsx --output results.xlsx
    python calculate_jira_scores.py jira_export.xlsx --top 20
    python calculate_jira_scores.py jira_export.xlsx --sheet "Sheet1"
"""

import sys
import argparse
from pathlib import Path
from jira_impact_score_processor import JiraImpactScoreProcessor


def main():
    parser = argparse.ArgumentParser(
        description='Calculate Jira ticket impact scores from Excel export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s jira_export.xlsx
  %(prog)s jira_export.xlsx --output results.xlsx
  %(prog)s jira_export.xlsx --top 20 --priority CRITICAL
  %(prog)s jira_export.xlsx --sheet "Calculation" --validate
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to Jira Excel export file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output Excel file path (default: <input>_processed.xlsx)',
        default=None
    )
    
    parser.add_argument(
        '-s', '--sheet',
        help='Sheet name to process (default: Calculation)',
        default='Calculation'
    )
    
    parser.add_argument(
        '-t', '--top',
        type=int,
        help='Show top N priority tickets (default: 10)',
        default=10
    )
    
    parser.add_argument(
        '-p', '--priority',
        choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL', 'ALL'],
        help='Filter by priority level',
        default='ALL'
    )
    
    parser.add_argument(
        '-v', '--validate',
        action='store_true',
        help='Validate calculated scores against existing scores'
    )
    
    parser.add_argument(
        '--no-export',
        action='store_true',
        help='Skip exporting results to Excel'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Show only summary statistics, no ticket details'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = str(input_path.parent / f"{input_path.stem}_processed.xlsx")
    
    print("=" * 80)
    print("JIRA IMPACT SCORE CALCULATOR")
    print("=" * 80)
    print(f"\nInput File:  {args.input_file}")
    print(f"Sheet Name:  {args.sheet}")
    if not args.no_export:
        print(f"Output File: {output_path}")
    print()
    
    # Initialize processor
    try:
        processor = JiraImpactScoreProcessor(args.input_file)
        
        # Load data
        print("Loading data...")
        processor.load_data(sheet_name=args.sheet)
        
        # Calculate scores
        print("Calculating impact scores...")
        results = processor.calculate_scores()
        
        # Validate if requested
        if args.validate:
            print("\nValidating calculations...")
            is_valid, discrepancies = processor.validate_scores()
            if is_valid:
                print("✓ All calculated scores match existing scores!")
            else:
                print(f"⚠ Found {len(discrepancies)} discrepancies:")
                for disc in discrepancies[:10]:  # Show first 10
                    print(f"  - {disc}")
                if len(discrepancies) > 10:
                    print(f"  ... and {len(discrepancies) - 10} more")
        
        # Get summary statistics
        print("\n" + "-" * 80)
        print("SUMMARY STATISTICS")
        print("-" * 80)
        stats = processor.get_summary_stats()
        print(f"Total Tickets:  {stats['total_tickets']}")
        print(f"Average Score:  {stats['average_score']:.1f}")
        print(f"Median Score:   {stats['median_score']:.1f}")
        print(f"Score Range:    {stats['min_score']:.1f} - {stats['max_score']:.1f}")
        
        print("\nPriority Distribution:")
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']:
            count = stats['priority_distribution'].get(priority, 0)
            if count > 0:
                percentage = (count / stats['total_tickets']) * 100
                print(f"  {priority:8s}: {count:3d} tickets ({percentage:5.1f}%)")
        
        # Show top priorities unless stats-only
        if not args.stats_only:
            print("\n" + "-" * 80)
            if args.priority != 'ALL':
                print(f"TOP {args.top} {args.priority} PRIORITY TICKETS")
                filtered = results[results['priority_level'] == args.priority]
                top_tickets = filtered.nlargest(args.top, 'calculated_impact_score')
            else:
                print(f"TOP {args.top} PRIORITY TICKETS")
                top_tickets = processor.get_top_priorities(n=args.top)
            
            print("-" * 80)
            
            if len(top_tickets) == 0:
                print(f"No tickets found with priority: {args.priority}")
            else:
                for idx, row in top_tickets.iterrows():
                    jira_id = str(row.get('jira', 'N/A')) if row.get('jira') else 'N/A'
                    score = row['calculated_impact_score']
                    priority = row['priority_level']
                    person = str(row.get('person', 'Unassigned')) if row.get('person') else 'Unassigned'
                    print(f"  {jira_id:12s} | Score: {score:6.1f} | {priority:8s} | {person}")
        
        # Export results
        if not args.no_export:
            print("\n" + "-" * 80)
            print("EXPORTING RESULTS")
            print("-" * 80)
            processor.export_results(output_path)
            print(f"✓ Results saved to: {output_path}")
        
        print("\n" + "=" * 80)
        print("Processing Complete!")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
