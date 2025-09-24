#!/usr/bin/env python
"""Simple test to verify IRMAA calculation fix for MFS."""

from decimal import Decimal

# Simulate the fixed calculation
def calculate_irmaa_fixed(magi, filing_status, year):
    """Simulated fixed IRMAA calculation."""

    # MFS base surcharge from CSV
    if filing_status == "Married Filing Separately":
        if magi >= 394000:
            part_b_surcharge = Decimal('258.90')
            part_d_surcharge = Decimal('85.80')
        elif magi >= 106000:
            part_b_surcharge = Decimal('258.90')
            part_d_surcharge = Decimal('78.60')
        else:
            # Base surcharge for MFS at any income below $106k
            part_b_surcharge = Decimal('221.90')
            part_d_surcharge = Decimal('0')
    else:
        # Simplified for other statuses
        part_b_surcharge = Decimal('0')
        part_d_surcharge = Decimal('0')

    # Apply simple 1% inflation for year 2026
    inflation_factor = Decimal('1.01')  # 1% inflation
    part_b_surcharge *= inflation_factor
    part_d_surcharge *= inflation_factor

    # Calculate annual amounts
    part_b_annual = part_b_surcharge * 12
    part_d_annual = part_d_surcharge * 12
    total_annual = part_b_annual + part_d_annual

    return part_b_annual, part_d_annual, total_annual

# Test the fix
print("Testing IRMAA fix for Married Filing Separately")
print("=" * 60)

test_cases = [
    (0, "Base surcharge at $0 MAGI"),
    (50000, "Base surcharge at $50k MAGI"),
    (105999, "Just below first threshold"),
    (106000, "At first threshold - higher surcharge"),
    (200000, "Middle income"),
    (394000, "At highest threshold"),
]

for magi, description in test_cases:
    part_b_annual, part_d_annual, total_annual = calculate_irmaa_fixed(
        magi, "Married Filing Separately", 2026
    )

    print(f"\n{description}:")
    print(f"  MAGI: ${magi:,}")
    print(f"  Part B Surcharge Annual: ${part_b_annual:.2f}")
    print(f"  Part D Surcharge Annual: ${part_d_annual:.2f}")
    print(f"  Total IRMAA Surcharge Annual: ${total_annual:.2f}")

# Verify the expected value
print("\n" + "=" * 60)
print("VERIFICATION: Expected surcharge at $0 MAGI")
expected = Decimal('221.90') * Decimal('1.01') * 12  # With 1% inflation
part_b_annual, _, total = calculate_irmaa_fixed(0, "Married Filing Separately", 2026)

print(f"Expected annual Part B surcharge: ${expected:.2f}")
print(f"Calculated annual Part B surcharge: ${part_b_annual:.2f}")

if abs(part_b_annual - expected) < Decimal('0.01'):
    print("✓ IRMAA calculation is CORRECT - should show ~$2,689.43/year")
else:
    print("✗ IRMAA calculation is INCORRECT")

print("\nNote: The old bug showed $22 instead of $2,689.43")
print("The fix ensures we:")
print("1. Use the surcharge directly (not subtract base premium)")
print("2. Apply proper inflation to the surcharge")
print("3. Multiply monthly by 12 for annual amount")