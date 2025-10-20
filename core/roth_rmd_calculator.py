"""
RMD (Required Minimum Distribution) calculation utilities for Roth conversion scenarios.

This module handles RMD calculations following IRS rules including
age-based requirements and life expectancy factors.
"""

import datetime
from decimal import Decimal
from .scenario_processor import RMD_TABLE


class RothRMDCalculator:
    """Handles RMD calculations for Roth conversion scenarios."""

    def __init__(self, client, spouse):
        """
        Initialize RMD calculator with client data.

        Args:
            client: dict - Primary client data
            spouse: dict - Spouse data (optional)
        """
        self.client = client
        self.spouse = spouse

    def get_rmd_start_age(self, birthdate):
        """
        Get the RMD start age based on current IRS rules and birth year.

        Args:
            birthdate: datetime.date or str - Birthdate

        Returns:
            int: RMD start age (72, 73, or 75)
        """
        birth_year = birthdate.year if hasattr(birthdate, 'year') else int(str(birthdate)[:4])

        if birth_year <= 1950:
            return 72  # Old rule (pre-SECURE 2.0) for those born 1950 or earlier
        elif birth_year <= 1951:
            return 73  # SECURE 2.0: Age 73 for those born 1951
        elif birth_year <= 1959:
            return 73  # SECURE 2.0: Age 73 for those born 1951-1959
        else:
            return 75  # Future rule (2033+) for those born 1960+

    def requires_rmd(self, asset):
        """
        Determine if an asset type requires RMD calculations.

        Args:
            asset: dict - Asset data with income_type field

        Returns:
            bool: True if asset requires RMD
        """
        income_type = asset.get("income_type", "")

        # Asset types that require RMDs
        rmd_asset_types = {
            "qualified", "401k", "traditional_ira", "sep_ira", "403b",
            "inherited traditional", "inherited traditional spouse",
            "inherited traditional non-spouse"
        }

        income_type_lower = income_type.lower()

        # Check if income type includes any RMD-required keywords
        return income_type in [
            "Qualified", "Traditional IRA", "401(k)", "SEP IRA", "403(b)",
            "Inherited Traditional", "Inherited Traditional Spouse",
            "Inherited Traditional Non-Spouse"
        ] or income_type_lower in rmd_asset_types

    def calculate_rmd_for_asset(self, asset, year, previous_year_balance, owner_age, debug_callback=None):
        """
        Calculate RMD for a single asset.

        Args:
            asset: dict - Asset data
            year: int - Current year
            previous_year_balance: Decimal/float - Balance at end of previous year
            owner_age: int - Age of the asset owner
            debug_callback: callable - Optional debug logging function

        Returns:
            Decimal: RMD amount
        """
        # Check if this asset type requires RMD
        if not self.requires_rmd(asset):
            return Decimal('0')

        # Get birthdate
        owner = asset.get("owned_by", "primary")
        if owner == "primary":
            birthdate = self.client.get('birthdate')
        else:
            birthdate = self.spouse.get('birthdate') if self.spouse else None

        if not birthdate:
            return Decimal('0')

        # Parse birthdate if it's a string
        if isinstance(birthdate, str):
            birthdate = datetime.datetime.strptime(birthdate, '%Y-%m-%d').date()

        # Get RMD start age
        rmd_start_age = self.get_rmd_start_age(birthdate)

        # Check if owner is old enough for RMD
        if owner_age < rmd_start_age:
            return Decimal('0')

        # Get life expectancy factor from IRS table
        life_expectancy_factor = RMD_TABLE.get(owner_age, None)
        if life_expectancy_factor is None:
            return Decimal('0')

        # Calculate RMD
        rmd_amount = Decimal(str(previous_year_balance)) / Decimal(str(life_expectancy_factor))

        if debug_callback:
            asset_name = asset.get('income_name', 'Unknown')
            debug_callback(f"Year {year} - Asset {asset_name}: Age {owner_age}, RMD = ${rmd_amount:,.2f}")

        return rmd_amount
