# Financial Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

A comprehensive financial analytics platform providing real-time market analysis, portfolio management, risk assessment, and AI-powered insights. Built with real-time data from Yahoo Finance and powered by Google Gemini AI.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Available Assets](#available-assets)
- [Security](#security)

---

## Overview

Professional-grade financial analytics dashboard delivering real-time market data, advanced risk metrics, time series forecasting with deep learning, and AI-powered insights through Google Gemini integration.

**Core Capabilities:**
- Real-time portfolio tracking and optimization
- Multi-method Value at Risk (VaR) calculations
- LSTM-based price forecasting with TensorFlow
- Market regime detection and anomaly analysis
- Natural language AI assistant for financial queries

---

## Key Features

### Portfolio Management
- Custom portfolio creation with 15+ major US stocks
- Multiple weighting strategies (equal weight, market cap, custom)
- Real-time performance tracking and S&P 500 benchmark comparison
- Risk metrics: Sharpe ratio, maximum drawdown, volatility
- Alpha and beta calculations

### Market Analytics
- Live stock data from Yahoo Finance
- Technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands
- Interactive candlestick charts with volume analysis
- Multiple timeframes: 1M, 3M, 6M, 1Y
- Real-time price and market index tracking

### Risk Analytics
- **Value at Risk (VaR)** - Three calculation methods:
  - Parametric (Variance-Covariance)
  - Historical Simulation (5th percentile)
  - Monte Carlo Simulation (10,000 scenarios)
- Stress testing: market crash, volatility spike, black swan scenarios
- Risk limits monitoring and position tracking
- Portfolio sensitivity analysis

### Time Series Forecasting
- **ARIMA**: Statistical time series modeling
- **ETS**: Exponential smoothing state space models
- **Prophet**: Facebook's forecasting algorithm
- **LSTM**: Deep learning neural network (TensorFlow/Keras)
  - 2-layer architecture: 50 LSTM units per layer
  - Dropout regularization (0.2)
  - 60-day lookback window
  - MinMaxScaler normalization
- Confidence intervals and backtesting
- Forecast horizons: 1-365 days

### Machine Learning Models
- Price prediction with ensemble methods
- Anomaly detection via Isolation Forest
- Market regime classification (K-Means, GMM)
- Feature engineering with technical indicators
- Model validation and performance metrics

### AI Assistant
- Google Gemini 1.5 Flash integration
- Natural language financial queries
- Real-time market context (S&P 500, VIX, stock data)
- Portfolio-aware recommendations
- Conversation history tracking

---

## Technology Stack

### Core Framework
- **Streamlit** 1.28+ - Interactive web dashboard
- **Python** 3.12+ - Primary programming language

### Data & Analytics
- **Pandas** 2.0+ - Data manipulation and analysis
- **NumPy** 1.24+ - Numerical computing
- **yfinance** - Real-time market data (Yahoo Finance API)

### Machine Learning
- **TensorFlow** 2.20+ - Deep learning framework (LSTM)
- **scikit-learn** 1.3+ - Classical ML algorithms
- **statsmodels** - Time series analysis (ARIMA, ETS)
- **Prophet** - Facebook's forecasting library

### Visualization
- **Plotly** 5.14+ - Interactive charts and graphs
- **Matplotlib** & **Seaborn** - Statistical visualizations

### Risk & Statistics
- **SciPy** 1.10+ - Statistical functions and distributions
- Custom VaR implementations (Parametric, Historical, Monte Carlo)

### AI Integration
- **google-generativeai** 0.8.5 - Google Gemini API client

---

## Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/financial-analytics-platform.git
cd financial-analytics-platform
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys** (Optional - for AI Assistant)
- Obtain Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- Enter key in the AI Assistant page when running the application
- Keys are stored only in browser session memory

5. **Run the application**
```bash
streamlit run demo/streamlit_app.py --server.port 8501
```

6. **Access the dashboard**
```
http://localhost:8501
```

---

## Usage

### Portfolio Management
1. Navigate to "Portfolio Management" page
2. Select stocks from available list (15+ major US stocks)
3. Choose weighting strategy: Equal, Market Cap, or Custom
4. Adjust custom weights using interactive sliders
5. View real-time portfolio metrics and S&P 500 comparison

### Risk Analytics
1. Go to "Risk Analytics" page
2. Build custom portfolio with position weights
3. Calculate VaR using Parametric, Historical, or Monte Carlo methods
4. Run stress tests: market crash (-20%), volatility spike, black swan
5. Monitor risk limits and position concentrations

### Time Series Forecasting
1. Select "Time Series Forecasting" page
2. Choose stock ticker from dropdown
3. Select forecast model: ARIMA, ETS, Prophet, LSTM, or Ensemble
4. Set forecast horizon (1-365 days)
5. View predictions with confidence intervals and backtesting results

### Machine Learning Models
1. Navigate to "ML Models" page
2. Choose analysis type:
   - Price Prediction (ensemble methods)
   - Anomaly Detection (Isolation Forest)
   - Market Regime Classification
3. Select stock and configure parameters
4. Review model performance and visualizations

### AI Assistant
1. Open "AI Assistant" page
2. Enter Google Gemini API key (first time only)
3. Ask questions in natural language:
   - "What's the current VIX level and what does it mean?"
   - "Analyze AAPL's risk metrics"
   - "Compare my portfolio against S&P 500"
4. Receive AI-powered insights with live market context

---

## Available Assets

### Stocks (15+)
- **Technology**: AAPL, GOOGL, MSFT, AMZN, TSLA, META, NVDA
- **Financial**: JPM, BAC, GS
- **Healthcare**: JNJ, PFE
- **Energy**: XOM, CVX
- **Retail**: WMT

### Market Indices (3)
- **^GSPC**: S&P 500 Index
- **^IXIC**: NASDAQ Composite
- **^VIX**: CBOE Volatility Index

---

## Security

### Data Privacy
- No user data or credentials saved to disk
- All data processed in-memory only
- Session-based state management

### API Key Security
- Gemini API keys stored only in browser session
- No server-side persistence
- User-controlled key management

### Network Security
- HTTPS for all external API calls (Yahoo Finance, Google AI)
- No data transmission to third parties
- Local-first architecture

### Session Isolation
- Each user session is independent
- No cross-session data sharing
- Automatic session cleanup on browser close
