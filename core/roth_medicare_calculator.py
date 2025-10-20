"""
Medicare and IRMAA calculation utilities for Roth conversion scenarios.

This module handles Medicare Part B/D costs and IRMAA surcharges
based on MAGI with 2-year lookback.
"""

from decimal import Decimal
from .tax_csv_loader import get_tax_loader


class RothMedicareCalculator:
    """Handles Medicare and IRMAA calculations for Roth conversion scenarios."""

    def __init__(self, scenario):
        """
        Initialize Medicare calculator with scenario data.

        Args:
            scenario: dict - Scenario data containing tax_filing_status
        """
        self.scenario = scenario

    def _get_filing_status(self):
        """Get normalized filing status for Medicare calculations."""
        status_mapping = {
            'single': 'Single',
            'married filing jointly': 'Married Filing Jointly',
            'married filing separately': 'Married Filing Separately'
        }

        tax_status = self.scenario.get('tax_filing_status', 'single')
        normalized_status = (tax_status or '').strip().lower()
        return status_mapping.get(normalized_status, 'Single')

    def calculate_medicare_costs(self, magi, year=None, medical_inflation_rate=0.05):
        """
        Calculate Medicare costs using CSV-based rates and IRMAA thresholds with inflation.

        Args:
            magi: float/Decimal - Modified Adjusted Gross Income
            year: int - Year for inflation-adjusted costs (optional)
            medical_inflation_rate: float - Annual medical inflation rate (default 5%)

        Returns:
            tuple: (total_medicare_annual, irmaa_surcharge_annual)
                Both are annual costs (monthly rates * 12)
        """
        tax_loader = get_tax_loader()
        import datetime

        # Get base Medicare rates from CSV (these are MONTHLY rates for base year)
        medicare_rates = tax_loader.get_medicare_base_rates()
        base_part_b = medicare_rates.get('part_b', Decimal('185'))
        base_part_d = medicare_rates.get('part_d', Decimal('71'))

        # Inflate base Medicare costs year-over-year if year is provided
        if year:
            current_year = datetime.datetime.now().year
            years_from_now = year - current_year
            if years_from_now > 0:
                inflation_factor = (1 + Decimal(str(medical_inflation_rate))) ** years_from_now
                base_part_b = base_part_b * inflation_factor
                base_part_d = base_part_d * inflation_factor

        filing_status = self._get_filing_status()

        # Calculate IRMAA surcharges (monthly amounts) with inflation if year provided
        if year:
            part_b_surcharge, part_d_irmaa = tax_loader.calculate_irmaa_with_inflation(
                Decimal(magi), filing_status, year
            )
        else:
            # Fallback to non-inflated calculation
            part_b_surcharge, part_d_irmaa = tax_loader.calculate_irmaa(
                Decimal(magi), filing_status
            )

        # For married filing jointly, double the base rates and IRMAA surcharges
        if filing_status == "Married Filing Jointly":
            base_part_b *= 2
            base_part_d *= 2
            part_b_surcharge *= 2
            part_d_irmaa *= 2

        # Convert monthly costs to ANNUAL costs
        total_medicare_monthly = base_part_b + part_b_surcharge + base_part_d + part_d_irmaa
        irmaa_surcharge_monthly = part_b_surcharge + part_d_irmaa

        # Multiply by 12 to get annual amounts
        total_medicare_annual = total_medicare_monthly * 12
        irmaa_surcharge_annual = irmaa_surcharge_monthly * 12

        return float(total_medicare_annual), float(irmaa_surcharge_annual)

    def calculate_year_medicare(self, year, primary_age, magi, magi_history):
        """
        Calculate Medicare costs for a specific year with 2-year MAGI lookback.

        Args:
            year: int - Year to calculate Medicare for
            primary_age: int - Primary client age
            magi: float - Current year MAGI
            magi_history: dict - Dictionary of {year: magi} for lookback

        Returns:
            dict: Medicare calculations with keys:
                - medicare_base: float
                - part_b: float
                - part_d: float
                - irmaa_surcharge: float
                - irmaa_bracket_number: int
                - total_medicare: float
            Returns None if age < 65
        """
        if not primary_age or primary_age < 65:
            return None

        # IRMAA is based on MAGI from 2 years prior per IRS rules
        lookback_year = year - 2
        lookback_magi = magi_history.get(lookback_year, magi)

        total_medicare, irmaa_surcharge = self.calculate_medicare_costs(lookback_magi, year)
        medicare_base = total_medicare - irmaa_surcharge

        # Calculate Part B and Part D breakdown (72% Part B, 28% Part D approximation)
        part_b = medicare_base * 0.72
        part_d = medicare_base * 0.28

        # TODO: Calculate actual IRMAA bracket number from lookback_magi
        irmaa_bracket_number = 0

        return {
            'medicare_base': medicare_base,
            'part_b': part_b,
            'part_d': part_d,
            'irmaa_surcharge': irmaa_surcharge,
            'irmaa_bracket_number': irmaa_bracket_number,
            'total_medicare': total_medicare
        }
