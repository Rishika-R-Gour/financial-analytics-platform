"""
Market Regime Detection Module
Identifies different market states (Bull, Bear, Sideways, High Volatility)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from scipy import stats


class MarketRegimeDetector:
    """
    Detects market regimes using clustering and statistical methods
    """
    
    def __init__(self, n_regimes: int = 3):
        """
        Initialize regime detector
        
        Args:
            n_regimes: Number of market regimes to detect (default: 3)
        """
        self.n_regimes = n_regimes
        self.model = None
        self.scaler = StandardScaler()
        self.regime_labels = {
            0: 'Bull Market',
            1: 'Bear Market',
            2: 'Sideways/Choppy',
            3: 'High Volatility'
        }
    
    def detect_regime(
        self,
        prices: pd.Series,
        method: str = 'kmeans'
    ) -> Dict[str, any]:
        """
        Detect current market regime
        
        Args:
            prices: Price time series
            method: Detection method ('kmeans', 'gmm', 'statistical')
            
        Returns:
            Dictionary with regime information
        """
        if method == 'kmeans':
            return self._kmeans_detection(prices)
        elif method == 'gmm':
            return self._gmm_detection(prices)
        elif method == 'statistical':
            return self._statistical_detection(prices)
        else:
            return self._kmeans_detection(prices)
    
    def _kmeans_detection(self, prices: pd.Series) -> Dict:
        """
        K-Means clustering for regime detection
        """
        # Calculate features
        features = self._calculate_regime_features(prices)
        
        # Scale features
        X = self.scaler.fit_transform(features)
        
        # K-Means clustering
        self.model = KMeans(n_clusters=self.n_regimes, random_state=42, n_init=10)
        regimes = self.model.fit_predict(X)
        
        # Interpret regimes based on cluster centers
        regime_interpretation = self._interpret_regimes(features, regimes)
        
        # Current regime
        current_regime = regimes[-1]
        current_regime_name = regime_interpretation[current_regime]
        
        # Calculate regime probabilities (distance-based)
        distances = self.model.transform(X[-1:])
        probabilities = self._distances_to_probabilities(distances[0])
        
        return {
            'method': 'kmeans',
            'current_regime': int(current_regime),
            'current_regime_name': current_regime_name,
            'regime_history': regimes.tolist(),
            'regime_probabilities': {
                regime_interpretation[i]: float(probabilities[i])
                for i in range(self.n_regimes)
            },
            'confidence': float(probabilities[current_regime]),
            'regime_interpretation': regime_interpretation
        }
    
    def _gmm_detection(self, prices: pd.Series) -> Dict:
        """
        Gaussian Mixture Model for regime detection
        
        More sophisticated than K-Means, models each regime as Gaussian distribution
        """
        # Calculate features
        features = self._calculate_regime_features(prices)
        
        # Scale features
        X = self.scaler.fit_transform(features)
        
        # GMM
        self.model = GaussianMixture(
            n_components=self.n_regimes,
            covariance_type='full',
            random_state=42
        )
        self.model.fit(X)
        
        # Predict regimes and probabilities
        regimes = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Interpret regimes
        regime_interpretation = self._interpret_regimes(features, regimes)
        
        # Current regime
        current_regime = regimes[-1]
        current_regime_name = regime_interpretation[current_regime]
        current_probabilities = probabilities[-1]
        
        return {
            'method': 'gmm',
            'current_regime': int(current_regime),
            'current_regime_name': current_regime_name,
            'regime_history': regimes.tolist(),
            'regime_probabilities': {
                regime_interpretation[i]: float(current_probabilities[i])
                for i in range(self.n_regimes)
            },
            'confidence': float(current_probabilities[current_regime]),
            'regime_interpretation': regime_interpretation
        }
    
    def _statistical_detection(self, prices: pd.Series) -> Dict:
        """
        Rule-based statistical regime detection
        """
        # Calculate indicators
        returns = prices.pct_change().dropna()
        volatility = returns.rolling(20).std()
        trend = prices.rolling(50).mean()
        
        # Recent values
        recent_return = returns.iloc[-20:].mean() if len(returns) >= 20 else 0
        recent_vol = volatility.iloc[-1] if len(volatility) > 0 else 0
        price_vs_trend = (prices.iloc[-1] / trend.iloc[-1] - 1) if len(trend) > 0 and trend.iloc[-1] > 0 else 0
        
        # Determine regime based on rules
        if recent_vol > volatility.mean() * 1.5:
            regime_name = 'High Volatility'
            regime_id = 3
        elif recent_return > 0.001 and price_vs_trend > 0:
            regime_name = 'Bull Market'
            regime_id = 0
        elif recent_return < -0.001 and price_vs_trend < 0:
            regime_name = 'Bear Market'
            regime_id = 1
        else:
            regime_name = 'Sideways/Choppy'
            regime_id = 2
        
        # Calculate confidence based on strength of signals
        confidence = min(abs(recent_return) * 100 + abs(price_vs_trend) * 50, 1.0)
        
        return {
            'method': 'statistical',
            'current_regime': regime_id,
            'current_regime_name': regime_name,
            'confidence': confidence,
            'indicators': {
                'recent_return': float(recent_return),
                'volatility': float(recent_vol),
                'trend_deviation': float(price_vs_trend)
            }
        }
    
    def _calculate_regime_features(self, prices: pd.Series) -> pd.DataFrame:
        """
        Calculate features for regime detection
        """
        # Returns
        returns = prices.pct_change().fillna(0)
        
        # Volatility (rolling std)
        volatility = returns.rolling(20).std().fillna(0)
        
        # Trend (price vs MA)
        ma50 = prices.rolling(50).mean()
        trend_strength = (prices - ma50) / ma50
        trend_strength = trend_strength.fillna(0)
        
        # Momentum
        momentum = prices.pct_change(20).fillna(0)
        
        # Volume proxy (absolute returns)
        volume_proxy = abs(returns)
        
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility,
            'trend_strength': trend_strength,
            'momentum': momentum,
            'volume': volume_proxy
        })
        
        return features
    
    def _interpret_regimes(
        self,
        features: pd.DataFrame,
        regimes: np.ndarray
    ) -> Dict[int, str]:
        """
        Interpret what each regime cluster represents
        """
        interpretation = {}
        
        for regime_id in range(self.n_regimes):
            # Get average characteristics of this regime
            regime_mask = regimes == regime_id
            regime_features = features[regime_mask]
            
            if len(regime_features) == 0:
                interpretation[regime_id] = f'Regime {regime_id}'
                continue
            
            avg_return = regime_features['returns'].mean()
            avg_vol = regime_features['volatility'].mean()
            avg_trend = regime_features['trend_strength'].mean()
            
            # Classify regime
            if avg_vol > features['volatility'].quantile(0.75):
                name = 'High Volatility'
            elif avg_return > 0.001 and avg_trend > 0:
                name = 'Bull Market'
            elif avg_return < -0.001 and avg_trend < 0:
                name = 'Bear Market'
            else:
                name = 'Sideways/Choppy'
            
            interpretation[regime_id] = name
        
        return interpretation
    
    def _distances_to_probabilities(self, distances: np.ndarray) -> np.ndarray:
        """
        Convert cluster distances to probabilities
        """
        # Invert distances (closer = higher probability)
        inv_distances = 1 / (distances + 1e-10)
        
        # Normalize to probabilities
        probabilities = inv_distances / inv_distances.sum()
        
        return probabilities
    
    def get_regime_statistics(
        self,
        prices: pd.Series,
        regime_history: List[int]
    ) -> Dict[str, any]:
        """
        Calculate statistics for each regime
        
        Args:
            prices: Price series
            regime_history: Historical regime labels
            
        Returns:
            Statistics for each regime
        """
        returns = prices.pct_change().dropna()
        
        stats = {}
        
        for regime_id in range(self.n_regimes):
            regime_mask = np.array(regime_history[1:]) == regime_id  # Skip first NaN return
            
            if regime_mask.sum() == 0:
                continue
            
            regime_returns = returns[regime_mask]
            
            stats[regime_id] = {
                'avg_return': float(regime_returns.mean()),
                'volatility': float(regime_returns.std()),
                'sharpe_ratio': float(regime_returns.mean() / regime_returns.std()) if regime_returns.std() > 0 else 0,
                'max_drawdown': float((regime_returns.cumsum().cummax() - regime_returns.cumsum()).max()),
                'win_rate': float((regime_returns > 0).sum() / len(regime_returns)),
                'duration': int(regime_mask.sum())
            }
        
        return stats
    
    def predict_regime_transition(
        self,
        current_regime: int,
        regime_history: List[int]
    ) -> Dict[int, float]:
        """
        Predict probability of transitioning to other regimes
        
        Args:
            current_regime: Current regime ID
            regime_history: Historical regimes
            
        Returns:
            Transition probabilities to each regime
        """
        # Build transition matrix
        regime_array = np.array(regime_history)
        transition_counts = np.zeros((self.n_regimes, self.n_regimes))
        
        for i in range(len(regime_array) - 1):
            from_regime = regime_array[i]
            to_regime = regime_array[i + 1]
            transition_counts[from_regime, to_regime] += 1
        
        # Convert to probabilities
        transition_probs = transition_counts / (transition_counts.sum(axis=1, keepdims=True) + 1e-10)
        
        # Get probabilities from current regime
        next_regime_probs = transition_probs[current_regime]
        
        return {
            regime_id: float(prob)
            for regime_id, prob in enumerate(next_regime_probs)
        }
