"""
Operational Risk Analysis Module
Implements operational risk assessment frameworks
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class OperationalRiskAnalyzer:
    """
    Operational risk analyzer using Advanced Measurement Approach (AMA)
    """
    
    def __init__(self):
        """Initialize operational risk analyzer"""
        self.risk_categories = [
            'Internal Fraud',
            'External Fraud',
            'Employment Practices',
            'Clients/Products/Business Practices',
            'Damage to Physical Assets',
            'Business Disruption',
            'Execution/Delivery/Process Management'
        ]
    
    def calculate_operational_var(self,
                                 loss_data: pd.DataFrame,
                                 confidence_level: float = 0.99,
                                 time_horizon_days: int = 252) -> Dict[str, float]:
        """
        Calculate Operational VaR using Loss Distribution Approach
        
        Args:
            loss_data: DataFrame with operational loss events
            confidence_level: Confidence level
            time_horizon_days: Time horizon in days
            
        Returns:
            Dictionary with operational VaR metrics
        """
        if 'amount' not in loss_data.columns:
            raise ValueError("loss_data must contain 'amount' column")
        
        losses = loss_data['amount'].values
        
        # Calculate frequency (events per year)
        if 'date' in loss_data.columns:
            date_range = (loss_data['date'].max() - loss_data['date'].min()).days
            frequency_per_year = len(losses) * 365 / date_range if date_range > 0 else len(losses)
        else:
            frequency_per_year = len(losses)
        
        # Calculate severity distribution
        mean_loss = np.mean(losses)
        std_loss = np.std(losses)
        
        # Operational VaR using simplified approach
        op_var = frequency_per_year * mean_loss + \
                np.sqrt(frequency_per_year) * std_loss * np.sqrt(time_horizon_days/252)
        
        return {
            'operational_var': op_var,
            'expected_annual_loss': frequency_per_year * mean_loss,
            'frequency_per_year': frequency_per_year,
            'mean_severity': mean_loss,
            'max_loss': np.max(losses),
            'confidence_level': confidence_level
        }
    
    def assess_key_risk_indicators(self, kri_data: Dict[str, float]) -> Dict[str, any]:
        """
        Assess Key Risk Indicators (KRIs)
        
        Args:
            kri_data: Dictionary of KRI names and values
            
        Returns:
            Dictionary with KRI assessment
        """
        thresholds = {
            'employee_turnover_rate': 0.15,
            'system_downtime_hours': 24,
            'failed_transactions_rate': 0.01,
            'customer_complaints': 100
        }
        
        risk_score = 0
        alerts = []
        
        for kri, value in kri_data.items():
            if kri in thresholds and value > thresholds[kri]:
                risk_score += 1
                alerts.append(f"{kri}: {value} exceeds threshold {thresholds[kri]}")
        
        return {
            'risk_score': risk_score,
            'risk_level': 'High' if risk_score >= 3 else 'Medium' if risk_score >= 1 else 'Low',
            'alerts': alerts,
            'kri_data': kri_data
        }
