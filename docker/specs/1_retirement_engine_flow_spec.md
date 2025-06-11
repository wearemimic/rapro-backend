
# Retirement Scenario Calculation Engine - Full Flow Spec
## Author: Dr. Elena Vargas

---

## High-Level Engine Flow

1️⃣ **Client Initialization (STEP 1)**  
- Pull client & spouse birthdates, tax status, retirement ages, mortality ages.  
- Calculate retirement start year, simulation year range, and filing status per year.

2️⃣ **Income Mapping (STEP 2)**  
- Build full income stream map year-by-year based on:  
    - Monthly amount
    - Start/end ages
    - COLA inflation
    - Exclusion ratios (for partial taxability)
    - Tax rates
- Aggregate gross income per year.

3️⃣ **Taxable Income & MAGI Engine (STEP 3)**  
- Aggregate income sources into taxable vs non-taxable streams.
- Apply Social Security combined income formula.
- Build MAGI calculation for IRMAA and Medicare.

4️⃣ **Federal Tax & AMT Engine (STEP 4)**  
- Apply progressive federal tax brackets after standard deduction.
- Apply Alternative Minimum Tax (AMT) rules.
- Select higher of regular tax or AMT.

5️⃣ **Medicare & IRMAA Engine (STEP 5)**  
- Apply Medicare eligibility at age 65.
- Inflate base premiums annually.
- Inflate IRMAA brackets 1% per year.
- Apply IRMAA surcharges based on MAGI from 2 years prior.
- Calculate total Medicare premiums per person, per year.

6️⃣ **Roth Conversion Engine (STEP 6)**  
- Advisor specifies household conversion schedule (start year, years, total annual conversion).
- Apply pro-rata account depletion across eligible balances.
- Apply full conversion amounts as taxable income.
- Flow-through to tax, MAGI, IRMAA.

7️⃣ **Asset Spend-Down & Growth Engine (STEP 7)**  
- Apply monthly contributions until retirement age.
- Apply growth rates annually.
- Apply withdrawals after retirement start year.
- Apply RMD override when applicable (IRS Uniform Lifetime Table).
- Apply Roth conversions as account depletion & Roth growth.
- Prevent negative balances.
- Survivor rules handle tax filing transitions.

---

## Engine Dependencies (Data Flow)

- STEP 1 → Feeds STEP 2
- STEP 2 → Feeds STEP 3 (Income)
- STEP 3 → Feeds STEP 4 (Taxable Income)
- STEP 3 → Feeds STEP 5 (MAGI → IRMAA)
- STEP 4 → Feeds net tax result
- STEP 5 → Feeds Medicare costs
- STEP 6 → Modifies STEP 3-5 by injecting Roth conversions into taxable income and MAGI
- STEP 7 → Fully calculates year-end balances, growth, withdrawals

---

## Output Table (Master Data per Year)

| Year | Client Age | Spouse Age | Total Income | MAGI | Federal Tax | Medicare Premiums | IRMAA | Roth Conversion | IRA Balance | 401k Balance | Roth Balance | Total Assets | Net Spendable Income |
|------|------------|------------|--------------|------|--------------|-------------------|-------|------------------|-------------|--------------|--------------|--------------|----------------------|

---

## Design Notes for Developers

- Fully modularized engine allows adding Phase 2 logic:  
    - Separate spouse Roth conversion schedules  
    - Detailed RMD table updates  
    - Multi-account prioritization strategies

- All MAGI-dependent functions (IRMAA) respect 2-year lookback.

- Roth conversions always modeled as taxable income additions.

- Contributions stop at retirement age for 401k, IRA, Roth, etc.

- Growth applied after contributions and withdrawals each year.

---

## End of Full Engine Flow Spec
