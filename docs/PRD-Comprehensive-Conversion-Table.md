# PRD: Comprehensive Conversion Table Implementation

## Objective
Create a comprehensive financial table for "After Conversion" data that matches the "Before Conversion" table structure with added conversion-specific columns.

## Background
Currently, the "Before Conversion" tab uses `ComprehensiveFinancialTable.vue` to display all financial data (income sources, asset balances, RMDs, taxes, Medicare/IRMAA, etc.). The "After Conversion" tab needs the same comprehensive view, but with additional conversion-specific columns:
- Roth Conversion Amount
- Conversion Tax (incremental tax due to conversion)
- Regular Income Tax (for comparison)

**Important**: We do NOT modify `ComprehensiveFinancialTable.vue` because it's used elsewhere (Income tab).

## Technical Approach

### Data Flow
1. Backend `RothConversionProcessor` already calculates all necessary data correctly:
   - MAGI includes conversion amount
   - Medicare/IRMAA calculated with conversion-inclusive MAGI
   - Tax breakdown: regular income tax vs total tax (with conversion)
   - Conversion tax = total tax - regular income tax

2. Current conversion results lack comprehensive structure:
   - Missing: `income_by_source`, structured `asset_balances`, detailed tax breakdowns
   - Has: year-by-year data but in simplified format

3. Solution: Transform conversion results into comprehensive format matching baseline

## Tasks

### Backend Work

#### Phase 1: Data Structure Transformation
- [ ] **Create helper function** `transform_conversion_to_comprehensive()`
  - Location: `core/roth_conversion_processor.py`
  - Input: `conversion_results` dictionary
  - Output: Comprehensive format matching `/api/scenarios/{id}/comprehensive-summary/`

- [ ] **Add income_by_source structure**
  - Extract Social Security, pension, RMDs, other income
  - Format as: `{"Social Security": [...], "Pension": [...], "RMDs": [...]}`

- [ ] **Add structured asset_balances**
  - Traditional IRA, Roth IRA, Taxable, HSA end-of-year balances
  - Format as: `{"Traditional IRA": [...], "Roth IRA": [...], ...}`

- [ ] **Add tax breakdown fields**
  - `regular_income_tax`: Tax without conversion
  - `conversion_tax`: Incremental tax due to conversion
  - `total_federal_tax`: Total tax (already exists)
  - `marginal_rate`: Tax bracket string (already calculated)
  - `effective_rate`: total_federal_tax / gross_income

- [ ] **Add Medicare/IRMAA detailed fields**
  - `part_b`: Part B cost
  - `part_d`: Part D cost
  - `irmaa_surcharge`: IRMAA surcharge amount
  - `irmaa_bracket_number`: Which IRMAA bracket (0-5)
  - `irmaa_threshold`: Threshold for current bracket

- [ ] **Add conversion-specific fields**
  - `roth_conversion_amount`: Conversion amount per year
  - Ensure all conversions are included in yearly data

#### Phase 2: API Endpoint (Optional)
- [ ] **Option A**: Transform data in existing endpoint
  - Modify response from `calculate-conversion` to include comprehensive format

- [ ] **Option B**: Create new endpoint
  - `POST /api/scenarios/{id}/comprehensive-conversion/`
  - Accepts conversion parameters
  - Returns comprehensive format

- [ ] **Decision**: Use Option A (simpler, fewer API calls)

#### Phase 3: Testing
- [ ] **Test comprehensive data structure**
  - Verify all fields match baseline format
  - Verify conversion-specific fields are correct
  - Test with single and married filing statuses
  - Test with various conversion amounts

### Frontend Work

#### Phase 1: Component Creation
- [ ] **Create `ComprehensiveConversionTable.vue`**
  - Location: `rapro-frontend/src/components/`
  - Copy `ComprehensiveFinancialTable.vue` as starting point
  - Modify to accept conversion data as prop instead of API fetch

- [ ] **Component props**
  ```javascript
  props: {
    comprehensiveData: {
      type: Object,
      required: true
    }
  }
  ```

- [ ] **Remove API fetch logic**
  - Delete `fetchComprehensiveData()` method
  - Use prop data directly

#### Phase 2: Add Conversion-Specific Columns

- [ ] **Add "Roth Conversion" column in Income Sources section**
  - Display: `row.roth_conversion_amount`
  - Format as currency
  - Position: After "Other Income" column

- [ ] **Add tax breakdown in Taxes section**
  - Column 1: "Regular Income Tax" (`regular_income_tax`)
  - Column 2: "Conversion Tax" (`conversion_tax`)
  - Column 3: "Total Federal Tax" (`total_federal_tax`)
  - Show comparison between regular and conversion tax

- [ ] **Update column headers**
  - Ensure all headers are clear and descriptive
  - Add tooltips if needed for conversion-specific columns

#### Phase 3: Integration

- [ ] **Update `RothConversionTab.vue`**
  - Import `ComprehensiveConversionTable`
  - Pass comprehensive conversion data as prop
  - Replace current "After Conversion" table

- [ ] **Data flow in RothConversionTab**
  ```javascript
  // When conversion calculation completes
  const response = await axios.post('/api/scenarios/.../calculate-conversion/');
  this.conversionComprehensiveData = response.data.comprehensive;

  // In template
  <ComprehensiveConversionTable
    :comprehensive-data="conversionComprehensiveData"
  />
  ```

#### Phase 4: Styling & UX

- [ ] **Highlight conversion-specific columns**
  - Use distinct color or styling for conversion columns
  - Make it clear which data is conversion-specific

- [ ] **Responsive design**
  - Ensure table works on mobile/tablet
  - Test horizontal scrolling if needed

- [ ] **Loading states**
  - Show loading indicator while calculating
  - Handle empty/error states gracefully

### Testing

#### Backend Tests
- [ ] **Test data transformation**
  - Unit test for `transform_conversion_to_comprehensive()`
  - Test all edge cases (zero income, high IRMAA, etc.)

- [ ] **Test API endpoint**
  - Integration test for conversion calculation
  - Verify comprehensive format is returned

#### Frontend Tests
- [ ] **Component tests**
  - Test ComprehensiveConversionTable renders correctly
  - Test with various data inputs
  - Test empty states

- [ ] **Integration tests**
  - Test full flow: calculate → display
  - Test comparison between Before/After tables

#### Manual Testing
- [ ] **Visual comparison**
  - Before and After tables should have same structure
  - Conversion columns should be clearly identifiable

- [ ] **Data accuracy**
  - Verify IRMAA calculations are correct
  - Verify tax calculations include conversion
  - Verify conversion tax = total tax - regular tax

### Documentation

- [ ] **API Documentation**
  - Document comprehensive data structure
  - Document conversion-specific fields
  - Provide example response

- [ ] **Component Documentation**
  - Document ComprehensiveConversionTable props
  - Provide usage examples
  - Document differences from ComprehensiveFinancialTable

- [ ] **Update CLAUDE.md**
  - Add notes about conversion table structure
  - Document data flow for future developers

## Success Criteria

1. ✅ "After Conversion" table shows ALL data that "Before Conversion" shows
2. ✅ Conversion-specific columns (Conversion Amount, Conversion Tax) are visible
3. ✅ IRMAA calculations reflect conversion impact on MAGI
4. ✅ Tax calculations show breakdown: regular vs conversion tax
5. ✅ Table structure is consistent with ComprehensiveFinancialTable
6. ✅ Code is maintainable and follows project standards
7. ✅ Architecture supports future Monte Carlo implementation (already verified)

## Out of Scope

- ❌ Monte Carlo simulation (future work)
- ❌ Modifications to ComprehensiveFinancialTable.vue (used elsewhere)
- ❌ Changes to core RothConversionProcessor calculations (already correct)

## Timeline Estimate

- Backend work: 2-3 hours
- Frontend work: 3-4 hours
- Testing: 1-2 hours
- Total: 6-9 hours

## Notes

- RothConversionProcessor already calculates everything correctly
- MAGI includes conversion amount (line 1137, 1170-1171 in roth_conversion_processor.py)
- Medicare/IRMAA uses conversion-inclusive MAGI (lines 1170-1171)
- Tax breakdown already calculated (lines 1147-1166)
- No architectural changes needed - only data transformation and display

## Future Work (Not Part of This PRD)

- Monte Carlo simulation for Roth conversions
- Additional optimization algorithms
- Multi-year conversion strategies
- Tax loss harvesting integration
