
# Roth Conversion Optimizer - API Contract Spec
## Author: Dr. Elena Vargas

---

## 🏗️ Overview

This document defines the full API contract between the frontend UI and backend optimization engine.

---

## 🔧 API Endpoint

- **URL:** `/api/optimizer/run-roth-optimizer`
- **Method:** `POST`
- **Auth:** Token-based authentication (advisor must be authorized user)
- **Response Type:** `application/json`

---

## 🔧 Request Payload

### Body Parameters

```json
{
  "scenario_id": "string",
  "client_id": "string",
  "advisor_overrides": {
    "pre_retirement_income_estimate": 80000,
    "monte_carlo_samples": 50000  // optional, default 10000
  }
}
```

### Parameter Notes

| Field | Description |
|-------|-------------|
| scenario_id | ID of the financial planning scenario |
| client_id | ID of the client |
| pre_retirement_income_estimate | Optional income override for years prior to retirement |
| monte_carlo_samples | Optional override for number of simulation iterations |

---

## 🔧 Backend Processing

- Backend loads full scenario from database using `scenario_id`.
- Backend runs full Monte Carlo Roth Optimization module (per specs defined).
- Backend produces:
  - Optimal solution summary
  - Scoring breakdown
  - Full year-by-year projection for selected optimal schedule

---

## 🔧 Successful Response Payload

```json
{
  "status": "success",
  "optimal_schedule": {
    "start_year": 2030,
    "duration": 5,
    "annual_conversion": 60000
  },
  "scoring_summary": {
    "lifetime_taxes": 425000,
    "lifetime_medicare": 175000,
    "total_irmaa": 42000,
    "final_roth_balance": 850000,
    "net_lifetime_income": 2100000,
    "income_volatility_score": 0.06
  },
  "year_by_year_projection": [
    {
      "year": 2030,
      "client_age": 65,
      "spouse_age": 63,
      "total_income": 125000,
      "magi": 125000,
      "federal_tax": 12500,
      "medicare_premiums": 4200,
      "irmaa": 900,
      "roth_conversion": 60000,
      "ira_balance": 180000,
      "401k_balance": 520000,
      "roth_balance": 110000,
      "total_assets": 1150000,
      "net_spendable_income": 95000
    },
    "... additional years ..."
  ]
}
```

---

## 🔧 Error Response Payload

### 1️⃣ Missing Data

```json
{
  "status": "error",
  "message": "Missing scenario data for scenario_id: XYZ123"
}
```

### 2️⃣ Simulation Failure

```json
{
  "status": "error",
  "message": "Optimization engine failed: IRMAA bracket inflation parameter missing."
}
```

---

## 🔧 Frontend Behavior

- Display optimizer progress while backend processes simulation.
- Present full output to advisor via the Advisor UI Flow Spec.
- Allow advisor to export results into reports.

---

## 🔧 Performance Guidelines

- Backend optimized for parallelization.
- Expected runtime: 10-60 seconds depending on simulation size.
- Timeout: 5-minute maximum.

---

## ✅ End of Optimizer API Contract Spec
