# API Documentation

## Risk Analytics API Endpoints

## POST /api/v1/risk/var/calculate

**Summary**: Calculate Value at Risk (VaR)

**Description**: Calculate VaR using various methodologies (parametric, historical simulation, Monte Carlo)

### Parameters

- **returns** (array) - Historical returns data
- **method** (string) - Default: `parametric`
- **confidence_level** (number) - Default: `0.95` - Confidence level (0-1)
- **time_horizon** (integer) - Default: `1` - Time horizon in days

### Response

```json
{
  "var": 123.45,  // Calculated VaR value
  "expected_shortfall": 123.45,  // Expected shortfall (CVaR)
  "confidence_level": 123.45,
  "method_used": "example_value"
}
```

### Example Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}' \
  http://localhost:5000/api/v1/risk/var/calculate
```

---

## POST /api/v1/risk/credit/score

**Summary**: Generate Credit Score

**Description**: Generate comprehensive credit score for counterparty exposure

### Parameters

- **counterparty_id** (string) *required*
- **exposure_amount** (number) *required*
- **financial_data** (object) - Financial ratios and metrics

### Response

```json
{
  "credit_score": 123.45,  // Numerical credit score
  "probability_of_default": 123.45,  // PD estimate
  "credit_rating": "example_value",  // Letter grade rating
  "expected_loss": 123.45  // Expected loss amount
}
```

### Example Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}' \
  http://localhost:5000/api/v1/risk/credit/score
```

---

## POST /api/v1/risk/market/calculate

**Summary**: Calculate Market Risk

**Description**: Calculate market risk metrics for trading positions

### Parameters

- **positions** (array) - Array of market positions
- **confidence_level** (number) - Default: `0.95`
- **time_horizon** (integer) - Default: `1`

### Response

```json
{
  "var_amount": 123.45,  // Market VaR amount
  "expected_shortfall": 123.45,
  "diversification_ratio": 123.45,
  "position_breakdown": []
}
```

### Example Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}' \
  http://localhost:5000/api/v1/risk/market/calculate
```

---

## POST /api/v1/risk/stress-test

**Summary**: Run Stress Test

**Description**: Execute stress testing scenarios on portfolio

### Parameters

- **portfolio_data** (object) *required*
- **scenario_id** (string) *required*
- **custom_shocks** (object) - Custom shock parameters

### Response

```json
{
  "scenario_id": "example_value",
  "total_loss": 123.45,
  "loss_percentage": 123.45,
  "breakdown_by_asset": []
}
```

### Example Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"example": "data"}' \
  http://localhost:5000/api/v1/risk/stress-test
```

---

## GET /api/v1/risk/dashboard

**Summary**: Get Risk Dashboard Data

**Description**: Retrieve comprehensive risk dashboard metrics

### Parameters

- **date** (string) - Date for risk metrics
- **business_unit** (string) - Filter by business unit

### Response

```json
{
  "risk_metrics": {},  // Current risk metrics
  "risk_breakdown": {},  // Risk by category
  "kri_alerts": [],  // Key risk indicator alerts
  "compliance_status": {}
}
```

### Example Request

```bash
curl -X GET \
  -H "Content-Type: application/json" \
  http://localhost:5000/api/v1/risk/dashboard
```

---
