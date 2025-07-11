#!/usr/bin/env python
"""
Test script for the Roth Conversion API endpoint.

This script sends a test request to the Roth Conversion API endpoint
and prints the response.
"""
import requests
import json
import datetime
import sys

def get_auth_token():
    """Get an authentication token from the API."""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        response = requests.post('http://localhost:8000/login/', json=login_data)
        response.raise_for_status()
        return response.json()['access']
    except requests.exceptions.RequestException as e:
        print(f"Error getting auth token: {e}")
        print("Make sure the server is running and the test user exists.")
        print("You may need to create a test user with:")
        print("python manage.py createsuperuser --email test@example.com")
        sys.exit(1)

def test_roth_conversion():
    """Test the Roth Conversion API endpoint."""
    # Get auth token
    token = get_auth_token()
    
    # Create test data
    current_year = datetime.datetime.now().year
    
    test_data = {
        "scenario": {
            "name": "Test Scenario",
            "retirement_age": 65,
            "medicare_age": 65,
            "mortality_age": 90,
            "part_b_inflation_rate": 3.0,
            "part_d_inflation_rate": 3.0,
            "apply_standard_deduction": True
        },
        "client": {
            "first_name": "Test",
            "last_name": "Client",
            "birthdate": f"{current_year - 60}-01-01",  # 60 years old
            "gender": "Male",
            "tax_status": "Single",
            "state": "CA"
        },
        "spouse": None,
        "assets": [
            {
                "id": 1,
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
                "id": 2,
                "income_type": "traditional_401k",
                "income_name": "401(k)",
                "owned_by": "primary",
                "current_asset_balance": 300000,
                "monthly_amount": 0,
                "monthly_contribution": 1000,
                "age_to_begin_withdrawal": 65,
                "age_to_end_withdrawal": 90,
                "rate_of_return": 6.0,
                "cola": 0,
                "exclusion_ratio": 0,
                "tax_rate": 0,
                "max_to_convert": 100000
            },
            {
                "id": 3,
                "income_type": "roth_ira",
                "income_name": "Existing Roth IRA",
                "owned_by": "primary",
                "current_asset_balance": 50000,
                "monthly_amount": 0,
                "monthly_contribution": 500,
                "age_to_begin_withdrawal": 65,
                "age_to_end_withdrawal": 90,
                "rate_of_return": 5.0,
                "cola": 0,
                "exclusion_ratio": 0,
                "tax_rate": 0
            }
        ],
        "optimizer_params": {
            "conversion_start_year": current_year,
            "years_to_convert": 5,
            "pre_retirement_income": 100000,
            "roth_growth_rate": 5.0,
            "max_annual_amount": 60000,
            "roth_withdrawal_amount": 20000,
            "roth_withdrawal_start_year": current_year + 10
        }
    }
    
    # Send request to API
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/roth-optimize/',
            headers=headers,
            json=test_data
        )
        
        # Print response
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            
            # Print summary of results
            print("\n=== Roth Conversion Results ===")
            print(f"Conversion Start Year: {result['optimal_schedule']['start_year']}")
            print(f"Duration: {result['optimal_schedule']['duration']} years")
            print(f"Annual Amount: ${result['optimal_schedule']['annual_amount']:,.2f}")
            print(f"Total Amount: ${result['optimal_schedule']['total_amount']:,.2f}")
            
            # Print comparison metrics
            print("\n=== Comparison Metrics ===")
            comparison = result['comparison']
            print(f"Tax Savings: ${comparison['tax_savings']:,.2f} ({comparison['tax_savings_pct']:.1f}%)")
            print(f"Medicare Savings: ${comparison['medicare_savings']:,.2f} ({comparison['medicare_savings_pct']:.1f}%)")
            print(f"IRMAA Savings: ${comparison['irmaa_savings']:,.2f} ({comparison['irmaa_savings_pct']:.1f}%)")
            print(f"Inheritance Tax Savings: ${comparison['inheritance_tax_savings']:,.2f} ({comparison['inheritance_tax_savings_pct']:.1f}%)")
            print(f"Total Savings: ${comparison['total_savings']:,.2f} ({comparison['total_savings_pct']:.1f}%)")
            
            # Save full response to file for detailed analysis
            with open('roth_conversion_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\nFull response saved to roth_conversion_response.json")
            
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    test_roth_conversion() 