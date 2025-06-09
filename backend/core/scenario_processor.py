import datetime
from decimal import Decimal
from core.models import Scenario, Client, Spouse, IncomeSource

# RMD Table based on IRS Uniform Lifetime Table
RMD_TABLE = {
    72: 27.4,
    73: 26.5,
    74: 25.5,
    75: 24.6,
    76: 23.7,
    77: 22.9,
    78: 22.0,
    79: 21.1,
    80: 20.2,
    81: 19.4,
    82: 18.5,
    83: 17.7,
    84: 16.8,
    85: 16.0,
    86: 15.2,
    87: 14.4,
    88: 13.7,
    89: 12.9,
    90: 12.2,
    91: 11.5,
    92: 10.8,
    93: 10.1,
    94: 9.5,
    95: 8.9,
    96: 8.4,
    97: 7.8,
    98: 7.3,
    99: 6.8,
    100: 6.4,
    101: 6.0,
    102: 5.6,
    103: 5.2,
    104: 4.9,
    105: 4.5,
    106: 4.2,
    107: 3.9,
    108: 3.7,
    109: 3.4,
    110: 3.1,
    111: 2.9,
    112: 2.6,
    113: 2.4,
    114: 2.1,
    115: 1.9,
}

class ScenarioProcessor:
    def __init__(self, scenario_id, debug=False):
        self.debug = debug
        self.scenario = Scenario.objects.get(id=scenario_id)
        self.client = self.scenario.client
        self.spouse = getattr(self.client, "spouse", None)
        self.primary_birthdate = self.client.birthdate
        self.spouse_birthdate = self.spouse_birthdate if self.spouse else None
        self.tax_status = self.client.tax_status
        self.assets = list(self.scenario.income_sources.values())

        # Log scenario ID and number of assets retrieved
        self._log_debug(f"Scenario ID: {scenario_id}, Number of assets retrieved: {len(self.assets)}")

        current_year = datetime.datetime.now().year
        retirement_age_primary = self.scenario.retirement_age or 65
        retirement_age_spouse = getattr(self.scenario, 'spouse_retirement_age', None) or 65
        mortality_age_primary = self.scenario.mortality_age or 90
        mortality_age_spouse = getattr(self.scenario, 'spouse_mortality_age', None) or mortality_age_primary

        current_age_primary = current_year - self.primary_birthdate.year
        if self.spouse_birthdate:
            current_age_spouse = current_year - self.spouse_birthdate.year
        else:
            current_age_spouse = None

        if self.tax_status == "Single" or not self.spouse_birthdate:
            years_until_retirement = retirement_age_primary - current_age_primary
            self.start_year = current_year + max(years_until_retirement, 0)
        else:
            years_until_retirement_primary = retirement_age_primary - current_age_primary
            years_until_retirement_spouse = retirement_age_spouse - current_age_spouse
            start_year_primary = current_year + max(years_until_retirement_primary, 0)
            start_year_spouse = current_year + max(years_until_retirement_spouse, 0)
            self.start_year = min(start_year_primary, start_year_spouse)

        end_year_primary = self.primary_birthdate.year + mortality_age_primary
        end_year_spouse = self.spouse_birthdate.year + mortality_age_spouse if self.spouse_birthdate else end_year_primary

        max_end_year = max(end_year_primary, end_year_spouse)

        for asset in self.assets:
            start_age = asset.get("age_to_begin_withdrawal")
            end_age = asset.get("age_to_end_withdrawal")
            owner = asset.get("owned_by", "primary")
            birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
            if birthdate and end_age is not None:
                asset_end_year = birthdate.year + end_age
                if asset_end_year > max_end_year:
                    max_end_year = asset_end_year

        self.end_year = max_end_year

    def calculate(self):
        results = []
        cumulative_federal_tax = 0
        for year in range(self.start_year, self.end_year + 1):
            primary_age = year - self.primary_birthdate.year
            spouse_age = year - self.spouse_birthdate.year if self.spouse_birthdate else None

            gross_income = self._calculate_gross_income(year)
            ss_income = self._calculate_social_security(year)
            taxable_ss = calculate_taxable_social_security(ss_income, gross_income, 0, self.tax_status)  # Assuming no tax-exempt interest for simplicity
            taxable_income = (gross_income - ss_income) + taxable_ss  # Corrected to add only the taxable portion
            federal_tax = self._calculate_federal_tax(taxable_income)
            cumulative_federal_tax += federal_tax
            medicare_base, irmaa, total_medicare = self._calculate_medicare_costs(taxable_income, year)
            # Convert total_medicare to Decimal for subtraction
            total_medicare = Decimal(total_medicare)
            net_income = gross_income + ss_income - federal_tax - total_medicare

            summary = {
                "year": year,
                "primary_age": primary_age,
                "spouse_age": spouse_age if self.tax_status != "Single" else None,
                "gross_income": round(gross_income, 2),
                "ss_income": round(ss_income, 2),
                "taxable_ss": round(taxable_ss, 2),  # Store taxable Social Security
                "taxable_income": round(taxable_income, 2),
                "federal_tax": round(federal_tax, 2),
                "cumulative_federal_tax": round(cumulative_federal_tax, 2),
                "medicare_base": round(medicare_base, 2),
                "irmaa": round(irmaa, 2),
                "total_medicare": round(total_medicare, 2),
                "net_income": round(net_income, 2)
            }

            self._log_debug(f"Year {year}: {summary}")
            results.append(summary)
        return results

    def _calculate_rmd(self, asset, year):
        """
        Calculate the Required Minimum Distribution (RMD) for a given asset in a specific year.
        """
        rmd_start_age = 72
        owner = asset.get("owned_by", "primary")
        birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
        if not birthdate:
            self._log_debug(f"Year {year} - No birthdate found for owner {owner}")
            return 0

        current_age = year - birthdate.year
        self._log_debug(f"Year {year} - Current age of owner: {current_age}")

        previous_year_balance = asset.get("previous_year_balance", 0)

        # Log the previous year balance
        self._log_debug(f"Year {year} - Previous Year Balance: {previous_year_balance}")

        # Fetch the life expectancy factor from the RMD table
        life_expectancy_factor = RMD_TABLE.get(current_age, None)
        if life_expectancy_factor is None:
            self._log_debug(f"Year {year} - No RMD factor found for age {current_age}")
            return 0

        # Convert life expectancy factor to Decimal for division
        life_expectancy_factor = Decimal(life_expectancy_factor)

        rmd_amount = previous_year_balance / life_expectancy_factor

        # Calculate RMD percentage
        rmd_percentage = 100 / life_expectancy_factor

        # Debugging lines
        self._log_debug(f"Year {year} - RMD percentage: {rmd_percentage:.2f}%")
        self._log_debug(f"Year {year} - Calculated RMD amount based on income and percentage: {rmd_amount}")
        self._log_debug(f"Year {year} - Expected RMD based on federal tables: {rmd_amount}")

        # Explicitly log the RMD value
        self._log_debug(f"DEBUG RMD = {rmd_amount}")

        return rmd_amount

    def _update_asset_balance(self, asset, year):
        """
        Update the asset balance by applying contributions, growth, and withdrawals.
        """
        owner = asset.get("owned_by", "primary")
        birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
        if not birthdate:
            return 0

        current_age = year - birthdate.year
        start_age = asset.get("age_to_begin_withdrawal")
        end_age = asset.get("age_to_end_withdrawal")
        rate_of_return = Decimal(asset.get("rate_of_return", 0)) / 100
        monthly_contribution = Decimal(asset.get("monthly_contribution", 0))

        # Log asset details
        self._log_debug(f"Processing asset: {asset.get('income_name', 'Unnamed Asset')} (Type: {asset.get('income_type', 'Unknown')})")
        self._log_debug(f"Asset details: {asset}")

        # Determine if the asset type should not have a balance
        non_balance_assets = ["social_security", "pension", "rental_income", "wages"]
        if asset.get("income_type") in non_balance_assets:
            self._log_debug(f"Year {year} - Asset type '{asset.get('income_type')}' does not have a balance. Calculating income only.")
            return 0

        # Calculate annual contributions only if current age is less than start age
        annual_contribution = 0
        if current_age < start_age:
            annual_contribution = monthly_contribution * 12

        # Fetch the account balance at the start of the year
        current_balance = asset.get("current_asset_balance", 0)

        self._log_debug(f"Year {year} - Initial 401k Balance: {current_balance}")
        self._log_debug(f"Year {year} - Annual Contribution: {annual_contribution}")

        # Calculate the number of years until retirement
        retirement_age = asset.get("age_to_begin_withdrawal", 65)
        years_until_retirement = max(0, retirement_age - current_age)

        # Iterate over each year until retirement
        for _ in range(years_until_retirement):
            # Apply contributions
            current_balance += annual_contribution
            
            # Apply growth
            current_balance *= (1 + rate_of_return)

        # Log the balance after applying contributions and growth over multiple years
        self._log_debug(f"Year {year} - 401k/IRA Balance after Contributions and Growth over {years_until_retirement} years: {current_balance}")

        # Update the asset balance for the next year
        asset["previous_year_balance"] = current_balance
        asset["current_asset_balance"] = current_balance

    def _calculate_gross_income(self, year: int) -> float:
        self._log_debug(f"Processing gross income for year {year}")
        income_total = 0
        for asset in self.assets:
            self._update_asset_balance(asset, year)
            owner = asset.get("owned_by", "primary")
            birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
            if not birthdate:
                continue

            current_age = year - birthdate.year
            start_age = asset.get("age_to_begin_withdrawal")
            end_age = asset.get("age_to_end_withdrawal")
            cola = Decimal(asset.get("cola", 0)) / 100  # Cost of Living Adjustment as decimal, e.g., 0.02 for 2%

            # self._log_debug(f"  Asset: {asset}, Current Age: {current_age}, Start Age: {start_age}, End Age: {end_age}, COLA: {cola}")

            if start_age is not None and end_age is not None and start_age <= current_age <= end_age:
                years_since_start = current_age - start_age
                monthly_amount = asset.get("monthly_amount", 0)
                inflated_amount = monthly_amount * (Decimal(1 + cola) ** years_since_start)
                annual_income = inflated_amount * 12  # Annualize monthly income

                # Check if the asset is subject to RMDs and adjust the income if necessary
                if asset.get("income_type") == "Traditional_401k":
                    rmd_amount = self._calculate_rmd(asset, year)
                    if rmd_amount > annual_income:
                        annual_income = rmd_amount

                income_total += annual_income

        return income_total

    def _calculate_social_security(self, year):
        self._log_debug(f"Processing social security income for year {year}")
        total_ss = 0
        for asset in self.assets:
            if asset.get("income_type") == "social_security":
                owner = asset.get("owned_by", "primary")
                birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
                if not birthdate:
                    continue
                current_age = year - birthdate.year
                start_age = asset.get("age_to_begin_withdrawal")
                end_age = asset.get("age_to_end_withdrawal")
                cola = Decimal('0.02')  # Set COLA to 2% for Social Security

                self._log_debug(f"  SS Asset: {asset}, Current Age: {current_age}, Start Age: {start_age}, End Age: {end_age}, COLA: {cola}")

                if start_age is not None and end_age is not None and start_age <= current_age <= end_age:
                    years_since_start = current_age - start_age
                    monthly_amount = asset.get("monthly_amount", 0)
                    inflated_amount = monthly_amount * (Decimal(1 + cola) ** years_since_start)
                    annual_income = inflated_amount * 12
                    total_ss += annual_income
                    self._log_debug(f"  Year {year} - Calculated Social Security Income: {annual_income}")
        self._log_debug(f"Total Social Security Income for year {year}: {total_ss}")
        return total_ss

    def _calculate_taxable_income(self, gross_income, ss_income):
        return gross_income + ss_income * Decimal("0.85")

    def _calculate_federal_tax(self, taxable_income):
        if self.tax_status == "Single":
            return taxable_income * Decimal("0.15")
        return taxable_income * Decimal("0.12")

    def _calculate_medicare_costs(self, taxable_income, year):
        self._log_debug(f"Calculating Medicare costs based on taxable income: {taxable_income}")
        base = 1700
        irmaa = 0

        # Determine IRMAA based on filing status and taxable income
        if self.tax_status == "Single":
            if taxable_income > 500000:
                irmaa = 616
            elif taxable_income > 200000:
                irmaa = 581
            elif taxable_income > 167000:
                irmaa = 472.80
            elif taxable_income > 133000:
                irmaa = 364.90
            elif taxable_income > 106000:
                irmaa = 256.90
            elif taxable_income < 106000:
                irmaa = 185.00
        elif self.tax_status == "Married Filing Jointly":
            if taxable_income > 750000:
                irmaa = 616
            elif taxable_income > 400000:
                irmaa = 581
            elif taxable_income > 334000:
                irmaa = 472.80
            elif taxable_income > 266000:
                irmaa = 364.90
            elif taxable_income > 212000:
                irmaa = 256.90
            elif taxable_income < 212000:
                irmaa = 185.00
        elif self.tax_status == "Married Filing Separately":
            if taxable_income > 394000:
                irmaa = 443.90
            elif taxable_income > 106000:
                irmaa = 406.90
            elif taxable_income < 106000:
                irmaa = 406.90

        # Retrieve inflation rates from the scenario
        part_b_inflation_rate = Decimal(self.scenario.part_b_inflation_rate) / 100
        part_d_inflation_rate = Decimal(self.scenario.part_d_inflation_rate) / 100

        # Convert irmaa to Decimal before applying the inflation rate
        irmaa = Decimal(irmaa)
        irmaa *= (1 + part_d_inflation_rate)

        # Adjust the base and IRMAA costs by the inflation rates
        base *= (1 + part_b_inflation_rate)

        # Calculate the number of years until the current year
        current_year = datetime.datetime.now().year
        years_until_current = year - current_year

        # Apply inflation for each year until the current year
        for _ in range(years_until_current):
            base *= (1 + part_b_inflation_rate)
            irmaa *= (1 + part_d_inflation_rate)

        # Log the adjusted values
        self._log_debug(f"Year {year} - Inflated Medicare Base: {base}, Inflated IRMAA: {irmaa}")

        total_medicare = irmaa * 12
        self._log_debug(f"Adjusted Medicare Base: {base}, Adjusted IRMAA: {irmaa}, Total Medicare: {total_medicare}")
        return base, irmaa, total_medicare

    def _log_debug(self, message):
        if self.debug:
            print(f"🔍 Debug: {message}")

def calculate_taxable_social_security(ss_benefits, agi, tax_exempt_interest, filing_status):
    # Convert inputs to Decimal for consistency
    ss_benefits = Decimal(ss_benefits)
    agi = Decimal(agi)
    tax_exempt_interest = Decimal(tax_exempt_interest)

    # Calculate provisional income
    provisional_income = agi + tax_exempt_interest + Decimal('0.5') * ss_benefits

    # Determine the base and additional thresholds based on filing status
    if filing_status == "Single":
        base_threshold = Decimal('25000')
        additional_threshold = Decimal('34000')
    elif filing_status == "Married Filing Jointly":
        base_threshold = Decimal('32000')
        additional_threshold = Decimal('44000')
    else:
        raise ValueError("Unsupported filing status")

    # Calculate the taxable portion of Social Security benefits
    if provisional_income <= base_threshold:
        taxable_ss = Decimal('0')
    elif provisional_income <= additional_threshold:
        taxable_ss = Decimal('0.5') * (provisional_income - base_threshold)
    else:
        taxable_ss = Decimal('0.85') * ss_benefits

    # Ensure the taxable amount does not exceed 85% of the benefits
    taxable_ss = min(taxable_ss, Decimal('0.85') * ss_benefits)

    return taxable_ss

def calculate_asset_value_at_retirement(current_balance, monthly_contribution, annual_growth_rate, years_until_retirement, years_in_retirement):
    # Convert annual growth rate to monthly
    monthly_growth_rate = Decimal(annual_growth_rate) / Decimal('12') / Decimal('100')

    # Calculate the number of months until retirement
    months_until_retirement = years_until_retirement * 12

    # Accumulation phase: calculate future value with contributions
    future_value_at_retirement = current_balance * (1 + monthly_growth_rate) ** months_until_retirement
    future_value_at_retirement += monthly_contribution * (((1 + monthly_growth_rate) ** months_until_retirement - 1) / monthly_growth_rate)

    # Decumulation phase: calculate future value without contributions
    months_in_retirement = years_in_retirement * 12
    future_value_at_end_of_retirement = future_value_at_retirement * (1 + monthly_growth_rate) ** months_in_retirement

    return future_value_at_end_of_retirement
