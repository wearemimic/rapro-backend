#!/usr/bin/env python3
"""
Test script to verify asset balance calculation fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from decimal import Decimal
from core.scenario_processor import ScenarioProcessor
from core.models import Scenario, Client, IncomeSource
import datetime

def test_asset_growth():
    """Test that $1M growing at 7% for 15 years equals the correct amount"""

    # Create a mock asset
    test_asset = {
        'current_asset_balance': Decimal('1000000'),
        'monthly_contribution': Decimal('0'),
        'rate_of_return': Decimal('0.07'),
        'age_to_begin_withdrawal': 75,
        'income_type': 'Qualified',
        'income_name': 'Test 401k'
    }

    # Create mock scenario with birthdate
    class MockScenario:
        def __init__(self):
            self.roth_conversion_start_year = None
            self.roth_conversion_duration = None
            self.roth_conversion_annual_amount = 0

    # Create processor
    processor = ScenarioProcessor(MockScenario())
    processor.assets = [test_asset]

    # Mock birthdate for age calculation (assuming client is 50 now)
    current_year = datetime.datetime.now().year
    birthdate = datetime.datetime(current_year - 50, 1, 1)

    # Calculate for 15 years in the future
    target_year = current_year + 15

    # Calculate the balance
    balance = processor._calculate_asset_balance(test_asset, target_year, birthdate)

    # Expected: $1M * (1.07)^15
    expected = Decimal('1000000') * (Decimal('1.07') ** 15)

    print(f"Initial Balance: $1,000,000")
    print(f"Growth Rate: 7%")
    print(f"Years: 15")
    print(f"Calculated Balance: ${balance:,.2f}")
    print(f"Expected Balance: ${expected:,.2f}")
    print(f"Difference: ${abs(balance - expected):,.2f}")

    # Check if it's correct (within $1 due to rounding)
    if abs(balance - expected) < 1:
        print("✅ PASS: Asset calculation is correct!")
        return True
    else:
        print("❌ FAIL: Asset calculation is still incorrect!")
        return False

if __name__ == "__main__":
    try:
        success = test_asset_growth()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)