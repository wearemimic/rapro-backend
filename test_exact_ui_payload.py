#!/usr/bin/env python
"""
Test with EXACT payload the UI sends for client 4, scenario 4
"""

import os
import sys
import django
import json
from decimal import Decimal

sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.models import Scenario, Client, Income
from core.roth_conversion_processor import RothConversionProcessor

# Get the actual scenario and client from database
scenario = Scenario.objects.get(id=4)
client = Client.objects.get(id=4)

# Get the actual assets
assets = []
for income in Income.objects.filter(scenario_id=4):
    asset_dict = {
        'id': income.id,
        'income_type': income.income_type,
        'income_name': income.income_name,
        'current_asset_balance': float(income.current_asset_balance or 0),
        'monthly_amount': float(income.monthly_amount or 0),
        'age_to_begin_withdrawal': income.age_to_begin_withdrawal,
        'rate_of_return': float(income.rate_of_return or 0),
        'cola': float(income.cola or 0),
    }
    
    # Add max_to_convert for qualified assets
    if income.income_type == 'Qualified':
        asset_dict['max_to_convert'] = float(income.current_asset_balance or 0)
    
    assets.append(asset_dict)

print(f"\n=== ACTUAL DATA FROM DATABASE ===")
print(f"Scenario ID: {scenario.id}")
print(f"Client ID: {client.id}")
print(f"Assets found: {len(assets)}")
for asset in assets:
    print(f"  - {asset['income_name']}: {asset['income_type']}, Balance: ${asset.get('current_asset_balance', 0):,.0f}")

# Create the processor with actual data
processor = RothConversionProcessor(
    scenario={
        'id': scenario.id,
        'scenario_name': scenario.scenario_name,
        'current_year': scenario.current_year,
        'start_year': scenario.start_year,
        'retirement_age': scenario.retirement_age,
        'mortality_age': scenario.mortality_age,
        'inflation_rate': float(scenario.inflation_rate or 0.03),
        'target_net_income': float(scenario.target_net_income or 0),
        'apply_standard_deduction': scenario.apply_standard_deduction,
    },
    client={
        'id': client.id,
        'birthdate': str(client.birthdate),
        'state': client.state,
        'tax_status': client.tax_status,
        'gender': client.gender,
        'first_name': client.first_name,
        'last_name': client.last_name,
    },
    spouse=None,
    assets=assets,
    conversion_params={
        'conversion_start_year': 2032,
        'years_to_convert': 5,
        'pre_retirement_income': 100000,
        'roth_growth_rate': 5,
        'roth_withdrawal_start_year': 2042,
        'roth_withdrawal_amount': 50000,
    }
)

print(f"\n=== PROCESSING ROTH CONVERSION ===")
result = processor.process()

# Check the results
baseline_results = result.get('baseline_results', [])
conversion_results = result.get('conversion_results', [])
metrics = result.get('metrics', {})

print(f"\n=== RESULTS SUMMARY ===")

# Check specific years
years_to_check = [2032, 2036, 2040, 2050]
for year in years_to_check:
    print(f"\n--- Year {year} ---")
    
    # Baseline
    for row in baseline_results:
        if row.get('year') == year:
            print(f"Baseline:")
            print(f"  Qualified: ${row.get('Qualified_balance', 0):,.0f}")
            print(f"  Roth: ${row.get('roth_ira_balance', 0):,.0f}")
            print(f"  RMD: ${row.get('rmd_amount', 0):,.0f}")
            break
    
    # Conversion
    for row in conversion_results:
        if row.get('year') == year:
            print(f"Conversion:")
            print(f"  Qualified: ${row.get('Qualified_balance', 0):,.0f}")
            print(f"  Roth: ${row.get('roth_ira_balance', 0):,.0f}")
            print(f"  RMD: ${row.get('rmd_amount', 0):,.0f}")
            print(f"  Conversion Amount: ${row.get('roth_conversion', 0):,.0f}")
            break

print(f"\n=== METRICS (FOR BAR CHART) ===")
print(f"Baseline Total RMDs: ${metrics.get('baseline', {}).get('total_rmds', 0):,.0f}")
print(f"Conversion Total RMDs: ${metrics.get('conversion', {}).get('total_rmds', 0):,.0f}")
print(f"RMD Reduction: ${metrics.get('baseline', {}).get('total_rmds', 0) - metrics.get('conversion', {}).get('total_rmds', 0):,.0f}")

print(f"\nBaseline Total Taxes: ${metrics.get('baseline', {}).get('lifetime_tax', 0):,.0f}")
print(f"Conversion Total Taxes: ${metrics.get('conversion', {}).get('lifetime_tax', 0):,.0f}")

print(f"\nBaseline Total Medicare: ${metrics.get('baseline', {}).get('lifetime_medicare', 0):,.0f}")
print(f"Conversion Total Medicare: ${metrics.get('conversion', {}).get('lifetime_medicare', 0):,.0f}")

# Check if there are any qualified assets with balances
print(f"\n=== ASSET BALANCE CHECK ===")
has_qualified = False
for row in baseline_results[:5]:
    if row.get('Qualified_balance', 0) > 0:
        has_qualified = True
        print(f"Year {row['year']}: Found Qualified balance of ${row['Qualified_balance']:,.0f}")
        break

if not has_qualified:
    print("⚠️ WARNING: No Qualified balances found in results!")
    print("This means the asset data might not be loading correctly.")