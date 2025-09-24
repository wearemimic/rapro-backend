"""
Test Tax Calculations
=====================
Tests for federal and state tax calculations, Social Security taxation,
AGI/MAGI calculations, and marginal/effective rates.
Based on Phase IV of Comprehensive Financial Summary PRD
"""

import unittest
from datetime import date, datetime
from decimal import Decimal
from django.test import TestCase
from core.models import Client, Scenario, IncomeSource
from core.scenario_processor import ScenarioProcessor, calculate_taxable_social_security
from core.tax_csv_loader import TaxCSVLoader


class TestTaxCalculations(TestCase):
    """Test suite for tax calculations following IRS rules"""

    def setUp(self):
        """Set up test data"""
        # Create test client
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
            name="Test Tax Scenario",
            retirement_age=65,
            mortality_age=90
        )

    def test_social_security_taxation_single(self):
        """Test Social Security taxation for single filer"""
        # Test case 1: Below base threshold ($25,000 for single)
        ss_benefits = Decimal('20000')
        agi_excl_ss = Decimal('15000')
        tax_exempt_interest = Decimal('0')

        taxable_ss = calculate_taxable_social_security(
            ss_benefits, agi_excl_ss, tax_exempt_interest, "Single"
        )

        # Provisional income = $15,000 + $10,000 = $25,000 (exactly at threshold)
        self.assertEqual(taxable_ss, Decimal('0'), "SS should not be taxable at base threshold")

        # Test case 2: Between base and additional thresholds ($25,000 - $34,000)
        ss_benefits = Decimal('24000')
        agi_excl_ss = Decimal('20000')

        taxable_ss = calculate_taxable_social_security(
            ss_benefits, agi_excl_ss, tax_exempt_interest, "Single"
        )

        # Provisional income = $20,000 + $12,000 = $32,000
        # Taxable = 50% of ($32,000 - $25,000) = 50% of $7,000 = $3,500
        self.assertEqual(taxable_ss, Decimal('3500'), "SS taxation should be 50% of excess over base")

        # Test case 3: Above additional threshold ($34,000)
        ss_benefits = Decimal('40000')
        agi_excl_ss = Decimal('30000')

        taxable_ss = calculate_taxable_social_security(
            ss_benefits, agi_excl_ss, tax_exempt_interest, "Single"
        )

        # Provisional income = $30,000 + $20,000 = $50,000
        # First tier: 50% of ($34,000 - $25,000) = $4,500
        # Second tier: 85% of ($50,000 - $34,000) = $13,600
        # Total: $4,500 + $13,600 = $18,100
        # But max is 85% of benefits = $34,000
        self.assertEqual(taxable_ss, Decimal('18100'), "SS taxation should follow two-tier formula")

    def test_social_security_taxation_married(self):
        """Test Social Security taxation for married filing jointly"""
        # Test case: Between base and additional thresholds ($32,000 - $44,000)
        ss_benefits = Decimal('36000')
        agi_excl_ss = Decimal('25000')
        tax_exempt_interest = Decimal('0')

        taxable_ss = calculate_taxable_social_security(
            ss_benefits, agi_excl_ss, tax_exempt_interest, "Married Filing Jointly"
        )

        # Provisional income = $25,000 + $18,000 = $43,000
        # Taxable = 50% of ($43,000 - $32,000) = 50% of $11,000 = $5,500
        self.assertEqual(taxable_ss, Decimal('5500'), "SS taxation for married should use correct thresholds")

    def test_federal_tax_brackets(self):
        """Test federal tax calculation using brackets from CSV"""
        tax_loader = TaxCSVLoader(2025)

        # Test single filer with $50,000 taxable income
        tax, bracket_str = tax_loader.calculate_federal_tax(Decimal('50000'), "Single")

        # For 2025 single filer:
        # 10% on first $11,600 = $1,160
        # 12% on $11,600 to $47,150 = $4,266
        # 22% on $47,150 to $50,000 = $627
        # Total = $1,160 + $4,266 + $627 = $6,053

        self.assertAlmostEqual(float(tax), 6053, delta=100,
                               msg="Federal tax calculation should match brackets")
        self.assertEqual(bracket_str, "22%", "Should be in 22% bracket")

    def test_standard_deduction(self):
        """Test standard deduction amounts from CSV"""
        tax_loader = TaxCSVLoader(2025)

        # Test single standard deduction
        single_deduction = tax_loader.get_standard_deduction("Single")
        self.assertGreater(single_deduction, Decimal('10000'), "Single standard deduction should be reasonable")

        # Test married filing jointly (should be roughly double)
        married_deduction = tax_loader.get_standard_deduction("Married Filing Jointly")
        self.assertGreater(married_deduction, single_deduction, "Married deduction should be higher than single")

    def test_state_tax_calculations(self):
        """Test state tax calculations with different state rules"""
        tax_loader = TaxCSVLoader(2025)

        # Test Florida (no state tax)
        fl_info = tax_loader.get_state_tax_info("FL")
        self.assertEqual(fl_info['income_tax_rate'], Decimal('0'), "Florida should have no state tax")

        # Test California (high tax, SS not taxed)
        ca_info = tax_loader.get_state_tax_info("CA")
        self.assertGreater(ca_info['income_tax_rate'], Decimal('0'), "California should have state tax")
        self.assertFalse(ca_info['ss_taxed'], "California should not tax SS")

    def test_marginal_and_effective_rates(self):
        """Test marginal and effective tax rate calculations"""
        # Create income source
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="social_security",
            income_name="Social Security",
            monthly_amount=2000,  # $24,000 annual
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90,
            cola=Decimal('0.03')
        )

        # Add a qualified account for additional income
        qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=500000,
            monthly_amount=3000,  # $36,000 annual
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Check first year results
        first_year = results[0]

        # Verify marginal rate is set
        self.assertIn('marginal_rate', first_year, "Marginal rate should be in results")
        self.assertGreater(first_year['marginal_rate'], 0, "Marginal rate should be positive")

        # Verify effective rate is set
        self.assertIn('effective_rate', first_year, "Effective rate should be in results")
        self.assertGreater(first_year['effective_rate'], 0, "Effective rate should be positive")

        # Effective rate should be less than marginal rate
        self.assertLess(first_year['effective_rate'], first_year['marginal_rate'],
                        "Effective rate should be less than marginal rate")

    def test_agi_calculation(self):
        """Test AGI calculation includes correct components"""
        # Create multiple income sources
        ss_asset = IncomeSource.objects.create(
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
            current_asset_balance=300000,
            monthly_amount=2000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # AGI should include taxable SS + other income
        # Verify AGI is calculated
        self.assertIn('agi', first_year, "AGI should be in results")
        self.assertGreater(first_year['agi'], 0, "AGI should be positive")

        # AGI should be less than total income (due to SS taxation rules)
        total_income = first_year['gross_income'] + first_year['ss_income']
        self.assertLess(first_year['agi'], total_income,
                        "AGI should be less than total income due to SS exclusion")

    def test_magi_calculation(self):
        """Test MAGI calculation for IRMAA determination"""
        # Create income sources
        asset = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="401k",
            current_asset_balance=1000000,
            monthly_amount=5000,  # $60,000 annual
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        first_year = results[0]

        # MAGI should be calculated
        self.assertIn('magi', first_year, "MAGI should be in results")
        self.assertGreater(first_year['magi'], 0, "MAGI should be positive")

        # MAGI should be at least as much as AGI
        self.assertGreaterEqual(first_year['magi'], first_year['agi'],
                                "MAGI should be at least AGI")

    def test_irmaa_thresholds(self):
        """Test IRMAA threshold calculations"""
        tax_loader = TaxCSVLoader(2025)

        # Test single filer IRMAA thresholds
        thresholds = tax_loader.get_irmaa_thresholds("Single")
        self.assertGreater(len(thresholds), 0, "Should have IRMAA thresholds")

        # First threshold should be lowest
        first_threshold = thresholds[0]['magi_threshold']
        self.assertGreater(first_threshold, Decimal('0'), "First IRMAA threshold should be positive")

        # Thresholds should increase
        for i in range(1, len(thresholds)):
            self.assertGreater(thresholds[i]['magi_threshold'], thresholds[i-1]['magi_threshold'],
                               "IRMAA thresholds should increase")

    def test_tax_calculation_with_roth_conversion(self):
        """Test that Roth conversions are included in taxable income"""
        # Create qualified account
        qualified = IncomeSource.objects.create(
            scenario=self.scenario,
            owned_by="primary",
            income_type="Qualified",
            income_name="Traditional IRA",
            current_asset_balance=200000,
            monthly_amount=1000,
            age_to_begin_withdrawal=65,
            age_to_end_withdrawal=90
        )

        # Set Roth conversion parameters
        self.scenario.roth_conversion_start_year = 2024
        self.scenario.roth_conversion_duration = 5
        self.scenario.roth_conversion_annual_amount = 20000
        self.scenario.save()

        processor = ScenarioProcessor(self.scenario.id, debug=False)
        results = processor.calculate()

        # Find a year with Roth conversion
        conversion_year = None
        for result in results:
            if result.get('roth_conversion', 0) > 0:
                conversion_year = result
                break

        self.assertIsNotNone(conversion_year, "Should have at least one year with Roth conversion")

        # Taxable income should include the Roth conversion
        self.assertGreater(conversion_year['federal_tax'], 0,
                           "Roth conversion should result in federal tax")


if __name__ == '__main__':
    unittest.main()