
# Advisor Roth Conversion Designer - UI Flow & Functional Spec v1.0
## Architect: Dr. Elena Vargas

---

## 🎯 Purpose

This module allows financial advisors to manually design Roth conversion schedules, simulate year-by-year impact, and compare baseline vs Roth conversion scenarios.

---

## 🧩 System Dependencies

- Full Calculation Engine (STEP 1-7)
- Roth Conversion Engine (STEP 6)
- Tax, Medicare, IRMAA, MAGI calculations
- Pre-loaded client scenario

---

## 🔧 Full UI Flow Specification

### 1️⃣ Section 1 — Asset Selection Panel

#### Display: Full List of Eligible Roth-Convertible Assets

| Asset | Owner | Value | Amount to Convert |
|-------|-------|-------|--------------------|
| IRA | Client | $X | [Input box] |
| 401k | Spouse | $Y | [Input box] |
| etc. | ... | ... | ... |

- Values preloaded from `core_incomesource` and scenario data.
- Editable input box for advisor to enter amount to convert from each account.
- Total amount requested cannot exceed available balance.
- Show running total of selected amounts.

#### Validation:

- Disable over-allocation (cannot input more than balance).
- Display warnings if total conversion exceeds balances.

---

### 2️⃣ Section 2 — Conversion Schedule Parameters

#### Input Fields:

- ✅ **Projected Pre-Retirement Household Income:** (Pre-filled from scenario income engine; editable override field.)
- ✅ **Conversion Start Year (or Age Selector):**  
  - Year dropdown based on both Client and Spouse.
  - Optional Age-Based picker (auto-translates to year).
- ✅ **Years to Convert (Slider):**  
  - Slider: 0 → 10 years (can be expanded for future versions).
  - If slider = 0, no conversion table generated.
- ✅ **Roth Growth Rate:**  
  - Editable input, default from scenario assumptions.
- ✅ **Age to Begin Roth Withdrawals (optional field for future phases):**
- ✅ **Monthly Roth Withdrawal (optional field for future phases):**

#### Logic:

- Once advisor selects start year and number of years, system calculates even distribution:

```python
Annual_Conversion = Total_Amount_Selected / Years_Selected
```

- Auto-update downstream tables in real-time.

---

### 3️⃣ Section 3 — Conversion Impact Table (Dynamic)

#### Table Columns:

| Year | Client/Spouse Ages | Income Before Conversion | Conversion Amount | Total Taxable Income | Tax Bracket (%) | Federal Tax | Medicare Costs |
|------|--------------------|--------------------------|--------------------|----------------------|----------------|--------------|----------------|

#### Calculation Notes:

- **Income Before Conversion:** pulled from existing Scenario Engine (STEP 3) per year.
- **Conversion Amount:** equal allocation across selected years.
- **Total Taxable Income:** pre-conversion income + Roth conversion for year.
- **Tax Bracket and Federal Tax:** full engine tax calculation applied.
- **Medicare Costs (including IRMAA):** applied with 2-year lookback.

#### Updates:

- Table fully recalculates live as advisor adjusts schedule.

---

### 4️⃣ Section 4 — Baseline vs Roth Conversion Comparison Table

| Metric | Baseline | Roth Conversion |
|--------|----------|------------------|
| Lifetime Federal Taxes | $ |
| Lifetime Medicare Premiums | $ |
| Lifetime IRMAA Surcharges | $ |
| Net Lifetime Spendable Income | $ |
| Final Roth IRA Balance | $ |
| Total Net Assets at Mortality | $ |
| Average IRMAA Tier Hit | Tier Level |

#### Logic:

- Baseline = scenario run without Roth conversions.
- Roth Conversion = scenario run with manual Roth inputs applied.
- Both scenarios run through full engine for full projection.

#### Display:

- Auto-updated side-by-side comparison presented after advisor completes Roth inputs.
- Include short helper text for advisor:  
  > "This summary compares your proposed Roth conversion against your client's baseline scenario, including full tax and Medicare impacts."

---

### 5️⃣ Section 5 — Action Buttons

- ✅ **Recalculate Conversion**
- ✅ **Save Roth Conversion Scenario**
- ✅ **Export Comparison Report (PDF)**

---

### 6️⃣ Section 6 — Optional UI Enhancements (Phase 2)

- Add IRMAA tier visual gauge for each year.
- Add simplified "Maximize to Safe Tax Bracket" button.
- Add Roth Conversion Goal Advisor (target lifetime taxes, IRMAA control, RMD suppression).

---

## 🧮 Backend Notes

- Use full existing engine for recalculation (STEP 1-7).
- Manual Roth conversion schedule fully overrides optimizer engine.
- Fully reuse backend data models and engine flow.

---

## 🔐 Financial Compliance Reminders

- Contributions always stop at retirement.
- Growth applied after withdrawals annually.
- No negative asset balances allowed.
- IRMAA brackets properly inflated 1% per year.
- IRMAA surcharges applied using 2-year MAGI lookback.
- Federal tax calculated after standard deductions by filing status.

---

## ✅ End of Advisor Roth Conversion Designer UI Spec v1.0
