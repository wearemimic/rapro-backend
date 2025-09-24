"""
Test Medicare & IRMAA Calculations
===================================
Tests for Medicare costs, IRMAA surcharges, Hold Harmless provisions,
and inflation adjustments.
Based on Phase V of Comprehensive Financial Summary PRD
"""

import unittest
from datetime import date, datetime
from decimal import Decimal
from django.test import TestCase
from core.models import Client, Scenario, IncomeSource
from core.scenario_processor import ScenarioProcessor
from core.tax_csv_loader import TaxCSVLoader


class TestMedicareIRMAACalculations(TestCase):
    """Test suite for Medicare and IRMAA calculations"""

    def setUp(self):
        """Set up test data"""
        # Create test client age 65 (Medicare eligible)
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
            name="Test Medicare Scenario",
            retirement_age=65,
            mortality_age=90,
            part_b_inflation_rate=Decimal('5.8'),  # Historical average
            part_d_inflation_rate=Decimal('4.0'),  # Historical average
            medicare_age=65  # Medicare starts at 65
        )

    def test_medicare_base_rates_loading(self):
        """Test that Medicare base rates load from CSV"""
        tax_loader = TaxCSVLoader(2025)
        rates = tax_loader.get_medicare_base_rates()

        # Check Part B base rate
        self.assertIn('part_b', rates, "Should have Part B rate")
        self.assertEqual(rates['part_b'], Decimal('185.00'), "Part B should be $185 for 2025")

        # Check Part D base rate
        self.assertIn('part_d', rates, "Should have Part D rate")
        self.assertEqual(rates['part_d'], Decimal('71.00'), "Part D should be $71 for 2025")

    def test_irmaa_threshold_loading(self):
        """Test that IRMAA thresholds load correctly from CSV"""
        tax_loader = TaxCSVLoader(2025)

        # Test single filer thresholds
        single_thresholds = tax_loader.get_irmaa_thresholds("Single")
        self.assertEqual(len(single_thresholds), 6, "Should have 6 IRMAA brackets for single")

        # First bracket should be no surcharge
        first = single_thresholds[0]
        self.assertEqual(first['magi_threshold'], Decimal('0'), "First bracket starts at $0")
        self.assertEqual(first['part_b_surcharge'], Decimal('0'), "First bracket has no surcharge")

        # Second bracket should start at $106,000 for single
        second = single_thresholds[1]
        self.assertEqual(second['magi_threshold'], Decimal('106000'), "Second bracket at $106,000")
        self.assertEqual(second['part_b_surcharge'], Decimal('71.90'), "Second bracket Part B surcharge")

    def test_irmaa_calculation_no_surcharge(self):
        """Test IRMAA calculation for income below threshold"""
        tax_loader = TaxCSVLoader(2025)

        # MAGI below first threshold
        magi = Decimal('80000')
        part_b_surcharge, part_d_surcharge = tax_loader.calculate_irmaa(magi, "Single")

        self.assertEqual(part_b_surcharge, Decimal('0'), "No Part B surcharge below threshold")
        self.assertEqual(part_d_surcharge, Decimal('0'), "No Part D surcharge below threshold")

    def test_irmaa_calculation_with_surcharge(self):
        """Test IRMAA calculation for higher income"""
        tax_loader = TaxCSVLoader(2025)

        # MAGI in second bracket ($106,000 - $133,000)
        magi = Decimal('120000')
        part_b_surcharge, part_d_surcharge = tax_loader.calculate_irmaa(magi, "Single")

        self.assertEqual(part_b_surcharge, Decimal('71.90'), "Part B surcharge for second bracket")
        self.assertEqual(part_d_surcharge, Decimal('13.70'), "Part D surcharge for second bracket")

    def test_irmaa_calculation_highest_bracket(self):
        """Test IRMAA calculation for highest income bracket"""
        tax_loader = TaxCSVLoader(2025)

        # MAGI above $500,000
        magi = Decimal('600000')
        part_b_surcharge, part_d_surcharge = tax_loader.calculate_irmaa(magi, "Single")

        self.assertEqual(part_b_surcharge, Decimal('431.00'), "Highest Part B surcharge")
        self.assertEqual(part_d_surcharge, Decimal('85.80'), "Highest Part D surcharge")

    def test_irmaa_inflation_adjustment(self):
        """Test IRMAA threshold inflation adjustments"""
        tax_loader = TaxCSVLoader(2025)

        # Get base thresholds
        base_thresholds = tax_loader.get_irmaa_thresholds("Single")

        # Get inflated thresholds for 2030 (5 years in future)
        inflated_thresholds = tax_loader.get_inflated_irmaa_thresholds("Single", 2030)

        # First non-zero threshold should be inflated
        base_threshold = base_thresholds[1]['magi_threshold']  # $106,000
        inflated_threshold = inflated_thresholds[1]['magi_threshold']

        # With 1% annual inflation for 5 years: 106,000 * (1.01)^5 ≈ 111,531
        expected = base_threshold * (Decimal('1.01') ** 5)
        self.assertAlmostEqual(float(inflated_threshold), float(expected), places=0,
                               msg="IRMAA thresholds should inflate at configured rate")

    def test_hold_harmless_protection(self):
        """Test Hold Harmless provision protects Social Security"""
        # Create Social Security income
        ss = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="social_security",
            income_name="Social Security",
            monthly_amount=2000,  # $24,000 annual
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90,
            cola=Decimal('0.03')
        )

        # Create modest income to stay in first IRMAA bracket (eligible for Hold Harmless)
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="Small IRA",
            current_asset_balance=100000,
            monthly_amount=500,  # $6,000 annual
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Find years where Hold Harmless might apply (when Medicare costs increase)
        hold_harmless_years = [r for r in results if r.get('hold_harmless_protected', False)]

        if hold_harmless_years:
            # If Hold Harmless is applied, verify it works correctly
            protected_year = hold_harmless_years[0]
            self.assertGreater(protected_year['hold_harmless_amount'], 0,
                               "Hold Harmless should reduce Medicare deduction")
            self.assertLess(protected_year['effective_medicare'], protected_year['total_medicare'],
                            "Effective Medicare should be less than total when protected")

    def test_medicare_costs_in_scenario(self):
        """Test full Medicare cost calculation in a scenario"""
        # Create income source with high enough income for IRMAA
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=2000000,
            monthly_amount=10000,  # $120,000 annual (triggers IRMAA)
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Check first year results (age 65)
        first_year = results[0]

        # Verify Medicare costs are calculated
        self.assertIn('medicare_base', first_year, "Should have Medicare base cost")
        self.assertIn('part_b', first_year, "Should have Part B cost")
        self.assertIn('part_d', first_year, "Should have Part D cost")
        self.assertIn('irmaa_surcharge', first_year, "Should have IRMAA surcharge")
        self.assertIn('irmaa_bracket_number', first_year, "Should have IRMAA bracket number")

        # With $120,000 income, should be in IRMAA bracket 2 (for single)
        self.assertGreater(first_year['irmaa_bracket_number'], 0,
                           "Should be in an IRMAA bracket with $120k income")
        self.assertGreater(first_year['irmaa_surcharge'], 0,
                           "Should have IRMAA surcharge with $120k income")

    def test_medicare_inflation_over_time(self):
        """Test that Medicare costs inflate over time"""
        # Create income source
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=1000000,
            monthly_amount=5000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Compare Medicare costs between first and fifth year
        if len(results) >= 5:
            year_1_medicare = results[0]['total_medicare']
            year_5_medicare = results[4]['total_medicare']

            # Medicare should inflate over time
            self.assertGreater(year_5_medicare, year_1_medicare,
                               "Medicare costs should increase with inflation")

    def test_married_filing_jointly_irmaa(self):
        """Test IRMAA calculations for married filing jointly"""
        # Update client to married filing jointly
        self.client.tax_status = "Married Filing Jointly"
        self.client.save()

        # Create spousal client
        spouse = Client.objects.create(
            advisor_id=1,
            first_name="Test",
            last_name="Spouse",
            email="spouse@example.com",
            birthdate=date(1959, 6, 1),  # Also 65 in 2024
            gender="Female",
            tax_status="Married Filing Jointly"
        )

        # Update scenario
        self.scenario.client = self.client
        self.scenario.save()

        # Create combined income source
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="Joint 401k",
            current_asset_balance=3000000,
            monthly_amount=15000,  # $180,000 annual
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        tax_loader = TaxCSVLoader(2025)

        # Test married thresholds (should be roughly double single thresholds)
        married_thresholds = tax_loader.get_irmaa_thresholds("Married Filing Jointly")
        single_thresholds = tax_loader.get_irmaa_thresholds("Single")

        # Second bracket threshold comparison
        married_second = married_thresholds[1]['magi_threshold']  # $212,000
        single_second = single_thresholds[1]['magi_threshold']    # $106,000

        self.assertEqual(married_second, single_second * 2,
                         "Married IRMAA threshold should be double single threshold")

    def test_medicare_part_d_surcharges(self):
        """Test that Part D surcharges are calculated correctly"""
        tax_loader = TaxCSVLoader(2025)

        # Test various income levels
        test_cases = [
            (Decimal('50000'), Decimal('0')),      # No surcharge
            (Decimal('110000'), Decimal('13.70')),  # First bracket
            (Decimal('150000'), Decimal('35.30')),  # Second bracket
            (Decimal('180000'), Decimal('57.00')),  # Third bracket
        ]

        for magi, expected_surcharge in test_cases:
            _, part_d_surcharge = tax_loader.calculate_irmaa(magi, "Single")
            self.assertEqual(part_d_surcharge, expected_surcharge,
                             f"Part D surcharge for MAGI ${magi} should be ${expected_surcharge}")

    def test_two_year_lookback_rule(self):
        """Test that IRMAA uses MAGI from 2 years prior"""
        # Create varying income over years
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=2000000,
            monthly_amount=5000,  # Start with $60k/year
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=70  # Short period to test lookback
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Check that lookback_magi is included in results
        for i, result in enumerate(results):
            self.assertIn('lookback_magi', result, "Results should include lookback_magi")

            # For years 3 and later, lookback_magi should match MAGI from 2 years prior
            if i >= 2:
                two_years_ago = results[i - 2]
                self.assertEqual(
                    result['lookback_magi'],
                    two_years_ago['magi'],
                    f"Year {i}: Lookback MAGI should match MAGI from 2 years prior"
                )

    def test_irmaa_bracket_determination(self):
        """Test correct IRMAA bracket determination in scenario processor"""
        # Create high income source
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="Large 401k",
            current_asset_balance=5000000,
            monthly_amount=20000,  # $240,000 annual (bracket 4)
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # With $240,000 income, should be in bracket 4 for single filer
        # (above $200,000 but below $500,000)
        self.assertEqual(first_year['irmaa_bracket_number'], 4,
                         "Should be in IRMAA bracket 4 with $240k income")

        # Should have the corresponding threshold
        self.assertIsNotNone(first_year.get('irmaa_bracket_threshold'),
                             "Should have IRMAA bracket threshold")


if __name__ == '__main__':
    unittest.main()