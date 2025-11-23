"""
Real-time Risk Monitoring Module
Provides continuous risk monitoring and alerting
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta


class RiskMonitor:
    """
    Real-time risk monitoring system with configurable alerts
    """
    
    def __init__(self):
        """Initialize risk monitor"""
        self.risk_limits = {}
        self.alerts = []
        self.alert_callbacks = []
    
    def set_risk_limit(
        self,
        metric_name: str,
        limit_value: float,
        alert_level: str = 'warning'
    ):
        """
        Set a risk limit for monitoring
        
        Args:
            metric_name: Name of the risk metric
            limit_value: Limit value that triggers alert
            alert_level: 'info', 'warning', or 'critical'
        """
        self.risk_limits[metric_name] = {
            'limit': limit_value,
            'level': alert_level
        }
    
    def check_limits(
        self,
        current_metrics: Dict[str, float]
    ) -> List[Dict]:
        """
        Check current metrics against configured limits
        
        Args:
            current_metrics: Dictionary of current metric values
            
        Returns:
            List of alerts triggered
        """
        alerts = []
        
        for metric_name, metric_value in current_metrics.items():
            if metric_name in self.risk_limits:
                limit_config = self.risk_limits[metric_name]
                
                if metric_value > limit_config['limit']:
                    alert = {
                        'metric': metric_name,
                        'value': metric_value,
                        'limit': limit_config['limit'],
                        'level': limit_config['level'],
                        'timestamp': datetime.now().isoformat(),
                        'breach_amount': metric_value - limit_config['limit']
                    }
                    alerts.append(alert)
                    self.alerts.append(alert)
                    
                    # Trigger callbacks
                    for callback in self.alert_callbacks:
                        callback(alert)
        
        return alerts
    
    def add_alert_callback(self, callback: Callable):
        """
        Add a callback function to be called when alerts are triggered
        
        Args:
            callback: Function to call with alert dictionary
        """
        self.alert_callbacks.append(callback)
    
    def get_recent_alerts(
        self,
        hours: int = 24,
        level: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent alerts
        
        Args:
            hours: Number of hours to look back
            level: Filter by alert level
            
        Returns:
            List of recent alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        if level:
            recent_alerts = [
                alert for alert in recent_alerts
                if alert['level'] == level
            ]
        
        return recent_alerts
    
    def calculate_risk_dashboard_metrics(
        self,
        portfolio_data: Dict
    ) -> Dict[str, any]:
        """
        Calculate comprehensive risk metrics for dashboard
        
        Args:
            portfolio_data: Dictionary with portfolio information
            
        Returns:
            Dictionary with dashboard metrics
        """
        return {
            'total_exposure': portfolio_data.get('total_exposure', 0),
            'var_95': portfolio_data.get('var_95', 0),
            'var_99': portfolio_data.get('var_99', 0),
            'current_drawdown': portfolio_data.get('drawdown', 0),
            'sharpe_ratio': portfolio_data.get('sharpe_ratio', 0),
            'positions_count': portfolio_data.get('n_positions', 0),
            'risk_utilization': portfolio_data.get('risk_utilization', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def start_monitoring(
        self,
        portfolio: any,
        risk_limits: Dict[str, float],
        refresh_interval: int = 60
    ):
        """
        Start continuous monitoring (placeholder for async implementation)
        
        Args:
            portfolio: Portfolio object to monitor
            risk_limits: Dictionary of risk limits
            refresh_interval: Refresh interval in seconds
        """
        # Set up risk limits
        for metric, limit in risk_limits.items():
            self.set_risk_limit(metric, limit)
        
        print(f"Monitoring started with {len(risk_limits)} risk limits")
        print(f"Refresh interval: {refresh_interval} seconds")
