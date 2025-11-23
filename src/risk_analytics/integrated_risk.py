"""
Integrated Risk Analysis Module
Combines multiple risk types for holistic risk assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class IntegratedRiskAnalyzer:
    """
    Integrated risk analyzer combining market, credit, and operational risks
    """
    
    def __init__(self):
        """Initialize integrated risk analyzer"""
        pass
    
    def calculate_total_risk(
        self,
        market_var: float,
        credit_var: float,
        operational_var: float,
        correlation_matrix: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Calculate total risk combining different risk types
        
        Args:
            market_var: Market VaR
            credit_var: Credit VaR
            operational_var: Operational VaR
            correlation_matrix: Correlation between risk types (3x3 matrix)
            
        Returns:
            Dictionary with total risk metrics
        """
        # Default correlation matrix (conservative approach)
        if correlation_matrix is None:
            correlation_matrix = np.array([
                [1.0, 0.3, 0.1],  # Market correlations
                [0.3, 1.0, 0.2],  # Credit correlations
                [0.1, 0.2, 1.0]   # Operational correlations
            ])
        
        # Risk vector
        risks = np.array([market_var, credit_var, operational_var])
        
        # Calculate total risk using correlation
        total_var = np.sqrt(risks @ correlation_matrix @ risks)
        
        # Diversification benefit
        undiversified_var = np.sum(risks)
        diversification_benefit = undiversified_var - total_var
        
        return {
            'total_var': total_var,
            'market_var': market_var,
            'credit_var': credit_var,
            'operational_var': operational_var,
            'undiversified_var': undiversified_var,
            'diversification_benefit': diversification_benefit,
            'diversification_ratio': diversification_benefit / undiversified_var if undiversified_var > 0 else 0
        }
    
    def calculate_risk_adjusted_return(
        self,
        returns: float,
        risk: float,
        risk_free_rate: float = 0.02
    ) -> Dict[str, float]:
        """
        Calculate risk-adjusted return metrics
        
        Args:
            returns: Portfolio returns
            risk: Total risk (VaR or volatility)
            risk_free_rate: Risk-free rate
            
        Returns:
            Dictionary with risk-adjusted metrics
        """
        # RAROC (Risk-Adjusted Return on Capital)
        raroc = (returns - risk_free_rate) / risk if risk > 0 else 0
        
        # RORAC (Return on Risk-Adjusted Capital)
        rorac = returns / risk if risk > 0 else 0
        
        return {
            'raroc': raroc,
            'rorac': rorac,
            'excess_return': returns - risk_free_rate,
            'risk': risk
        }
    
    def aggregate_portfolio_risks(
        self,
        positions: pd.DataFrame,
        risk_factors: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Aggregate risks across portfolio positions
        
        Args:
            positions: DataFrame with position details
            risk_factors: Dictionary of risk factor sensitivities
            
        Returns:
            Dictionary with aggregated risk metrics
        """
        total_exposure = positions['exposure'].sum() if 'exposure' in positions.columns else 0
        total_risk = 0
        
        # Calculate weighted risk contribution
        if 'exposure' in positions.columns and 'risk_weight' in positions.columns:
            positions['risk_contribution'] = positions['exposure'] * positions['risk_weight']
            total_risk = positions['risk_contribution'].sum()
        
        return {
            'total_exposure': total_exposure,
            'total_risk': total_risk,
            'risk_concentration': total_risk / total_exposure if total_exposure > 0 else 0,
            'n_positions': len(positions)
        }
