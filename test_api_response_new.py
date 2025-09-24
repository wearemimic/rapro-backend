#!/usr/bin/env python
"""
Test what the API actually returns for the Roth conversion endpoint
"""
import os
import sys
import django
import json

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.models import Scenario, Client, Investment
from core.roth_conversion_processor import RothConversionProcessor

# Get the actual scenario and client from database
scenario = Scenario.objects.get(id=4)
client = Client.objects.get(id=4)

# Get investments for this scenario
investments = Investment.objects.filter(scenario_id=4)
assets = []
for inv in investments:
    assets.append({
        'id': inv.id,
        'income_type': inv.investment_type,
        'income_name': inv.investment_name,
        'current_asset_balance': float(inv.current_balance or 0),
        'monthly_amount': 0,
        'age_to_begin_withdrawal': inv.withdrawal_age,
        'rate_of_return': float(inv.rate_of_return or 0),
        'cola': 0,
        'max_to_convert': float(inv.current_balance or 0) if inv.investment_type == 'Qualified' else 0
    })

print(f"\n=== TESTING API RESPONSE STRUCTURE ===")
print(f"Scenario ID: {scenario.id}")
print(f"Client ID: {client.id}")
print(f"Assets found: {len(assets)}")

# Create processor with conversion params
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

# Process the conversion
result = processor.process()

# Check the API response structure (mimicking views_main.py)
print(f"\n=== API RESPONSE STRUCTURE ===")
print(f"Result keys: {result.keys()}")

# Check baseline metrics
baseline_metrics = result.get('metrics', {}).get('baseline', {})
print(f"\nBaseline metrics keys: {baseline_metrics.keys()}")
print(f"Baseline total_rmds: ${baseline_metrics.get('total_rmds', 0):,.0f}")
print(f"Baseline lifetime_tax: ${baseline_metrics.get('lifetime_tax', 0):,.0f}")

# Check conversion metrics
conversion_metrics = result.get('metrics', {}).get('conversion', {})
print(f"\nConversion metrics keys: {conversion_metrics.keys()}")
print(f"Conversion total_rmds: ${conversion_metrics.get('total_rmds', 0):,.0f}")
print(f"Conversion lifetime_tax: ${conversion_metrics.get('lifetime_tax', 0):,.0f}")

# Check year-by-year data
baseline_results = result.get('baseline_results', [])
conversion_results = result.get('conversion_results', [])

print(f"\n=== YEAR-BY-YEAR DATA ===")
print(f"Baseline results: {len(baseline_results)} years")
print(f"Conversion results: {len(conversion_results)} years")

# Check a sample year (2050)
print(f"\n=== YEAR 2050 DATA ===")
for row in baseline_results:
    if row.get('year') == 2050:
        print(f"Baseline 2050:")
        print(f"  Qualified_balance: ${row.get('Qualified_balance', 0):,.0f}")
        print(f"  roth_ira_balance: ${row.get('roth_ira_balance', 0):,.0f}")
        print(f"  rmd_amount: ${row.get('rmd_amount', 0):,.0f}")
        break

for row in conversion_results:
    if row.get('year') == 2050:
        print(f"Conversion 2050:")
        print(f"  Qualified_balance: ${row.get('Qualified_balance', 0):,.0f}")
        print(f"  roth_ira_balance: ${row.get('roth_ira_balance', 0):,.0f}")
        print(f"  rmd_amount: ${row.get('rmd_amount', 0):,.0f}")
        print(f"  roth_conversion: ${row.get('roth_conversion', 0):,.0f}")
        break

# Simulate the transformed API response (as in views_main.py)
print(f"\n=== SIMULATED API RESPONSE (as sent to UI) ===")
transformed_result = {
    'baseline': {
        'metrics': result['metrics']['baseline'],
        'year_by_year': result['baseline_results']
    },
    'conversion': {
        'metrics': result['metrics']['conversion'],
        'year_by_year': result['conversion_results']
    },
    'comparison': result['metrics'].get('comparison', {}),
    'optimal_schedule': {
        'start_year': result['conversion_params']['conversion_start_year'],
        'duration': result['conversion_params']['years_to_convert'],
        'annual_amount': result['conversion_params']['annual_conversion'],
        'total_amount': result['conversion_params']['total_conversion'],
        'score_breakdown': result['metrics']['conversion']
    },
    'asset_balances': result.get('asset_balances', {}),
    'scenarioResults': result['conversion_results']
}

print(f"Transformed baseline.metrics.total_rmds: ${transformed_result['baseline']['metrics'].get('total_rmds', 0):,.0f}")
print(f"Transformed optimal_schedule.score_breakdown.total_rmds: ${transformed_result['optimal_schedule']['score_breakdown'].get('total_rmds', 0):,.0f}")