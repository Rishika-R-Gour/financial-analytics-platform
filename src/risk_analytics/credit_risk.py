"""
Credit Risk Analysis Module
Implements credit scoring, PD modeling, and credit exposure analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime
from scipy import stats


class CreditRiskAnalyzer:
    """
    Credit risk analyzer for assessing creditworthiness and default risk
    """
    
    def __init__(self, default_pd: float = 0.02, lgd: float = 0.45, ead_buffer: float = 1.2):
        """
        Initialize credit risk analyzer
        
        Args:
            default_pd: Default probability of default (2%)
            lgd: Loss given default rate (45%)
            ead_buffer: Exposure at default buffer (120%)
        """
        self.default_pd = default_pd
        self.lgd = lgd
        self.ead_buffer = ead_buffer
    
    def calculate_credit_score(
        self,
        features: Dict[str, float],
        model: str = 'simple'
    ) -> Dict[str, Union[float, str]]:
        """
        Calculate credit score based on applicant features
        
        Args:
            features: Dictionary of credit features
            model: Scoring model to use ('simple', 'advanced')
            
        Returns:
            Dictionary with credit score and rating
        """
        if model == 'simple':
            score = self._simple_credit_score(features)
        elif model == 'advanced':
            score = self._advanced_credit_score(features)
        else:
            raise ValueError(f"Unknown model: {model}")
        
        # Determine credit rating
        rating = self._get_credit_rating(score)
        
        # Calculate probability of default based on score
        pd = self._score_to_pd(score)
        
        return {
            'credit_score': score,
            'credit_rating': rating,
            'probability_of_default': pd,
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
    
    def _simple_credit_score(self, features: Dict[str, float]) -> float:
        """
        Simple credit scoring model
        
        Expected features:
        - income: Annual income
        - debt: Total debt
        - credit_history_years: Years of credit history
        - payment_history_score: Payment history score (0-100)
        - utilization_rate: Credit utilization rate (0-1)
        """
        # Extract features with defaults
        income = features.get('income', 50000)
        debt = features.get('debt', 10000)
        credit_history = features.get('credit_history_years', 5)
        payment_history = features.get('payment_history_score', 70)
        utilization = features.get('utilization_rate', 0.3)
        
        # Calculate debt-to-income ratio
        dti = debt / income if income > 0 else 1.0
        
        # Base score
        score = 600
        
        # Income factor (max +100)
        if income >= 100000:
            score += 100
        elif income >= 75000:
            score += 75
        elif income >= 50000:
            score += 50
        elif income >= 30000:
            score += 25
        
        # DTI factor (max -150)
        if dti <= 0.1:
            score += 50
        elif dti <= 0.2:
            score += 25
        elif dti <= 0.36:
            score += 0
        elif dti <= 0.5:
            score -= 50
        else:
            score -= 100
        
        # Credit history factor (max +50)
        score += min(credit_history * 5, 50)
        
        # Payment history factor (max +100)
        score += (payment_history - 50)  # Scale from 0-100 to -50 to +50
        
        # Utilization factor (max -100)
        if utilization <= 0.1:
            score += 50
        elif utilization <= 0.3:
            score += 25
        elif utilization <= 0.5:
            score += 0
        elif utilization <= 0.75:
            score -= 50
        else:
            score -= 100
        
        # Ensure score is in valid range (300-850)
        score = max(300, min(850, score))
        
        return score
    
    def _advanced_credit_score(self, features: Dict[str, float]) -> float:
        """Advanced credit scoring with more sophisticated calculations"""
        # Start with simple score
        score = self._simple_credit_score(features)
        
        # Additional factors
        num_accounts = features.get('num_credit_accounts', 3)
        recent_inquiries = features.get('recent_inquiries', 0)
        delinquencies = features.get('delinquencies', 0)
        
        # Account diversity bonus
        if 3 <= num_accounts <= 10:
            score += 20
        elif num_accounts > 10:
            score += 10
        
        # Recent inquiries penalty
        score -= min(recent_inquiries * 10, 50)
        
        # Delinquencies penalty
        score -= min(delinquencies * 30, 150)
        
        # Ensure score is in valid range
        score = max(300, min(850, score))
        
        return score
    
    def _get_credit_rating(self, score: float) -> str:
        """Convert credit score to letter rating"""
        if score >= 800:
            return 'AAA'
        elif score >= 740:
            return 'AA'
        elif score >= 670:
            return 'A'
        elif score >= 580:
            return 'BBB'
        elif score >= 500:
            return 'BB'
        elif score >= 400:
            return 'B'
        else:
            return 'C'
    
    def _score_to_pd(self, score: float) -> float:
        """Convert credit score to probability of default"""
        # Logistic transformation
        # Higher score = lower PD
        # Score 850 -> ~0.1% PD
        # Score 300 -> ~50% PD
        normalized_score = (score - 300) / 550  # Normalize to 0-1
        pd = 1 / (1 + np.exp(8 * (normalized_score - 0.5)))
        return pd
    
    def calculate_expected_loss(
        self,
        exposure: float,
        pd: Optional[float] = None,
        lgd: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate expected loss (EL) for a credit exposure
        EL = PD × LGD × EAD
        
        Args:
            exposure: Exposure at default (EAD)
            pd: Probability of default (uses default if not provided)
            lgd: Loss given default (uses default if not provided)
            
        Returns:
            Dictionary with expected loss metrics
        """
        if pd is None:
            pd = self.default_pd
        if lgd is None:
            lgd = self.lgd
        
        # Calculate expected loss
        el = pd * lgd * exposure
        
        # Calculate unexpected loss (UL) using simplified formula
        # UL = sqrt(PD × (1-PD) × LGD² × EAD²)
        ul = np.sqrt(pd * (1 - pd) * (lgd ** 2) * (exposure ** 2))
        
        # Economic capital (typically UL at 99.9% confidence)
        ec = ul * stats.norm.ppf(0.999)
        
        return {
            'exposure_at_default': exposure,
            'probability_of_default': pd,
            'loss_given_default': lgd,
            'expected_loss': el,
            'unexpected_loss': ul,
            'economic_capital': ec,
            'return_on_risk_capital': (exposure * 0.05) / ec if ec > 0 else 0  # Assuming 5% margin
        }
    
    def calculate_credit_var(
        self,
        exposures: List[float],
        pds: List[float],
        lgds: Optional[List[float]] = None,
        confidence_level: float = 0.95,
        correlation: float = 0.3
    ) -> Dict[str, float]:
        """
        Calculate Credit VaR for a portfolio of exposures
        
        Args:
            exposures: List of exposure amounts
            pds: List of default probabilities
            lgds: List of loss given default rates (uses default if not provided)
            confidence_level: Confidence level for VaR
            correlation: Default correlation between exposures
            
        Returns:
            Dictionary with credit VaR metrics
        """
        n = len(exposures)
        
        if lgds is None:
            lgds = [self.lgd] * n
        
        # Calculate expected losses
        els = [pd * lgd * ead for pd, lgd, ead in zip(pds, lgds, exposures)]
        total_el = sum(els)
        
        # Calculate portfolio standard deviation (simplified with constant correlation)
        variance = 0
        for i in range(n):
            for j in range(n):
                pd_i, lgd_i, ead_i = pds[i], lgds[i], exposures[i]
                pd_j, lgd_j, ead_j = pds[j], lgds[j], exposures[j]
                
                if i == j:
                    variance += pd_i * (1 - pd_i) * (lgd_i * ead_i) ** 2
                else:
                    variance += correlation * np.sqrt(pd_i * (1 - pd_i) * pd_j * (1 - pd_j)) * \
                               lgd_i * ead_i * lgd_j * ead_j
        
        portfolio_std = np.sqrt(variance)
        
        # Calculate VaR
        z_score = stats.norm.ppf(confidence_level)
        credit_var = total_el + z_score * portfolio_std
        
        return {
            'credit_var': credit_var,
            'expected_loss': total_el,
            'unexpected_loss': portfolio_std,
            'confidence_level': confidence_level,
            'n_exposures': n,
            'total_exposure': sum(exposures),
            'avg_pd': np.mean(pds),
            'correlation': correlation
        }
    
    def assess_concentration_risk(
        self,
        exposures: pd.DataFrame,
        group_by: str = 'industry'
    ) -> Dict[str, Union[float, pd.DataFrame]]:
        """
        Assess concentration risk in credit portfolio
        
        Args:
            exposures: DataFrame with exposure details
            group_by: Column to group exposures by (e.g., 'industry', 'geography')
            
        Returns:
            Dictionary with concentration metrics
        """
        # Calculate total exposure
        total_exposure = exposures['exposure'].sum()
        
        # Group by specified column
        if group_by in exposures.columns:
            grouped = exposures.groupby(group_by)['exposure'].sum()
            concentrations = (grouped / total_exposure * 100).sort_values(ascending=False)
        else:
            concentrations = pd.Series()
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        # HHI = sum of squared market shares
        shares = exposures['exposure'] / total_exposure
        hhi = (shares ** 2).sum() * 10000  # Multiply by 10000 for standard HHI scale
        
        # Determine concentration level
        if hhi < 1500:
            concentration_level = 'Low'
        elif hhi < 2500:
            concentration_level = 'Moderate'
        else:
            concentration_level = 'High'
        
        # Calculate top-N exposure concentration
        top_5_exposure = exposures.nlargest(5, 'exposure')['exposure'].sum()
        top_10_exposure = exposures.nlargest(10, 'exposure')['exposure'].sum()
        
        return {
            'total_exposure': total_exposure,
            'hhi_index': hhi,
            'concentration_level': concentration_level,
            'top_5_concentration': (top_5_exposure / total_exposure * 100),
            'top_10_concentration': (top_10_exposure / total_exposure * 100),
            'n_exposures': len(exposures),
            'concentrations_by_group': concentrations.to_dict() if not concentrations.empty else {}
        }
    
    def calculate_credit_migration_matrix(
        self,
        initial_ratings: List[str],
        final_ratings: List[str]
    ) -> pd.DataFrame:
        """
        Calculate credit migration (transition) matrix
        Shows probability of moving between credit ratings
        
        Args:
            initial_ratings: List of initial credit ratings
            final_ratings: List of final credit ratings (same length as initial)
            
        Returns:
            DataFrame with migration probabilities
        """
        # Define rating categories
        ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'C', 'D']
        
        # Create migration matrix
        migration_matrix = pd.DataFrame(0.0, index=ratings, columns=ratings)
        
        # Count transitions
        for initial, final in zip(initial_ratings, final_ratings):
            if initial in ratings and final in ratings:
                migration_matrix.loc[initial, final] += 1
        
        # Convert to probabilities (normalize by row)
        migration_matrix = migration_matrix.div(migration_matrix.sum(axis=1), axis=0).fillna(0)
        
        return migration_matrix
    
    def calculate_cvar_credit(
        self,
        exposures: List[float],
        pds: List[float],
        lgds: Optional[List[float]] = None,
        confidence_level: float = 0.95,
        n_simulations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate Credit CVaR (Conditional VaR / Expected Shortfall) using Monte Carlo
        
        Args:
            exposures: List of exposure amounts
            pds: List of default probabilities
            lgds: List of loss given default rates
            confidence_level: Confidence level
            n_simulations: Number of Monte Carlo simulations
            
        Returns:
            Dictionary with CVaR metrics
        """
        if lgds is None:
            lgds = [self.lgd] * len(exposures)
        
        # Run Monte Carlo simulations
        losses = []
        
        for _ in range(n_simulations):
            # Simulate defaults
            defaults = np.random.rand(len(exposures)) < np.array(pds)
            
            # Calculate total loss
            total_loss = sum(
                ead * lgd if default else 0
                for ead, lgd, default in zip(exposures, lgds, defaults)
            )
            losses.append(total_loss)
        
        # Sort losses
        losses = np.array(sorted(losses, reverse=True))
        
        # Calculate VaR
        var_idx = int(n_simulations * confidence_level)
        credit_var = losses[var_idx]
        
        # Calculate CVaR (average of losses beyond VaR)
        credit_cvar = np.mean(losses[:var_idx]) if var_idx > 0 else credit_var
        
        return {
            'credit_cvar': credit_cvar,
            'credit_var': credit_var,
            'expected_loss': np.mean(losses),
            'max_loss': losses[0],
            'confidence_level': confidence_level,
            'n_simulations': n_simulations
        }
