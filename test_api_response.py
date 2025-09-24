#!/usr/bin/env python
"""
Test script to verify the exact API response structure for the Roth conversion endpoint.
This shows what the UI actually receives.
"""

import os
import sys
import django
import json
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.roth_conversion_processor import RothConversionProcessor

def test_api_response():
    """Test what the API actually returns"""
    
    # Exact payload from UI
    payload = {
        'scenario': {
            'id': 4,
            'scenario_name': 'Test Scenario',
            'current_year': 2025,
            'start_year': 2040,
            'retirement_age': 65,
            'mortality_age': 90,
            'inflation_rate': 0.03,
            'target_net_income': 60000,
            'apply_standard_deduction': True,
        },
        'client': {
            'id': 4,
            'birthdate': '1975-01-01',
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
    
    # Create processor
    processor = RothConversionProcessor(
        scenario=payload['scenario'],
        client=payload['client'],
        spouse=payload['spouse'],
        assets=payload['assets'],
        conversion_params=payload['optimizer_params']
    )
    
    # Process
    result = processor.process()
    
    print("\n" + "="*80)
    print("API RESPONSE STRUCTURE FOR UI")
    print("="*80)
    
    # Check conversion results
    conversion_results = result.get('conversion_results', [])
    
    print("\n1. CHECKING YEAR 2032 (First conversion year):")
    for row in conversion_results:
        if row.get('year') == 2032:
            print(f"   - Qualified_balance: ${row.get('Qualified_balance', 0):,.0f}")
            print(f"   - roth_ira_balance: ${row.get('roth_ira_balance', 0):,.0f}")
            print(f"   - roth_conversion: ${row.get('roth_conversion', 0):,.0f}")
            break
    
    print("\n2. CHECKING YEAR 2036 (Last conversion year):")
    for row in conversion_results:
        if row.get('year') == 2036:
            print(f"   - Qualified_balance: ${row.get('Qualified_balance', 0):,.0f}")
            print(f"   - roth_ira_balance: ${row.get('roth_ira_balance', 0):,.0f}")
            print(f"   - roth_conversion: ${row.get('roth_conversion', 0):,.0f}")
            break
    
    print("\n3. CHECKING YEAR 2050 (RMD age 75):")
    for row in conversion_results:
        if row.get('year') == 2050:
            print(f"   - Qualified_balance: ${row.get('Qualified_balance', 0):,.0f}")
            print(f"   - roth_ira_balance: ${row.get('roth_ira_balance', 0):,.0f}")
            print(f"   - rmd_amount: ${row.get('rmd_amount', 0):,.0f}")
            
            print("\n   DATA STRUCTURE (for frontend):")
            print("   {")
            print(f"     'year': {row.get('year')},")
            print(f"     'Qualified_balance': {float(row.get('Qualified_balance', 0))},  // Direct property")
            print(f"     'roth_ira_balance': {float(row.get('roth_ira_balance', 0))},  // Direct property")
            print(f"     'rmd_amount': {float(row.get('rmd_amount', 0))},  // Direct property")
            print("     // Note: NO 'asset_balances' wrapper object!")
            print("   }")
            break
    
    # Check metrics
    print("\n4. METRICS COMPARISON:")
    baseline_rmds = result['metrics']['baseline'].get('total_rmds', 0)
    conversion_rmds = result['metrics']['conversion'].get('total_rmds', 0)
    
    print(f"   Baseline Total RMDs: ${baseline_rmds:,.0f}")
    print(f"   Conversion Total RMDs: ${conversion_rmds:,.0f}")
    print(f"   RMD Reduction: ${baseline_rmds - conversion_rmds:,.0f}")
    
    # Check if frontend should show changes
    print("\n5. WHAT THE UI GRAPHS SHOULD SHOW:")
    print("   - Asset Timeline (Conversion): Qualified balance dropping to $0 by 2036")
    print("   - Asset Timeline (Conversion): Roth balance growing from $0 to $1.2M+")
    print("   - RMD Timeline: RMDs dropping to $0 after conversion")
    print("   - Tax Timeline: Different tax patterns due to conversion")
    
    return result

if __name__ == "__main__":
    test_api_response()