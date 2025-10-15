"""
Jira Impact Score Calculator - Excel Processor

This module processes Excel exports from Jira and calculates impact scores
for ticket prioritization.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImpactScoreComponents:
    """Data class to hold all components of the impact score calculation."""
    impact_severity: int
    customer_arr: int
    sla_breach: int
    frequency: int
    workaround: int
    rca_action_item: int
    support_multiplier: float = 0.0
    account_multiplier: float = 0.0


class JiraImpactScoreProcessor:
    """Process Jira Excel exports and calculate impact scores."""
    
    # Column name mappings (handles variations in export formats)
    COLUMN_MAPPINGS = {
        'jira': ['Jira', 'jira', 'Jira ID', 'Issue Key', 'Key'],
        'last_update': ['Last update', 'Last Update', 'Updated', 'Last Updated'],
        'impact_severity': ['Impact & Severity\nMax 38', 'Impact & Severity', 'Severity', 'Impact'],
        'customer_arr': ['Customer ARR\nMax 15', 'Customer ARR', 'ARR', 'Customer Value'],
        'sla_breach': ['SLA Breach\nMax 8', 'SLA Breach', 'SLA'],
        'frequency': ['Frequency\nMax 16', 'Frequency', 'Occurrences'],
        'workaround': ['Workaround\nMax 15', 'Workaround'],
        'rca_action_item': ['RCA Action Item\nMax 8', 'RCA Action Item', 'RCA', 'RCA AI'],
        'support_multiplier': ['Support Multiplier\n(optional) 0-15%', 'Support Multiplier', 'CloudOps Multiplier'],
        'account_multiplier': ['Account Multiplier\n(optional) 0-15%', 'Account Multiplier'],
        'person': ['Person', 'Assignee', 'Owner']
    }
    
    def __init__(self, excel_path: str):
        """
        Initialize the processor with a Jira Excel export.
        
        Args:
            excel_path: Path to the Excel file
        """
        self.excel_path = Path(excel_path)
        self.df = None
        self.processed_df = None
        
    def load_data(self, sheet_name: str = 'Calculation') -> pd.DataFrame:
        """
        Load data from Excel file.
        
        Args:
            sheet_name: Name of the sheet to load (default: 'Calculation')
            
        Returns:
            DataFrame with loaded data
        """
        try:
            self.df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            print(f"✓ Loaded {len(self.df)} tickets from {self.excel_path}")
            return self.df
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def _find_column(self, standard_name: str) -> Optional[str]:
        """Find the actual column name in the DataFrame."""
        possible_names = self.COLUMN_MAPPINGS.get(standard_name, [])
        for col in self.df.columns:
            if col in possible_names:
                return col
        return None
    
    def _normalize_columns(self) -> pd.DataFrame:
        """Normalize column names to standard format."""
        column_map = {}
        for standard_name in self.COLUMN_MAPPINGS.keys():
            actual_col = self._find_column(standard_name)
            if actual_col:
                column_map[actual_col] = standard_name
        
        return self.df.rename(columns=column_map)
    
    def calculate_scores(self) -> pd.DataFrame:
        """
        Calculate impact scores for all tickets in the DataFrame.
        
        Returns:
            DataFrame with calculated impact scores
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Normalize column names
        df = self._normalize_columns()
        
        # Fill NaN values with 0 for numeric columns
        numeric_columns = [
            'impact_severity', 'customer_arr', 'sla_breach', 
            'frequency', 'workaround', 'rca_action_item',
            'support_multiplier', 'account_multiplier'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Calculate impact scores
        impact_scores = []
        for idx, row in df.iterrows():
            try:
                components = ImpactScoreComponents(
                    impact_severity=int(row.get('impact_severity', 0)),
                    customer_arr=int(row.get('customer_arr', 0)),
                    sla_breach=int(row.get('sla_breach', 0)),
                    frequency=int(row.get('frequency', 0)),
                    workaround=int(row.get('workaround', 0)),
                    rca_action_item=int(row.get('rca_action_item', 0)),
                    support_multiplier=float(row.get('support_multiplier', 0)),
                    account_multiplier=float(row.get('account_multiplier', 0))
                )
                
                score = self._calculate_impact_score(components)
                impact_scores.append(score)
            except Exception as e:
                print(f"Warning: Error calculating score for row {idx}: {str(e)}")
                impact_scores.append(0)
        
        df['calculated_impact_score'] = impact_scores
        
        # Add priority classification
        df['priority_level'] = df['calculated_impact_score'].apply(self._classify_priority)
        
        self.processed_df = df
        return df
    
    @staticmethod
    def _calculate_impact_score(components: ImpactScoreComponents) -> float:
        """Calculate the impact score using the standard formula."""
        base_score = (
            components.impact_severity +
            components.customer_arr +
            components.sla_breach +
            components.frequency +
            components.workaround +
            components.rca_action_item
        )
        
        total_multiplier = 1 + components.support_multiplier + components.account_multiplier
        impact_score = base_score * total_multiplier
        
        return round(impact_score, 1)
    
    @staticmethod
    def _classify_priority(score: float) -> str:
        """Classify priority level based on impact score."""
        if score >= 90:
            return 'CRITICAL'
        elif score >= 70:
            return 'HIGH'
        elif score >= 50:
            return 'MEDIUM'
        elif score >= 30:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of the processed tickets."""
        if self.processed_df is None:
            raise ValueError("No processed data. Call calculate_scores() first.")
        
        df = self.processed_df
        
        return {
            'total_tickets': len(df),
            'average_score': df['calculated_impact_score'].mean(),
            'median_score': df['calculated_impact_score'].median(),
            'max_score': df['calculated_impact_score'].max(),
            'min_score': df['calculated_impact_score'].min(),
            'priority_distribution': df['priority_level'].value_counts().to_dict(),
            'tickets_by_priority': {
                priority: df[df['priority_level'] == priority]['jira'].tolist()
                for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']
                if priority in df['priority_level'].values
            }
        }
    
    def export_results(self, output_path: str, include_all_columns: bool = True):
        """
        Export processed results to Excel.
        
        Args:
            output_path: Path for the output Excel file
            include_all_columns: If True, include all original columns
        """
        if self.processed_df is None:
            raise ValueError("No processed data. Call calculate_scores() first.")
        
        if include_all_columns:
            export_df = self.processed_df
        else:
            # Export only key columns
            key_columns = [
                'jira', 'last_update', 'calculated_impact_score', 
                'priority_level', 'person'
            ]
            export_df = self.processed_df[[col for col in key_columns if col in self.processed_df.columns]]
        
        # Sort by impact score descending
        export_df = export_df.sort_values('calculated_impact_score', ascending=False)
        
        export_df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✓ Results exported to {output_path}")
    
    def get_top_priorities(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N highest priority tickets.
        
        Args:
            n: Number of top tickets to return
            
        Returns:
            DataFrame with top priority tickets
        """
        if self.processed_df is None:
            raise ValueError("No processed data. Call calculate_scores() first.")
        
        return self.processed_df.nlargest(n, 'calculated_impact_score')
    
    def validate_scores(self, tolerance: float = 0.1) -> Tuple[bool, List[str]]:
        """
        Validate calculated scores against existing scores if present.
        
        Args:
            tolerance: Acceptable difference between calculated and existing scores
            
        Returns:
            Tuple of (all_valid, list_of_discrepancies)
        """
        if self.processed_df is None:
            raise ValueError("No processed data. Call calculate_scores() first.")
        
        # Check if original impact score column exists
        impact_score_col = self._find_column('impact_score')
        if not impact_score_col:
            return True, ["No existing impact scores to validate against"]
        
        df = self.processed_df
        discrepancies = []
        
        for idx, row in df.iterrows():
            if pd.notna(row.get('calculated_impact_score')) and pd.notna(row.get(impact_score_col)):
                calc_score = row['calculated_impact_score']
                orig_score = row[impact_score_col]
                
                if abs(calc_score - orig_score) > tolerance:
                    jira_id = row.get('jira', f'Row {idx}')
                    discrepancies.append(
                        f"{jira_id}: Calculated={calc_score}, Original={orig_score}, Diff={calc_score - orig_score:.1f}"
                    )
        
        return len(discrepancies) == 0, discrepancies


def main():
    """Example usage of the Jira Impact Score Processor."""
    
    print("=" * 80)
    print("JIRA IMPACT SCORE PROCESSOR")
    print("=" * 80)
    
    # Initialize processor
    processor = JiraImpactScoreProcessor('/mnt/user-data/uploads/Support_Impact_score_computation.xlsx')
    
    # Load data
    print("\n1. Loading Jira export data...")
    processor.load_data(sheet_name='Calculation')
    
    # Calculate scores
    print("\n2. Calculating impact scores...")
    results = processor.calculate_scores()
    
    # Validate against existing scores
    print("\n3. Validating calculations...")
    is_valid, discrepancies = processor.validate_scores()
    if is_valid:
        print("   ✓ All calculated scores match existing scores!")
    else:
        print(f"   ⚠ Found {len(discrepancies)} discrepancies:")
        for disc in discrepancies[:5]:  # Show first 5
            print(f"     - {disc}")
    
    # Get summary statistics
    print("\n4. Summary Statistics:")
    stats = processor.get_summary_stats()
    print(f"   Total Tickets: {stats['total_tickets']}")
    print(f"   Average Score: {stats['average_score']:.1f}")
    print(f"   Median Score: {stats['median_score']:.1f}")
    print(f"   Score Range: {stats['min_score']:.1f} - {stats['max_score']:.1f}")
    print("\n   Priority Distribution:")
    for priority, count in sorted(stats['priority_distribution'].items(), 
                                   key=lambda x: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL'].index(x[0])):
        print(f"     {priority}: {count} tickets")
    
    # Show top priorities
    print("\n5. Top 5 Priority Tickets:")
    top_tickets = processor.get_top_priorities(n=5)
    for idx, row in top_tickets.iterrows():
        print(f"   {row.get('jira', 'N/A')}: Score={row['calculated_impact_score']:.1f} ({row['priority_level']}) - {row.get('person', 'Unassigned')}")
    
    # Export results
    print("\n6. Exporting results...")
    processor.export_results('/mnt/user-data/outputs/jira_impact_scores_processed.xlsx')
    
    print("\n" + "=" * 80)
    print("Processing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
