# Roth Conversion System - Architecture Issue Analysis

## The Core Problem

The Roth conversion system has a fundamental architecture issue where conversions that occur BEFORE the retirement start year are not being applied to asset balances.

### Scenario Example
- **Current Year**: 2025
- **Conversion Years**: 2032-2036 (pre-retirement)
- **Retirement Start**: 2040
- **Conversion Amount**: $1,000,000 total ($200k/year for 5 years)

### What's Happening

1. **RothConversionProcessor** creates two scenarios:
   - Baseline: No conversion parameters
   - Conversion: With conversion parameters (2032-2036)

2. **ScenarioProcessor.calculate()** starts from retirement year (2040)
   - It doesn't process years 2032-2036
   - The conversions that should have depleted the account never get applied
   - By 2040, the account still has $1M instead of $0

3. **Result**: RMDs continue to be calculated on the full $1M balance

## Why `pending_roth_conversion` is Always 0

Looking at the logs:
- Every year shows `pending_roth_conversion': Decimal('0')`
- The `_calculate_roth_conversion()` method checks if current year is in conversion window
- But since we start calculating at 2040, and conversions were 2032-2036, we're always AFTER the conversion window
- Therefore, no conversions are ever calculated or applied

## The Architecture Flaw

The ScenarioProcessor has two phases:
1. **Initialization/Projection** (current year to retirement year)
2. **Calculation** (retirement year to mortality)

Conversions happening during phase 1 are not being applied - they're just projected growth without conversion logic.

## Solutions

### Option 1: Apply Past Conversions During Initialization
When initializing assets for the first calculation year, check if conversions should have happened and adjust balances:

```python
def _initialize_asset_with_conversions(self, asset, year):
    # Apply conversions that happened before calculation start
    if self.scenario.roth_conversion_start_year:
        conversion_end = self.scenario.roth_conversion_start_year + self.scenario.roth_conversion_duration
        if year > conversion_end:
            # All conversions complete, adjust balance
            total_converted = self.scenario.roth_conversion_annual_amount * self.scenario.roth_conversion_duration
            asset["current_asset_balance"] -= total_converted
```

### Option 2: Start Calculation from Conversion Year
Change the ScenarioProcessor to start calculating from the earlier of:
- Retirement start year
- Roth conversion start year

This would ensure conversions are processed in real-time.

### Option 3: Pre-process Conversions
Before the main calculation loop, apply all past conversions to adjust initial balances.

## Current Workaround in RothConversionProcessor

The RothConversionProcessor tries to handle this by:
1. Adding synthetic pre-retirement years
2. Manually calculating conversion amounts for those years
3. Adjusting balances in the synthetic results

But this doesn't actually affect the ScenarioProcessor's internal calculations.

## Impact on Results

- **Baseline RMDs**: Calculated correctly on full balance
- **Conversion RMDs**: Should be $0 after full conversion, but showing ~$180k
- **Difference**: The ~$70k reduction is likely from withdrawals, not conversions

## Recommended Fix

The cleanest solution is to modify the ScenarioProcessor to:

1. Check for past conversions when initializing assets
2. Apply those conversions to the initial balances
3. Create/update Roth accounts with the converted amounts
4. Mark accounts as fully converted if applicable

This ensures that when the calculation starts at retirement year, the balances already reflect any pre-retirement conversions.