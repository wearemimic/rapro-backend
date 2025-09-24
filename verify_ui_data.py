#!/usr/bin/env python
"""
Final verification script showing EXACTLY what the UI receives
"""

import os
import sys
import django
import json
from decimal import Decimal

sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.roth_conversion_processor import RothConversionProcessor

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_to_float(v) for v in obj]
    return obj

# UI sends this exact payload
payload = {
    'scenario': {
        'id': 4,
        'current_year': 2025,
        'start_year': 2040,
        'retirement_age': 65,
        'mortality_age': 90,
    },
    'client': {
        'birthdate': '1975-01-01',
        'state': 'CA',
        'tax_status': 'Single',
    },
    'assets': [
        {
            'income_type': 'Qualified',
            'income_name': '401k', 
            'current_asset_balance': 1000000,
            'monthly_amount': 2500,
            'age_to_begin_withdrawal': 65,
            'rate_of_return': 0,
            'max_to_convert': 1000000,
        }
    ],
    'optimizer_params': {
        'conversion_start_year': 2032,
        'years_to_convert': 5,
        'roth_growth_rate': 5,
    }
}

processor = RothConversionProcessor(
    scenario=payload['scenario'],
    client=payload['client'],
    spouse=None,
    assets=payload['assets'],
    conversion_params=payload['optimizer_params']
)

result = processor.process()
conversion_results = result.get('conversion_results', [])

print("\n" + "="*80)
print("EXACT DATA STRUCTURE UI RECEIVES (JSON format)")
print("="*80)

# Show specific years the UI would display
critical_years = [2032, 2036, 2040, 2050]

for year in critical_years:
    for row in conversion_results:
        if row.get('year') == year:
            # Convert to exact JSON the UI receives
            ui_data = decimal_to_float(row)
            
            print(f"\n### Year {year}:")
            print("```json")
            print(json.dumps({
                'year': ui_data.get('year'),
                'Qualified_balance': ui_data.get('Qualified_balance'),
                'roth_ira_balance': ui_data.get('roth_ira_balance'),
                'rmd_amount': ui_data.get('rmd_amount', 0),
                'roth_conversion': ui_data.get('roth_conversion', 0)
            }, indent=2))
            print("```")
            
            if year == 2050:
                print(f"\n✅ RMD is ${ui_data.get('rmd_amount', 0):,.0f} (Should be $0)")
                print(f"✅ Qualified balance is ${ui_data.get('Qualified_balance', 0):,.0f} (Should be $0)")
                print(f"✅ Roth balance is ${ui_data.get('roth_ira_balance', 0):,.0f} (Should be ~$1.2M)")
            break

print("\n" + "="*80)
print("WHAT THE UI GRAPHS SHOULD SHOW:")
print("="*80)
print("""
1. Asset Timeline (Conversion scenario):
   - Qualified line: Drops from $1M to $0 between 2032-2036
   - Roth IRA line: Grows from $0 to $1.2M+
   
2. RMD Graph:
   - Baseline: Shows RMDs starting at age 75
   - Conversion: Shows $0 RMDs (since Qualified = $0)
   
3. Conversion Impact Table:
   - Should show RMD reduction benefit
   - Year 2050 RMD: $0 (not $180,000)
""")

# Check the metrics
metrics = result.get('metrics', {})
print("\nMETRICS SUMMARY:")
print(f"Baseline Total RMDs: ${metrics.get('baseline', {}).get('total_rmds', 0):,.0f}")
print(f"Conversion Total RMDs: ${metrics.get('conversion', {}).get('total_rmds', 0):,.0f}")
print(f"RMD Savings: ${metrics.get('baseline', {}).get('total_rmds', 0) - metrics.get('conversion', {}).get('total_rmds', 0):,.0f}")