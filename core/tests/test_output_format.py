"""
Test Output Format
==================
Tests that the scenario processor output matches the PRD specification
for Phase VI: Net Income & Output
"""

import unittest
from datetime import date
from decimal import Decimal
from django.test import TestCase
from core.models import Client, Scenario, IncomeSource
from core.scenario_processor import ScenarioProcessor


class TestOutputFormat(TestCase):
    """Test suite for verifying output format matches PRD specification"""

    def setUp(self):
        """Set up test data"""
        # Create test client
        self.client = Client.objects.create(
            advisor_id=1,
            first_name="Test",
            last_name="Client",
            email="test@example.com",
            birthdate=date(1959, 1, 1),  # Age 65 in 2024
            gender="Male",
            tax_status="Single"
        )

        # Create test scenario
        self.scenario = Scenario.objects.create(
            client=self.client,
            name="Test Output Format Scenario",
            retirement_age=65,
            mortality_age=90
        )

    def test_income_by_source_dictionary(self):
        """Test that income_by_source dictionary contains IncomeSource IDs as keys"""
        # Create multiple income sources
        ss = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="social_security",
            income_name="Social Security",
            monthly_amount=2000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=3000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # Verify income_by_source field exists
        self.assertIn('income_by_source', first_year, "Should have income_by_source dictionary")

        income_by_source = first_year['income_by_source']
        self.assertIsInstance(income_by_source, dict, "income_by_source should be a dictionary")

        # Should have entries for our income sources
        # Note: IDs should be present as keys
        self.assertIn(ss.id, income_by_source, f"SS ID {ss.id} should be in income_by_source")
        self.assertIn(qualified.id, income_by_source, f"Qualified ID {qualified.id} should be in income_by_source")

    def test_asset_balances_dictionary(self):
        """Test that asset_balances dictionary contains IncomeSource IDs as keys"""
        # Create assets with balances
        qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=2000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        roth = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Roth",
            income_name="Roth IRA",
            current_asset_balance=200000,
            monthly_amount=0,
            age_to_begin_withdrawal=70,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # Verify asset_balances field exists
        self.assertIn('asset_balances', first_year, "Should have asset_balances dictionary")

        asset_balances = first_year['asset_balances']
        self.assertIsInstance(asset_balances, dict, "asset_balances should be a dictionary")

        # Should have balances for our assets
        self.assertIn(qualified.id, asset_balances, f"Qualified ID {qualified.id} should be in asset_balances")
        self.assertIn(roth.id, asset_balances, f"Roth ID {roth.id} should be in asset_balances")

        # Verify balances are positive
        self.assertGreater(asset_balances[qualified.id], 0, "Qualified balance should be positive")
        self.assertGreater(asset_balances[roth.id], 0, "Roth balance should be positive")

    def test_rmd_required_dictionary(self):
        """Test that rmd_required dictionary contains assets requiring RMDs"""
        # Create qualified account (subject to RMDs)
        qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="Traditional IRA",
            current_asset_balance=1000000,
            monthly_amount=1000,
            age_to_begin_withdrawal=73,  # RMD age
            age_to_end_withdrawal=90
        )

        # Update client age to trigger RMDs
        self.client.birthdate = date(1951, 1, 1)  # Age 73 in 2024
        self.client.save()

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Find a year where RMDs should occur
        rmd_year = None
        for result in results:
            if result.get('primary_age', 0) >= 73:
                rmd_year = result
                break

        self.assertIsNotNone(rmd_year, "Should have at least one year with RMDs")

        # Verify rmd_required field exists
        self.assertIn('rmd_required', rmd_year, "Should have rmd_required dictionary")
        self.assertIn('rmd_total', rmd_year, "Should have rmd_total field")

        rmd_required = rmd_year['rmd_required']
        if rmd_year['rmd_total'] > 0:
            self.assertIsInstance(rmd_required, dict, "rmd_required should be a dictionary")
            # Should have RMD for qualified account
            self.assertIn(qualified.id, rmd_required, f"Qualified ID {qualified.id} should have RMD")
            self.assertGreater(rmd_required[qualified.id], 0, "RMD amount should be positive")

    def test_net_income_fields(self):
        """Test that all PRD-required net income fields are present"""
        # Create income source
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=5000,  # $60k/year
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # Check all PRD-required net income fields
        required_fields = [
            'gross_income_total',    # Total income before deductions
            'after_tax_income',      # After federal and state taxes
            'after_medicare_income', # After taxes and Medicare
            'remaining_income',      # Final remaining income
        ]

        for field in required_fields:
            self.assertIn(field, first_year, f"Missing required field: {field}")

        # Verify logical progression (each should be less than or equal to previous)
        gross = first_year['gross_income_total']
        after_tax = first_year['after_tax_income']
        after_medicare = first_year['after_medicare_income']
        remaining = first_year['remaining_income']

        self.assertLessEqual(after_tax, gross, "After-tax income should be <= gross income")
        self.assertLessEqual(after_medicare, after_tax, "After-Medicare income should be <= after-tax income")
        self.assertEqual(remaining, after_medicare, "Remaining income should equal after-Medicare income")

    def test_all_prd_fields_present(self):
        """Test that all fields specified in PRD section 6.1 are present"""
        # Create comprehensive test data
        ss = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="social_security",
            income_name="Social Security",
            monthly_amount=2000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=3000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # Demographics fields
        demographic_fields = ['year', 'primary_age']
        for field in demographic_fields:
            self.assertIn(field, first_year, f"Missing demographic field: {field}")

        # Income dictionaries
        self.assertIn('income_by_source', first_year, "Missing income_by_source dictionary")
        self.assertIn('asset_balances', first_year, "Missing asset_balances dictionary")
        self.assertIn('rmd_required', first_year, "Missing rmd_required dictionary")
        self.assertIn('rmd_total', first_year, "Missing rmd_total field")

        # Tax fields
        tax_fields = ['agi', 'magi', 'taxable_income', 'federal_tax', 'state_tax',
                      'marginal_rate', 'effective_rate']
        for field in tax_fields:
            self.assertIn(field, first_year, f"Missing tax field: {field}")

        # Medicare/IRMAA fields
        medicare_fields = ['irmaa_bracket_number', 'irmaa_threshold', 'part_b', 'part_d',
                           'irmaa_surcharge', 'total_medicare']
        for field in medicare_fields:
            self.assertIn(field, first_year, f"Missing Medicare field: {field}")

        # Net income fields
        net_income_fields = ['gross_income_total', 'after_tax_income',
                             'after_medicare_income', 'remaining_income']
        for field in net_income_fields:
            self.assertIn(field, first_year, f"Missing net income field: {field}")

    def test_backward_compatibility(self):
        """Test that legacy fields are still present for backward compatibility"""
        # Create income source
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=3000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # Check legacy fields still exist
        legacy_fields = [
            'asset_incomes',       # Legacy name for income_by_source
            'rmd_amount',          # Legacy name for rmd_total
            'net_income',          # Legacy net income calculation
            'remaining_income_after_taxes',  # Legacy field
            'remaining_ss'         # Legacy Social Security remainder
        ]

        for field in legacy_fields:
            self.assertIn(field, first_year, f"Missing legacy field: {field}")

        # Verify legacy fields match new fields where applicable
        self.assertEqual(first_year['asset_incomes'], first_year['income_by_source'],
                         "asset_incomes should match income_by_source")
        self.assertEqual(first_year['rmd_amount'], first_year['rmd_total'],
                         "rmd_amount should match rmd_total")


if __name__ == '__main__':
    unittest.main()