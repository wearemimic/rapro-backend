#!/usr/bin/env python
"""
Test the exact API call the UI makes
"""
import requests
import json

# The exact payload the UI sends for a $1,000,000 conversion
payload = {
    "scenario": {
        "id": 4,
        "roth_conversion_start_year": 2032,
        "roth_conversion_duration": 5,
        "roth_conversion_annual_amount": 200000,  # $1M / 5 years
        "roth_withdrawal_amount": 50000,
        "roth_withdrawal_start_year": 2042,
        "pre_retirement_income": 100000,
        "retirement_age": 65,
        "mortality_age": 90,
        "part_b_inflation_rate": 3.0,
        "part_d_inflation_rate": 3.0
    },
    "client": {
        "id": 4,
        "tax_status": "Single",
        "birthdate": "1975-01-01",
        "name": "Test Client",
        "gender": "M",
        "state": "CA"
    },
    "spouse": None,
    "assets": [
        {
            "id": 1,
            "income_type": "Qualified",
            "income_name": "401k",
            "current_asset_balance": 1000000,
            "monthly_amount": 0,
            "age_to_begin_withdrawal": 65,
            "rate_of_return": 5,
            "cola": 0,
            "max_to_convert": 1000000
        }
    ],
    "optimizer_params": {
        "mode": "manual",
        "conversion_start_year": 2032,
        "years_to_convert": 5,
        "annual_conversion_amount": 200000,
        "roth_growth_rate": 5,
        "max_annual_amount": 200000,
        "max_total_amount": 1000000,
        "roth_withdrawal_amount": 50000,
        "roth_withdrawal_start_year": 2042
    }
}

# Make the API call
print("Making API call to /api/roth-optimize/...")
response = requests.post(
    "http://localhost:8000/api/roth-optimize/",
    json=payload,
    headers={
        "Content-Type": "application/json",
        # Note: Would need actual auth token in real test
    }
)

if response.status_code == 200:
    data = response.json()
    
    print("\n=== API RESPONSE ANALYSIS ===")
    print(f"Response keys: {list(data.keys())}")
    
    if 'baseline' in data and 'metrics' in data['baseline']:
        print(f"\nBaseline RMDs: ${data['baseline']['metrics'].get('total_rmds', 0):,.0f}")
    
    if 'optimal_schedule' in data and 'score_breakdown' in data['optimal_schedule']:
        print(f"Optimal RMDs: ${data['optimal_schedule']['score_breakdown'].get('total_rmds', 0):,.0f}")
    
    # Check what the UI would see
    print("\n=== WHAT THE UI SEES ===")
    print(f"Bar chart baseline RMDs (data.baseline.metrics.total_rmds): ${data.get('baseline', {}).get('metrics', {}).get('total_rmds', 0):,.0f}")
    print(f"Bar chart optimal RMDs (data.optimal_schedule.score_breakdown.total_rmds): ${data.get('optimal_schedule', {}).get('score_breakdown', {}).get('total_rmds', 0):,.0f}")
    
else:
    print(f"API call failed with status {response.status_code}")
    print(response.text)