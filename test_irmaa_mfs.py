#!/usr/bin/env python
"""Test IRMAA calculation for Married Filing Separately status."""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.insert(0, '/Users/marka/Documents/git/retirementadvisorpro/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.tax_csv_loader import get_tax_loader

def test_mfs_irmaa():
    """Test IRMAA surcharge calculation for MFS filing status."""
    tax_loader = get_tax_loader()

    # Test cases for MFS at different income levels
    test_cases = [
        (0, "Base surcharge (MAGI $0)"),
        (50000, "Base surcharge (MAGI $50k)"),
        (105999, "Just below first threshold"),
        (106000, "At first threshold"),
        (200000, "Middle income"),
        (394000, "At highest threshold"),
        (500000, "Above highest threshold")
    ]

    print("Testing IRMAA calculations for Married Filing Separately")
    print("=" * 70)

    for magi, description in test_cases:
        # Get surcharges for 2026 (current year + 1 for testing)
        part_b_surcharge, part_d_surcharge = tax_loader.calculate_irmaa_with_inflation(
            Decimal(magi),
            "Married Filing Separately",
            2026
        )

        # Annual amounts
        part_b_annual = part_b_surcharge * 12
        part_d_annual = part_d_surcharge * 12
        total_annual = part_b_annual + part_d_annual

        print(f"\n{description}:")
        print(f"  MAGI: ${magi:,}")
        print(f"  Part B Surcharge: ${part_b_surcharge:.2f}/month = ${part_b_annual:.2f}/year")
        print(f"  Part D Surcharge: ${part_d_surcharge:.2f}/month = ${part_d_annual:.2f}/year")
        print(f"  Total IRMAA Surcharge: ${total_annual:.2f}/year")

    # Special test: Verify the expected $2,662.80 annual surcharge at $0 MAGI
    print("\n" + "=" * 70)
    print("VERIFICATION: Expected surcharge at $0 MAGI for MFS")
    part_b_surcharge_base, part_d_surcharge_base = tax_loader.calculate_irmaa_with_inflation(
        Decimal(0),
        "Married Filing Separately",
        2026
    )
    expected_monthly = Decimal('221.90')  # From CSV
    expected_annual = expected_monthly * 12

    print(f"Expected monthly Part B surcharge: ${expected_monthly:.2f}")
    print(f"Actual monthly Part B surcharge: ${part_b_surcharge_base:.2f}")
    print(f"Expected annual Part B surcharge: ${expected_annual:.2f}")
    print(f"Actual annual Part B surcharge: ${part_b_surcharge_base * 12:.2f}")

    if abs(part_b_surcharge_base - expected_monthly) < Decimal('1'):
        print("✓ Base surcharge calculation is CORRECT")
    else:
        print("✗ Base surcharge calculation is INCORRECT")

if __name__ == "__main__":
    test_mfs_irmaa()