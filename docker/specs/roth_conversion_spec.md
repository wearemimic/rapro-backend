# Roth Conversion Module – Development Specification

This document details the requirements and architecture for integrating a Roth Conversion feature into the retirement scenario platform. The module will simulate the financial impacts of converting pre-tax retirement accounts to Roth IRAs, including tax, Medicare/IRMAA, and account balance changes.

REMEMBER FOR NOW DO NOT UPDATE THE scenario_processor.py

---

## 🗂️ Part 1: `roth_conversion_processor.py`

### ✅ Objective
Generate a modified year-by-year scenario output reflecting Roth conversions, including pre-retirement years if applicable.

### 📥 Inputs
- **Scenario ID** (must be validated for advisor access)
- **Conversion Start Year**
- **Years to Convert** (conversion is evenly distributed unless it cannot be calculated; show message if not possible)
- **Pre-Retirement Income**  
  *(entered as annual value — not monthly)*  
  Pre-Retirement Income is treated as a standard income source for tax calculations. It contributes to total income and MAGI, and is combined if the client is married (household-level).
- **Roth Growth Rate (%)**
- **Max Annual Conversion Amount**
- **Roth Withdrawal Amount**  
  *(entered as annual amount; processor converts to monthly internally)* ROTH becomes a new income source and withdrawals are tax free and excluded from MAGI  
  **Roth withdrawals must begin after the final year of conversion; frontend UI must enforce this check.**
- **Roth Withdrawal Start Year**
- **Per-Asset Conversion Values** (e.g., {asset_id: amount}) (must not exceed max_to_convert for any asset — raise error if violated)  
  If the total conversion amount cannot be evenly distributed over the selected years, raise a validation error. Partial-year conversion is not currently supported.  
  The backend enforces both per-asset and global annual limits. If the combined per-year asset allocations exceed the max annual conversion amount, raise a validation error.  
  If `years_to_convert` = 1, multiple assets can still be used. The total conversion amount is distributed across all assets and must not exceed the per-year max.
- **Total per-asset conversion cap** (frontend must validate inputs do not exceed available balances)

All income fields are **household-level**. MAGI and IRMAA are calculated per individual using household total MAGI and filing status rules (e.g., MFJ vs. Single).

### 🧮 Processing Steps
1. **Load Scenario + Income Sources**

   1a. The `modified_yearly_summary` must match the structure used in `scenario_processor.py`, including fields like:
       - "year", "age", "MAGI", "federal_tax", "medicare_cost", "irmaa", etc.

   1b. Do not mutate original assets in the database. Instead:
       - Clone the income source list in-memory
       - Apply conversions and balance reductions only in the copy  
       The cloned income sources are used entirely within `roth_conversion_processor.py` and are not passed to `scenario_processor.py`, which must remain untouched.

   Example (Python):
   ```python
   cloned_income_sources = copy.deepcopy(scenario.income_sources.all())
   for asset in cloned_income_sources:
       if asset.id in conversion_map:
           asset.current_asset_balance -= conversion_map[asset.id]
   ```

2. **Identify Roth-Convertible Assets** (IRA, 401k)  
   Distribute total conversion amount evenly across the selected conversion years. If the total is not divisible, round the final year’s conversion amount to ensure total matches exactly.  
   If `years_to_convert` = 1, multiple assets can still be used. The total conversion amount is distributed across all assets and must not exceed the per-year max.

3. **Deduct Conversion Amounts from Source Assets**  
   Distribute total conversion amount evenly across the selected conversion years. If the total is not divisible, round the final year’s conversion amount to ensure total matches exactly.  
   Conversion amounts are **subtracted year-by-year** from each source asset during processing, not all at once up front.  
   If `years_to_convert` = 1, multiple assets can still be used. The total conversion amount is distributed across all assets and must not exceed the per-year max.

4. **Create Synthetic Roth Asset**:
   - Initial balance = total converted amount
   - Grows annually at specified rate
   - Withdrawals begin at withdrawal start year  
     Roth withdrawals may occur during or after the conversion period. Ensure withdrawals and conversions are not double-counted in MAGI.  
     **If Roth Withdrawal Start Year is earlier than the final year of conversion, raise a validation error. Withdrawals must not occur until conversion is complete.**  
     Roth withdrawals continue annually at the specified amount until balance reaches $0 or client dies. If the balance is insufficient to support full withdrawals, only available funds are withdrawn.  
   After the conversion period ends but before Roth withdrawals begin, the Roth asset continues compounding annually using the specified growth rate.

5. **Extend Timeline Pre-Retirement if Needed**:
   Extend the projection timeline if the Roth Conversion Start Year is earlier than either person's retirement year:

   a. Determine the earliest year:
      - Take the minimum of:
        • Conversion Start Year
        • Client Retirement Year
        • Spouse Retirement Year (if married)

   b. For each pre-retirement year inserted:
      - Set income = Pre-Retirement Income (from user input)  
      Pre-Retirement Income is treated as a standard income source for tax calculations. It contributes to total income and MAGI, and is combined if the client is married (household-level).
      - Add Roth Conversion Amount to MAGI
      - Recalculate:
        • Total MAGI
        • Federal Tax
        • Medicare + IRMAA (starting at age 65)  
      IRMAA and Medicare are only calculated for individuals age 65+. If one spouse is under 65, IRMAA applies only to the other.  
      - Do NOT assume any other income unless explicitly present

      During conversion years that fall after retirement begins, use actual income sources from scenario (not pre-retirement income). Only use `pre_retirement_income` in years **before** any actual income begins.

      Note: Create a synthetic annual income row in pre-retirement years using `Pre-Retirement Income`.  
      This is used solely for MAGI/tax/IRMAA purposes and is not saved in income_sources.

⏳ Timeline Processing Flow:
For each year (starting from earliest of conversion start, client retirement, or spouse retirement):
1. Calculate Pre-Retirement Income (if applicable)
2. Apply Roth Conversion (if year within conversion window)
3. Apply Roth Withdrawal (if year >= withdrawal start year)
4. Recalculate MAGI, Tax, Medicare/IRMAA, Spend-down

6. **Recalculate Year-by-Year**:
   - Total Income
   - MAGI  
     **MAGI Formula**:  
     `MAGI = Total Income – Standard Deduction + Roth Conversions + Tax-Exempt Interest (if applicable)`
   - Tax Bracket
   - Federal Tax
   - Medicare/IRMAA
   - Asset Spend Down
   - Growth starts in the first year the asset receives conversion funds
   - Roth balance update formula:
     ```python
     balance -= withdrawal
     balance *= (1 + growth_rate)
     ```
   Each year’s Roth balance should be tracked and included in the output to support debugging and future visualization.

7. **Output Modified Timeline** (dict or JSON)

---

## 🔄 Roth Asset History Storage

The year-by-year Roth balance is saved per conversion plan. This enables report generation, audit trails, and comparisons. Use a JSON field in the database or a related table.

---

## 🗂️ Part 2: Frontend Table & Chart Generation

### 📊 Components
- **Conversion Impact Table**
  - Year | Age(s) | Income Before Conversion | Conversion Amount | Taxable Income | Tax Bracket | Federal Tax | Medicare Cost  
  If a year includes both a Roth conversion and withdrawal, display **two separate columns** in the table: `conversion_amount` and `withdrawal_amount`. Avoid merging into a single column.

- **Bar Chart Comparison**
  - RMDs (if we didn’t do a conversion compared to doing one)  
    Suppress RMD values if Roth conversion eliminates all IRA/401k funds before required minimum distribution age.
  - State & Federal Taxes (if we didn’t do a conversion compared to doing one)
  - Medicare & IRMAA (if we didn’t do a conversion compared to doing one)
  - Inheritance Tax (if we didn’t do a conversion compared to doing one)  
    Roth IRA balances are excluded from inheritance tax calculations. Only remaining balances in traditional accounts are subject to the configured inheritance tax rate.
  - Total Expenses (if we didn’t do a conversion compared to doing one)

- **Savings Summary Box**
  - Shows total dollar and percentage savings

Chart Data Mapping:
- X-Axis: Year
- Y-Axis: 
  • Bar 1: Federal Tax
  • Bar 2: Medicare + IRMAA
  • Line: **Remaining Income** = Total Income – (Federal Tax + Medicare + IRMAA)

### 📥 Data Source
- JSON output from `roth_conversion_processor.py`

### 🧪 UX Logic
- Chart/table refreshes after clicking “Recalculate Conversion”
- Table handles extended years (pre-retirement)
- Chart aligns colors and categories between Before/After sets

---

## 🗂️ Part 3: Before vs After Comparison Logic

### 🎯 Objective
Visually and numerically show the impact of Roth conversions.

### 🔄 Inputs
- Original scenario output from `scenario_processor.py`  
  Baseline data should be snapshotted and stored per scenario (e.g., JSONBlob or DB field). Do not re-run the baseline on each conversion; always compare against this stored snapshot. On first run, the baseline output should be snapshotted and reused for future comparisons. Do not recalculate “before” values live when processing Roth scenarios.
- Modified output from `roth_conversion_processor.py`

### 🔍 Logic
- Year-by-year expense category totals
- Sum lifetime totals by category
- Compute savings: Before – After
- Show % reduction in lifetime expenses

### 📦 Output
- Bar chart + numeric table
- JSON object with:
  ```json
  {
    "rmd_savings": 24000,
    "tax_savings": 56000,
    "irmaa_savings": 30000,
    "inheritance_tax_savings": 40000,
    "total_savings": 150000,
    "savings_percent": 0.27
  }
  ```

Savings Calculations:
- IRMAA savings = sum(IRMAA_before) - sum(IRMAA_after)
- Inheritance tax savings = % inheritance tax rate × difference in final asset values (IRA/401k)  
  Roth IRA balances are excluded from inheritance tax calculations. Only remaining balances in traditional accounts are subject to the configured inheritance tax rate.  
  (define % as config constant or user input)

---

## 🧾 Constants & Assumptions

- Tax Brackets: Use 2025 federal brackets; inflation-adjust if needed  
  [View 2025 brackets](https://www.irs.gov/newsroom/irs-provides-tax-inflation-adjustments-for-tax-year-2025)  
  Or embed actual bracket thresholds in a later version.
- IRMAA Brackets: Inflate 1% per year
- Medicare Base Premiums: Inflate 6.45% per year
- Standard Deductions:
  • Single: $14,600
  • MFJ: $29,200
- Inheritance Tax Rate: Configurable % (default: 25%)
- Filing status affects IRMAA brackets and tax rates. Use per-client status (Single, MFJ, etc.) for correct calculations.
- Apply IRMAA to each person individually once they turn 65.

---

## 🧪 Example Inputs & Test Scenarios

---

### 🔧 Example Input JSON
```json
{
  "scenario_id": 123,
  "conversion_start_year": 2030,
  "years_to_convert": 5,
  "pre_retirement_income": 75000,
  "roth_growth_rate": 0.06,
  "max_annual_conversion": 50000,
  "roth_withdrawal_amount": 20000,
  "roth_withdrawal_start_year": 2040,
  "asset_conversion_map": {
    "45": 150000,  // 401k
    "47": 100000   // IRA
  }
}
```

### ✅ Test Case 1: Single Client, Pre-Retirement Conversion
- Client retires at 65 in 2033.
- Roth conversion begins in 2030.
- Pre-retirement income is $75,000/year.
- Withdrawals from Roth start in 2040.
- Expect IRMAA = $0 for ages < 65.
- MAGI for 2030–2032 includes $75,000 + Roth conversion.

### ✅ Test Case 2: Married Couple, Staggered Ages
- Client retires in 2031 (age 62), spouse retires in 2035 (age 65).
- Conversion starts in 2029.
- IRMAA applies to spouse starting 2035 only.
- Roth withdrawals begin in 2039.
- Per-asset limits and annual max respected.

---

## 🧱 Database Changes

### 📌 `RothConversionPlan` (New Model)
| Field | Type | Notes |
|-------|------|-------|
| scenario | FK to Scenario | One plan per scenario |
| start_year | Integer | Year conversion begins |
| years_to_convert | Integer | Total duration |
| max_annual_conversion | Decimal | Cap per year |
| pre_retirement_income | Decimal | Used before retirement |
| roth_growth_rate | Float | Compounded annually |
| roth_withdrawal_amount | Decimal | Monthly |
| roth_withdrawal_start_year | Integer | Year withdrawals begin |
| asset_conversion_map | JSON | {asset_id: amount} |

---

## 🔁 Integration Workflow

1. **User creates a client** (via the standard onboarding flow)  
2. **User creates a baseline retirement scenario** with all income/asset sources  
3. **Scenario is calculated** using `scenario_processor.py` (this file is NEVER modified)  
4. **User clicks “Roth Conversion” inside that scenario**  
5. **User fills out Roth conversion form**, providing:  
   - Conversion Start Year  
   - Years to Convert  
   - Pre-Retirement Income  
   - Roth Growth Rate (%)  
   - Max Annual Conversion Amount  
   - Roth Withdrawal Amount  
   - Roth Withdrawal Start Year  
   - Per-Asset Conversion Values (e.g. {asset_id: amount})  
6. Form is submitted to backend API: `POST /api/roth-conversion/run`  
   Frontend must validate that all of the following fields are required:
   - `conversion_start_year`, `years_to_convert`, `pre_retirement_income`, `max_annual_conversion`, `roth_growth_rate`, `asset_conversion_map`  
   Optional:
   - `roth_withdrawal_amount`, `roth_withdrawal_start_year` (defaults to 0 if not provided)  
   Frontend UI must enforce that Roth withdrawals start **after** the final year of conversion.
7. Backend:  
   - Loads scenario  
   - Applies conversion plan logic via `roth_conversion_processor.py`  
   - Rebuilds modified year-by-year timeline  
   - Calculates Before/After summary  
8. Frontend:  
   - Renders new timeline table and comparison charts  
   - Displays savings summary box (in dollars + percent)

---

## ✅ Output Example
| Year | Age | Income | Conversion | MAGI | Fed Tax | Medicare | IRMAA |
|------|-----|--------|------------|------|---------|----------|--------|
| 2030 | 60  | $100,000 | $15,000 | $115,000 | $10,000 | $3,000 | $0 |
| ...  | ... | ... | ... | ... | ... | ... | ... |

# 
# ---
#

## ⚠️ Gotchas & Developer Notes

### 🔹 Deepcopy of ORM Objects
When cloning `income_sources`, ensure that the Django queryset is explicitly converted to a list before `copy.deepcopy()`:
```python
cloned_income_sources = copy.deepcopy(list(scenario.income_sources.all()))
```
Avoid directly deep copying querysets, which may result in unexpected behavior.

---

### 🔹 Conversion Year Rounding
If the total amount is not divisible evenly across `years_to_convert`, apply the remainder to the **final year** so the total matches the user input exactly. This must not result in under- or over-conversion.

---

### 🔹 Withdrawal Before Conversion Ends
If `roth_withdrawal_start_year` is earlier than the final conversion year, **raise a backend validation error**. This is also enforced on the frontend.

---

### 🔹 MAGI: Tax-Exempt Interest
If tax-exempt income needs to be included in MAGI, ensure that this value is either passed into the processor or explicitly documented as a source field.

---

### 🔹 Roth Growth Ordering
Annual Roth asset growth is calculated **after** the withdrawal for the year is applied:
```python
balance -= withdrawal
balance *= (1 + growth_rate)
```

---

### 🔹 Mortality Age Defaults
If mortality age is not provided in the scenario data, assume a default of `95` for both client and spouse (if applicable).

---

### 🔹 IRMAA and Filing Status
MAGI is summed at the **household level**, and IRMAA thresholds are applied individually using filing status rules. IRMAA applies only when a person is age 65+.

---

### 🔹 Frontend Row Markers for Synthetic Years
Rows that are inserted due to pre-retirement projection extension (via `pre_retirement_income`) should be flagged in the output like:
```json
"synthetic": true
```
This allows the frontend to distinguish baseline vs. inserted years.

---

### 🔹 Before/After Snapshot Storage
Baseline snapshot of `scenario_processor.py` output should be stored in a JSONField per scenario. Recommended approach:
- Save to `baseline_output` field on `Scenario`
- Or store in new `RothConversionComparison` table, keyed by `scenario_id + timestamp`

---

### 🔹 Error Format for Validation Failures
All backend validation errors should return JSON using this structure:
```json
{
  "error": "Asset conversion amount exceeds available balance.",
  "field": "asset_conversion_map",
  "invalid_asset_id": "45"
}
```
This allows the frontend to clearly indicate which asset or field caused the failure.