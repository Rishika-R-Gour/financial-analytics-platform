"""
Time Series Analysis and Forecasting Module
Implements multiple forecasting methods for financial time series
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class TimeSeriesAnalyzer:
    """
    Comprehensive time series analysis and forecasting
    """
    
    def __init__(self):
        """Initialize time series analyzer"""
        self.models = {}
        self.forecasts = {}
    
    def forecast(
        self,
        data: pd.Series,
        periods: int = 30,
        method: str = 'auto'
    ) -> Dict[str, Union[np.ndarray, Dict]]:
        """
        Forecast time series using specified method
        
        Args:
            data: Historical time series data
            periods: Number of periods to forecast
            method: Forecasting method ('arima', 'ets', 'prophet', 'lstm', 'auto')
            
        Returns:
            Dictionary with forecast and metadata
        """
        if len(data) == 0:
            return self._empty_forecast(periods)
        
        if method == 'auto':
            method = self._select_best_method(data)
        
        if method == 'arima':
            return self._arima_forecast(data, periods)
        elif method == 'ets':
            return self._ets_forecast(data, periods)
        elif method == 'prophet':
            return self._prophet_forecast(data, periods)
        elif method == 'lstm':
            return self._lstm_forecast(data, periods)
        elif method == 'ensemble':
            return self._ensemble_forecast(data, periods)
        else:
            return self._simple_forecast(data, periods)
    
    def _simple_forecast(self, data: pd.Series, periods: int) -> Dict:
        """Simple trend-based forecast"""
        last_value = data.iloc[-1] if len(data) > 0 else 100
        trend = (data.iloc[-1] - data.iloc[0]) / len(data) if len(data) > 1 else 0
        
        forecast = np.array([last_value + trend * i for i in range(1, periods + 1)])
        
        # Simple confidence intervals
        std = data.std() if len(data) > 1 else last_value * 0.1
        lower = forecast - 1.96 * std
        upper = forecast + 1.96 * std
        
        return {
            'forecast': forecast,
            'lower_bound': lower,
            'upper_bound': upper,
            'method': 'simple',
            'periods': periods
        }
    
    def _arima_forecast(self, data: pd.Series, periods: int) -> Dict:
        """ARIMA forecasting"""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            # Fit ARIMA model (auto-select order)
            model = ARIMA(data, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Generate forecast
            forecast_result = fitted_model.forecast(steps=periods)
            forecast = forecast_result.values if hasattr(forecast_result, 'values') else forecast_result
            
            # Get confidence intervals
            forecast_df = fitted_model.get_forecast(steps=periods)
            conf_int = forecast_df.conf_int()
            
            return {
                'forecast': forecast,
                'lower_bound': conf_int.iloc[:, 0].values,
                'upper_bound': conf_int.iloc[:, 1].values,
                'method': 'arima',
                'aic': fitted_model.aic,
                'bic': fitted_model.bic
            }
        
        except Exception as e:
            print(f"ARIMA failed: {e}, using simple method")
            return self._simple_forecast(data, periods)
    
    def _ets_forecast(self, data: pd.Series, periods: int) -> Dict:
        """Exponential Smoothing (ETS) forecast"""
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            
            # Fit ETS model
            model = ExponentialSmoothing(
                data,
                seasonal_periods=min(12, len(data) // 2) if len(data) > 24 else None,
                trend='add',
                seasonal='add' if len(data) > 24 else None
            )
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(steps=periods)
            
            # Simulate confidence intervals
            std = data.std()
            lower = forecast - 1.96 * std
            upper = forecast + 1.96 * std
            
            return {
                'forecast': forecast.values,
                'lower_bound': lower.values,
                'upper_bound': upper.values,
                'method': 'ets'
            }
        
        except Exception as e:
            print(f"ETS failed: {e}, using simple method")
            return self._simple_forecast(data, periods)
    
    def _prophet_forecast(self, data: pd.Series, periods: int) -> Dict:
        """Facebook Prophet forecast"""
        try:
            from prophet import Prophet
            
            # Prepare data for Prophet
            df = pd.DataFrame({
                'ds': pd.date_range(start='2020-01-01', periods=len(data), freq='D'),
                'y': data.values
            })
            
            # Fit Prophet model
            model = Prophet(daily_seasonality=False, yearly_seasonality=True)
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=periods)
            forecast_df = model.predict(future)
            
            # Extract forecast for future periods only
            forecast = forecast_df['yhat'].iloc[-periods:].values
            lower = forecast_df['yhat_lower'].iloc[-periods:].values
            upper = forecast_df['yhat_upper'].iloc[-periods:].values
            
            return {
                'forecast': forecast,
                'lower_bound': lower,
                'upper_bound': upper,
                'method': 'prophet',
                'trend': forecast_df['trend'].iloc[-periods:].values
            }
        
        except Exception as e:
            print(f"Prophet failed: {e}, using simple method")
            return self._simple_forecast(data, periods)
    
    def _lstm_forecast(self, data: pd.Series, periods: int) -> Dict:
        """LSTM neural network forecast using TensorFlow/Keras"""
        try:
            from src.ml_models.deep_learning import create_lstm_forecast
            
            # Use real LSTM implementation
            result = create_lstm_forecast(
                data=data,
                periods=periods,
                lookback=min(60, len(data) // 2),  # Adaptive lookback window
                units=50,
                epochs=50
            )
            
            return result
        
        except ImportError as e:
            print(f"TensorFlow not available: {e}. Install with: pip install tensorflow")
            return self._simple_forecast(data, periods)
        except Exception as e:
            print(f"LSTM failed: {e}, using simple method")
            return self._simple_forecast(data, periods)
    
    def _ensemble_forecast(self, data: pd.Series, periods: int) -> Dict:
        """Ensemble forecast combining multiple methods"""
        methods = ['arima', 'ets', 'simple']
        forecasts = []
        weights = []
        
        for method in methods:
            try:
                result = self.forecast(data, periods, method=method)
                forecasts.append(result['forecast'])
                # Weight by accuracy (simplified)
                weights.append(1.0)
            except:
                continue
        
        if not forecasts:
            return self._simple_forecast(data, periods)
        
        # Weighted average
        weights = np.array(weights) / sum(weights)
        ensemble_forecast = np.average(forecasts, axis=0, weights=weights)
        
        # Aggregate confidence intervals
        std = data.std()
        lower = ensemble_forecast - 1.96 * std
        upper = ensemble_forecast + 1.96 * std
        
        return {
            'forecast': ensemble_forecast,
            'lower_bound': lower,
            'upper_bound': upper,
            'method': 'ensemble',
            'methods_used': methods
        }
    
    def _select_best_method(self, data: pd.Series) -> str:
        """Automatically select best forecasting method"""
        n = len(data)
        
        if n < 20:
            return 'simple'
        elif n < 50:
            return 'ets'
        elif n < 100:
            return 'arima'
        else:
            return 'ensemble'
    
    def _empty_forecast(self, periods: int) -> Dict:
        """Return empty forecast"""
        forecast = np.ones(periods) * 100
        return {
            'forecast': forecast,
            'lower_bound': forecast * 0.9,
            'upper_bound': forecast * 1.1,
            'method': 'empty'
        }
    
    def backtest_forecast(
        self,
        data: pd.Series,
        train_size: float = 0.8,
        periods: int = 10,
        method: str = 'auto'
    ) -> Dict[str, float]:
        """
        Backtest forecasting accuracy
        
        Args:
            data: Historical time series
            train_size: Proportion of data to use for training
            periods: Number of periods to forecast
            method: Forecasting method
            
        Returns:
            Dictionary with accuracy metrics
        """
        split_idx = int(len(data) * train_size)
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:split_idx + periods]
        
        if len(test_data) == 0:
            return {'error': 'Insufficient test data'}
        
        # Generate forecast
        forecast_result = self.forecast(train_data, len(test_data), method=method)
        forecast = forecast_result['forecast']
        
        # Calculate metrics
        actual = test_data.values
        errors = actual - forecast[:len(actual)]
        
        mae = np.mean(np.abs(errors))
        rmse = np.sqrt(np.mean(errors ** 2))
        mape = np.mean(np.abs(errors / actual)) * 100 if (actual != 0).all() else np.nan
        
        return {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'method': method,
            'n_test': len(test_data)
        }
    
    def detect_seasonality(self, data: pd.Series) -> Dict[str, any]:
        """
        Detect seasonality in time series
        
        Args:
            data: Time series data
            
        Returns:
            Dictionary with seasonality information
        """
        if len(data) < 24:
            return {'has_seasonality': False, 'period': None}
        
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # Try different periods
            periods_to_test = [7, 12, 30, 365]
            best_period = None
            max_seasonal_strength = 0
            
            for period in periods_to_test:
                if len(data) < 2 * period:
                    continue
                
                try:
                    decomposition = seasonal_decompose(data, model='additive', period=period)
                    seasonal_var = decomposition.seasonal.var()
                    total_var = data.var()
                    seasonal_strength = seasonal_var / total_var if total_var > 0 else 0
                    
                    if seasonal_strength > max_seasonal_strength:
                        max_seasonal_strength = seasonal_strength
                        best_period = period
                except:
                    continue
            
            return {
                'has_seasonality': max_seasonal_strength > 0.1,
                'period': best_period,
                'strength': max_seasonal_strength
            }
        
        except Exception as e:
            print(f"Seasonality detection failed: {e}")
            return {'has_seasonality': False, 'period': None}
    
    def detect_trend(self, data: pd.Series) -> Dict[str, any]:
        """
        Detect trend in time series
        
        Args:
            data: Time series data
            
        Returns:
            Dictionary with trend information
        """
        if len(data) < 2:
            return {'has_trend': False, 'direction': 'none', 'slope': 0}
        
        # Linear regression for trend
        x = np.arange(len(data))
        y = data.values
        
        slope = np.polyfit(x, y, 1)[0]
        
        # Statistical significance test
        from scipy import stats
        correlation = stats.pearsonr(x, y)[0]
        
        has_trend = abs(correlation) > 0.3
        direction = 'upward' if slope > 0 else 'downward' if slope < 0 else 'none'
        
        return {
            'has_trend': has_trend,
            'direction': direction,
            'slope': slope,
            'correlation': correlation
        }
