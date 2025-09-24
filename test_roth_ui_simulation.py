#!/usr/bin/env python
"""
Test script that simulates EXACTLY what the UI is doing when calling the Roth conversion API.
This will help us debug why the UI still shows wrong results.
"""

import os
import sys
import django
import json
import requests
from decimal import Decimal
from datetime import date

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.roth_conversion_processor import RothConversionProcessor
from core.scenario_processor import ScenarioProcessor


def simulate_ui_api_call():
    """
    Simulate exactly what the UI sends to the API endpoint.
    Based on the user's scenario: client 4, scenario 4
    """
    
    # This is what the UI would send (based on actual scenario)
    api_payload = {
        'scenario': {
            'id': 4,
            'scenario_name': 'Test Scenario',
            'current_year': 2025,
            'start_year': 2040,  # Retirement year
            'retirement_age': 65,
            'mortality_age': 90,
            'inflation_rate': 0.03,
            'target_net_income': 60000,
            'apply_standard_deduction': True,
        },
        'client': {
            'id': 4,
            'birthdate': '1975-01-01',  # Age 50 in 2025
            'state': 'CA',
            'tax_status': 'Single',
            'gender': 'M',
            'first_name': 'Test',
            'last_name': 'Client',
        },
        'spouse': None,
        'assets': [
            {
                'id': 8,
                'income_type': 'Qualified',
                'income_name': '401k',
                'current_asset_balance': 1000000,
                'monthly_amount': 2500,
                'age_to_begin_withdrawal': 65,
                'rate_of_return': 0,
                'max_to_convert': 1000000,
            },
            {
                'id': 7,
                'income_type': 'social_security',
                'income_name': 'Social Security',
                'monthly_amount': 4500,
                'age_to_begin_withdrawal': 65,
                'cola': 2,
            }
        ],
        'optimizer_params': {
            'conversion_start_year': 2032,
            'years_to_convert': 5,
            'pre_retirement_income': 100000,
            'roth_growth_rate': 5,
            'roth_withdrawal_start_year': 2042,
            'roth_withdrawal_amount': 50000,
        }
    }
    
    return api_payload


def test_roth_conversion_processor_directly():
    """Test the RothConversionProcessor as the API does"""
    print("\n" + "="*80)
    print("TESTING ROTH CONVERSION PROCESSOR (UI SIMULATION)")
    print("="*80)
    
    payload = simulate_ui_api_call()
    
    # Create processor exactly as the API does
    processor = RothConversionProcessor(
        scenario=payload['scenario'],
        client=payload['client'],
        spouse=payload['spouse'],
        assets=payload['assets'],
        conversion_params=payload['optimizer_params']
    )
    
    # Process the conversion
    print("\nProcessing conversion...")
    result = processor.process()
    
    # Check key metrics
    print("\n" + "-"*40)
    print("RESULTS:")
    print("-"*40)
    
    baseline_rmds = result['metrics']['baseline'].get('total_rmds', 0)
    conversion_rmds = result['metrics']['conversion'].get('total_rmds', 0)
    
    print(f"Baseline Total RMDs: ${baseline_rmds:,.0f}")
    print(f"Conversion Total RMDs: ${conversion_rmds:,.0f}")
    print(f"RMD Reduction: ${baseline_rmds - conversion_rmds:,.0f}")
    
    # Check specific years in the results
    baseline_results = result['baseline_results']
    conversion_results = result['conversion_results']
    
    # Find year 2050 (age 75, RMD age)
    for i, year_data in enumerate(baseline_results):
        if year_data.get('year') == 2050:
            baseline_2050 = year_data
            conversion_2050 = conversion_results[i] if i < len(conversion_results) else None
            
            print(f"\nYear 2050 (Age 75) Comparison:")
            print(f"  Baseline:")
            print(f"    Qualified Balance: ${baseline_2050.get('Qualified_balance', 0):,.0f}")
            print(f"    RMD: ${baseline_2050.get('rmd_amount', 0):,.0f}")
            
            if conversion_2050:
                print(f"  After Conversion:")
                print(f"    Qualified Balance: ${conversion_2050.get('Qualified_balance', 0):,.0f}")
                print(f"    Roth Balance: ${conversion_2050.get('roth_ira_balance', 0):,.0f}")
                print(f"    RMD: ${conversion_2050.get('rmd_amount', 0):,.0f}")
            break
    
    # Check if conversions were applied
    print("\n" + "-"*40)
    print("CONVERSION APPLICATION CHECK:")
    print("-"*40)
    
    # Look for conversion amounts in the results
    conversions_found = False
    for year_data in conversion_results[:10]:  # Check first 10 years
        if year_data.get('roth_conversion', 0) > 0:
            conversions_found = True
            print(f"Year {year_data['year']}: Conversion = ${year_data['roth_conversion']:,.0f}")
    
    if not conversions_found:
        print("⚠️  WARNING: No conversions found in results!")
    
    return result


def check_scenario_processor_directly():
    """Test ScenarioProcessor directly with conversion parameters"""
    print("\n" + "="*80)
    print("TESTING SCENARIO PROCESSOR DIRECTLY")
    print("="*80)
    
    payload = simulate_ui_api_call()
    
    # Add conversion parameters to scenario
    scenario_with_conversion = payload['scenario'].copy()
    scenario_with_conversion['roth_conversion_start_year'] = 2032
    scenario_with_conversion['roth_conversion_duration'] = 5
    scenario_with_conversion['roth_conversion_annual_amount'] = 200000  # $1M / 5 years
    
    print(f"\nScenario with conversion params:")
    print(f"  Start Year: {scenario_with_conversion['roth_conversion_start_year']}")
    print(f"  Duration: {scenario_with_conversion['roth_conversion_duration']}")
    print(f"  Annual Amount: ${scenario_with_conversion['roth_conversion_annual_amount']:,}")
    
    # Create processor
    processor = ScenarioProcessor.from_dicts(
        scenario=scenario_with_conversion,
        client=payload['client'],
        spouse=payload['spouse'],
        assets=payload['assets'],
        debug=True
    )
    
    # Run calculation
    results = processor.calculate()
    
    # Check for conversions
    print("\n" + "-"*40)
    print("CHECKING FOR CONVERSIONS:")
    print("-"*40)
    
    for year_data in results[:5]:  # Check first 5 years
        year = year_data.get('year')
        conversion = year_data.get('roth_conversion', 0)
        qualified_balance = year_data.get('Qualified_balance', 0)
        roth_balance = year_data.get('roth_ira_balance', 0)
        
        print(f"Year {year}: Conversion=${conversion:,.0f}, Qualified=${qualified_balance:,.0f}, Roth=${roth_balance:,.0f}")
    
    # Check year 2050 (RMD age)
    for year_data in results:
        if year_data.get('year') == 2050:
            print(f"\nYear 2050 (RMD Age):")
            print(f"  Qualified Balance: ${year_data.get('Qualified_balance', 0):,.0f}")
            print(f"  Roth Balance: ${year_data.get('roth_ira_balance', 0):,.0f}")
            print(f"  RMD: ${year_data.get('rmd_amount', 0):,.0f}")
            break
    
    return results


def check_debug_logs():
    """Check what's happening in the debug logs"""
    print("\n" + "="*80)
    print("CHECKING DEBUG OUTPUT")
    print("="*80)
    
    # Run a simple test with debug enabled
    scenario = {
        'id': 1,
        'retirement_age': 65,
        'mortality_age': 90,
        'start_year': 2040,
        'roth_conversion_start_year': 2032,
        'roth_conversion_duration': 5,
        'roth_conversion_annual_amount': 200000,
    }
    
    client = {
        'birthdate': date(1975, 1, 1),
        'state': 'CA',
        'tax_status': 'Single',
    }
    
    assets = [{
        'income_type': 'Qualified',
        'current_asset_balance': 1000000,
        'rate_of_return': 0,
        'age_to_begin_withdrawal': 65,
    }]
    
    processor = ScenarioProcessor.from_dicts(
        scenario=scenario,
        client=client,
        spouse=None,
        assets=assets,
        debug=True
    )
    
    # Just check the first year to see what's happening
    results = processor.calculate()
    
    return results[0] if results else None


def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("# UI SIMULATION TEST - ROTH CONVERSION")
    print("#"*80)
    
    # Test 1: RothConversionProcessor (as UI uses it)
    roth_result = test_roth_conversion_processor_directly()
    
    # Test 2: ScenarioProcessor directly
    scenario_results = check_scenario_processor_directly()
    
    # Test 3: Debug output
    debug_result = check_debug_logs()
    
    # Summary
    print("\n" + "#"*80)
    print("# SUMMARY")
    print("#"*80)
    
    baseline_rmds = roth_result['metrics']['baseline'].get('total_rmds', 0)
    conversion_rmds = roth_result['metrics']['conversion'].get('total_rmds', 0)
    
    print(f"RothConversionProcessor Results:")
    print(f"  Baseline RMDs: ${baseline_rmds:,.0f}")
    print(f"  Conversion RMDs: ${conversion_rmds:,.0f}")
    print(f"  Reduction: ${baseline_rmds - conversion_rmds:,.0f}")
    
    if conversion_rmds > 0:
        print(f"\n⚠️  ISSUE: RMDs still showing as ${conversion_rmds:,.0f} after conversion")
        print("  Expected: $0 after full $1M conversion")
    else:
        print("\n✅ SUCCESS: RMDs correctly reduced to $0")


if __name__ == "__main__":
    main()