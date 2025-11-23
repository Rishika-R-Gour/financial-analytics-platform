"""
Value at Risk (VaR) Calculator Module
Implements multiple VaR calculation methodologies
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime


class VaRCalculator:
    """
    Value at Risk calculator with multiple methodologies:
    - Parametric (Variance-Covariance)
    - Historical Simulation
    - Monte Carlo Simulation
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR calculator
        
        Args:
            confidence_level: Confidence level for VaR calculation (default: 0.95)
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def calculate_var(
        self,
        returns: Union[pd.Series, np.ndarray],
        method: str = 'parametric',
        confidence_level: Optional[float] = None,
        time_horizon: int = 1,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate VaR using specified method
        
        Args:
            returns: Historical returns data
            method: VaR calculation method ('parametric', 'historical', 'monte_carlo')
            confidence_level: Confidence level (overrides default if provided)
            time_horizon: Time horizon in days
            **kwargs: Additional method-specific parameters
            
        Returns:
            Dictionary containing VaR and related metrics
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
        
        # Convert to numpy array if needed
        if isinstance(returns, pd.Series):
            returns = returns.values
        
        # Remove NaN values
        returns = returns[~np.isnan(returns)]
        
        if len(returns) == 0:
            raise ValueError("No valid returns data provided")
        
        # Calculate VaR based on method
        if method.lower() == 'parametric':
            result = self._parametric_var(returns, confidence_level, time_horizon)
        elif method.lower() == 'historical':
            result = self._historical_var(returns, confidence_level, time_horizon)
        elif method.lower() == 'monte_carlo':
            n_simulations = kwargs.get('n_simulations', 10000)
            result = self._monte_carlo_var(returns, confidence_level, time_horizon, n_simulations)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'parametric', 'historical', or 'monte_carlo'")
        
        # Add metadata
        result['method'] = method
        result['confidence_level'] = confidence_level
        result['time_horizon'] = time_horizon
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    def _parametric_var(
        self,
        returns: np.ndarray,
        confidence_level: float,
        time_horizon: int
    ) -> Dict[str, float]:
        """
        Calculate VaR using parametric (variance-covariance) method
        Assumes normal distribution of returns
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level
            time_horizon: Time horizon in days
            
        Returns:
            Dictionary with VaR metrics
        """
        # Calculate mean and standard deviation
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        
        # Calculate z-score for confidence level
        z_score = stats.norm.ppf(1 - confidence_level)
        
        # Calculate VaR (negative z-score because we're looking at losses)
        var_1day = -(mu + z_score * sigma)
        
        # Scale to time horizon (square root of time rule)
        var_horizon = var_1day * np.sqrt(time_horizon)
        
        return {
            'var': var_horizon,
            'var_1day': var_1day,
            'mean_return': mu,
            'volatility': sigma,
            'z_score': z_score
        }
    
    def _historical_var(
        self,
        returns: np.ndarray,
        confidence_level: float,
        time_horizon: int
    ) -> Dict[str, float]:
        """
        Calculate VaR using historical simulation method
        No distribution assumptions, uses actual historical data
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level
            time_horizon: Time horizon in days
            
        Returns:
            Dictionary with VaR metrics
        """
        # Sort returns in ascending order (worst to best)
        sorted_returns = np.sort(returns)
        
        # Find the percentile corresponding to confidence level
        percentile = (1 - confidence_level) * 100
        var_1day = -np.percentile(sorted_returns, percentile)
        
        # Scale to time horizon
        var_horizon = var_1day * np.sqrt(time_horizon)
        
        # Calculate expected shortfall (CVaR) - average of losses beyond VaR
        threshold_idx = int(len(sorted_returns) * (1 - confidence_level))
        cvar_1day = -np.mean(sorted_returns[:threshold_idx]) if threshold_idx > 0 else var_1day
        cvar_horizon = cvar_1day * np.sqrt(time_horizon)
        
        return {
            'var': var_horizon,
            'var_1day': var_1day,
            'cvar': cvar_horizon,
            'cvar_1day': cvar_1day,
            'worst_return': sorted_returns[0],
            'best_return': sorted_returns[-1]
        }
    
    def _monte_carlo_var(
        self,
        returns: np.ndarray,
        confidence_level: float,
        time_horizon: int,
        n_simulations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate VaR using Monte Carlo simulation
        Simulates future returns based on historical distribution
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level
            time_horizon: Time horizon in days
            n_simulations: Number of Monte Carlo simulations
            
        Returns:
            Dictionary with VaR metrics
        """
        # Calculate parameters from historical data
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        
        # Generate simulated returns
        simulated_returns = np.random.normal(mu, sigma, (n_simulations, time_horizon))
        
        # Calculate cumulative returns for each simulation
        cumulative_returns = np.sum(simulated_returns, axis=1)
        
        # Sort simulations
        sorted_simulations = np.sort(cumulative_returns)
        
        # Calculate VaR at confidence level
        percentile = (1 - confidence_level) * 100
        var_horizon = -np.percentile(sorted_simulations, percentile)
        var_1day = var_horizon / np.sqrt(time_horizon)
        
        # Calculate CVaR
        threshold_idx = int(n_simulations * (1 - confidence_level))
        cvar_horizon = -np.mean(sorted_simulations[:threshold_idx]) if threshold_idx > 0 else var_horizon
        
        return {
            'var': var_horizon,
            'var_1day': var_1day,
            'cvar': cvar_horizon,
            'n_simulations': n_simulations,
            'mean_simulated_return': np.mean(cumulative_returns),
            'std_simulated_return': np.std(cumulative_returns),
            'worst_scenario': sorted_simulations[0],
            'best_scenario': sorted_simulations[-1]
        }
    
    def calculate_portfolio_var(
        self,
        returns_df: pd.DataFrame,
        weights: Union[List[float], np.ndarray],
        method: str = 'parametric',
        confidence_level: Optional[float] = None,
        time_horizon: int = 1,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate VaR for a portfolio of assets
        
        Args:
            returns_df: DataFrame with returns for each asset (columns)
            weights: Portfolio weights (must sum to 1)
            method: VaR calculation method
            confidence_level: Confidence level
            time_horizon: Time horizon in days
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with portfolio VaR metrics
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
        
        # Convert weights to numpy array
        weights = np.array(weights)
        
        # Validate weights
        if not np.isclose(np.sum(weights), 1.0):
            raise ValueError("Portfolio weights must sum to 1")
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Calculate VaR
        result = self.calculate_var(
            portfolio_returns,
            method=method,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            **kwargs
        )
        
        # Add portfolio-specific metrics
        result['weights'] = weights.tolist()
        result['assets'] = returns_df.columns.tolist()
        
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()
        result['correlation_matrix'] = corr_matrix.to_dict()
        
        return result
    
    def backtest_var(
        self,
        returns: Union[pd.Series, np.ndarray],
        var_estimates: Union[List[float], np.ndarray],
        confidence_level: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Backtest VaR model by comparing estimates with actual losses
        
        Args:
            returns: Actual returns
            var_estimates: VaR estimates for each period
            confidence_level: Confidence level used for VaR
            
        Returns:
            Dictionary with backtest results
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
        
        # Convert to numpy arrays
        if isinstance(returns, pd.Series):
            returns = returns.values
        var_estimates = np.array(var_estimates)
        
        # Count violations (actual loss > VaR estimate)
        losses = -returns
        violations = losses > var_estimates
        n_violations = np.sum(violations)
        n_observations = len(returns)
        
        # Calculate violation rate
        violation_rate = n_violations / n_observations
        expected_violation_rate = 1 - confidence_level
        
        # Kupiec test (likelihood ratio test)
        if n_violations > 0 and violation_rate < 1:
            lr_stat = -2 * (
                np.log((1 - expected_violation_rate) ** (n_observations - n_violations) *
                      expected_violation_rate ** n_violations) -
                np.log((1 - violation_rate) ** (n_observations - n_violations) *
                      violation_rate ** n_violations)
            )
            p_value = 1 - stats.chi2.cdf(lr_stat, 1)
        else:
            lr_stat = np.nan
            p_value = np.nan
        
        return {
            'n_violations': int(n_violations),
            'n_observations': int(n_observations),
            'violation_rate': violation_rate,
            'expected_violation_rate': expected_violation_rate,
            'kupiec_lr_stat': lr_stat,
            'kupiec_p_value': p_value,
            'test_passed': p_value > 0.05 if not np.isnan(p_value) else None
        }
    
    def calculate_marginal_var(
        self,
        returns_df: pd.DataFrame,
        weights: Union[List[float], np.ndarray],
        asset_idx: int,
        confidence_level: Optional[float] = None
    ) -> float:
        """
        Calculate marginal VaR for a specific asset in the portfolio
        Shows how much VaR changes with a small change in asset weight
        
        Args:
            returns_df: DataFrame with returns for each asset
            weights: Current portfolio weights
            asset_idx: Index of the asset to calculate marginal VaR for
            confidence_level: Confidence level
            
        Returns:
            Marginal VaR value
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
        
        weights = np.array(weights)
        
        # Calculate current portfolio VaR
        current_var = self.calculate_portfolio_var(
            returns_df, weights, confidence_level=confidence_level
        )['var']
        
        # Create small perturbation
        delta = 0.01
        perturbed_weights = weights.copy()
        perturbed_weights[asset_idx] += delta
        
        # Normalize weights
        perturbed_weights = perturbed_weights / perturbed_weights.sum()
        
        # Calculate VaR with perturbed weights
        perturbed_var = self.calculate_portfolio_var(
            returns_df, perturbed_weights, confidence_level=confidence_level
        )['var']
        
        # Marginal VaR is the change in VaR per unit change in weight
        marginal_var = (perturbed_var - current_var) / delta
        
        return marginal_var
