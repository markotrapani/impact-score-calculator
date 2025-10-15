#!/usr/bin/env python3
"""
Jira Impact Score Estimator - For Individual Tickets

This tool estimates impact scores for individual Jira tickets by prompting the user
for each scoring component when the data isn't available in the export.

Usage:
    python estimate_impact_score.py [jira_export.xlsx]
    python estimate_impact_score.py --interactive
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Tuple
import pandas as pd


class ImpactScoreEstimator:
    """Interactive impact score estimator for individual Jira tickets."""
    
    # Scoring definitions
    SEVERITY_OPTIONS = {
        'P1': (38, 'Service stopped with no backup/redundancy, multiple services degraded, immediate financial/security impact'),
        'P2': (30, 'Single service degraded, immediate financial/security impact'),
        'P3': (22, 'Non-critical service stopped/degraded, critical service at risk, possible financial impact'),
        'P4': (16, 'Non-critical service at risk'),
        'P5': (8, 'No current or potential impact (informational)'),
    }
    
    ARR_OPTIONS = {
        '1': (15, 'ARR > $1M'),
        '2': (13, '$1M > ARR > $500K'),
        '3': (10, '$500K > ARR > $100K'),
        '4': (8, '>10 low ARR customers'),
        '5': (5, '<10 low ARR customers'),
        '6': (0, 'Single low ARR customer'),
    }
    
    SLA_OPTIONS = {
        'Y': (8, 'SLA breached or manual recovery required'),
        'N': (0, 'SLA not breached or automatic recovery'),
    }
    
    FREQUENCY_OPTIONS = {
        '1': (0, '1 occurrence'),
        '2': (8, '2-4 occurrences'),
        '3': (16, '>4 occurrences'),
    }
    
    WORKAROUND_OPTIONS = {
        '1': (5, 'Simple workaround (single command), no performance impact'),
        '2': (10, 'Complex workaround (multiple steps), no performance impact'),
        '3': (12, 'Workaround available with performance impact'),
        '4': (15, 'No workaround; fix requires new version'),
    }
    
    RCA_OPTIONS = {
        'Y': (8, 'Ticket is part of RCA action items'),
        'N': (0, 'Ticket is not part of RCA action items'),
    }
    
    @staticmethod
    def try_extract_from_excel(file_path: str) -> Optional[Dict]:
        """Try to extract impact score data from Jira Excel export."""
        try:
            df = pd.read_excel(file_path)
            
            # Check if this is a batch format (has the right columns)
            if 'Impact & Severity\nMax 38' in df.columns:
                return {
                    'jira_id': df['Jira'].values[0] if 'Jira' in df.columns else 'Unknown',
                    'impact_severity': int(df['Impact & Severity\nMax 38'].values[0]),
                    'customer_arr': int(df['Customer ARR\nMax 15'].values[0]),
                    'sla_breach': int(df['SLA Breach\nMax 8'].values[0]),
                    'frequency': int(df['Frequency\nMax 16'].values[0]),
                    'workaround': int(df['Workaround\nMax 15'].values[0]),
                    'rca_action_item': int(df['RCA Action Item\nMax 8'].values[0]),
                    'support_multiplier': float(df.get('Support Multiplier\n(optional) 0-15%', [0])[0]),
                    'account_multiplier': float(df.get('Account Multiplier\n(optional) 0-15%', [0])[0]),
                }
            
            # Try to extract from single ticket export
            jira_id = df['Issue key'].values[0] if 'Issue key' in df.columns else 'Unknown'
            impact_score = df['Custom field (Impact Score)'].values[0] if 'Custom field (Impact Score)' in df.columns else None
            
            if pd.notna(impact_score):
                print(f"Found existing Impact Score: {impact_score}")
                print("Note: Individual component scores are not available in this export format.")
                print("The scores are stored as an image/screenshot, not as data fields.")
                return None
            
            return None
            
        except Exception as e:
            print(f"Could not extract data from Excel: {e}")
            return None
    
    @staticmethod
    def prompt_severity() -> int:
        """Prompt user to select severity/impact level."""
        print("\n" + "="*80)
        print("1. IMPACT & SEVERITY (Max 38 points)")
        print("="*80)
        for key, (score, desc) in ImpactScoreEstimator.SEVERITY_OPTIONS.items():
            print(f"  {key} ({score:2d} pts): {desc}")
        
        while True:
            choice = input("\nSelect priority level (P1-P5): ").strip().upper()
            if choice in ImpactScoreEstimator.SEVERITY_OPTIONS:
                score, _ = ImpactScoreEstimator.SEVERITY_OPTIONS[choice]
                print(f"✓ Selected: {choice} = {score} points")
                return score
            print("Invalid choice. Please select P1, P2, P3, P4, or P5.")
    
    @staticmethod
    def prompt_arr() -> int:
        """Prompt user to select customer ARR level."""
        print("\n" + "="*80)
        print("2. CUSTOMER ARR (Max 15 points)")
        print("="*80)
        for key, (score, desc) in ImpactScoreEstimator.ARR_OPTIONS.items():
            print(f"  {key} ({score:2d} pts): {desc}")
        
        while True:
            choice = input("\nSelect ARR level (1-6): ").strip()
            if choice in ImpactScoreEstimator.ARR_OPTIONS:
                score, _ = ImpactScoreEstimator.ARR_OPTIONS[choice]
                print(f"✓ Selected: {score} points")
                return score
            print("Invalid choice. Please select 1-6.")
    
    @staticmethod
    def prompt_sla() -> int:
        """Prompt user for SLA breach status."""
        print("\n" + "="*80)
        print("3. SLA BREACH (Max 8 points)")
        print("="*80)
        for key, (score, desc) in ImpactScoreEstimator.SLA_OPTIONS.items():
            print(f"  {key} ({score} pts): {desc}")
        
        while True:
            choice = input("\nWas SLA breached? (Y/N): ").strip().upper()
            if choice in ImpactScoreEstimator.SLA_OPTIONS:
                score, _ = ImpactScoreEstimator.SLA_OPTIONS[choice]
                print(f"✓ Selected: {score} points")
                return score
            print("Invalid choice. Please enter Y or N.")
    
    @staticmethod
    def prompt_frequency() -> int:
        """Prompt user for frequency of occurrence."""
        print("\n" + "="*80)
        print("4. FREQUENCY (Max 16 points)")
        print("="*80)
        for key, (score, desc) in ImpactScoreEstimator.FREQUENCY_OPTIONS.items():
            print(f"  {key} ({score:2d} pts): {desc}")
        
        while True:
            choice = input("\nSelect frequency (1-3): ").strip()
            if choice in ImpactScoreEstimator.FREQUENCY_OPTIONS:
                score, _ = ImpactScoreEstimator.FREQUENCY_OPTIONS[choice]
                print(f"✓ Selected: {score} points")
                return score
            print("Invalid choice. Please select 1, 2, or 3.")
    
    @staticmethod
    def prompt_workaround() -> int:
        """Prompt user for workaround availability."""
        print("\n" + "="*80)
        print("5. WORKAROUND (Max 15 points)")
        print("="*80)
        for key, (score, desc) in ImpactScoreEstimator.WORKAROUND_OPTIONS.items():
            print(f"  {key} ({score:2d} pts): {desc}")
        
        while True:
            choice = input("\nSelect workaround option (1-4): ").strip()
            if choice in ImpactScoreEstimator.WORKAROUND_OPTIONS:
                score, _ = ImpactScoreEstimator.WORKAROUND_OPTIONS[choice]
                print(f"✓ Selected: {score} points")
                return score
            print("Invalid choice. Please select 1-4.")
    
    @staticmethod
    def prompt_rca() -> int:
        """Prompt user for RCA action item status."""
        print("\n" + "="*80)
        print("6. RCA ACTION ITEM (Max 8 points)")
        print("="*80)
        for key, (score, desc) in ImpactScoreEstimator.RCA_OPTIONS.items():
            print(f"  {key} ({score} pts): {desc}")
        
        while True:
            choice = input("\nIs this part of RCA action items? (Y/N): ").strip().upper()
            if choice in ImpactScoreEstimator.RCA_OPTIONS:
                score, _ = ImpactScoreEstimator.RCA_OPTIONS[choice]
                print(f"✓ Selected: {score} points")
                return score
            print("Invalid choice. Please enter Y or N.")
    
    @staticmethod
    def prompt_multipliers() -> Tuple[float, float]:
        """Prompt user for optional multipliers."""
        print("\n" + "="*80)
        print("7. OPTIONAL MULTIPLIERS (0-30% total)")
        print("="*80)
        
        print("\nSupport Multiplier (0-15%): For bugs blocking releases or high service risk")
        while True:
            try:
                support = input("Enter support multiplier percentage (0-15) or press Enter for 0: ").strip()
                if support == '':
                    support_mult = 0.0
                    break
                support_mult = float(support) / 100
                if 0 <= support_mult <= 0.15:
                    break
                print("Please enter a value between 0 and 15.")
            except ValueError:
                print("Please enter a valid number.")
        
        print(f"✓ Support Multiplier: {support_mult:.0%}")
        
        print("\nAccount Multiplier (0-15%): For impact on deals, customer confidence, etc.")
        while True:
            try:
                account = input("Enter account multiplier percentage (0-15) or press Enter for 0: ").strip()
                if account == '':
                    account_mult = 0.0
                    break
                account_mult = float(account) / 100
                if 0 <= account_mult <= 0.15:
                    break
                print("Please enter a value between 0 and 15.")
            except ValueError:
                print("Please enter a valid number.")
        
        print(f"✓ Account Multiplier: {account_mult:.0%}")
        
        return support_mult, account_mult
    
    @staticmethod
    def calculate_score(components: Dict) -> Tuple[float, float, str]:
        """Calculate impact score from components."""
        base_score = (
            components['impact_severity'] +
            components['customer_arr'] +
            components['sla_breach'] +
            components['frequency'] +
            components['workaround'] +
            components['rca_action_item']
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
    
    @staticmethod
    def display_results(components: Dict, base_score: float, final_score: float, priority: str):
        """Display calculation results."""
        print("\n" + "="*80)
        print("IMPACT SCORE CALCULATION RESULTS")
        print("="*80)
        
        print("\nComponent Breakdown:")
        print(f"  Impact & Severity:    {components['impact_severity']:2d} points")
        print(f"  Customer ARR:         {components['customer_arr']:2d} points")
        print(f"  SLA Breach:           {components['sla_breach']:2d} points")
        print(f"  Frequency:            {components['frequency']:2d} points")
        print(f"  Workaround:           {components['workaround']:2d} points")
        print(f"  RCA Action Item:      {components['rca_action_item']:2d} points")
        print(f"  {'─'*40}")
        print(f"  BASE SCORE:           {base_score:.0f} points")
        
        if components['support_multiplier'] > 0 or components['account_multiplier'] > 0:
            print(f"\nMultipliers Applied:")
            print(f"  Support Multiplier:   {components['support_multiplier']:.0%}")
            print(f"  Account Multiplier:   {components['account_multiplier']:.0%}")
            print(f"  Total Multiplier:     {components['support_multiplier'] + components['account_multiplier']:.0%}")
        
        print(f"\n{'='*80}")
        print(f"  FINAL IMPACT SCORE:   {final_score} points")
        print(f"  PRIORITY LEVEL:       {priority}")
        print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(
        description='Estimate impact score for individual Jira tickets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Optional: Path to Jira Excel export'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Force interactive mode (ignore Excel data)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("JIRA TICKET IMPACT SCORE ESTIMATOR")
    print("="*80)
    
    components = None
    
    # Try to extract from file if provided and not in force-interactive mode
    if args.file and not args.interactive:
        print(f"\nAttempting to extract data from: {args.file}")
        components = ImpactScoreEstimator.try_extract_from_excel(args.file)
    
    # If no data extracted or force-interactive, use interactive mode
    if components is None:
        print("\nEntering INTERACTIVE MODE - Please answer the following questions:\n")
        
        components = {
            'impact_severity': ImpactScoreEstimator.prompt_severity(),
            'customer_arr': ImpactScoreEstimator.prompt_arr(),
            'sla_breach': ImpactScoreEstimator.prompt_sla(),
            'frequency': ImpactScoreEstimator.prompt_frequency(),
            'workaround': ImpactScoreEstimator.prompt_workaround(),
            'rca_action_item': ImpactScoreEstimator.prompt_rca(),
        }
        
        support_mult, account_mult = ImpactScoreEstimator.prompt_multipliers()
        components['support_multiplier'] = support_mult
        components['account_multiplier'] = account_mult
    
    # Calculate score
    base_score, final_score, priority = ImpactScoreEstimator.calculate_score(components)
    
    # Display results
    ImpactScoreEstimator.display_results(components, base_score, final_score, priority)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
