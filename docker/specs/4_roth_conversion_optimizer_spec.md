
# Roth Conversion Optimizer Module - Developer Build Spec
## Author: Dr. Elena Vargas

---

## 🏗️ Overview

This module automatically finds the optimal Roth conversion schedule for each client using AI-powered simulation.

---

## 🔧 System Inputs

- Full client scenario loaded from existing engine:
  - Client/Spouse DOB
  - Filing Status
  - Retirement Ages
  - Mortality Ages
  - Income Sources (`core_incomesource`)
  - Existing 401k, IRA, Roth, Brokerage balances
  - Monthly Contributions & Growth Rates
- All parameters needed for STEP 1-7 engine.
- Medicare Inflation Rate (advisor input)
- IRMAA Bracket Inflation (fixed at 1% annual)
- Advisor Roth Optimization Preferences (optional future version):
  - Maximize tax savings
  - Minimize IRMAA
  - Maximize Roth growth
  - Net spendable income stability

---

## 🔧 Core Process Flow

### 1️⃣ Build Baseline Scenario (No Roth Conversions)

- Run complete engine (STEP 1-7) for client’s full simulation range.
- Store baseline results:
  - Lifetime tax paid
  - Lifetime Medicare paid
  - IRMAA surcharges
  - Final Roth balances
  - Cumulative net spendable income

### 2️⃣ Generate Conversion Candidates

- For each candidate schedule:
  - Start Year: any year from current year to retirement year (or slightly beyond)
  - Duration: 1-15 years
  - Annual Conversion Amount: range from $20,000/year up to full balance depletion
  - Use Monte Carlo sampling OR grid search OR hybrid (stochastic grid search)

```python
for candidate in candidate_schedules:
    run_full_engine_with(candidate)
```

- Validate feasibility of each schedule:
  - No over-conversion (cannot convert more than balance)
  - Growth applied before conversion withdrawal each year

### 3️⃣ Full Engine Re-Run (STEP 1-7)

- For every candidate, re-run full engine:
  - Apply Roth conversion schedule inside STEP 6.
  - Taxable income, MAGI, IRMAA all re-calculated each year.
  - Asset balances updated each year.

### 4️⃣ Scoring Function

- Calculate multi-factor score for each candidate:

```python
score = (
    weight_taxes * total_taxes_paid
  + weight_medicare * total_medicare_paid
  + weight_income_volatility * std_dev(net_spendable_income)
  - weight_roth_growth * roth_balance_at_mortality
)
```

- Default weights (v1.0):
  - Taxes: 50%
  - Medicare: 20%
  - Roth Growth: 20%
  - Income Stability: 10%

### 5️⃣ Rank & Select Best Solution

- Select candidate schedule with lowest score.
- Store:
  - Optimal Start Year
  - Optimal Duration
  - Annual Conversion Amount
  - Final scoring breakdown

### 6️⃣ Output Model

| Field | Description |
|-------|-------------|
| Start Year | Recommended Roth conversion start year |
| Duration | Number of years to convert |
| Annual Amount | Conversion dollar amount per year |
| Lifetime Tax | Total taxes paid |
| Lifetime Medicare | Total Medicare premiums paid |
| Total IRMAA | Total IRMAA surcharges paid |
| Final Roth | Final Roth balance at mortality |
| Cumulative Net Income | Total net spendable income |
| Income Stability | Income volatility score |

---

## 🔧 Performance Optimization

- Use vectorized pandas dataframes for full year-by-year calculations.
- Use parallel processing / multiprocessing for candidate runs.
- Use numpy random samplers for Monte Carlo candidate schedule generation.
- Cap simulations to ~10,000-100,000 candidates per optimization run.

---

## 🛑 Business Rules

- Roth conversions fully taxable in conversion year.
- MAGI IRMAA lookback still applies.
- Contributions stop at retirement age.
- Growth applied after withdrawals annually.
- RMDs still apply when applicable during or after conversions.

---

## ✅ Phase 1 Goal

- Fully autonomous Roth optimization for financial advisors.

## 🚀 Phase 2 Expansion

- Allow separate spouse-level Roth schedules.
- Allow IRMAA tier targeting logic.
- Allow advisor goal-based optimization sliders.
- Allow multi-goal reporting comparisons.

---

## ✅ End of Developer Build Spec
