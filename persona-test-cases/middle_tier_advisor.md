# Sample Test Cases for Persona: Middle-Tier Financial Advisor

## Module: Roth Conversion Planning

### Test Case 1: Basic Roth Conversion Flow
- Advisor enters $1M IRA balance
- Advisor selects 5-year conversion starting at age 65
- Client is married filing jointly
- Confirm projected MAGI, federal taxes, and IRMAA surcharges update correctly
- Validate yearly taxable income vs Roth conversion amount

### Test Case 2: Roth Conversion with Income Limits
- Advisor inputs other income sources (Social Security + Pension)
- Advisor selects partial Roth conversions under IRMAA thresholds
- Validate Roth optimizer recommends tax-efficient annual amounts
- Verify output table shows MAGI impact for each year

---

## Module: Social Security Timing

### Test Case 3: Spousal Benefits Filing
- Client: 67, Spouse: 63
- Advisor selects spousal filing restricted application
- Confirm correct spousal benefit calculation
- Verify optimal filing recommendations are generated

### Test Case 4: Early Filing Penalty
- Client files at 62
- Confirm system applies early filing reduction properly
- Verify lifetime benefit total vs waiting to full retirement age

---

## Module: Medicare & IRMAA

### Test Case 5: IRMAA Impact with Roth Conversions
- Roth conversion pushes MAGI into IRMAA brackets
- Confirm system calculates Part B and Part D IRMAA surcharges
- Validate yearly inflation on IRMAA thresholds (1% inflation default)

### Test Case 6: Surviving Spouse Rule
- Spouse dies at 72
- Confirm filing status changes to single for surviving spouse
- Validate correct single IRMAA brackets applied

---

## Module: Client Report Generation

### Test Case 7: Client-Friendly Summary
- Advisor selects Roth + SS + Medicare summary report
- Confirm PDF output includes charts, tables, and action prompts
- Validate formatting is client-facing and presentable

---

## Module: AI Next-Step Engine

### Test Case 8: Action Recommendation Prompt
- Advisor updates scenario with new income source
- Confirm system re-analyzes plan and recommends:
  - Roth adjustments
  - Tax bracket strategies
  - IRMAA considerations
  - Social Security filing strategy
  