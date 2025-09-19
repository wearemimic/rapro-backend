"""
Test RMD Calculations
=====================
Tests for Required Minimum Distribution calculations per IRS rules
Based on Phase III of Comprehensive Financial Summary PRD
"""

import unittest
from datetime import date, datetime
from decimal import Decimal
from django.test import TestCase
from core.models import Client, Scenario, IncomeSource
from core.scenario_processor import ScenarioProcessor


class TestRMDCalculations(TestCase):
    """Test suite for RMD calculations following IRS rules"""

    def setUp(self):
        """Set up test data"""
        # Create test client born in 1950 (age 74 in 2024)
        self.client = Client.objects.create(
            advisor_id=1,
            first_name="Test",
            last_name="Client",
            email="test@example.com",
            birthdate=date(1950, 1, 1),
            gender="Male",
            tax_status="Single"
        )

        # Create test scenario
        self.scenario = Scenario.objects.create(
            client=self.client,
            name="Test RMD Scenario",
            retirement_age=65,
            mortality_age=90
        )

    def test_rmd_table_completeness(self):
        """Test that RMD table includes all required ages 72-120+"""
        from core.scenario_processor import RMD_TABLE

        # Check ages 72-120 are present
        for age in range(72, 121):
            self.assertIn(age, RMD_TABLE, f"RMD table missing age {age}")

        # Check specific IRS values
        self.assertEqual(RMD_TABLE[72], 27.4)
        self.assertEqual(RMD_TABLE[75], 24.6)
        self.assertEqual(RMD_TABLE[80], 20.2)
        self.assertEqual(RMD_TABLE[90], 12.2)
        self.assertEqual(RMD_TABLE[100], 6.4)
        self.assertEqual(RMD_TABLE[110], 3.5)
        self.assertEqual(RMD_TABLE[120], 2.0)

    def test_rmd_start_age_by_birth_year(self):
        """Test SECURE Act 2.0 RMD start ages"""
        # Create qualified account
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            age_to_begin_withdrawal=72,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=True)

        # Test birth year 1949 - should be 72
        birthdate_1949 = date(1949, 6, 15)
        rmd_age = processor._get_rmd_start_age({"income_type": "Qualified"}, birthdate_1949)
        self.assertEqual(rmd_age, 72, "Birth year 1949 should have RMD start age 72")

        # Test birth year 1955 - should be 73
        birthdate_1955 = date(1955, 6, 15)
        rmd_age = processor._get_rmd_start_age({"income_type": "Qualified"}, birthdate_1955)
        self.assertEqual(rmd_age, 73, "Birth year 1955 should have RMD start age 73")

        # Test birth year 1960 - should be 75
        birthdate_1960 = date(1960, 6, 15)
        rmd_age = processor._get_rmd_start_age({"income_type": "Qualified"}, birthdate_1960)
        self.assertEqual(rmd_age, 75, "Birth year 1960+ should have RMD start age 75")

    def test_rmd_calculation_at_age_73(self):
        """Test RMD calculation for someone at age 73"""
        # Create qualified account with $500,000 balance
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="Traditional IRA",
            current_asset_balance=500000,
            age_to_begin_withdrawal=73,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)

        # Manually set up asset for RMD calculation
        test_asset = {
            "id": asset.id,
            "income_type": "Qualified",
            "income_name": "Traditional IRA",
            "owned_by": "primary",
            "previous_year_balance": 500000,  # Previous year-end balance
            "current_asset_balance": 500000
        }

        # Calculate RMD for age 73 (year 2023 for someone born in 1950)
        year = 2023
        rmd_amount = processor._calculate_rmd(test_asset, year)

        # At age 73, divisor is 26.5
        expected_rmd = Decimal('500000') / Decimal('26.5')
        self.assertAlmostEqual(
            float(rmd_amount),
            float(expected_rmd),
            places=2,
            msg=f"RMD at age 73 should be $500,000 / 26.5 = ${expected_rmd:.2f}"
        )

    def test_inherited_account_10_year_rule(self):
        """Test 10-year rule for inherited non-spouse accounts"""
        # Create inherited account
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Inherited Traditional Non-Spouse",
            income_name="Inherited IRA",
            current_asset_balance=200000,
            age_to_begin_withdrawal=50,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)

        # Test inherited account in year 9 (no RMD required)
        test_asset = {
            "income_type": "Inherited Traditional Non-Spouse",
            "inheritance_year": 2020,
            "current_asset_balance": 200000,
            "previous_year_balance": 200000,
            "owned_by": "primary"
        }

        # Year 9 after inheritance - no RMD required
        year = 2029
        rmd_amount = processor._calculate_rmd(test_asset, year)
        self.assertEqual(rmd_amount, Decimal('0'), "No RMD required in years 1-9 for inherited non-spouse")

        # Year 10 after inheritance - must withdraw entire balance
        year = 2030
        rmd_amount = processor._calculate_rmd(test_asset, year)
        self.assertEqual(rmd_amount, Decimal('200000'), "Must withdraw entire balance in year 10")

    def test_inherited_roth_requires_rmd(self):
        """Test that inherited Roth accounts DO require RMDs"""
        processor = ScenarioProcessor(self.scenario.id, debug=False)

        # Test inherited Roth spouse
        roth_spouse = {"income_type": "Inherited Roth Spouse"}
        self.assertTrue(
            processor._requires_rmd(roth_spouse),
            "Inherited Roth Spouse accounts should require RMDs"
        )

        # Test inherited Roth non-spouse
        roth_nonspouse = {"income_type": "Inherited Roth Non-Spouse"}
        self.assertTrue(
            processor._requires_rmd(roth_nonspouse),
            "Inherited Roth Non-Spouse accounts should require RMDs"
        )

        # Test regular Roth (should NOT require RMD)
        regular_roth = {"income_type": "Roth"}
        self.assertFalse(
            processor._requires_rmd(regular_roth),
            "Regular Roth accounts should NOT require RMDs during owner's lifetime"
        )

    def test_rmd_greater_than_withdrawal(self):
        """Test that RMD overrides planned withdrawal when larger"""
        # Create account with small planned withdrawal
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=1000000,
            monthly_amount=2000,  # $24,000 annual withdrawal
            age_to_begin_withdrawal=73,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)

        # At age 80 with $1M balance, RMD should be ~$49,505 (1M / 20.2)
        # This is greater than planned $24,000 withdrawal

        test_asset = {
            "income_type": "Qualified",
            "owned_by": "primary",
            "previous_year_balance": 1000000,
            "withdrawal_amount": 24000,
            "monthly_amount": 2000
        }

        # Calculate for age 80
        self.client.birthdate = date(1944, 1, 1)  # Makes them 80 in 2024
        year = 2024
        rmd_amount = processor._calculate_rmd(test_asset, year)

        # RMD at age 80 with $1M should be $1M / 20.2 = $49,504.95
        expected_rmd = Decimal('1000000') / Decimal('20.2')
        self.assertAlmostEqual(
            float(rmd_amount),
            float(expected_rmd),
            places=0,
            msg="RMD should override smaller planned withdrawal"
        )

    def test_edge_case_zero_balance(self):
        """Test RMD calculation with zero balance"""
        processor = ScenarioProcessor(self.scenario.id, debug=False)

        test_asset = {
            "income_type": "Qualified",
            "owned_by": "primary",
            "previous_year_balance": 0,
            "current_asset_balance": 0
        }

        year = 2024
        rmd_amount = processor._calculate_rmd(test_asset, year)
        self.assertEqual(rmd_amount, 0, "RMD should be 0 when balance is 0")

    def test_edge_case_age_over_120(self):
        """Test RMD calculation for ages over 120"""
        processor = ScenarioProcessor(self.scenario.id, debug=False)

        # Create very old client
        old_client = Client.objects.create(
            advisor_id=1,
            first_name="Very",
            last_name="Old",
            email="old@example.com",
            birthdate=date(1900, 1, 1),  # 124 years old in 2024
            gender="Male",
            tax_status="Single"
        )

        test_asset = {
            "income_type": "Qualified",
            "owned_by": "primary",
            "previous_year_balance": 100000
        }

        # For age > 120, should use divisor of 2.0
        processor.primary_birthdate = old_client.birthdate
        year = 2024
        rmd_amount = processor._calculate_rmd(test_asset, year)

        # Should use 2.0 divisor for ages 120+
        expected_rmd = Decimal('100000') / Decimal('2.0')
        self.assertEqual(rmd_amount, expected_rmd, "Ages over 120 should use 2.0 divisor")


if __name__ == '__main__':
    unittest.main()