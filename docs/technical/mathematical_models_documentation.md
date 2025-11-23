# Mathematical Models Documentation

This document describes the mathematical models and formulas used in the Financial Analytics Platform.

## Risk Models

### Value at Risk (VaR) - Parametric Method

**Description**: Assumes normal distribution of returns

**Formula**: `VaR = μ - z_α × σ × √t`

**Variables:**
- `μ`: Expected return
- `z_α`: Z-score for confidence level α
- `σ`: Standard deviation of returns
- `t`: Time horizon

**Key Assumptions:**
- Normal distribution of returns
- Constant volatility
- Independent returns

**Use Cases:**
- Quick risk estimates
- Linear portfolios
- Market risk measurement

---

### Value at Risk (VaR) - Historical Simulation

**Description**: Uses historical return distribution without distributional assumptions

**Formula**: `VaR = Percentile(Historical Returns, α)`

**Variables:**
- `α`: Confidence level (e.g., 5% for 95% VaR)

**Key Assumptions:**
- Historical patterns repeat
- No structural breaks

**Use Cases:**
- Non-linear portfolios
- Fat-tailed distributions
- Back-testing validation

---

### Expected Shortfall (CVaR)

**Description**: Average loss beyond VaR threshold

**Formula**: `CVaR = E[Loss | Loss > VaR]`

**Variables:**
- `E[·]`: Expected value operator
- `Loss`: Portfolio loss
- `VaR`: Value at Risk threshold

**Key Assumptions:**
- Same as underlying VaR method

**Use Cases:**
- Coherent risk measure
- Risk capital allocation
- Regulatory compliance

---

### Credit Scoring Model

**Description**: Machine learning based credit risk assessment

**Formula**: `Credit Score = f(X₁, X₂, ..., Xₙ)`

**Variables:**
- `f(·)`: ML model function (XGBoost/Random Forest)
- `X₁...Xₙ`: Financial ratios and metrics

**Key Assumptions:**
- Feature stability
- Training data representativeness

**Use Cases:**
- Counterparty assessment
- Credit limit setting
- Portfolio optimization

---

### Probability of Default (PD)

**Description**: Logistic regression model for default probability

**Formula**: `PD = 1 / (1 + e^-(β₀ + β₁X₁ + ... + βₙXₙ))`

**Variables:**
- `β₀...βₙ`: Model coefficients
- `X₁...Xₙ`: Financial predictors
- `e`: Euler's number

**Key Assumptions:**
- Logistic relationship
- Linear predictors
- Independent observations

**Use Cases:**
- Expected loss calculation
- Regulatory capital
- Pricing decisions

---

### Loss Given Default (LGD)

**Description**: Recovery rate based model for loss severity

**Formula**: `LGD = 1 - Recovery Rate`

**Variables:**
- `Recovery Rate`: Expected recovery percentage

**Key Assumptions:**
- Historical recovery patterns
- Collateral effectiveness

**Use Cases:**
- Expected loss calculation
- Economic capital
- Stress testing

---

### Beta Coefficient

**Description**: Systematic risk measure relative to market

**Formula**: `β = Cov(Rᵢ, Rₘ) / Var(Rₘ)`

**Variables:**
- `Rᵢ`: Asset returns
- `Rₘ`: Market returns
- `Cov(·)`: Covariance
- `Var(·)`: Variance

**Key Assumptions:**
- Linear relationship with market
- Constant beta
- Normal returns

**Use Cases:**
- Portfolio risk management
- Asset pricing
- Performance attribution

---

### Sharpe Ratio

**Description**: Risk-adjusted return measure

**Formula**: `Sharpe Ratio = (Rₚ - Rₑ) / σₚ`

**Variables:**
- `Rₚ`: Portfolio return
- `Rₑ`: Risk-free rate
- `σₚ`: Portfolio standard deviation

**Key Assumptions:**
- Normal returns
- Constant risk-free rate

**Use Cases:**
- Performance evaluation
- Portfolio comparison
- Strategy selection

---

## Model Validation Techniques

### VaR Backtesting
**Description**: Kupiec test for VaR model accuracy
**Formula**: `LR = -2 ln[(1-p)^(T-N) × p^N] + 2 ln[(1-N/T)^(T-N) × (N/T)^N]`
**Purpose**: Test if VaR violations match expected frequency

### Credit Model Validation
**Description**: ROC-AUC and Gini coefficient for discriminatory power
**Formula**: `Gini = 2 × AUC - 1`
**Purpose**: Measure model ability to distinguish defaults from non-defaults

### Bias Testing
**Description**: Statistical tests for systematic model bias
**Formula**: `Bias = E[Predicted] - E[Actual]`
**Purpose**: Detect systematic over/under-prediction
