# Roth Calculator Analysis and Implementation Guide

## Overview
The Roth Calculator is a sophisticated financial planning tool that helps advisors optimize Roth IRA conversions for their clients. It analyzes the trade-offs between paying taxes now on conversions versus future tax savings, RMD reductions, and IRMAA (Medicare premium surcharge) avoidance.

## Current Architecture

### Frontend Components
- **RothConversionTab.vue**: Main UI component for Roth conversion analysis
- **AssetSelectionPanel.vue**: Component for selecting eligible assets for conversion
- **ScenarioCreate.vue**: Where retirement income and investment accounts are defined
- **InvestmentModal.vue**: Modal for adding investment accounts with specific types

### Backend Components
- **RothConversionProcessor.py**: Main processor for Roth conversion calculations
- **ScenarioProcessor.py**: Core retirement scenario calculator with IRMAA and RMD logic
- **RothConversionAPIView**: API endpoint at `/api/roth-optimize/`

## Asset Type System

### Income Sources (Non-convertible)
- `social_security` - Social Security benefits
- `Pension` - Pension income
- `Wages` - Employment income
- `Rental_Income` - Rental property income
- `Other` - Other income sources

### Investment Account Types
#### Eligible for Roth Conversion:
- **`Qualified`** - Traditional tax-deferred accounts (401k, Traditional IRA, etc.)
- **`Inherited Traditional Spouse`** - Inherited traditional accounts from spouse
- **`Inherited Traditional Non-Spouse`** - Inherited traditional accounts from non-spouse

#### NOT Eligible for Roth Conversion:
- **`Non-Qualified`** - Taxable brokerage accounts (already taxed)
- **`Roth`** - Roth IRA/401k accounts (already tax-free)
- **`Inherited Roth Spouse`** - Inherited Roth from spouse (already tax-free)
- **`Inherited Roth Non-Spouse`** - Inherited Roth from non-spouse (already tax-free)

## How the Roth Calculator Works

### 1. Asset Selection Phase
- User selects which qualified accounts to convert
- Specifies conversion amounts (up to account balance)
- Sets conversion timeline (start year and duration)
- Configures Roth withdrawal parameters

### 2. Calculation Process

#### Baseline Scenario (No Conversion)
1. Calculate yearly income from all sources
2. Apply Social Security taxation rules
3. Calculate federal taxes with standard deduction
4. Calculate RMDs for qualified accounts starting at age 73
5. Calculate MAGI (Modified Adjusted Gross Income)
6. Apply IRMAA surcharges based on MAGI thresholds
7. Track asset balances through retirement

#### Conversion Scenario
1. Add Roth conversion amounts to taxable income during conversion years
2. Reduce qualified account balances by conversion amounts
3. Create synthetic Roth account with converted funds
4. Apply growth to Roth account (tax-free)
5. Recalculate taxes with higher income during conversion years
6. Recalculate IRMAA with higher MAGI during conversions
7. Calculate reduced RMDs from smaller qualified balances
8. Apply Roth withdrawals (tax-free) starting at specified year

### 3. IRMAA Calculation

#### MAGI Thresholds (2025)
**Single Filers:**
- ≤ $106,000: No surcharge
- $106,001 - $133,000: +$71.90/month
- $133,001 - $167,000: +$179.80/month
- $167,001 - $200,000: +$287.80/month
- $200,001 - $500,000: +$396.00/month
- > $500,000: +$431.00/month

**Married Filing Jointly:**
- ≤ $212,000: No surcharge
- $212,001 - $266,000: +$71.90/month
- $266,001 - $334,000: +$179.80/month
- $334,001 - $400,000: +$287.80/month
- $400,001 - $750,000: +$396.00/month
- > $750,000: +$431.00/month

**Part D IRMAA** adds additional surcharges at same thresholds

### 4. RMD Calculation
- Required for `Qualified` and `Inherited Traditional` accounts
- Starts at age 73 (or 75 for those born 1960+)
- Uses IRS Uniform Lifetime Table
- Inherited Non-Spouse accounts follow 10-year rule
- RMDs increase taxable income and MAGI

### 5. Comparison Metrics
The calculator compares baseline vs. conversion scenarios:
- **Lifetime RMDs**: Total required distributions
- **Federal Taxes**: Total taxes paid over retirement
- **Medicare Costs**: Base premiums + IRMAA surcharges
- **Inheritance Tax**: Tax on remaining traditional balances
- **Net Spendable Income**: After-tax retirement income
- **Final Roth Balance**: Tax-free legacy for heirs

## Current Implementation Issues

### 1. Asset Type Filtering Bug
**Location**: RothConversionTab.vue lines 588-591
**Issue**: Still checking for old asset types (`traditional_401k`, `traditional_ira`, etc.)
**Fix Required**: Update to check for `Qualified`, `Inherited Traditional Spouse`, `Inherited Traditional Non-Spouse`

```javascript
// CURRENT (WRONG)
eligibleAssets() {
  return assets.filter(asset => {
    const type = asset.income_type.trim().toLowerCase();
    return ['traditional_401k', 'traditional_ira', 'ira', 'roth_401k', 'roth_ira'].includes(type);
  });
}

// SHOULD BE
eligibleAssets() {
  return assets.filter(asset => {
    const type = asset.income_type;
    return ['Qualified', 'Inherited Traditional Spouse', 'Inherited Traditional Non-Spouse'].includes(type);
  });
}
```

### 2. Data Flow
1. **Frontend** → Sends asset list with `max_to_convert` amounts
2. **RothConversionProcessor** → Calculates conversion schedule
3. **ScenarioProcessor** → Runs baseline and conversion scenarios
4. **API Response** → Returns comparison metrics and year-by-year data
5. **Frontend** → Displays charts and tables

## Key Features to Enhance

### 1. IRMAA Bracket Visualization
- Show current MAGI position relative to thresholds
- Highlight bracket changes from conversions
- Project future IRMAA costs

### 2. Optimal Conversion Amount Finder
- Calculate conversion amount that stays within IRMAA bracket
- Maximize conversions without triggering next surcharge level
- Consider multi-year optimization

### 3. Tax Bracket Management
- Show marginal tax rate for each conversion year
- Optimize to fill lower tax brackets
- Avoid pushing into higher brackets unnecessarily

### 4. RMD Impact Display
- Show RMD reduction over lifetime
- Calculate tax savings from lower RMDs
- Display breakeven analysis

## API Request Structure

```javascript
{
  scenario: {
    retirement_age: 65,
    mortality_age: 90,
    roth_conversion_start_year: 2025,
    roth_conversion_duration: 5,
    // ... other scenario fields
  },
  client: {
    birthdate: "1960-01-01",
    tax_status: "Married Filing Jointly",
    // ... other client fields
  },
  spouse: {
    birthdate: "1962-01-01",
    // ... spouse fields if applicable
  },
  assets: [
    {
      income_type: "Qualified",
      current_asset_balance: 500000,
      max_to_convert: 100000,
      // ... other asset fields
    }
  ],
  optimizer_params: {
    mode: "manual",
    conversion_start_year: 2025,
    years_to_convert: 5,
    annual_conversion_amount: 20000,
    roth_growth_rate: 5.0,
    max_annual_amount: 50000,
    roth_withdrawal_amount: 2000,
    roth_withdrawal_start_year: 2035
  }
}
```

## Critical Calculation Points

### 1. Provisional Income for Social Security Taxation
```
Provisional Income = AGI (excluding SS) + Tax-exempt interest + 50% of SS benefits
```

### 2. MAGI for IRMAA
```
MAGI = AGI + Tax-exempt interest + Foreign income exclusions
Note: Roth conversions increase MAGI
```

### 3. RMD Calculation
```
RMD = Previous Year Balance / Life Expectancy Factor
```

### 4. Effective Tax Rate on Conversion
```
Marginal Rate + State Tax + Potential IRMAA Surcharge = Total Cost
```

## Testing Considerations

1. **Edge Cases**:
   - Conversions that push into next IRMAA bracket
   - RMDs that exceed planned withdrawals
   - Inherited account special rules
   - Spouse mortality scenarios

2. **Validation**:
   - Cannot convert more than account balance
   - Cannot convert Roth or Non-Qualified accounts
   - Conversion must occur before mortality age
   - Withdrawals cannot exceed Roth balance

## Future Enhancements

1. **Multi-year Optimization**
   - Automatically find optimal conversion schedule
   - Consider varying conversion amounts by year
   - Account for tax law changes

2. **State Tax Integration**
   - Include state tax calculations
   - Consider state-specific retirement tax benefits
   - Account for potential relocation

3. **Estate Planning Features**
   - Calculate heir tax implications
   - Optimize for wealth transfer
   - Consider charitable giving strategies

4. **Risk Analysis**
   - Monte Carlo simulation for market returns
   - Sensitivity analysis for key assumptions
   - Longevity risk assessment

## Implementation Fixes Applied

### 1. Frontend Asset Type Filtering (COMPLETED ✅)
**File**: `/frontend/src/views/RothConversionTab.vue`
**Lines**: 583-597, 1007-1012

**Problem**: Frontend was filtering for old asset types (`traditional_401k`, `traditional_ira`, etc.)
**Fix**: Updated to use correct asset types:
```javascript
// OLD (WRONG)
['traditional_401k', 'traditional_ira', 'ira', 'roth_401k', 'roth_ira']

// NEW (CORRECT)  
['Qualified', 'Inherited Traditional Spouse', 'Inherited Traditional Non-Spouse']
```

### 2. Missing Backend Conversion Parameter (COMPLETED ✅)
**File**: `/frontend/src/views/RothConversionTab.vue`
**Line**: 1033

**Problem**: Backend expected `roth_conversion_annual_amount` but frontend wasn't sending it
**Fix**: Added missing field to scenario data:
```javascript
scenarioData = {
  ...this.scenario,
  roth_conversion_annual_amount: annualConversion,  // Added this line
  // ... other fields
}
```

### 3. Backend Field Name Inconsistency (COMPLETED ✅)
**File**: `/backend/core/roth_conversion_processor.py` 
**Lines**: 687, 591

**Problem**: Pre-retirement conversion rows used `conversion_amount` field, frontend expects `roth_conversion`
**Fix**: Changed field name in both baseline and conversion pre-retirement rows:
```python
# OLD (WRONG)
'conversion_amount': float(self.annual_conversion)

# NEW (CORRECT)
'roth_conversion': float(self.annual_conversion)
```

### 4. Enhanced Pre-retirement Row Data (COMPLETED ✅)
**File**: `/backend/core/roth_conversion_processor.py`
**Lines**: 676-692, 576-592

**Problem**: Pre-retirement rows missing standard fields expected by frontend
**Fix**: Added complete field structure:
```python
pre_retirement_row = {
    'year': year,
    'primary_age': primary_age,
    'spouse_age': spouse_age,
    'gross_income': float(self.pre_retirement_income),
    'ss_income': 0,
    'taxable_ss': 0,
    'magi': float(self.pre_retirement_income) + float(self.annual_conversion),
    'taxable_income': float(self.pre_retirement_income) + float(self.annual_conversion),
    'federal_tax': 0,
    'medicare_base': 0,
    'irmaa_surcharge': 0,
    'total_medicare': 0,
    'net_income': float(self.pre_retirement_income),
    'roth_conversion': float(self.annual_conversion) if conversion_year else 0,
}
```

## Current Status: DEBUGGING REQUIRED ⚠️

### Remaining Issue
Despite the fixes above, conversion amounts still show as `$0.00` in the table and console logs show:
- Years 2030-2039: All fields `undefined` (should have pre-retirement data)
- Years 2040+: `Roth Conversion Amount: 0` (should show conversion amounts during 2032-2036)

### Possible Causes
1. **Backend restart failed** - Changes to Python files not loaded
2. **RothConversionProcessor not being called** - API falling back to baseline scenario
3. **Response structure mismatch** - Frontend reading wrong part of API response
4. **Silent backend errors** - RothConversionProcessor failing without error logs

### Debug Steps
1. Check API response structure in browser console
2. Verify backend restart with explicit Docker commands
3. Add backend logging to confirm RothConversionProcessor execution
4. Check if frontend is using baseline vs conversion results

### Expected Behavior
When working correctly:
- Years 2032-2036: `Roth Conversion Amount: 100000`
- Pre-retirement years: Should have income data from `pre_retirement_income`
- Conversion years: Should show increased taxable income and MAGI

## Summary

The Roth Calculator is a powerful tool that helps advisors make data-driven decisions about Roth conversions. By properly accounting for taxes, IRMAA surcharges, RMDs, and long-term growth, it provides comprehensive analysis of conversion strategies. 

**Status**: Frontend asset filtering and backend parameter passing have been fixed, but conversion amounts are still not displaying. Further debugging of the backend processing and data flow is required.