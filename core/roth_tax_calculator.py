"""
Tax calculation utilities for Roth conversion scenarios.

This module handles all tax-related calculations including federal tax,
state tax, standard deductions, and tax brackets.
"""

from decimal import Decimal
from .tax_csv_loader import get_tax_loader


class RothTaxCalculator:
    """Handles all tax calculations for Roth conversion scenarios."""

    def __init__(self, scenario):
        """
        Initialize tax calculator with scenario data.

        Args:
            scenario: dict - Scenario data containing tax_filing_status and primary_state
        """
        self.scenario = scenario

    def _get_filing_status(self):
        """Get normalized filing status for tax calculations."""
        status_mapping = {
            'single': 'Single',
            'married filing jointly': 'Married Filing Jointly',
            'married filing separately': 'Married Filing Separately',
            'head of household': 'Head of Household',
            'qualifying widow(er)': 'Qualifying Widow(er)'
        }

        tax_status = self.scenario.get('tax_filing_status', 'single')
        normalized_status = (tax_status or '').strip().lower()
        return status_mapping.get(normalized_status, 'Single')

    def calculate_federal_tax_and_bracket(self, taxable_income):
        """
        Calculate federal tax using CSV-based tax bracket data.

        Args:
            taxable_income: Decimal/float - Taxable income amount

        Returns:
            tuple: (tax_amount, bracket_string)
        """
        tax_loader = get_tax_loader()
        filing_status = self._get_filing_status()
        tax, bracket_str = tax_loader.calculate_federal_tax(Decimal(taxable_income), filing_status)
        return tax, bracket_str

    def get_standard_deduction(self):
        """
        Get standard deduction for the tax year.

        Returns:
            Decimal: Standard deduction amount
        """
        tax_loader = get_tax_loader()
        filing_status = self._get_filing_status()
        return tax_loader.get_standard_deduction(filing_status)

    def calculate_state_tax(self, agi, taxable_ss=0):
        """
        Calculate state tax based on scenario's primary state.

        Args:
            agi: float/Decimal - Adjusted Gross Income
            taxable_ss: float/Decimal - Taxable Social Security amount

        Returns:
            float: State tax amount
        """
        tax_loader = get_tax_loader()
        state_tax = Decimal('0')

        primary_state = self.scenario.get('primary_state')
        if primary_state:
            state_info = tax_loader.get_state_tax_info(primary_state)

            # Check if retirement income is exempt
            retirement_exempt = state_info.get('retirement_income_exempt', 'false')
            if retirement_exempt != 'true':
                state_tax_rate = Decimal(str(state_info.get('income_tax_rate', 0)))

                # Start with AGI as the base for state taxation
                state_taxable_income = Decimal(str(agi))

                # Some states don't tax Social Security
                ss_taxed = state_info.get('ss_taxed', 'false')
                if ss_taxed == 'false' or ss_taxed is False:
                    state_taxable_income = Decimal(str(agi)) - Decimal(str(taxable_ss))

                # Apply state tax rate
                state_tax = max(Decimal('0'), state_taxable_income * state_tax_rate)

        return float(state_tax)

    def calculate_year_taxes(self, year, gross_income, conversion_amount, taxable_ss=0):
        """
        Calculate all taxes for a given year with conversion.

        Args:
            year: int - Year to calculate taxes for
            gross_income: Decimal/float - Gross income for the year
            conversion_amount: Decimal/float - Roth conversion amount
            taxable_ss: Decimal/float - Taxable Social Security amount

        Returns:
            dict: Tax calculations with keys:
                - regular_income_tax: float
                - conversion_tax: float
                - federal_tax: float
                - state_tax: float
                - tax_bracket: str
                - marginal_rate: float
                - effective_rate: float
                - taxable_income: float
                - agi: float
                - magi: float
        """
        standard_deduction = self.get_standard_deduction()

        # Calculate AGI and MAGI
        agi = float(gross_income) + float(taxable_ss) + float(conversion_amount)
        magi = agi

        # Calculate regular income tax (without conversion)
        agi_without_conversion = float(gross_income) + float(taxable_ss)
        regular_taxable_income = max(0, agi_without_conversion - float(standard_deduction))
        regular_income_tax, _ = self.calculate_federal_tax_and_bracket(regular_taxable_income)

        # Calculate total federal tax (with conversion)
        total_taxable_income = max(0, agi - float(standard_deduction))
        federal_tax, tax_bracket = self.calculate_federal_tax_and_bracket(total_taxable_income)

        # Conversion tax is the incremental tax
        conversion_tax = float(federal_tax) - float(regular_income_tax)

        # Calculate state tax
        state_tax = self.calculate_state_tax(agi, taxable_ss)

        # Calculate effective rate
        effective_rate = (float(federal_tax) / agi * 100) if agi > 0 else 0

        # Extract marginal rate from bracket
        marginal_rate = 0
        if tax_bracket and '%' in tax_bracket:
            marginal_rate = float(tax_bracket.split('%')[0])

        return {
            'regular_income_tax': float(regular_income_tax),
            'conversion_tax': conversion_tax,
            'federal_tax': float(federal_tax),
            'state_tax': state_tax,
            'tax_bracket': tax_bracket,
            'marginal_rate': marginal_rate,
            'effective_rate': effective_rate,
            'taxable_income': total_taxable_income,
            'agi': agi,
            'magi': magi
        }
