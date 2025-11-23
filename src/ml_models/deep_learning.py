"""
Deep Learning Models for Financial Time Series Forecasting
LSTM (Long Short-Term Memory) implementation using TensorFlow/Keras
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class LSTMForecaster:
    """LSTM model for time series forecasting"""
    
    def __init__(self, lookback: int = 60, units: int = 50, epochs: int = 50):
        """
        Initialize LSTM forecaster
        
        Args:
            lookback: Number of previous time steps to use for prediction
            units: Number of LSTM units in each layer
            epochs: Number of training epochs
        """
        self.lookback = lookback
        self.units = units
        self.epochs = epochs
        self.model = None
        self.scaler = None
        self.is_fitted = False
        
    def _prepare_data(self, data: pd.Series) -> Tuple[np.ndarray, np.ndarray, object]:
        """Prepare data for LSTM"""
        try:
            from sklearn.preprocessing import MinMaxScaler
            
            # Scale data
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))
            
            # Create sequences
            X, y = [], []
            for i in range(self.lookback, len(scaled_data)):
                X.append(scaled_data[i-self.lookback:i, 0])
                y.append(scaled_data[i, 0])
            
            X, y = np.array(X), np.array(y)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            
            return X, y, scaler
            
        except Exception as e:
            raise ValueError(f"Error preparing data: {e}")
    
    def fit(self, data: pd.Series) -> 'LSTMForecaster':
        """
        Train LSTM model
        
        Args:
            data: Time series data to train on
        """
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.optimizers import Adam
            
            # Prepare data
            X, y, self.scaler = self._prepare_data(data)
            
            # Build model
            self.model = Sequential([
                LSTM(units=self.units, return_sequences=True, input_shape=(X.shape[1], 1)),
                Dropout(0.2),
                LSTM(units=self.units, return_sequences=False),
                Dropout(0.2),
                Dense(units=25),
                Dense(units=1)
            ])
            
            # Compile model
            self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
            
            # Train model (suppress verbose output)
            self.model.fit(X, y, epochs=self.epochs, batch_size=32, verbose=0)
            
            self.is_fitted = True
            return self
            
        except ImportError:
            raise ImportError("TensorFlow is required for LSTM. Install with: pip install tensorflow")
        except Exception as e:
            raise ValueError(f"Error training LSTM model: {e}")
    
    def forecast(self, data: pd.Series, periods: int) -> dict:
        """
        Generate forecast
        
        Args:
            data: Historical time series data
            periods: Number of periods to forecast
            
        Returns:
            Dictionary with forecast, confidence intervals, and metrics
        """
        if not self.is_fitted:
            self.fit(data)
        
        try:
            # Prepare last lookback window
            scaled_data = self.scaler.transform(data.values.reshape(-1, 1))
            last_sequence = scaled_data[-self.lookback:]
            
            # Generate forecasts
            forecasts = []
            current_sequence = last_sequence.copy()
            
            for _ in range(periods):
                # Reshape for prediction
                X_pred = current_sequence.reshape(1, self.lookback, 1)
                
                # Predict next value
                pred_scaled = self.model.predict(X_pred, verbose=0)
                forecasts.append(pred_scaled[0, 0])
                
                # Update sequence
                current_sequence = np.append(current_sequence[1:], pred_scaled)
            
            # Inverse transform forecasts
            forecasts = np.array(forecasts).reshape(-1, 1)
            forecasts = self.scaler.inverse_transform(forecasts).flatten()
            
            # Calculate confidence intervals (simple approach)
            train_std = np.std(data.values)
            lower_bound = forecasts - 1.96 * train_std
            upper_bound = forecasts + 1.96 * train_std
            
            return {
                'forecast': forecasts,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'method': 'LSTM',
                'model_info': {
                    'lookback': self.lookback,
                    'units': self.units,
                    'epochs': self.epochs
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error generating forecast: {e}")


def create_lstm_forecast(data: pd.Series, periods: int = 30, **kwargs) -> dict:
    """
    Convenience function to create LSTM forecast
    
    Args:
        data: Time series data
        periods: Number of periods to forecast
        **kwargs: Additional parameters for LSTMForecaster
    
    Returns:
        Forecast dictionary
    """
    forecaster = LSTMForecaster(**kwargs)
    return forecaster.forecast(data, periods)
