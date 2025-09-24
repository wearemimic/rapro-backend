# Roth Conversion Module

## Overview

The Roth Conversion Module is a component of the Retirement Advisor Pro platform that allows users to analyze the impact of converting traditional retirement assets (IRA, 401k) to Roth assets. The module calculates the financial implications of Roth conversions, including:

- Tax implications during conversion years
- Long-term tax savings in retirement
- Impact on Required Minimum Distributions (RMDs)
- Medicare premium reductions (IRMAA savings)
- Inheritance tax benefits
- Overall lifetime financial projections

## Architecture

The module consists of the following components:

1. **RothConversionProcessor**: Core class that handles the calculation of Roth conversion scenarios
2. **RothConversionAPIView**: API endpoint that processes client requests and returns conversion analysis
3. **Frontend Integration**: Vue.js components that visualize the conversion analysis

### Key Files

- `roth_conversion_processor.py`: Contains the `RothConversionProcessor` class
- `views.py`: Contains the `RothConversionAPIView` API endpoint
- `urls.py`: URL routing for the API endpoint
- `tests/test_roth_conversion.py`: Unit tests for the Roth conversion processor
- `tests/test_roth_conversion_manual.py`: Manual test script for quick testing

## API Endpoint

### Roth Conversion Analysis

**URL**: `/roth-optimize/`  
**Method**: `POST`  
**Authentication**: JWT required

#### Request Body

```json
{
  "scenario": {
    "retirement_age": 65,
    "mortality_age": 90,
    "part_b_inflation_rate": 3.0,
    "part_d_inflation_rate": 3.0
  },
  "client": {
    "birthdate": "1963-01-01",
    "tax_status": "Single",
    "gender": "M",
    "first_name": "John",
    "last_name": "Doe",
    "state": "CA"
  },
  "spouse": null,
  "assets": [
    {
      "id": "asset1",
      "income_type": "traditional_ira",
      "income_name": "Traditional IRA",
      "owned_by": "primary",
      "current_asset_balance": 500000,
      "monthly_amount": 0,
      "monthly_contribution": 0,
      "age_to_begin_withdrawal": 72,
      "age_to_end_withdrawal": 90,
      "rate_of_return": 5.0,
      "cola": 0,
      "exclusion_ratio": 0,
      "tax_rate": 0,
      "max_to_convert": 200000
    },
    {
      "id": "asset2",
      "income_type": "traditional_401k",
      "income_name": "Traditional 401(k)",
      "owned_by": "primary",
      "current_asset_balance": 300000,
      "monthly_amount": 0,
      "monthly_contribution": 0,
      "age_to_begin_withdrawal": 72,
      "age_to_end_withdrawal": 90,
      "rate_of_return": 5.0,
      "cola": 0,
      "exclusion_ratio": 0,
      "tax_rate": 0,
      "max_to_convert": 100000
    }
  ],
  "optimizer_params": {
    "conversion_start_year": 2024,
    "years_to_convert": 5,
    "pre_retirement_income": 100000,
    "roth_growth_rate": 5.0,
    "max_annual_amount": 60000,
    "roth_withdrawal_amount": 20000,
    "roth_withdrawal_start_year": 2034
  }
}
```

#### Response

```json
{
  "baseline_results": [...],  // Year-by-year results without conversion
  "conversion_results": [...],  // Year-by-year results with conversion
  "metrics": {
    "baseline": {
      "lifetime_tax": 100000,
      "lifetime_medicare": 20000,
      "total_irmaa": 5000,
      "total_rmds": 200000,
      "cumulative_net_income": 800000,
      "final_roth": 0,
      "inheritance_tax": 50000
    },
    "conversion": {
      "lifetime_tax": 120000,
      "lifetime_medicare": 18000,
      "total_irmaa": 4000,
      "total_rmds": 150000,
      "cumulative_net_income": 820000,
      "final_roth": 300000,
      "inheritance_tax": 30000
    },
    "comparison": {
      "lifetime_tax": {
        "baseline": 100000,
        "conversion": 120000,
        "difference": 20000,
        "percent_change": 20.0
      },
      // Other metrics...
      "total_expenses": {
        "baseline": 175000,
        "conversion": 172000,
        "difference": -3000,
        "percent_change": -1.71
      }
    }
  },
  "asset_balances": {
    "years": [2023, 2024, ...],
    "baseline": {
      "asset1": [500000, 525000, ...],
      "asset2": [300000, 315000, ...],
      "roth_ira": [0, 0, ...]
    },
    "conversion": {
      "asset1": [460000, 483000, ...],
      "asset2": [280000, 294000, ...],
      "roth_ira": [60000, 123000, ...]
    }
  },
  "conversion_params": {
    "annual_conversion": 60000,
    "total_conversion": 300000,
    "years_to_convert": 5,
    "conversion_start_year": 2024,
    "roth_withdrawal_start_year": 2034,
    "roth_withdrawal_amount": 20000
  }
}
```

## Implementation Details

### RothConversionProcessor

The `RothConversionProcessor` class extends the functionality of the `ScenarioProcessor` to model Roth conversions. Key features include:

1. **Asset Preparation**: Identifies convertible assets and creates a synthetic Roth asset to track conversions
2. **Scenario Comparison**: Runs both baseline (no conversion) and conversion scenarios
3. **Metrics Calculation**: Calculates key financial metrics for both scenarios
4. **Asset Balance Projections**: Generates year-by-year asset balance projections for visualization

#### Key Methods

- `_prepare_assets_for_conversion()`: Prepares assets for conversion and calculates conversion amounts
- `_prepare_baseline_scenario()`: Creates a scenario without Roth conversions
- `_prepare_conversion_scenario()`: Creates a scenario with Roth conversions
- `_extract_metrics()`: Extracts key financial metrics from scenario results
- `_compare_metrics()`: Compares metrics between baseline and conversion scenarios
- `_extract_asset_balances()`: Extracts asset balance projections for visualization
- `process()`: Main method that orchestrates the entire conversion analysis

### Key Metrics Calculated

1. **Lifetime Tax**: Total federal taxes paid over the projection period
2. **Lifetime Medicare**: Total Medicare premiums paid over the projection period
3. **Total IRMAA**: Total Income-Related Monthly Adjustment Amount (Medicare surcharges)
4. **Total RMDs**: Total Required Minimum Distributions from traditional retirement accounts
5. **Cumulative Net Income**: Total after-tax income over the projection period
6. **Final Roth**: Final balance in Roth accounts at the end of the projection period
7. **Inheritance Tax**: Estimated tax on inherited retirement assets

## Frontend Integration

The Roth Conversion Module integrates with the frontend through the `RothConversionTab.vue` component. This component:

1. Allows users to select assets for conversion
2. Provides controls for conversion parameters (start year, duration, etc.)
3. Displays comparison charts for baseline vs. conversion scenarios
4. Shows detailed financial metrics and projections

## Testing

### Unit Tests

The module includes comprehensive unit tests in `tests/test_roth_conversion.py`. These tests cover:

1. Initialization of the processor
2. Asset preparation for conversion
3. Scenario preparation
4. Metrics extraction and comparison
5. Asset balance projection
6. Full processing flow

### Manual Testing

A manual test script is provided in `tests/test_roth_conversion_manual.py`. This script:

1. Creates sample data for testing
2. Mocks the `ScenarioProcessor` to avoid database dependencies
3. Processes a Roth conversion scenario
4. Displays the results in a readable format
5. Saves the full results to a JSON file for further analysis

To run the manual test:

```bash
cd backend
python -m core.tests.test_roth_conversion_manual
```

## Future Enhancements

Potential future enhancements for the Roth Conversion Module include:

1. **Optimization Algorithm**: Automatically determine the optimal conversion schedule
2. **Tax Bracket Analysis**: Show detailed tax bracket analysis for conversion years
3. **State Tax Integration**: Include state tax implications in the analysis
4. **Monte Carlo Simulations**: Add probabilistic modeling for market returns
5. **Sensitivity Analysis**: Allow users to see how different parameters affect the results
6. **Withdrawal Strategy Integration**: Combine with optimal withdrawal strategy analysis

## Conclusion

The Roth Conversion Module provides a powerful tool for retirement planning, allowing users to make informed decisions about Roth conversions based on comprehensive financial analysis. By comparing baseline and conversion scenarios, users can see the long-term impact of Roth conversions on their retirement finances. 