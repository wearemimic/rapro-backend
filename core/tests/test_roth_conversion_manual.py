"""
Manual test script for the RothConversionProcessor.

This script allows testing the RothConversionProcessor without database dependencies.
Run it directly with: python test_roth_conversion_manual.py
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime, date
import copy

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the processor
from core.roth_conversion_processor import RothConversionProcessor

# Mock the ScenarioProcessor class to avoid database dependencies
class MockScenarioProcessor:
    @classmethod
    def from_dicts(cls, scenario, client, spouse, assets, debug=False):
        instance = cls()
        instance.scenario = scenario
        instance.client = client
        instance.spouse = spouse
        instance.assets = assets
        instance.debug = debug
        return instance
        
    def calculate(self):
        # Return a simplified result set
        current_year = datetime.now().year
        years = range(current_year, current_year + 30)
        results = []
        
        for year in years:
            row = {
                'year': year,
                'federal_tax': 10000 + (year - years[0]) * 500,
                'medicare_base': 2000 + (year - years[0]) * 100,
                'irmaa_surcharge': 500 + (year - years[0]) * 50,
                'net_income': 80000 + (year - years[0]) * 1000,
            }
            
            # Add asset balances
            for asset in self.assets:
                asset_id = asset.get('id') or asset.get('income_type')
                balance = float(asset.get('current_asset_balance', 0))
                
                # Simple growth model
                growth_rate = asset.get('rate_of_return', 5.0) / 100
                years_passed = year - years[0]
                
                # If this is a Roth asset in the conversion scenario
                if asset.get('is_synthetic_roth', False) and hasattr(self.scenario, 'roth_conversion_annual_amount'):
                    # Add conversion amount for the first N years
                    if years_passed < 5:  # Assuming 5 years of conversion
                        balance += float(self.scenario.roth_conversion_annual_amount or 0) * (years_passed + 1)
                
                # Apply growth
                balance *= (1 + growth_rate) ** years_passed
                
                # Add RMD if applicable
                rmd = 0
                if 'traditional' in asset.get('income_type', '').lower() and years_passed >= 12:  # RMD age
                    rmd = balance * 0.04  # Simplified RMD calculation
                    balance -= rmd
                    
                row[f"{asset_id}_balance"] = balance
                row[f"{asset_id}_rmd"] = rmd
            
            results.append(row)
            
        return results

# Mock the ScenarioProcessor import in the roth_conversion_processor module
import sys
import types
from core.scenario_processor import ScenarioProcessor
sys.modules['core.scenario_processor'].ScenarioProcessor = MockScenarioProcessor

def decimal_default(obj):
    """Helper function to serialize Decimal objects to float for JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def main():
    """Run a manual test of the RothConversionProcessor."""
    print("Running manual test of RothConversionProcessor...")
    
    # Create test data
    current_year = datetime.now().year
    
    # Sample scenario
    scenario = {
        'retirement_age': 65,
        'mortality_age': 90,
        'part_b_inflation_rate': 3.0,
        'part_d_inflation_rate': 3.0,
    }
    
    # Sample client
    client = {
        'birthdate': f"{current_year - 60}-01-01",  # 60 years old
        'tax_status': 'Single',
        'gender': 'M',
        'first_name': 'John',
        'last_name': 'Doe',
        'state': 'CA'
    }
    
    # No spouse for simplicity
    spouse = None
    
    # Sample assets
    assets = [
        {
            'id': 'asset1',
            'income_type': 'traditional_ira',
            'income_name': 'Traditional IRA',
            'owned_by': 'primary',
            'current_asset_balance': Decimal('500000'),
            'monthly_amount': Decimal('0'),
            'monthly_contribution': Decimal('0'),
            'age_to_begin_withdrawal': 72,
            'age_to_end_withdrawal': 90,
            'rate_of_return': 5.0,
            'cola': 0,
            'exclusion_ratio': 0,
            'tax_rate': 0,
            'max_to_convert': Decimal('200000')  # Amount to convert
        },
        {
            'id': 'asset2',
            'income_type': 'traditional_401k',
            'income_name': 'Traditional 401(k)',
            'owned_by': 'primary',
            'current_asset_balance': Decimal('300000'),
            'monthly_amount': Decimal('0'),
            'monthly_contribution': Decimal('0'),
            'age_to_begin_withdrawal': 72,
            'age_to_end_withdrawal': 90,
            'rate_of_return': 5.0,
            'cola': 0,
            'exclusion_ratio': 0,
            'tax_rate': 0,
            'max_to_convert': Decimal('100000')  # Amount to convert
        }
    ]
    
    # Sample conversion parameters
    conversion_params = {
        'conversion_start_year': current_year + 1,
        'years_to_convert': 5,
        'pre_retirement_income': Decimal('100000'),
        'roth_growth_rate': 5.0,
        'max_annual_amount': Decimal('60000'),
        'roth_withdrawal_amount': Decimal('20000'),
        'roth_withdrawal_start_year': current_year + 10
    }
    
    # Create and process the Roth conversion
    processor = RothConversionProcessor(
        scenario=scenario,
        client=client,
        spouse=spouse,
        assets=assets,
        conversion_params=conversion_params
    )
    
    # Process the conversion and get results
    result = processor.process()
    
    # Print the results in a readable format
    print("\nRoth Conversion Results:")
    print("========================")
    
    # Print conversion parameters
    print("\nConversion Parameters:")
    print(f"  Start Year: {result['conversion_params']['conversion_start_year']}")
    print(f"  Years to Convert: {result['conversion_params']['years_to_convert']}")
    print(f"  Annual Conversion: ${result['conversion_params']['annual_conversion']:,.2f}")
    print(f"  Total Conversion: ${result['conversion_params']['total_conversion']:,.2f}")
    
    # Print metrics comparison
    print("\nMetrics Comparison:")
    comparison = result['metrics']['comparison']
    
    metrics_to_display = [
        ('lifetime_tax', 'Lifetime Taxes'),
        ('lifetime_medicare', 'Lifetime Medicare'),
        ('total_irmaa', 'Total IRMAA'),
        ('total_rmds', 'Total RMDs'),
        ('inheritance_tax', 'Inheritance Tax'),
        ('total_expenses', 'Total Expenses')
    ]
    
    print(f"{'Metric':<20} {'Baseline':<15} {'Conversion':<15} {'Difference':<15} {'% Change':<10}")
    print("-" * 75)
    
    for key, label in metrics_to_display:
        if key in comparison:
            baseline = comparison[key]['baseline']
            conversion = comparison[key]['conversion']
            difference = comparison[key]['difference']
            pct_change = comparison[key]['percent_change']
            
            print(f"{label:<20} ${baseline:>13,.2f} ${conversion:>13,.2f} ${difference:>13,.2f} {pct_change:>9.2f}%")
    
    # Print asset balances for the first and last year
    print("\nAsset Balances:")
    years = result['asset_balances']['years']
    first_year = years[0]
    last_year = years[-1]
    
    print(f"\nFirst Year ({first_year}):")
    print(f"{'Asset':<20} {'Baseline':<15} {'Conversion':<15} {'Difference':<15}")
    print("-" * 65)
    
    for asset_name in result['asset_balances']['baseline']:
        baseline_value = result['asset_balances']['baseline'][asset_name][0]
        conversion_value = result['asset_balances']['conversion'][asset_name][0]
        difference = conversion_value - baseline_value
        
        print(f"{asset_name:<20} ${baseline_value:>13,.2f} ${conversion_value:>13,.2f} ${difference:>13,.2f}")
    
    print(f"\nLast Year ({last_year}):")
    print(f"{'Asset':<20} {'Baseline':<15} {'Conversion':<15} {'Difference':<15}")
    print("-" * 65)
    
    for asset_name in result['asset_balances']['baseline']:
        baseline_value = result['asset_balances']['baseline'][asset_name][-1]
        conversion_value = result['asset_balances']['conversion'][asset_name][-1]
        difference = conversion_value - baseline_value
        
        print(f"{asset_name:<20} ${baseline_value:>13,.2f} ${conversion_value:>13,.2f} ${difference:>13,.2f}")
    
    # Save the full results to a JSON file for further analysis
    with open('roth_conversion_results.json', 'w') as f:
        json.dump(result, f, default=decimal_default, indent=2)
    
    print("\nFull results saved to 'roth_conversion_results.json'")

if __name__ == '__main__':
    main() 