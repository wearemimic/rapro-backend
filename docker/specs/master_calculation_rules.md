
# Master Calculation Rules & Edge Case Reference - Roth Conversion Optimizer SaaS Build
## Architect: Dr. Elena Vargas

---

## 🏗️ Purpose

This document consolidates ALL of the core calculation rules, logic nuances, edge cases, and financial compliance details discussed throughout the full spec build.

It supplements the previous spec documents and should be included alongside them as a system-level AI reference.

---

## 🧮 Universal Calculation Rules

### Client Initialization (STEP 1)

- Client and Spouse handled independently but combined for tax purposes unless stated otherwise.
- Filing Status options: Single, Married Filing Jointly, Married Filing Separately.
- Retirement ages for client and spouse are independently set.
- Mortality ages independently set (used for scenario simulation range).
- RMD ages handled per Secure Act 2.0 (starting age 73, flexible for future versions).

---

## 🧮 Income Mapping (STEP 2)

- Income Sources include:
  - Social Security (with COLA)
  - Pension (with COLA)
  - Rental Income (with COLA)
  - Annuities
  - Taxable Investment Accounts (Growth applied)
  - Roth IRA (Growth applied)
  - Traditional IRA / 401(k) / 403(b) (Growth applied)
  - Employer Retirement Plans
  - Wages (Pre-retirement)
  - Self-Employment Income (Pre-retirement)
  - Inheritance
  - Other Taxable / Non-Taxable Income streams

- COLA applied annually to all income streams where applicable.
- All monthly amounts are converted to annual for calculations (`monthly_amount * 12`).
- Contributions (`monthly_contribution`) stop at retirement age per owner.

---

## 🧮 Taxable Income & MAGI (STEP 3)

- Standard Deduction applied per filing status.
- Social Security taxability handled per IRS combined income formula.
- MAGI includes:
  - All taxable income
  - Tax-exempt interest (muni bonds)
  - Roth conversions
  - Non-taxable income streams as applicable

---

## 🧮 Federal Tax & AMT (STEP 4)

- Full 2025 IRS Federal Tax Brackets applied.
- AMT calculated using:
  - Exemption amount & phaseout
  - 26% / 28% marginal AMT rates
- Federal Tax Liability = Higher of regular tax or AMT.

---

## 🧮 Medicare Premium & IRMAA (STEP 5)

- Medicare eligibility starts at age 65.
- Base Medicare premiums inflated annually at 6.45% (user-controlled rate).
- IRMAA brackets inflated annually at 1% starting from 2025 values.
- IRMAA tiers determined based on MAGI from 2-years prior.
- IRMAA surcharge amounts also inflated at 6.45% alongside base premiums.

#### IRMAA 2025 Brackets Used as Base:

| Tier | MFJ | Single |
|------|-----|--------|
| 1 | $206,000 | $103,000 |
| 2 | $258,000 | $129,000 |
| 3 | $322,000 | $161,000 |
| 4 | $386,000 | $193,000 |
| 5 | $750,000 | $500,000 |

---

## 🧮 Roth Conversion Engine (STEP 6)

- Phase 1 logic: Joint Household Conversion Schedule (applies combined taxable income for tax purposes).
- Conversion Inputs:
  - Start Year
  - Duration (# of years)
  - Annual Conversion Amount
- Account depletion applied pro-rata across eligible accounts (IRA, 401k, etc).
- Conversion amounts fully taxable in year converted.
- Growth applied after conversion depletion for both IRA and Roth balances.

---

## 🧮 Asset Spend-Down & Growth Engine (STEP 7)

- Monthly contributions applied until retirement age (per owner).
- Growth applied annually after contributions and withdrawals.
- Withdrawals occur post-retirement per scheduled income withdrawal amounts.
- RMD applied at RMD age:
  - If calculated RMD exceeds scheduled withdrawal, RMD overrides the withdrawal.
- RMD calculation uses IRS Uniform Lifetime Table divisor per age.
- Negative balances prevented at all times.

---

## 🧮 Edge Case Handling

- Survivor Rule: Upon spouse death, survivor switches to Single filing status; Roth and taxable balances continue fully controlled by survivor.
- If Roth conversion is scheduled before retirement, contributions still apply until retirement age.
- If Roth conversion occurs post-retirement, contributions are zero but growth still applies.
- Partial account depletion allowed: conversions are capped by available balance.
- Conversion schedules terminate early if accounts deplete before full duration completes.
- IRMAA surcharges reflect correct 2-year lookback logic — optimizer engine accounts for how pre-retirement conversions impact IRMAA at Medicare eligibility start.

---

## 🧮 Roth Optimizer Logic (Monte Carlo Engine)

- Search ranges:
  - Start Year: current year to ~retirement year + 5
  - Duration: 1-15 years
  - Annual Conversion: $20,000 to available balance limits

- Score Function Factors:
  - Lifetime Taxes Paid
  - Lifetime Medicare Paid
  - Lifetime IRMAA Paid
  - Final Roth Balance at Mortality
  - Net Lifetime Spendable Income
  - Income Stability (Volatility Score)

- Sampling approach uses randomized grid + parallel multiprocessing to run thousands of full scenario calculations per candidate schedule.

---

## 🧮 SaaS Compliance Safety Notes

- IRS compliance maintained across tax, AMT, RMD, Social Security, Medicare, IRMAA.
- MAGI is strictly calculated for IRMAA rules, including 2-year lag.
- No income stream double counting allowed.
- Growth always applied after contribution/withdrawal events annually.
- Contributions stop upon retirement age for both client & spouse independently.
- All monthly fields converted to annual throughout calculations.

---

## ✅ End of Master Calculation Rules Document
