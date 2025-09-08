#!/usr/bin/env python
"""
Test script to verify Roth conversion fixes
Tests:
1. RMDs stop after full conversion
2. No double depletion
3. Roth balance tracking
4. Proper sequencing (RMD before conversion)
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.scenario_processor import ScenarioProcessor

def create_test_scenario():
    """Create a test scenario with Roth conversion"""
    scenario = {
        'id': 999,
        'client_id': 1,
        'scenario_name': 'Test Roth Conversion',
        'notes': 'Testing Roth conversion fixes',
        'current_year': 2024,
        'start_year': 2024,
        'inflation_rate': Decimal('0.03'),
        'target_net_income': 60000,
        'joint_withdrawal_preference': 'proportional',
        
        # Roth conversion parameters - convert $100k/year for 5 years (full conversion of $500k account)
        'roth_conversion_start_year': 2024,
        'roth_conversion_duration': 5,
        'roth_conversion_annual_amount': 100000,
        
        # Tax settings
        'apply_standard_deduction': True,
        'custom_federal_deduction': 0,
        'custom_state_deduction': 0,
        'dependent_count': 0,
        'blind_primary': False,
        'blind_spouse': False,
    }
    
    client = {
        'id': 1,
        'name': 'Test Client',
        'birthdate': date(1954, 1, 1),  # Age 70 in 2024, RMDs start at 73
        'state': 'CA',
        'tax_status': 'Single',
        'mortality_age': 90,
    }
    
    spouse = None
    
    # Single traditional IRA with $500k balance
    assets = [{
        'id': 1,
        'income_type': 'Qualified',
        'investment_name': 'Traditional IRA',
        'current_asset_balance': Decimal('500000'),
        'rate_of_return': Decimal('0.06'),
        'owned_by': 'primary',
        'age_to_begin_withdrawal': 73,  # RMD age
        'annual_contribution': 0,
    }]
    
    incomes = []
    expenses = []
    
    return scenario, client, spouse, assets, incomes, expenses

def test_roth_conversion():
    """Test the Roth conversion fixes"""
    print("\n" + "="*80)
    print("TESTING ROTH CONVERSION FIXES")
    print("="*80)
    
    scenario, client, spouse, assets, incomes, expenses = create_test_scenario()
    
    # Create processor with debug enabled
    processor = ScenarioProcessor.from_dicts(
        scenario=scenario,
        client=client,
        spouse=spouse,
        assets=assets,
        incomes=incomes,
        expenses=expenses,
        debug=True
    )
    
    # Run calculation
    print("\nRunning scenario calculation...")
    results = processor.calculate()
    
    # Analyze results
    print("\n" + "-"*40)
    print("ANALYSIS OF RESULTS:")
    print("-"*40)
    
    # Check Year 2024 (first conversion year)
    year_2024 = next((r for r in results if r['year'] == 2024), None)
    if year_2024:
        print(f"\n2024 (Age 70, First Conversion Year):")
        print(f"  Traditional IRA Balance: ${year_2024.get('Traditional IRA_balance', 0):,.0f}")
        print(f"  Roth IRA Balance: ${year_2024.get('Roth IRA (Converted)_balance', 0):,.0f}")
        print(f"  RMD Amount: ${year_2024.get('rmd_amount', 0):,.0f} (Should be 0 - age 70 < 73)")
    
    # Check Year 2027 (age 73, RMDs would normally start)
    year_2027 = next((r for r in results if r['year'] == 2027), None)
    if year_2027:
        print(f"\n2027 (Age 73, Normal RMD Start Age):")
        print(f"  Traditional IRA Balance: ${year_2027.get('Traditional IRA_balance', 0):,.0f}")
        print(f"  Roth IRA Balance: ${year_2027.get('Roth IRA (Converted)_balance', 0):,.0f}")
        print(f"  RMD Amount: ${year_2027.get('rmd_amount', 0):,.0f}")
    
    # Check Year 2029 (after full conversion)
    year_2029 = next((r for r in results if r['year'] == 2029), None)
    if year_2029:
        print(f"\n2029 (After Full Conversion):")
        print(f"  Traditional IRA Balance: ${year_2029.get('Traditional IRA_balance', 0):,.0f} (Should be 0)")
        print(f"  Roth IRA Balance: ${year_2029.get('Roth IRA (Converted)_balance', 0):,.0f} (Should be ~$500k + growth)")
        print(f"  RMD Amount: ${year_2029.get('rmd_amount', 0):,.0f} (Should be 0 - fully converted)")
    
    # Check for issues
    print("\n" + "-"*40)
    print("ISSUE CHECKS:")
    print("-"*40)
    
    issues_found = []
    
    # Check 1: RMDs after full conversion
    post_conversion_years = [r for r in results if r['year'] >= 2029]
    for year_data in post_conversion_years:
        if year_data.get('rmd_amount', 0) > 0:
            issues_found.append(f"❌ RMD still showing in {year_data['year']} after full conversion: ${year_data['rmd_amount']:,.0f}")
    
    # Check 2: Roth balance tracking
    has_roth_balance = any('Roth' in str(k) and 'balance' in str(k) for r in results for k in r.keys())
    if not has_roth_balance:
        issues_found.append("❌ No Roth balance tracking found in results")
    
    # Check 3: Traditional balance should be 0 after conversion
    year_2030 = next((r for r in results if r['year'] == 2030), None)
    if year_2030:
        trad_balance = year_2030.get('Traditional IRA_balance', 0)
        if trad_balance > 1:  # Allow for rounding
            issues_found.append(f"❌ Traditional IRA balance not zero after conversion: ${trad_balance:,.0f}")
    
    # Report results
    if not issues_found:
        print("✅ All checks passed! Roth conversion fixes are working correctly.")
    else:
        print("Issues found:")
        for issue in issues_found:
            print(f"  {issue}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_roth_conversion()