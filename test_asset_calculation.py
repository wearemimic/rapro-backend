#!/usr/bin/env python
"""Test asset balance calculation to verify the formula."""

def calculate_balance_current_method(initial_balance, growth_rate, years, monthly_contribution=0):
    """Current method in scenario_processor.py"""
    balance = initial_balance
    annual_contribution = monthly_contribution * 12

    for year in range(years):
        # Add contributions first (if any)
        balance += annual_contribution
        # Then apply growth
        balance *= (1 + growth_rate)

    return balance

def calculate_balance_correct_method(initial_balance, growth_rate, years, monthly_contribution=0):
    """Correct compound interest formula"""
    balance = initial_balance
    annual_contribution = monthly_contribution * 12

    for year in range(years):
        # Apply growth first on existing balance
        balance *= (1 + growth_rate)
        # Then add contributions (if any)
        balance += annual_contribution

    return balance

def calculate_balance_no_contributions(initial_balance, growth_rate, years):
    """Pure compound interest without contributions"""
    return initial_balance * ((1 + growth_rate) ** years)

# Test case from the user
initial_balance = 1_000_000
growth_rate = 0.07  # 7%
years = 15
monthly_contribution = 0  # No contributions mentioned

print("Asset Balance Calculation Test")
print("=" * 50)
print(f"Initial Balance: ${initial_balance:,}")
print(f"Growth Rate: {growth_rate:.1%}")
print(f"Years: {years}")
print(f"Monthly Contribution: ${monthly_contribution}")
print()

# Calculate using different methods
current_result = calculate_balance_current_method(initial_balance, growth_rate, years, monthly_contribution)
correct_result = calculate_balance_correct_method(initial_balance, growth_rate, years, monthly_contribution)
pure_compound = calculate_balance_no_contributions(initial_balance, growth_rate, years)

print("Results:")
print(f"Current Method: ${current_result:,.2f}")
print(f"Correct Method: ${correct_result:,.2f}")
print(f"Pure Compound (no contributions): ${pure_compound:,.2f}")
print(f"User Reported Value: $2,952,164")
print(f"User Expected Value: ~$2,759,032")
print()

# Now test with a non-zero contribution to see the difference
monthly_contribution_test = 1000  # $1000/month
current_with_contrib = calculate_balance_current_method(initial_balance, growth_rate, years, monthly_contribution_test)
correct_with_contrib = calculate_balance_correct_method(initial_balance, growth_rate, years, monthly_contribution_test)

print(f"With ${monthly_contribution_test}/month contribution:")
print(f"Current Method: ${current_with_contrib:,.2f}")
print(f"Correct Method: ${correct_with_contrib:,.2f}")
print(f"Difference: ${current_with_contrib - correct_with_contrib:,.2f}")