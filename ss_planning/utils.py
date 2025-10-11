"""
Social Security Planning Utility Functions

This module provides utility functions for Social Security calculations,
including FRA determination, life expectancy lookups, and benefit adjustments.
"""

from datetime import datetime
from decimal import Decimal


# Full Retirement Age (FRA) by birth year
FRA_BY_BIRTH_YEAR = {
    1937: 65.0,
    1938: 65 + 2/12,
    1939: 65 + 4/12,
    1940: 65 + 6/12,
    1941: 65 + 8/12,
    1942: 65 + 10/12,
    1943: 66.0,
    1954: 66.0,
    1955: 66 + 2/12,
    1956: 66 + 4/12,
    1957: 66 + 6/12,
    1958: 66 + 8/12,
    1959: 66 + 10/12,
    1960: 67.0,
}

# SSA Period Life Table - Expected additional years of life
# Source: SSA Actuarial Life Table 2020
LIFE_EXPECTANCY_TABLES = {
    'male': {
        60: 22.6,
        62: 21.8,
        65: 18.5,
        67: 16.8,
        70: 14.4,
        75: 11.3,
        80: 8.5,
        85: 6.2,
        90: 4.3,
    },
    'female': {
        60: 25.3,
        62: 24.3,
        65: 21.0,
        67: 19.2,
        70: 16.7,
        75: 13.4,
        80: 10.2,
        85: 7.4,
        90: 5.1,
    }
}

# 2025 Earnings Test Limits
EARNINGS_TEST_LIMITS = {
    2025: {
        'before_fra': 22320,  # $1 withheld for every $2 over this
        'fra_year': 59520,     # $1 withheld for every $3 over this (year reaching FRA)
    }
}

# Social Security benefit adjustment factors
EARLY_RETIREMENT_PENALTY_MONTHLY = 0.0067  # 0.67% per month before FRA
DELAYED_RETIREMENT_CREDIT_MONTHLY = 0.0067  # 0.67% per month after FRA (8% per year)
MIN_ADJUSTMENT_FACTOR = 0.7   # 30% reduction at age 62
MAX_ADJUSTMENT_FACTOR = 1.24  # 24% increase at age 70


def calculate_fra(birthdate):
    """
    Calculate Full Retirement Age based on birthdate.

    Args:
        birthdate (datetime.date or str): Client's birthdate

    Returns:
        float: Full Retirement Age (e.g., 66.5 for 66 and 6 months)
    """
    if isinstance(birthdate, str):
        birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()

    birth_year = birthdate.year

    # Before 1937
    if birth_year < 1937:
        return 65.0

    # After 1960
    if birth_year >= 1960:
        return 67.0

    # Look up in table
    for year in sorted(FRA_BY_BIRTH_YEAR.keys()):
        if birth_year <= year:
            return FRA_BY_BIRTH_YEAR[year]

    # Default to 67 if not found
    return 67.0


def get_life_expectancy(current_age, gender='male', health_status='good'):
    """
    Get life expectancy from SSA actuarial tables with health adjustments.

    Args:
        current_age (int): Current age of person
        gender (str): 'male' or 'female'
        health_status (str): 'poor', 'fair', 'good', or 'excellent'

    Returns:
        int: Expected age at death
    """
    gender = gender.lower()
    if gender not in ['male', 'female']:
        gender = 'male'

    table = LIFE_EXPECTANCY_TABLES.get(gender, LIFE_EXPECTANCY_TABLES['male'])

    # Find closest age in table or interpolate
    if current_age in table:
        additional_years = table[current_age]
    else:
        # Interpolate between closest ages
        ages = sorted(table.keys())
        if current_age < ages[0]:
            additional_years = table[ages[0]]
        elif current_age > ages[-1]:
            additional_years = table[ages[-1]]
        else:
            # Find surrounding ages
            for i, age in enumerate(ages):
                if age > current_age:
                    lower_age = ages[i-1]
                    upper_age = age
                    lower_years = table[lower_age]
                    upper_years = table[upper_age]

                    # Linear interpolation
                    ratio = (current_age - lower_age) / (upper_age - lower_age)
                    additional_years = lower_years + ratio * (upper_years - lower_years)
                    break

    # Apply health status adjustment
    health_adjustments = {
        'poor': -3,
        'fair': -1,
        'good': 0,
        'excellent': 3
    }
    adjustment = health_adjustments.get(health_status, 0)

    life_expectancy = current_age + additional_years + adjustment

    return int(round(life_expectancy))


def calculate_benefit_adjustment(claiming_age, fra=67.0):
    """
    Calculate Social Security benefit adjustment factor based on claiming age.

    Args:
        claiming_age (float): Age when benefits are claimed
        fra (float): Full Retirement Age

    Returns:
        float: Adjustment factor (e.g., 0.75 for 25% reduction, 1.24 for 24% increase)
    """
    claiming_age = float(claiming_age)
    fra = float(fra)

    adjustment_factor = 1.0

    if claiming_age < fra:
        # Early retirement reduction
        months_early = (fra - claiming_age) * 12
        adjustment_factor -= months_early * EARLY_RETIREMENT_PENALTY_MONTHLY
    elif claiming_age > fra:
        # Delayed retirement credit
        months_delayed = (claiming_age - fra) * 12
        adjustment_factor += months_delayed * DELAYED_RETIREMENT_CREDIT_MONTHLY

    # Apply bounds
    adjustment_factor = max(MIN_ADJUSTMENT_FACTOR, min(adjustment_factor, MAX_ADJUSTMENT_FACTOR))

    return round(adjustment_factor, 4)


def calculate_monthly_benefit(amount_at_fra, claiming_age, fra=67.0):
    """
    Calculate monthly Social Security benefit based on claiming age.

    Args:
        amount_at_fra (Decimal or float): Monthly benefit at FRA
        claiming_age (float): Age when claiming
        fra (float): Full Retirement Age

    Returns:
        Decimal: Adjusted monthly benefit
    """
    if isinstance(amount_at_fra, float):
        amount_at_fra = Decimal(str(amount_at_fra))

    adjustment_factor = calculate_benefit_adjustment(claiming_age, fra)

    return amount_at_fra * Decimal(str(adjustment_factor))


def calculate_earnings_test_reduction(annual_earnings, claiming_age, fra, year=2025):
    """
    Calculate Social Security benefit reduction due to earnings test.

    Args:
        annual_earnings (Decimal): Annual earned income
        claiming_age (float): Age when claiming
        fra (float): Full Retirement Age
        year (int): Tax year

    Returns:
        Decimal: Annual benefit reduction amount
    """
    if claiming_age >= fra:
        return Decimal(0)  # No earnings test at or after FRA

    annual_earnings = Decimal(str(annual_earnings))
    limits = EARNINGS_TEST_LIMITS.get(year, EARNINGS_TEST_LIMITS[2025])
    limit = Decimal(str(limits['before_fra']))

    excess_earnings = max(Decimal(0), annual_earnings - limit)

    # $1 withheld for every $2 over limit
    reduction = excess_earnings / Decimal(2)

    return reduction


def get_current_age(birthdate):
    """
    Calculate current age from birthdate.

    Args:
        birthdate (datetime.date or str): Birthdate

    Returns:
        int: Current age
    """
    if isinstance(birthdate, str):
        birthdate = datetime.strptime(birthdate, '%Y-%m-%d').date()

    today = datetime.now().date()
    age = today.year - birthdate.year

    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1

    return age


def format_fra_display(fra):
    """
    Format FRA for display (e.g., 66.666 -> "66 and 8 months").

    Args:
        fra (float): Full Retirement Age

    Returns:
        str: Formatted FRA string
    """
    years = int(fra)
    months = round((fra - years) * 12)

    if months == 0:
        return str(years)
    else:
        return f"{years} and {months} months" if months > 1 else f"{years} and {months} month"
