#!/usr/bin/env python
"""
Complete test script for Roth conversion that replicates the exact flow
of RothConversionProcessor to debug the issue.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date
import json

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.scenario_processor import ScenarioProcessor
from core.roth_conversion_processor import RothConversionProcessor

def create_test_data():
    """Create test data matching user's scenario"""
    
    # Client data (age 50 in 2025, retiring at 65 in 2040)
    client = {
        'id': 4,
        'name': 'Test Client',
        'birthdate': date(1975, 1, 1),  # Age 50 in 2025
        'state': 'CA',
        'tax_status': 'Single',
        'mortality_age': 90,
        'gender': 'M',
        'first_name': 'Test',
        'last_name': 'Client',
        'email': 'test@example.com'
    }
    
    # Scenario data
    scenario = {
        'id': 4,
        'client_id': 4,
        'scenario_name': 'Test Roth Conversion',
        'notes': 'Testing $1M conversion',
        'current_year': 2025,
        'start_year': 2040,  # Retirement year
        'inflation_rate': Decimal('0.03'),
        'target_net_income': 60000,
        'joint_withdrawal_preference': 'proportional',
        'mortality_age': 90,
        'retirement_age': 65,
        
        # Tax settings
        'apply_standard_deduction': True,
        'custom_federal_deduction': 0,
        'custom_state_deduction': 0,
        'dependent_count': 0,
        'blind_primary': False,
        'blind_spouse': False,
        
        # Social Security adjustment
        'reduction_2030_ss': False,
        'ss_adjustment_year': 2030,
        'ss_adjustment_direction': 'decrease',
        'ss_adjustment_type': 'percentage',
        'ss_adjustment_amount': 23.0,
    }
    
    # Assets - $1M in 401k
    assets = [{
        'id': 8,
        'scenario_id': 4,
        'owned_by': 'primary',
        'income_type': 'Qualified',
        'income_name': '401k',
        'current_asset_balance': Decimal('1000000'),
        'monthly_amount': 2500,  # Monthly withdrawal in retirement
        'monthly_contribution': 2083.33,  # Current contributions
        'age_to_begin_withdrawal': 65,
        'age_to_end_withdrawal': 90,
        'rate_of_return': 0,  # 0% for testing
        'cola': 0,
        'exclusion_ratio': 0,
        'tax_rate': 0,
        'max_to_convert': 1000000,  # Full balance available for conversion
    }]
    
    # Social Security income
    incomes = [{
        'id': 7,
        'scenario_id': 4,
        'owned_by': 'primary',
        'income_type': 'social_security',
        'income_name': 'Social Security',
        'current_asset_balance': 0,
        'monthly_amount': 4500,
        'monthly_contribution': 0,
        'age_to_begin_withdrawal': 65,
        'age_to_end_withdrawal': 90,
        'rate_of_return': 0,
        'cola': 2,  # 2% COLA
        'exclusion_ratio': 0,
        'tax_rate': 0,
        'max_to_convert': 0,
    }]
    
    # Combine assets for processor
    all_assets = assets + incomes
    
    return scenario, client, None, all_assets  # No spouse

def test_baseline_scenario():
    """Test baseline scenario without conversion"""
    print("\n" + "="*80)
    print("TESTING BASELINE SCENARIO (No Conversion)")
    print("="*80)
    
    scenario, client, spouse, assets = create_test_data()
    
    # Create processor
    processor = ScenarioProcessor.from_dicts(
        scenario=scenario,
        client=client,
        spouse=spouse,
        assets=assets,
        debug=True
    )
    
    # Run calculation
    results = processor.calculate()
    
    # Analyze RMDs
    total_rmds = 0
    for year_data in results:
        year = year_data['year']
        age = year_data.get('primary_age', 0)
        
        # Look for RMD data
        for key, value in year_data.items():
            if 'balance' in key and 'Qualified' in key:
                qualified_balance = value
            if 'rmd' in key.lower() or key == 'withdrawal_amount':
                if value and value > 0 and age >= 73:  # RMD age
                    print(f"Year {year} (Age {age}): RMD = ${value:,.0f}, Qualified Balance = ${qualified_balance:,.0f}")
                    total_rmds += value
    
    print(f"\nTotal RMDs over lifetime: ${total_rmds:,.0f}")
    return results, total_rmds

def test_conversion_scenario(conversion_start_year, years_to_convert, total_to_convert):
    """Test scenario with Roth conversion"""
    print("\n" + "="*80)
    print(f"TESTING CONVERSION SCENARIO")
    print(f"Converting ${total_to_convert:,.0f} starting {conversion_start_year} over {years_to_convert} years")
    print("="*80)
    
    scenario, client, spouse, assets = create_test_data()
    
    # Add Roth conversion parameters
    annual_conversion = total_to_convert / years_to_convert
    scenario['roth_conversion_start_year'] = conversion_start_year
    scenario['roth_conversion_duration'] = years_to_convert
    scenario['roth_conversion_annual_amount'] = annual_conversion
    
    print(f"Annual conversion amount: ${annual_conversion:,.0f}")
    
    # Create processor
    processor = ScenarioProcessor.from_dicts(
        scenario=scenario,
        client=client,
        spouse=spouse,
        assets=assets,
        debug=True
    )
    
    # Run calculation
    results = processor.calculate()
    
    # Analyze results
    total_rmds = 0
    total_converted = 0
    
    for year_data in results:
        year = year_data['year']
        age = year_data.get('primary_age', 0)
        
        # Track balances
        qualified_balance = 0
        roth_balance = 0
        rmd_amount = 0
        conversion_amount = year_data.get('roth_conversion', 0)
        
        for key, value in year_data.items():
            if 'balance' in key:
                if 'Qualified' in key or '401' in key:
                    qualified_balance = value
                elif 'roth' in key.lower():
                    roth_balance = value
            if 'rmd' in key.lower():
                rmd_amount = value
        
        # Print key years
        if year in [conversion_start_year, conversion_start_year + years_to_convert - 1, 
                   conversion_start_year + years_to_convert, 2050, 2060]:
            print(f"Year {year} (Age {age}):")
            print(f"  Qualified: ${qualified_balance:,.0f}")
            print(f"  Roth: ${roth_balance:,.0f}")
            print(f"  RMD: ${rmd_amount:,.0f}")
            print(f"  Conversion: ${conversion_amount:,.0f}")
        
        if age >= 73:
            total_rmds += rmd_amount
        total_converted += conversion_amount
    
    print(f"\nTotal RMDs over lifetime: ${total_rmds:,.0f}")
    print(f"Total amount converted: ${total_converted:,.0f}")
    
    return results, total_rmds

def test_roth_conversion_processor():
    """Test using the actual RothConversionProcessor"""
    print("\n" + "="*80)
    print("TESTING WITH RothConversionProcessor")
    print("="*80)
    
    scenario, client, spouse, assets = create_test_data()
    
    # Test parameters matching user's scenario
    conversion_start_year = 2032  # Pre-retirement conversion
    years_to_convert = 5
    total_to_convert = 1000000
    roth_withdrawal_start = 2042
    roth_withdrawal_amount = 50000
    
    # Create RothConversionProcessor
    processor = RothConversionProcessor(
        scenario=scenario,
        client=client,
        spouse=spouse,
        assets=assets,
        conversion_start_year=conversion_start_year,
        years_to_convert=years_to_convert,
        roth_withdrawal_start_year=roth_withdrawal_start,
        roth_withdrawal_amount=roth_withdrawal_amount,
        roth_growth_rate=5,
        pre_retirement_income=100000,
        max_annual_amount=0,  # No max
        debug=True
    )
    
    # Process conversion
    processor.process_conversion()
    
    # Get comparison
    comparison = processor.get_comparison()
    
    print("\nBaseline vs Conversion Comparison:")
    print(f"Baseline Total RMDs: ${comparison['baseline']['total_rmds']:,.0f}")
    print(f"Conversion Total RMDs: ${comparison['conversion']['total_rmds']:,.0f}")
    print(f"RMD Reduction: ${comparison['baseline']['total_rmds'] - comparison['conversion']['total_rmds']:,.0f}")
    
    print(f"\nBaseline Lifetime Tax: ${comparison['baseline']['lifetime_tax']:,.0f}")
    print(f"Conversion Lifetime Tax: ${comparison['conversion']['lifetime_tax']:,.0f}")
    
    # Check specific years
    baseline_results = comparison['baseline_results']
    conversion_results = comparison['conversion_results']
    
    # Find year 2050 (age 75, after RMD start)
    for i, year_data in enumerate(conversion_results):
        if year_data['year'] == 2050:
            print(f"\nYear 2050 (Age 75) - After Conversion Complete:")
            print(f"  Baseline RMD: ${baseline_results[i].get('rmd_amount', 0):,.0f}")
            print(f"  Conversion RMD: ${year_data.get('rmd_amount', 0):,.0f}")
            
            # Check balances
            for key, value in year_data.items():
                if 'balance' in key:
                    print(f"  {key}: ${value:,.0f}")
    
    return comparison

def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("# COMPREHENSIVE ROTH CONVERSION TEST")
    print("#"*80)
    
    # Test 1: Baseline (no conversion)
    baseline_results, baseline_rmds = test_baseline_scenario()
    
    # Test 2: With conversion
    conversion_results, conversion_rmds = test_conversion_scenario(
        conversion_start_year=2032,
        years_to_convert=5,
        total_to_convert=1000000
    )
    
    # Test 3: Using RothConversionProcessor
    comparison = test_roth_conversion_processor()
    
    # Summary
    print("\n" + "#"*80)
    print("# SUMMARY")
    print("#"*80)
    print(f"Baseline RMDs: ${baseline_rmds:,.0f}")
    print(f"Conversion RMDs: ${conversion_rmds:,.0f}")
    print(f"RMD Reduction: ${baseline_rmds - conversion_rmds:,.0f}")
    
    if conversion_rmds > 0:
        print(f"\n⚠️  WARNING: RMDs still showing after conversion!")
        print(f"   Expected: $0")
        print(f"   Actual: ${conversion_rmds:,.0f}")
        print("\nThis indicates the conversion is not fully depleting the qualified account.")
    else:
        print("\n✅ SUCCESS: RMDs reduced to $0 after full conversion!")

if __name__ == "__main__":
    main()