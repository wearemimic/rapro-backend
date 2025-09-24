
# Retirement Scenario Calculation Engine - Sample Test Case
## Author: Dr. Elena Vargas

---

## Scenario Summary

- Client: John Doe, DOB: 1965-01-01
- Spouse: Jane Doe, DOB: 1967-01-01
- Filing Status: Married Filing Jointly (MFJ)
- Retirement Ages: Client 65, Spouse 65
- Mortality Ages: Client 90, Spouse 90
- Simulation Start Year: 2030

---

## Income Sources

| Account | Owner | Balance | Monthly Amount | Start Age | End Age | COLA | Rate of Return | Contributions |
|---------|-------|---------|----------------|-----------|---------|------|----------------|----------------|
| 401k | Client | $800,000 | $0 | N/A | N/A | N/A | 5% | $1,500 |
| 401k | Spouse | $500,000 | $0 | N/A | N/A | N/A | 5% | $1,000 |
| IRA | Client | $200,000 | $0 | N/A | N/A | N/A | 5% | $0 |
| Roth IRA | Client | $50,000 | $0 | N/A | N/A | N/A | 6% | $0 |
| Pension | Client | N/A | $2,000 | 65 | 90 | 2% | N/A | $0 |
| Social Security | Client | N/A | $2,500 | 67 | 90 | 2% | N/A | $0 |
| Social Security | Spouse | N/A | $1,800 | 67 | 90 | 2% | N/A | $0 |
| Rental Income | Joint | N/A | $1,200 | 65 | 90 | 2% | N/A | $0 |
| Taxable Account | Joint | $300,000 | N/A | N/A | N/A | N/A | 4% | $0 |

---

## Roth Conversion Schedule

- Start Year: 2030 (Pre-Retirement)
- Duration: 5 Years
- Annual Conversion Amount: $60,000 (Joint Household Schedule)
- Accounts eligible: IRA + 401k balances
- Roth Growth Rate: 6%

---

## Assumptions

- Standard Deduction: Indexed to tax year (using 2025 base values)
- Federal Tax Brackets: 2025 values
- AMT: Active per current law
- Medicare Inflation Rate: 6.45%
- IRMAA Bracket Inflation: 1% annually
- 2-Year IRMAA Lookback Applied

---

## Sample Year-by-Year Output (Partial Extract)

| Year | Client Age | Spouse Age | Total Income | MAGI | Fed Tax | Medicare Premiums | IRMAA | Roth Conv | IRA | 401k | Roth | Taxable | Net Income |
|------|------------|------------|--------------|------|---------|-------------------|-------|-----------|-----|------|------|---------|------------|
| 2030 | 65 | 63 | $125,000 | $125,000 | $12,500 | $0 | $0 | $60,000 | $180k | $520k | $110k | $350k | $95k |
| 2031 | 66 | 64 | $128,000 | $128,000 | $13,000 | $0 | $0 | $60,000 | $115k | $350k | $178k | $360k | $98k |
| 2032 | 67 | 65 | $165,000 | $165,000 | $19,500 | $4,200 | $900 | $60,000 | $75k | $250k | $260k | $375k | $101k |
| 2033 | 68 | 66 | $168,000 | $168,000 | $20,200 | $4,400 | $950 | $60,000 | $40k | $150k | $350k | $385k | $102k |
| 2034 | 69 | 67 | $175,000 | $175,000 | $21,000 | $4,700 | $1,000 | $60,000 | $0 | $50k | $445k | $395k | $103k |
| 2035 | 70 | 68 | $155,000 | $155,000 | $17,500 | $4,900 | $1,050 | $0 | $0 | $55k | $472k | $410k | $104k |

---

## Output Observations

- Roth balance grows as conversions occur.
- IRA & 401k balances deplete over conversion period.
- Federal tax increases during conversion years.
- Medicare IRMAA surcharges begin post age 65 and track MAGI 2 years prior.
- Contributions stop once client & spouse retire.

---

## End of Sample Test Case
