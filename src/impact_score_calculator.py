"""
Jira Ticket Impact Score Calculator

This module implements the impact score calculation formula used for prioritizing
Jira tickets based on severity, business impact, and customer effect.
"""

from typing import Optional
from dataclasses import dataclass


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


class ImpactScoreCalculator:
    """Calculator for Jira ticket impact scores."""
    
    # Impact & Severity scores
    SEVERITY_P1 = 38
    SEVERITY_P2 = 30
    SEVERITY_P3 = 22
    SEVERITY_P4 = 16
    SEVERITY_P5 = 8
    
    # Customer ARR scores
    ARR_OVER_1M = 15
    ARR_500K_TO_1M = 13
    ARR_100K_TO_500K = 10
    ARR_MANY_LOW = 8
    ARR_FEW_LOW = 5
    ARR_SINGLE_LOW = 0
    
    # SLA Breach scores
    SLA_BREACHED = 8
    SLA_NOT_BREACHED = 0
    
    # Frequency scores
    FREQ_OVER_4 = 16
    FREQ_2_TO_4 = 8
    FREQ_SINGLE = 0
    
    # Workaround scores
    WORKAROUND_NONE = 15
    WORKAROUND_WITH_PERF_IMPACT = 12
    WORKAROUND_COMPLEX = 10
    WORKAROUND_SIMPLE = 5
    
    # RCA Action Item scores
    RCA_YES = 8
    RCA_NO = 0
    
    @staticmethod
    def calculate_impact_score(components: ImpactScoreComponents) -> float:
        """
        Calculate the impact score using the formula:
        Impact Score = Base Score × (1 + Support Multiplier + Account Multiplier)
        
        Args:
            components: ImpactScoreComponents containing all scoring factors
            
        Returns:
            float: The calculated impact score
            
        Raises:
            ValueError: If any component is out of valid range
        """
        # Validate components
        ImpactScoreCalculator._validate_components(components)
        
        # Calculate base score
        base_score = (
            components.impact_severity +
            components.customer_arr +
            components.sla_breach +
            components.frequency +
            components.workaround +
            components.rca_action_item
        )
        
        # Apply multipliers
        total_multiplier = 1 + components.support_multiplier + components.account_multiplier
        impact_score = base_score * total_multiplier
        
        return round(impact_score, 1)
    
    @staticmethod
    def _validate_components(components: ImpactScoreComponents) -> None:
        """Validate that all components are within acceptable ranges."""
        if not 0 <= components.impact_severity <= 38:
            raise ValueError(f"Impact & Severity must be 0-38, got {components.impact_severity}")
        
        if not 0 <= components.customer_arr <= 15:
            raise ValueError(f"Customer ARR must be 0-15, got {components.customer_arr}")
        
        if components.sla_breach not in [0, 8]:
            raise ValueError(f"SLA Breach must be 0 or 8, got {components.sla_breach}")
        
        if not 0 <= components.frequency <= 16:
            raise ValueError(f"Frequency must be 0-16, got {components.frequency}")
        
        if not 0 <= components.workaround <= 15:
            raise ValueError(f"Workaround must be 0-15, got {components.workaround}")
        
        if components.rca_action_item not in [0, 8]:
            raise ValueError(f"RCA Action Item must be 0 or 8, got {components.rca_action_item}")
        
        if not 0 <= components.support_multiplier <= 0.15:
            raise ValueError(f"Support Multiplier must be 0-0.15, got {components.support_multiplier}")
        
        if not 0 <= components.account_multiplier <= 0.15:
            raise ValueError(f"Account Multiplier must be 0-0.15, got {components.account_multiplier}")
    
    @staticmethod
    def get_severity_score(priority: str) -> int:
        """Get impact & severity score based on priority level."""
        priority_map = {
            'P1': ImpactScoreCalculator.SEVERITY_P1,
            'P2': ImpactScoreCalculator.SEVERITY_P2,
            'P3': ImpactScoreCalculator.SEVERITY_P3,
            'P4': ImpactScoreCalculator.SEVERITY_P4,
            'P5': ImpactScoreCalculator.SEVERITY_P5,
        }
        return priority_map.get(priority.upper(), 0)
    
    @staticmethod
    def get_arr_score(arr_value: Optional[float] = None, customer_count: Optional[int] = None) -> int:
        """
        Get customer ARR score based on ARR value or customer count.
        
        Args:
            arr_value: Annual Recurring Revenue in dollars
            customer_count: Number of affected low ARR customers
            
        Returns:
            int: ARR score
        """
        if arr_value is not None:
            if arr_value > 1_000_000:
                return ImpactScoreCalculator.ARR_OVER_1M
            elif arr_value > 500_000:
                return ImpactScoreCalculator.ARR_500K_TO_1M
            elif arr_value > 100_000:
                return ImpactScoreCalculator.ARR_100K_TO_500K
        
        if customer_count is not None:
            if customer_count > 10:
                return ImpactScoreCalculator.ARR_MANY_LOW
            elif customer_count > 1:
                return ImpactScoreCalculator.ARR_FEW_LOW
            elif customer_count == 1:
                return ImpactScoreCalculator.ARR_SINGLE_LOW
        
        return 0
    
    @staticmethod
    def get_frequency_score(occurrences: int) -> int:
        """Get frequency score based on number of occurrences."""
        if occurrences > 4:
            return ImpactScoreCalculator.FREQ_OVER_4
        elif occurrences >= 2:
            return ImpactScoreCalculator.FREQ_2_TO_4
        else:
            return ImpactScoreCalculator.FREQ_SINGLE


def example_calculations():
    """Demonstrate example calculations."""
    
    print("=" * 80)
    print("JIRA IMPACT SCORE CALCULATOR - EXAMPLES")
    print("=" * 80)
    
    # Example 1: High Priority Customer Issue
    print("\nExample 1: High Priority Customer Issue")
    print("-" * 40)
    components1 = ImpactScoreComponents(
        impact_severity=30,  # P2
        customer_arr=15,     # ARR > $1M
        sla_breach=0,
        frequency=0,         # First occurrence
        workaround=10,       # Complex workaround
        rca_action_item=8,   # Part of RCA
        support_multiplier=0.0,
        account_multiplier=0.0
    )
    score1 = ImpactScoreCalculator.calculate_impact_score(components1)
    base1 = (components1.impact_severity + components1.customer_arr + 
             components1.sla_breach + components1.frequency + 
             components1.workaround + components1.rca_action_item)
    print(f"Base Score: {base1}")
    print(f"Impact Score: {score1}")
    
    # Example 2: Critical Issue with Multipliers
    print("\nExample 2: Critical Issue with Multipliers")
    print("-" * 40)
    components2 = ImpactScoreComponents(
        impact_severity=38,  # P1
        customer_arr=15,     # ARR > $1M
        sla_breach=8,        # SLA breached
        frequency=16,        # >4 occurrences
        workaround=15,       # No workaround
        rca_action_item=8,   # Part of RCA
        support_multiplier=0.15,  # 15% multiplier
        account_multiplier=0.15   # 15% multiplier
    )
    score2 = ImpactScoreCalculator.calculate_impact_score(components2)
    base2 = (components2.impact_severity + components2.customer_arr + 
             components2.sla_breach + components2.frequency + 
             components2.workaround + components2.rca_action_item)
    print(f"Base Score: {base2}")
    print(f"Multipliers: Support=15%, Account=15%")
    print(f"Impact Score: {score2}")
    
    # Example 3: Lower Priority Issue
    print("\nExample 3: Lower Priority Issue")
    print("-" * 40)
    components3 = ImpactScoreComponents(
        impact_severity=8,   # P5
        customer_arr=5,      # <10 low ARR customers
        sla_breach=0,
        frequency=8,         # 2-4 occurrences
        workaround=5,        # Simple workaround
        rca_action_item=0,
        support_multiplier=0.0,
        account_multiplier=0.0
    )
    score3 = ImpactScoreCalculator.calculate_impact_score(components3)
    base3 = (components3.impact_severity + components3.customer_arr + 
             components3.sla_breach + components3.frequency + 
             components3.workaround + components3.rca_action_item)
    print(f"Base Score: {base3}")
    print(f"Impact Score: {score3}")
    
    # Using helper methods
    print("\n" + "=" * 80)
    print("USING HELPER METHODS")
    print("=" * 80)
    
    print("\nSeverity Scores:")
    for priority in ['P1', 'P2', 'P3', 'P4', 'P5']:
        print(f"  {priority}: {ImpactScoreCalculator.get_severity_score(priority)}")
    
    print("\nARR Scores:")
    print(f"  ARR $1.5M: {ImpactScoreCalculator.get_arr_score(arr_value=1_500_000)}")
    print(f"  ARR $750K: {ImpactScoreCalculator.get_arr_score(arr_value=750_000)}")
    print(f"  ARR $250K: {ImpactScoreCalculator.get_arr_score(arr_value=250_000)}")
    print(f"  15 low ARR customers: {ImpactScoreCalculator.get_arr_score(customer_count=15)}")
    print(f"  5 low ARR customers: {ImpactScoreCalculator.get_arr_score(customer_count=5)}")
    
    print("\nFrequency Scores:")
    for count in [1, 3, 6]:
        print(f"  {count} occurrence(s): {ImpactScoreCalculator.get_frequency_score(count)}")


if __name__ == "__main__":
    example_calculations()
