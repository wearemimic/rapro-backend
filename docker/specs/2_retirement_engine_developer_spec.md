
# Retirement Scenario Calculation Engine - Developer Build Spec
## Author: Dr. Elena Vargas

---

## 🏗️ Overview

This document provides the **technical build spec** for developers to implement the full calculation engine.

---

## 🧩 System Modules

### Module 1: Scenario Initialization (STEP 1)

- Load client & spouse records from database (`core_client`, `core_spouse`).
- Calculate client/spouse ages each year.
- Determine retirement start year, simulation start & end year.

**Key Output:** Simulation year range and ages table.

---

### Module 2: Income Stream Mapping (STEP 2)

- Load all income sources (`core_incomesource`):
  - income_type, monthly_amount, age_to_begin_withdrawal, age_to_end_withdrawal, cola, exclusion_ratio, tax_rate, rate_of_return, monthly_contribution, current_asset_balance.
- Calculate income start/end years from client/spouse birthdates.
- Apply annual COLA inflation.
- Store annualized income stream per year.

**Key Output:** Income stream map (gross income per year).

---

### Module 3: Taxable Income & MAGI Engine (STEP 3)

- Aggregate total income per year.
- Classify taxability of each income type.
- Apply Social Security combined income formula to determine taxable portion.
- Calculate MAGI for IRMAA (includes muni interest & Roth conversions).
- Apply standard deduction by filing status.

**Key Output:** Taxable income, MAGI, taxable SS.

---

### Module 4: Federal Tax & AMT Engine (STEP 4)

- Apply progressive tax brackets to taxable income.
- Apply AMT exemption calculation.
- Calculate AMT tax using 26% / 28% rates.
- Federal tax liability = max(regular tax, AMT tax).

**Key Output:** Federal tax, AMTI, AMT liability.

---

### Module 5: Medicare Premium & IRMAA Engine (STEP 5)

- Check Medicare eligibility at age 65.
- Inflate Part B and D base premiums annually using advisor-selected Medicare inflation rate.
- Inflate IRMAA brackets 1% annually from 2025 base.
- Apply IRMAA surcharges based on 2-year lookback MAGI.
- Total Medicare = Base Premium + IRMAA surcharge.

**Key Output:** Medicare premiums (client & spouse).

---

### Module 6: Roth Conversion Engine (STEP 6)

- Accept advisor-defined joint conversion schedule: start year, duration, annual conversion amount.
- Apply pro-rata asset depletion across eligible balances (IRA, 401k, etc.).
- Conversion amount treated as additional taxable income & MAGI.
- Update Roth balances accordingly with growth.

**Key Output:** Updated taxable income, Roth balances, IRA balances.

---

### Module 7: Asset Spend-Down & Growth Engine (STEP 7)

- Apply monthly contributions (pre-retirement only).
- Apply growth rates per account after contributions.
- Apply withdrawals (monthly withdrawal amounts).
- Apply RMD override at RMD age (IRS table).
- Prevent negative balances.
- Handle Roth growth (no withdrawals required).

**Key Output:** Year-end balances for IRA, 401k, Roth, Brokerage.

---

## 🔄 Module Dependencies

- Module 1 → Feeds Module 2
- Module 2 → Feeds Module 3
- Module 3 → Feeds Modules 4 & 5
- Module 6 → Modifies Module 3–5 dynamically
- Module 7 → Pulls final balances after all prior modules run

---

## 🗃️ Database Tables Used

### core_client
- id, birthdate, tax_status

### core_spouse
- id, birthdate, client_id

### core_incomesource
- owned_by, income_type, current_asset_balance, monthly_amount, age_to_begin_withdrawal, age_to_end_withdrawal, rate_of_return, cola, exclusion_ratio, tax_rate, scenario_id, monthly_contribution

---

## 🛑 Special Business Rules

- MAGI used for IRMAA comes from 2 years prior.
- Contributions stop at retirement age.
- Growth applied AFTER withdrawals each year.
- Roth balances never decrease (unless distributions logic added later).
- RMD override applies if calculated RMD > requested withdrawals.
- Separate Roth conversion schedules per spouse reserved for Phase 2.

---

## 🧮 Output Model

- Build full year-by-year output table as single dataset.
- Use this for advisor-facing graphs, reports, and scenario comparisons.

| Year | Client Age | Spouse Age | Total Income | MAGI | Federal Tax | Medicare Premiums | IRMAA | Roth Conversion | IRA Balance | 401k Balance | Roth Balance | Total Assets | Net Spendable Income |
|------|------------|------------|--------------|------|--------------|-------------------|-------|------------------|-------------|--------------|--------------|--------------|----------------------|

---

## ✅ End of Developer Build Spec
