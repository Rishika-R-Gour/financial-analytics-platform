"""
Stress Testing Module
Implements scenario-based stress testing for portfolios
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class StressTester:
    """
    Stress testing engine for portfolio risk assessment
    """
    
    def __init__(self):
        """Initialize stress tester"""
        self.scenarios = self._get_default_scenarios()
    
    def _get_default_scenarios(self) -> Dict[str, Dict]:
        """
        Get default stress test scenarios
        
        Returns:
            Dictionary of stress scenarios
        """
        return {
            'market_crash': {
                'equity_shock': -0.30,  # 30% drop
                'volatility_shock': 2.0,  # 2x volatility
                'credit_spread_shock': 0.03  # +300 bps
            },
            'interest_rate_shock': {
                'rate_shock': 0.02,  # +200 bps
                'curve_steepening': 0.01  # +100 bps on long end
            },
            'credit_crisis': {
                'default_rate_shock': 3.0,  # 3x default rate
                'recovery_rate_shock': -0.20,  # -20% recovery
                'credit_spread_shock': 0.05  # +500 bps
            },
            'liquidity_crisis': {
                'bid_ask_spread_shock': 5.0,  # 5x spreads
                'volume_shock': -0.70  # 70% volume drop
            },
            'pandemic': {
                'equity_shock': -0.35,
                'volatility_shock': 3.0,
                'operational_loss_shock': 2.0
            }
        }
    
    def run_stress_test(
        self,
        portfolio_value: float,
        positions: pd.DataFrame,
        scenario_name: str
    ) -> Dict[str, float]:
        """
        Run stress test on portfolio
        
        Args:
            portfolio_value: Current portfolio value
            positions: DataFrame with position details
            scenario_name: Name of scenario to test
            
        Returns:
            Dictionary with stress test results
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.scenarios[scenario_name]
        
        # Calculate impact based on scenario
        stressed_value = portfolio_value
        
        if 'equity_shock' in scenario:
            equity_exposure = positions[positions['asset_class'] == 'equity']['value'].sum() \
                if 'asset_class' in positions.columns else portfolio_value * 0.6
            stressed_value += equity_exposure * scenario['equity_shock']
        
        if 'rate_shock' in scenario:
            bond_exposure = positions[positions['asset_class'] == 'fixed_income']['value'].sum() \
                if 'asset_class' in positions.columns else portfolio_value * 0.3
            duration = 5.0  # Simplified duration
            stressed_value += bond_exposure * (-duration * scenario['rate_shock'])
        
        if 'credit_spread_shock' in scenario:
            credit_exposure = positions[positions['asset_class'] == 'credit']['value'].sum() \
                if 'asset_class' in positions.columns else portfolio_value * 0.1
            duration = 4.0
            stressed_value += credit_exposure * (-duration * scenario['credit_spread_shock'])
        
        # Calculate impact metrics
        impact = stressed_value - portfolio_value
        impact_pct = (impact / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        return {
            'scenario': scenario_name,
            'original_value': portfolio_value,
            'stressed_value': stressed_value,
            'impact': impact,
            'impact_percentage': impact_pct,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_all_scenarios(
        self,
        portfolio_value: float,
        positions: pd.DataFrame
    ) -> List[Dict]:
        """
        Run all stress test scenarios
        
        Args:
            portfolio_value: Current portfolio value
            positions: DataFrame with position details
            
        Returns:
            List of results for all scenarios
        """
        results = []
        for scenario_name in self.scenarios.keys():
            result = self.run_stress_test(portfolio_value, positions, scenario_name)
            results.append(result)
        return results
    
    def add_custom_scenario(
        self,
        name: str,
        shocks: Dict[str, float]
    ):
        """
        Add a custom stress scenario
        
        Args:
            name: Scenario name
            shocks: Dictionary of shock parameters
        """
        self.scenarios[name] = shocks
