"""
Market Risk Analysis Module
Implements market risk metrics and portfolio risk assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime
from scipy import stats


class MarketRiskAnalyzer:
    """
    Market risk analyzer for portfolio and securities analysis
    """
    
    def __init__(self):
        """Initialize market risk analyzer"""
        self.risk_free_rate = 0.02  # 2% default risk-free rate
    
    def calculate_portfolio_risk(
        self,
        returns_df: pd.DataFrame,
        weights: Union[List[float], np.ndarray]
    ) -> Dict[str, float]:
        """
        Calculate comprehensive portfolio risk metrics
        
        Args:
            returns_df: DataFrame with asset returns (columns = assets)
            weights: Portfolio weights
            
        Returns:
            Dictionary with risk metrics
        """
        weights = np.array(weights)
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Basic statistics
        mean_return = portfolio_returns.mean()
        volatility = portfolio_returns.std()
        
        # Annualized metrics (assuming daily returns)
        annual_return = mean_return * 252
        annual_volatility = volatility * np.sqrt(252)
        
        # Sharpe ratio
        sharpe = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Sortino ratio (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else volatility
        sortino = (annual_return - self.risk_free_rate) / (downside_std * np.sqrt(252)) if downside_std > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Skewness and kurtosis
        skewness = stats.skew(portfolio_returns)
        kurtosis = stats.kurtosis(portfolio_returns)
        
        return {
            'mean_return': mean_return,
            'volatility': volatility,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_drawdown,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_beta(
        self,
        asset_returns: pd.Series,
        market_returns: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate beta and related metrics relative to market
        
        Args:
            asset_returns: Returns of the asset
            market_returns: Market/benchmark returns
            
        Returns:
            Dictionary with beta metrics
        """
        # Remove NaN values
        valid_data = pd.DataFrame({
            'asset': asset_returns,
            'market': market_returns
        }).dropna()
        
        if len(valid_data) < 2:
            return {'beta': np.nan, 'alpha': np.nan, 'r_squared': np.nan}
        
        # Calculate covariance and variance
        covariance = valid_data['asset'].cov(valid_data['market'])
        market_variance = valid_data['market'].var()
        
        # Calculate beta
        beta = covariance / market_variance if market_variance > 0 else np.nan
        
        # Calculate alpha (intercept from regression)
        asset_mean = valid_data['asset'].mean()
        market_mean = valid_data['market'].mean()
        alpha = asset_mean - beta * market_mean
        
        # Calculate R-squared
        correlation = valid_data['asset'].corr(valid_data['market'])
        r_squared = correlation ** 2
        
        return {
            'beta': beta,
            'alpha': alpha * 252,  # Annualized
            'r_squared': r_squared,
            'correlation': correlation
        }
    
    def calculate_greeks(
        self,
        option_type: str,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate option Greeks using Black-Scholes model
        
        Args:
            option_type: 'call' or 'put'
            spot_price: Current price of underlying
            strike_price: Strike price
            time_to_expiry: Time to expiration in years
            volatility: Implied volatility
            risk_free_rate: Risk-free rate (uses default if not provided)
            
        Returns:
            Dictionary with Greeks
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        if time_to_expiry <= 0:
            return {
                'delta': 1.0 if option_type == 'call' and spot_price > strike_price else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }
        
        # Calculate d1 and d2
        d1 = (np.log(spot_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        # Calculate Greeks
        if option_type.lower() == 'call':
            delta = stats.norm.cdf(d1)
            theta = (-spot_price * stats.norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) -
                    risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(d2))
            rho = strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(d2)
        else:  # put
            delta = stats.norm.cdf(d1) - 1
            theta = (-spot_price * stats.norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) +
                    risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(-d2))
            rho = -strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(-d2)
        
        # Common Greeks
        gamma = stats.norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
        vega = spot_price * stats.norm.pdf(d1) * np.sqrt(time_to_expiry)
        
        # Convert theta to daily
        theta_daily = theta / 365
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta_daily,
            'vega': vega / 100,  # Per 1% change in volatility
            'rho': rho / 100  # Per 1% change in interest rate
        }
    
    def calculate_tracking_error(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate tracking error and information ratio
        
        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Dictionary with tracking metrics
        """
        # Calculate active returns
        active_returns = portfolio_returns - benchmark_returns
        
        # Tracking error (standard deviation of active returns)
        tracking_error = active_returns.std() * np.sqrt(252)  # Annualized
        
        # Information ratio
        mean_active_return = active_returns.mean() * 252  # Annualized
        information_ratio = mean_active_return / tracking_error if tracking_error > 0 else 0
        
        return {
            'tracking_error': tracking_error,
            'active_return': mean_active_return,
            'information_ratio': information_ratio
        }
    
    def calculate_correlation_risk(
        self,
        returns_df: pd.DataFrame
    ) -> Dict[str, Union[float, pd.DataFrame]]:
        """
        Analyze correlation risk in portfolio
        
        Args:
            returns_df: DataFrame with asset returns
            
        Returns:
            Dictionary with correlation metrics
        """
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()
        
        # Calculate average correlation (excluding diagonal)
        n = len(corr_matrix)
        if n > 1:
            avg_correlation = (corr_matrix.sum().sum() - n) / (n * (n - 1))
        else:
            avg_correlation = 0.0
        
        # Find highest and lowest correlations
        corr_values = []
        for i in range(n):
            for j in range(i + 1, n):
                corr_values.append({
                    'asset1': corr_matrix.index[i],
                    'asset2': corr_matrix.columns[j],
                    'correlation': corr_matrix.iloc[i, j]
                })
        
        if corr_values:
            corr_df = pd.DataFrame(corr_values)
            highest_corr = corr_df.nlargest(1, 'correlation').iloc[0]
            lowest_corr = corr_df.nsmallest(1, 'correlation').iloc[0]
        else:
            highest_corr = None
            lowest_corr = None
        
        return {
            'correlation_matrix': corr_matrix,
            'average_correlation': avg_correlation,
            'highest_correlation': highest_corr.to_dict() if highest_corr is not None else None,
            'lowest_correlation': lowest_corr.to_dict() if lowest_corr is not None else None
        }
    
    def calculate_liquidity_risk(
        self,
        volumes: pd.Series,
        prices: pd.Series,
        position_size: float
    ) -> Dict[str, float]:
        """
        Calculate liquidity risk metrics
        
        Args:
            volumes: Trading volumes
            prices: Prices
            position_size: Size of position to liquidate
            
        Returns:
            Dictionary with liquidity metrics
        """
        # Average daily volume
        avg_volume = volumes.mean()
        
        # Days to liquidate (assuming we can trade 10% of daily volume)
        liquidity_participation_rate = 0.10
        days_to_liquidate = position_size / (avg_volume * liquidity_participation_rate)
        
        # Bid-ask spread estimate (using price volatility as proxy)
        returns = prices.pct_change().dropna()
        spread_estimate = returns.std() * 2  # Simplified spread estimate
        
        # Liquidity cost estimate
        liquidity_cost = spread_estimate * prices.iloc[-1] * position_size
        
        return {
            'avg_daily_volume': avg_volume,
            'days_to_liquidate': days_to_liquidate,
            'estimated_spread': spread_estimate,
            'estimated_liquidity_cost': liquidity_cost,
            'liquidity_score': min(100, max(0, 100 - days_to_liquidate * 10))  # 0-100 scale
        }
