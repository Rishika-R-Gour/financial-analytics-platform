"""
Anomaly Detection Module
Detects unusual patterns and outliers in financial data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


class AnomalyDetector:
    """
    Detects anomalies in financial time series data
    """
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of anomalies (0.05 = 5%)
        """
        self.contamination = contamination
        self.model = None
        self.scaler = StandardScaler()
    
    def detect_price_anomalies(
        self,
        prices: pd.Series,
        method: str = 'isolation_forest'
    ) -> Dict[str, any]:
        """
        Detect anomalies in price data
        
        Args:
            prices: Time series of prices
            method: Detection method ('isolation_forest', 'zscore', 'dbscan')
            
        Returns:
            Dictionary with anomaly indices and scores
        """
        if method == 'isolation_forest':
            return self._isolation_forest_detection(prices)
        elif method == 'zscore':
            return self._zscore_detection(prices)
        elif method == 'dbscan':
            return self._dbscan_detection(prices)
        else:
            return self._isolation_forest_detection(prices)
    
    def _isolation_forest_detection(self, prices: pd.Series) -> Dict:
        """
        Isolation Forest anomaly detection
        
        Uses ensemble of decision trees to isolate anomalies
        """
        # Prepare features
        returns = prices.pct_change().fillna(0)
        volatility = returns.rolling(20).std().fillna(0)
        volume_proxy = abs(returns)  # Proxy for volume
        
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility,
            'abs_returns': volume_proxy,
            'price_level': prices
        })
        
        # Scale features
        X = self.scaler.fit_transform(features)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        
        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self.model.fit_predict(X)
        anomaly_scores = self.model.score_samples(X)
        
        # Get anomaly indices
        anomaly_indices = np.where(predictions == -1)[0]
        anomaly_dates = prices.index[anomaly_indices] if hasattr(prices.index, '__getitem__') else anomaly_indices
        
        return {
            'method': 'isolation_forest',
            'anomaly_indices': anomaly_indices.tolist(),
            'anomaly_dates': anomaly_dates.tolist() if hasattr(anomaly_dates, 'tolist') else list(anomaly_dates),
            'anomaly_scores': anomaly_scores[anomaly_indices].tolist(),
            'n_anomalies': len(anomaly_indices),
            'contamination_rate': len(anomaly_indices) / len(prices)
        }
    
    def _zscore_detection(self, prices: pd.Series, threshold: float = 3.0) -> Dict:
        """
        Z-score based anomaly detection
        
        Flags values more than 3 standard deviations from mean
        """
        returns = prices.pct_change().dropna()
        
        # Calculate z-scores
        mean = returns.mean()
        std = returns.std()
        z_scores = (returns - mean) / std
        
        # Identify anomalies
        anomaly_mask = abs(z_scores) > threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        anomaly_dates = returns.index[anomaly_indices] if hasattr(returns.index, '__getitem__') else anomaly_indices
        
        return {
            'method': 'zscore',
            'anomaly_indices': anomaly_indices.tolist(),
            'anomaly_dates': anomaly_dates.tolist() if hasattr(anomaly_dates, 'tolist') else list(anomaly_dates),
            'z_scores': z_scores[anomaly_mask].tolist(),
            'n_anomalies': len(anomaly_indices),
            'threshold': threshold
        }
    
    def _dbscan_detection(self, prices: pd.Series) -> Dict:
        """
        DBSCAN clustering for anomaly detection
        
        Points not belonging to any cluster are anomalies
        """
        # Prepare features
        returns = prices.pct_change().fillna(0)
        volatility = returns.rolling(20).std().fillna(0)
        
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility
        })
        
        # Scale features
        X = self.scaler.fit_transform(features)
        
        # DBSCAN clustering
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        clusters = dbscan.fit_predict(X)
        
        # Cluster -1 means noise/anomalies
        anomaly_indices = np.where(clusters == -1)[0]
        anomaly_dates = prices.index[anomaly_indices] if hasattr(prices.index, '__getitem__') else anomaly_indices
        
        return {
            'method': 'dbscan',
            'anomaly_indices': anomaly_indices.tolist(),
            'anomaly_dates': anomaly_dates.tolist() if hasattr(anomaly_dates, 'tolist') else list(anomaly_dates),
            'n_anomalies': len(anomaly_indices),
            'n_clusters': len(set(clusters)) - (1 if -1 in clusters else 0)
        }
    
    def detect_volume_anomalies(
        self,
        volume: pd.Series,
        threshold: float = 2.5
    ) -> Dict[str, any]:
        """
        Detect unusual trading volume
        
        Args:
            volume: Trading volume series
            threshold: Z-score threshold
            
        Returns:
            Dictionary with volume anomalies
        """
        # Calculate rolling statistics
        rolling_mean = volume.rolling(20).mean()
        rolling_std = volume.rolling(20).std()
        
        # Z-scores
        z_scores = (volume - rolling_mean) / rolling_std
        
        # Identify spikes
        anomaly_mask = abs(z_scores) > threshold
        anomaly_indices = np.where(anomaly_mask)[0]
        
        return {
            'anomaly_indices': anomaly_indices.tolist(),
            'z_scores': z_scores[anomaly_mask].tolist(),
            'n_anomalies': len(anomaly_indices),
            'avg_volume': volume.mean(),
            'spike_volumes': volume[anomaly_mask].tolist()
        }
    
    def detect_pattern_breaks(
        self,
        prices: pd.Series,
        window: int = 50
    ) -> Dict[str, any]:
        """
        Detect breaks in price patterns (support/resistance violations)
        
        Args:
            prices: Price series
            window: Lookback window
            
        Returns:
            Dictionary with pattern breaks
        """
        rolling_max = prices.rolling(window).max()
        rolling_min = prices.rolling(window).min()
        rolling_range = rolling_max - rolling_min
        
        # Detect breakouts (price exceeds recent range)
        upper_breaks = prices > rolling_max.shift(1)
        lower_breaks = prices < rolling_min.shift(1)
        
        breakout_indices = np.where(upper_breaks | lower_breaks)[0]
        
        return {
            'breakout_indices': breakout_indices.tolist(),
            'n_breakouts': len(breakout_indices),
            'upper_breaks': np.where(upper_breaks)[0].tolist(),
            'lower_breaks': np.where(lower_breaks)[0].tolist(),
            'avg_range': rolling_range.mean()
        }
    
    def generate_alerts(
        self,
        anomalies: Dict[str, any],
        prices: pd.Series,
        severity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Generate actionable alerts from detected anomalies
        
        Args:
            anomalies: Anomaly detection results
            prices: Price series
            severity_threshold: Minimum severity to alert
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if 'anomaly_indices' not in anomalies:
            return alerts
        
        for idx in anomalies['anomaly_indices']:
            if idx >= len(prices):
                continue
                
            price = prices.iloc[idx] if hasattr(prices, 'iloc') else prices[idx]
            
            # Calculate severity
            if 'anomaly_scores' in anomalies:
                score_idx = anomalies['anomaly_indices'].index(idx)
                severity = abs(anomalies['anomaly_scores'][score_idx])
            elif 'z_scores' in anomalies:
                score_idx = anomalies['anomaly_indices'].index(idx)
                severity = abs(anomalies['z_scores'][score_idx]) / 5.0  # Normalize
            else:
                severity = 0.5
            
            if severity >= severity_threshold:
                alerts.append({
                    'index': idx,
                    'date': anomalies['anomaly_dates'][anomalies['anomaly_indices'].index(idx)] if 'anomaly_dates' in anomalies else idx,
                    'price': float(price),
                    'severity': float(severity),
                    'type': 'price_anomaly',
                    'message': f"⚠️ Unusual price movement detected: ${price:.2f}"
                })
        
        return sorted(alerts, key=lambda x: x['severity'], reverse=True)
