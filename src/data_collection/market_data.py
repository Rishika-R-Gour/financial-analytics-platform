"""
Market Data Collection Module
Handles collection of market data from various sources
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime, timedelta


class MarketDataCollector:
    """
    Market data collector for stocks, indices, and other securities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize market data collector
        
        Args:
            api_key: API key for data provider
        """
        self.api_key = api_key
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get historical stock data
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            import yfinance as yf
            
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            return df
        
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            # Return sample data as fallback
            return self._generate_sample_data(symbol, start_date, end_date)
    
    def _generate_sample_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Generate sample market data for testing
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with synthetic OHLCV data
        """
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n = len(dates)
        
        # Generate random walk for prices
        np.random.seed(hash(symbol) % (2**32))
        base_price = 100
        returns = np.random.normal(0.0005, 0.02, n)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, n)),
            'High': prices * (1 + np.abs(np.random.uniform(0, 0.02, n))),
            'Low': prices * (1 - np.abs(np.random.uniform(0, 0.02, n))),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, n)
        }, index=dates)
        
        return df
    
    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """
        Calculate returns from prices
        
        Args:
            prices: Series of prices
            
        Returns:
            Series of returns
        """
        return prices.pct_change().dropna()
    
    def get_multiple_stocks(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary of DataFrames keyed by symbol
        """
        data = {}
        for symbol in symbols:
            data[symbol] = self.get_stock_data(symbol, start_date, end_date)
        return data
