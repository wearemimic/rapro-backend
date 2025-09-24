
# Retirement Income Scenario Calculation — Technical Specification

## Purpose:
Calculate projected year-by-year financial results for a client's retirement scenario, including:
- Income sources
- Federal taxes
- Roth conversions
- Medicare premiums & IRMAA surcharges
- Social Security benefits
- Asset spend-downs
- Survivor adjustments

---

## Data Inputs

### 1️⃣ Client Data (`core_client`)
- First Name
- Last Name
- Date of Birth
- Tax Filing Status (`Single`, `Married Filing Jointly`, `Married Filing Separately`)
- Spouse First Name / Last Name / Date of Birth (if applicable)

### 2️⃣ Scenario Data (`core_scenario`)
- Retirement Age (client)
- Retirement Age (spouse if applicable)
- Medicare Start Age (default 65, adjustable)
- Mortality Age (client)
- Mortality Age (spouse if applicable)
- Scenario Status (`Draft`, `In Progress`, `Reviewed`, `Archived`)
- Scenario Name (editable inline)

### 3️⃣ Income Source Data (`core_incomesource`)
- Income Type (earned, pension, rental, annuity, IRA, 401(k), Social Security, Roth Conversion, Other)
- Monthly Amount
- Age to Begin Withdrawal
- Age to End Withdrawal
- COLA Adjustment (annual inflation assumption per source)
- Tax Rate Override (optional)
- Rate of Return (for invested sources)

### 4️⃣ Scenario Global Parameters
- Inflation Rate (user input or default)
- Market Return Rate (user input)
- Standard Deviation (for Monte Carlo or Stress Tests)
- Federal Tax Brackets (static or API-loaded annually)
- Medicare Inflation Rate: 6.45% per year (base + IRMAA)
- IRMAA Bracket Inflation Rate: 1% per year

---

## Calculation Engine Logic

### Step 1: Build Projection Years
- For Single:
  - Start year = current year + (retirement_age - current_age)
  - End year = start year + (mortality_age - retirement_age)
- For Married:
  - Calculate earliest retirement age for either spouse for start year.
  - End year = last spouse mortality year.

### Step 2: Income Projections
- For each year:
  - Calculate each income source based on start/stop ages.
  - Apply growth rates for assets such as 401k and IRA
  - Apply COLA adjustments annually.
  - Apply tax rate override where applicable.

### Step 3: Social Security Calculation
- Start at selected filing ages.
- Apply COLA adjustments.
- Allow life expectancy override to calculate break-even and lifetime benefit tables.( in the social security break even tab)
- Survivorship logic after spouse death.

### Step 4: Federal Tax Calculation
- Use progressive tax brackets based on filing status.
- MAGI = Total Income - Standard Deduction + Roth Conversions + Tax-Exempt Interest.
- Apply tax rate per bracket.

### Step 5: Medicare & IRMAA Calculation
- Starts at the age the client chooses to take it in the scenario builder
- Base premiums: Part B & Part D inflated at the rate that is chosen in the scenario builder
- IRMAA brackets inflated 1% annually.
- Apply surcharge tiers based on MAGI each year.
- Survivorship adjustments (single IRMAA brackets after spouse death).

### Step 6: Roth Conversion Logic
- Allow Roth conversion schedule per scenario.
- Conversion amount increases MAGI and affects IRMAA.
- Conversion spread evenly over user-selected number of years.

### Step 7: Asset Spend-Down
- Display spend-down projections for:
  - IRA
  - 401(k)
  - Roth IRA
  - Other investment accounts
- Apply rate of return assumptions and withdrawal sequences.

---

## Output

### 5 tabs of outputs
## Tab 1 Financial overview

| Year | Age (Client) | Age (Spouse only if not single) | Total  Income | MAGI | Federal Tax | IRMAA B/D Surcharges | Total Medicare |  Net Spendable Income |
|------|--------------|---------------------------------|---------------|------|-------------|----------------------|----------------|---------------------------|

## Tab 2 Social Security overview

| Year | Age (Client) | SSI Benefit (total Social Security) | Total Medicare |  SSI Tax Percentage | Net Spendable Income |
|------|--------------|-------------------------------------|----------------|---------------------|----------------------|

## Tab 3 Medicare overview

| Year | SSI Benefit (total Social Security) | Total Income | MAGI |  Part B (Client) | Part D  (Client) | Part B (spouse only if not single) | Part D (spouse only if not single)  | Total Cost |
|------|-------------------------------------|--------------|------|------------------|------------------|------------------------------------|------------------------------------|---------|

## Tab 4 Income Listing

| Income Type | Owner | 
|------|-------------------------------------|

## Tab 5 Skip for now

## Tab 6 Social Security Worksheets Skip for now





### Graphs
- Total Income Line Chart
- Medicare Costs (Base + IRMAA) Stacked Bar Chart
- Remaining Income Line Chart
- Asset Spend-Down Graphs (IRA, 401k, Roth, Other)
- Social Security Breakeven Chart & Lifetime Value Table

### Export Options
- PDF report builder: select which graphs/tables to include.
- Multiple layout options for advisor deliverables.

---

## Enhancements Already Logged
- Inline scenario name editing
- Editable life expectancy for Social Security calculations
- Fully exportable PDF reports
- Report builder to select display order of charts/tables
- Dynamic Medicare table with IRMAA display
- Drag-to-copy functionality for editable tables (Income Tab)
- SSA-44 Form generation for IRMAA appeal workflows (future)

---

## Backend Framework
- **Language:** Python 3.12
- **Framework:** FastAPI (backend API)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Monte Carlo Module:** NumPy, pandas, numba

---

## Frontend Framework
- **Framework:** Vue.js 3 (with Vite build system)
- **UI Theme:** Front Dashboard (Bootstrap-based)
- **PDF Export:** html2canvas + jsPDF

---

## Open Items / Future Work
- More advanced Monte Carlo stress testing tied into income projection
- Better survivorship modeling for post-spouse-death income adjustments
- Enhanced Roth conversion optimizer
- SSA-44 automation
- Historical IRMAA bracket database for real-world audit trail

---

## CURRENT COMPLETION STATUS:
> About 70-75% of this spec is already in the codebase, based on our recent builds.
