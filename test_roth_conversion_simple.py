#!/usr/bin/env python
"""
Simple test script for the Roth Conversion Processor.

This script tests the basic functionality of the RothConversionProcessor
without requiring the Django test framework.
"""
import sys
import os
import datetime
from decimal import Decimal
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

# Create a mock ScenarioProcessor class to avoid database dependencies
class MockScenarioProcessor:
    @classmethod
    def from_dicts(cls, scenario, client, spouse, assets, debug=False):
        """Mock implementation that returns a simple processor instance."""
        instance = cls()
        instance.scenario = scenario
        instance.client = client
        instance.spouse = spouse
        instance.assets = assets
        instance.debug = debug
        return instance
        
    def calculate(self):
        """Mock implementation that returns a simple year-by-year result."""
        # Generate a simple year-by-year result
        current_year = datetime.datetime.now().year
        retirement_year = current_year + 5
        
        # Get retirement age from scenario
        retirement_age = self.scenario.get('retirement_age', 65)
        mortality_age = self.scenario.get('mortality_age', 90)
        
        # Calculate primary age
        if isinstance(self.client.get('birthdate'), str):
            birth_year = datetime.datetime.strptime(self.client['birthdate'], '%Y-%m-%d').year
        else:
            birth_year = datetime.datetime.now().year - 60  # Default to 60 years old
        
        current_age = current_year - birth_year
        years_to_simulate = mortality_age - current_age
        
        # Create a simple year-by-year result
        results = []
        
        # Add assets to track
        asset_balances = {}
        for asset in self.assets:
            asset_type = asset.get('income_type', 'unknown')
            asset_balances[f"{asset_type}_balance"] = float(asset.get('current_asset_balance', 0))
        
        # Generate year-by-year data
        for i in range(years_to_simulate):
            year = current_year + i
            age = current_age + i
            
            # Simple tax calculation (just for testing)
            gross_income = 100000 if year < retirement_year else 80000
            taxable_income = gross_income * 0.85
            federal_tax = taxable_income * 0.22
            
            # Simple Medicare calculation
            medicare_base = 0 if age < 65 else 2000
            irmaa_surcharge = 0 if age < 65 else 1000
            
            # Simple RMD calculation
            rmd_amount = 0
            if age >= 72:
                for asset in self.assets:
                    if asset.get('income_type') in ['traditional_ira', 'traditional_401k', 'ira', '401k']:
                        balance = asset_balances.get(f"{asset.get('income_type')}_balance", 0)
                        rmd = balance / 25.0  # Simple RMD calculation
                        asset_balances[f"{asset.get('income_type')}_rmd"] = rmd
                        rmd_amount += rmd
            
            # Update asset balances
            for asset_type, balance in asset_balances.items():
                if asset_type.endswith('_balance'):
                    # Simple growth calculation
                    growth_rate = 0.05  # 5% growth
                    asset_balances[asset_type] = balance * (1 + growth_rate)
            
            # Create year data
            year_data = {
                'year': year,
                'primary_age': age,
                'spouse_age': age - 2 if self.spouse else None,
                'gross_income': gross_income,
                'taxable_income': taxable_income,
                'federal_tax': federal_tax,
                'medicare_base': medicare_base,
                'irmaa_surcharge': irmaa_surcharge,
                'net_income': gross_income - federal_tax - medicare_base - irmaa_surcharge,
                'rmd_total': rmd_amount
            }
            
            # Add asset balances to year data
            for asset_type, balance in asset_balances.items():
                year_data[asset_type] = balance
            
            results.append(year_data)
        
        return results

# Import our module, replacing the ScenarioProcessor with our mock
import core.roth_conversion_processor
core.roth_conversion_processor.ScenarioProcessor = MockScenarioProcessor
from core.roth_conversion_processor import RothConversionProcessor

def run_test():
    """Run a simple test of the RothConversionProcessor."""
    current_year = datetime.datetime.now().year
    
    # Test scenario
    scenario = {
        "name": "Test Scenario",
        "retirement_age": 65,
        "medicare_age": 65,
        "mortality_age": 90,
        "part_b_inflation_rate": 3.0,
        "part_d_inflation_rate": 3.0,
        "apply_standard_deduction": True
    }
    
    # Test client
    client_data = {
        "first_name": "Test",
        "last_name": "Client",
        "birthdate": f"{current_year - 60}-01-01",  # 60 years old
        "gender": "Male",
        "tax_status": "Single",
        "state": "CA"
    }
    
    # Test assets
    assets = [
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
    ]
    
    # Test conversion parameters
    conversion_params = {
        "conversion_start_year": current_year,
        "years_to_convert": 5,
        "pre_retirement_income": 100000,
        "roth_growth_rate": 5.0,
        "max_annual_amount": 60000,
        "roth_withdrawal_amount": 20000,
        "roth_withdrawal_start_year": current_year + 10
    }
    
    # Create the processor
    processor = RothConversionProcessor(
        scenario=scenario,
        client=client_data,
        spouse=None,
        assets=assets,
        conversion_params=conversion_params
    )
    
    # Test initialization
    print("=== Testing Initialization ===")
    print(f"Conversion Start Year: {processor.conversion_start_year}")
    print(f"Years to Convert: {processor.years_to_convert}")
    print(f"Pre-Retirement Income: {processor.pre_retirement_income}")
    print(f"Roth Growth Rate: {processor.roth_growth_rate}")
    print(f"Max Annual Amount: {processor.max_annual_amount}")
    print(f"Roth Withdrawal Amount: {processor.roth_withdrawal_amount}")
    print(f"Roth Withdrawal Start Year: {processor.roth_withdrawal_start_year}")
    print(f"Retirement Year: {processor.retirement_year}")
    
    # Test prepare_assets_for_conversion
    print("\n=== Testing Prepare Assets for Conversion ===")
    annual_conversion, total_conversion = processor._prepare_assets_for_conversion()
    print(f"Annual Conversion: {annual_conversion}")
    print(f"Total Conversion: {total_conversion}")
    print(f"Number of Assets: {len(processor.assets)}")
    print(f"Synthetic Roth Asset: {processor.assets[3]['income_type']} - {processor.assets[3]['income_name']}")
    
    # Test prepare_baseline_scenario
    print("\n=== Testing Prepare Baseline Scenario ===")
    baseline_scenario = processor._prepare_baseline_scenario()
    print(f"Roth Conversion Start Year: {baseline_scenario.get('roth_conversion_start_year')}")
    print(f"Roth Conversion Duration: {baseline_scenario.get('roth_conversion_duration')}")
    print(f"Roth Conversion Annual Amount: {baseline_scenario.get('roth_conversion_annual_amount')}")
    
    # Test prepare_conversion_scenario
    print("\n=== Testing Prepare Conversion Scenario ===")
    conversion_scenario = processor._prepare_conversion_scenario()
    print(f"Roth Conversion Start Year: {conversion_scenario.get('roth_conversion_start_year')}")
    print(f"Roth Conversion Duration: {conversion_scenario.get('roth_conversion_duration')}")
    print(f"Roth Conversion Annual Amount: {conversion_scenario.get('roth_conversion_annual_amount')}")
    print(f"Pre-Retirement Income: {conversion_scenario.get('pre_retirement_income')}")
    
    # Test process (with mock ScenarioProcessor)
    print("\n=== Testing Process ===")
    try:
        result = processor.process()
        print("Process completed successfully!")
        print(f"Optimal Schedule Start Year: {result['optimal_schedule']['start_year']}")
        print(f"Optimal Schedule Duration: {result['optimal_schedule']['duration']}")
        print(f"Optimal Schedule Annual Amount: {result['optimal_schedule']['annual_amount']}")
        print(f"Optimal Schedule Total Amount: {result['optimal_schedule']['total_amount']}")
        
        # Save the result to a file for inspection
        with open('roth_conversion_test_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("Result saved to roth_conversion_test_result.json")
    except Exception as e:
        print(f"Error in process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test() 