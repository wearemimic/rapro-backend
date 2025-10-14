"""
Inheritance Tax Calculator Service

This module provides a reusable service for calculating federal estate/inheritance tax
on estates, specifically for investment accounts that are subject to estate taxation.

Only the following investment account types are included in calculations:
- Taxable: Qualified, Non-Qualified, Inherited Traditional (Spouse/Non-Spouse)
- Non-Taxable: Roth, Inherited Roth (Spouse/Non-Spouse)

All other income types (Social Security, Pensions, Wages, etc.) are excluded as they
are income streams, not assets.
"""

from decimal import Decimal
from typing import Dict, Any, Optional


class InheritanceTaxCalculator:
    """
    Reusable service for calculating inheritance tax on estates.
    Only calculates on investment account assets per ScenarioCreate.vue definitions.
    """

    # Define which investment types are taxable vs non-taxable
    TAXABLE_INVESTMENT_TYPES = {
        'Qualified',
        'Non-Qualified',
        'Inherited Traditional Spouse',
        'Inherited Traditional Non-Spouse'
    }

    NON_TAXABLE_INVESTMENT_TYPES = {
        'Roth',
        'Inherited Roth Spouse',
        'Inherited Roth Non-Spouse'
    }

    def __init__(self, tax_loader):
        """
        Initialize the calculator with a tax loader.

        Args:
            tax_loader: TaxCSVLoader instance for accessing estate tax brackets
        """
        self.tax_loader = tax_loader

    def get_taxable_assets(self, year_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and categorize assets from year projection data.

        Args:
            year_data: Dictionary containing year-by-year projection data with asset balances

        Returns:
            Dictionary with categorized assets:
            {
                'taxable': {asset_type: balance, ...},
                'non_taxable': {asset_type: balance, ...},
                'total_taxable': Decimal,
                'total_non_taxable': Decimal,
                'total_estate': Decimal
            }
        """
        taxable_assets = {}
        non_taxable_assets = {}
        processed_keys = set()  # Track processed keys to avoid duplicates

        # DEBUG: Log all balance keys found
        balance_keys = [k for k in year_data.keys() if k.endswith('_balance')]
        print(f"\n{'='*80}")
        print(f"INHERITANCE TAX CALCULATOR: Found {len(balance_keys)} balance keys in final year data:")
        for key in sorted(balance_keys):
            print(f"  - {key}: ${year_data[key]:,.2f}" if isinstance(year_data[key], (int, float, Decimal)) else f"  - {key}: {year_data[key]}")
        print(f"{'='*80}\n")

        # Scan through year_data looking for investment account balances
        for key, value in year_data.items():
            # Look for balance fields (e.g., 'qualified_balance', 'roth_balance', etc.)
            if not key.endswith('_balance'):
                continue

            # Skip if not a numeric value
            if not isinstance(value, (int, float, Decimal)):
                continue

            balance = Decimal(str(value))

            # Skip zero or negative balances
            if balance <= 0:
                continue

            # Determine the investment type from the key
            # Keys are like: 'qualified_balance', 'non_qualified_balance', 'roth_balance'
            key_lower = key.lower()

            # Skip if we've already processed this key (in either case variation)
            if key_lower in processed_keys:
                print(f"SKIPPING DUPLICATE: {key} (already processed as {key_lower})")
                continue
            processed_keys.add(key_lower)

            # Check against our defined investment types
            if 'qualified_balance' in key_lower and 'non_qualified' not in key_lower:
                # Qualified account (taxable)
                taxable_assets['Qualified'] = taxable_assets.get('Qualified', Decimal('0')) + balance
            elif 'non_qualified_balance' in key_lower or 'nonqualified_balance' in key_lower:
                # Non-Qualified brokerage (taxable)
                taxable_assets['Non-Qualified'] = taxable_assets.get('Non-Qualified', Decimal('0')) + balance
            elif 'inherited_traditional_spouse_balance' in key_lower:
                # Inherited Traditional Spouse (taxable)
                taxable_assets['Inherited Traditional Spouse'] = taxable_assets.get('Inherited Traditional Spouse', Decimal('0')) + balance
            elif 'inherited_traditional_non_spouse_balance' in key_lower or 'inherited_traditional_nonspouse_balance' in key_lower:
                # Inherited Traditional Non-Spouse (taxable)
                taxable_assets['Inherited Traditional Non-Spouse'] = taxable_assets.get('Inherited Traditional Non-Spouse', Decimal('0')) + balance
            elif ('roth_balance' in key_lower or 'roth_ira_balance' in key_lower) and 'inherited' not in key_lower:
                # Roth account (non-taxable)
                non_taxable_assets['Roth'] = non_taxable_assets.get('Roth', Decimal('0')) + balance
            elif 'inherited_roth_spouse_balance' in key_lower:
                # Inherited Roth Spouse (non-taxable)
                non_taxable_assets['Inherited Roth Spouse'] = non_taxable_assets.get('Inherited Roth Spouse', Decimal('0')) + balance
            elif 'inherited_roth_non_spouse_balance' in key_lower or 'inherited_roth_nonspouse_balance' in key_lower:
                # Inherited Roth Non-Spouse (non-taxable)
                non_taxable_assets['Inherited Roth Non-Spouse'] = non_taxable_assets.get('Inherited Roth Non-Spouse', Decimal('0')) + balance

        # Calculate totals
        total_taxable = sum(taxable_assets.values(), Decimal('0'))
        total_non_taxable = sum(non_taxable_assets.values(), Decimal('0'))
        total_estate = total_taxable + total_non_taxable

        return {
            'taxable': taxable_assets,
            'non_taxable': non_taxable_assets,
            'total_taxable': total_taxable,
            'total_non_taxable': total_non_taxable,
            'total_estate': total_estate
        }

    def calculate_inheritance_tax(self, total_taxable_estate: Decimal) -> Decimal:
        """
        Calculate federal estate tax using CSV-based brackets.

        Args:
            total_taxable_estate: Total value of taxable estate (Decimal)

        Returns:
            Decimal: Estate tax owed
        """
        if total_taxable_estate <= 0:
            return Decimal('0')

        return self.tax_loader.calculate_estate_tax(total_taxable_estate)

    def generate_inheritance_report(
        self,
        year_data: Dict[str, Any],
        include_breakdown: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete inheritance tax report.

        Args:
            year_data: Dictionary containing year projection data with asset balances
            include_breakdown: Whether to include detailed asset breakdown

        Returns:
            Dictionary with complete inheritance tax analysis:
            {
                'estate_tax': Decimal - total estate tax owed,
                'total_taxable_estate': Decimal - sum of taxable assets,
                'total_non_taxable_estate': Decimal - sum of non-taxable assets,
                'total_estate_value': Decimal - total estate value,
                'net_to_heirs': Decimal - estate value after taxes,
                'assets_breakdown': {  # if include_breakdown=True
                    'taxable_assets': {asset_type: balance, ...},
                    'non_taxable_assets': {asset_type: balance, ...}
                }
            }
        """
        # Get asset categorization
        assets = self.get_taxable_assets(year_data)

        # Calculate estate tax on taxable portion only
        estate_tax = self.calculate_inheritance_tax(assets['total_taxable'])

        # Calculate net to heirs (total estate minus estate tax)
        net_to_heirs = assets['total_estate'] - estate_tax

        report = {
            'estate_tax': estate_tax,
            'total_taxable_estate': assets['total_taxable'],
            'total_non_taxable_estate': assets['total_non_taxable'],
            'total_estate_value': assets['total_estate'],
            'net_to_heirs': net_to_heirs
        }

        if include_breakdown:
            report['assets_breakdown'] = {
                'taxable_assets': assets['taxable'],
                'non_taxable_assets': assets['non_taxable']
            }

        return report

    @staticmethod
    def calculate_inheritance_tax_savings(
        baseline_report: Dict[str, Any],
        optimized_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate the savings from estate tax optimization (e.g., Roth conversion).

        Args:
            baseline_report: Report from generate_inheritance_report() for baseline scenario
            optimized_report: Report from generate_inheritance_report() for optimized scenario

        Returns:
            Dictionary with savings analysis:
            {
                'estate_tax_savings': Decimal - reduction in estate tax,
                'taxable_estate_reduction': Decimal - reduction in taxable estate,
                'net_to_heirs_increase': Decimal - increase in net to heirs,
                'estate_tax_reduction_pct': float - percentage reduction in estate tax
            }
        """
        baseline_tax = baseline_report['estate_tax']
        optimized_tax = optimized_report['estate_tax']

        estate_tax_savings = baseline_tax - optimized_tax
        taxable_estate_reduction = baseline_report['total_taxable_estate'] - optimized_report['total_taxable_estate']
        net_to_heirs_increase = optimized_report['net_to_heirs'] - baseline_report['net_to_heirs']

        # Calculate percentage reduction
        estate_tax_reduction_pct = 0.0
        if baseline_tax > 0:
            estate_tax_reduction_pct = float((estate_tax_savings / baseline_tax) * 100)

        return {
            'estate_tax_savings': estate_tax_savings,
            'taxable_estate_reduction': taxable_estate_reduction,
            'net_to_heirs_increase': net_to_heirs_increase,
            'estate_tax_reduction_pct': estate_tax_reduction_pct
        }
