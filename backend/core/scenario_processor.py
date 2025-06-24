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
        self.spouse_birthdate = self.spouse.birthdate if self.spouse else None
        self.tax_status = self.client.tax_status
        self.assets = list(self.scenario.income_sources.values())

        # Log scenario ID and number of assets retrieved
        self._log_debug(f"Scenario ID: {scenario_id}, Number of assets retrieved: {len(self.assets)}")

        # STEP 1: Scenario Initialization
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
        
        print("\n==== STARTING RETIREMENT INCOME CALCULATION ====")

        # Determine mortality years
        primary_mortality_year = self.primary_birthdate.year + (self.scenario.mortality_age or 90)
        spouse_mortality_year = self.spouse_birthdate.year + (self.scenario.spouse_mortality_age or (self.scenario.mortality_age or 90)) if self.spouse_birthdate else None
        last_mortality_year = max(primary_mortality_year, spouse_mortality_year) if spouse_mortality_year else primary_mortality_year

        # Track living status
        primary_alive = True
        spouse_alive = True if self.spouse_birthdate else False
        tax_status = self.tax_status

        for year in range(self.start_year, last_mortality_year + 1):
            primary_age = year - self.primary_birthdate.year
            spouse_age = year - self.spouse_birthdate.year if self.spouse_birthdate else None

            # Check mortality
            if primary_alive and year > primary_mortality_year:
                primary_alive = False
                print(f"Primary deceased in year {year}")
            if spouse_alive and spouse_mortality_year and year > spouse_mortality_year:
                spouse_alive = False
                print(f"Spouse deceased in year {year}")

            # Switch tax status if one spouse dies
            if tax_status == "Married Filing Jointly" and (not primary_alive or not spouse_alive):
                tax_status = "Single"
                print(f"Tax status switched to Single in year {year}")

            # If both deceased, stop calculations
            if not primary_alive and not spouse_alive:
                print(f"Both deceased in year {year}, stopping calculations.")
                break

            print(f"\n--- Processing Year: {year} | Primary Age: {primary_age if primary_alive else 'deceased'} | Spouse Age: {spouse_age if spouse_alive else 'deceased'} ---")

            # Only include income/assets for living persons
            gross_income = 0
            ss_income = 0
            if primary_alive or spouse_alive:
                gross_income = self._calculate_gross_income(year, primary_alive, spouse_alive)
                ss_income = self._calculate_social_security(year, primary_alive, spouse_alive)
            agi_excl_ss = Decimal(gross_income) - Decimal(ss_income)
            
            print(f"INCOME BREAKDOWN:")
            print(f"  Gross Income: ${gross_income:,.2f}")
            print(f"  Social Security: ${ss_income:,.2f}")
            print(f"  AGI excluding SS: ${agi_excl_ss:,.2f}")

            # Calculate provisional income for debug
            provisional_income = agi_excl_ss + Decimal('0.5') * Decimal(ss_income)
            print(f"\nPROVISIONAL INCOME CALCULATION:")
            print(f"  AGI excluding SS: ${agi_excl_ss:,.2f}")
            print(f"  + 50% of SS (${ss_income:,.2f} × 0.5): ${Decimal('0.5') * Decimal(ss_income):,.2f}")
            print(f"  = Provisional Income: ${provisional_income:,.2f}")
            
            # Get IRS thresholds based on filing status
            if self.tax_status == "Single":
                base_threshold = Decimal('25000')
                additional_threshold = Decimal('34000')
            else:  # Married Filing Jointly
                base_threshold = Decimal('32000')
                additional_threshold = Decimal('44000')
                
            print(f"\nIRS THRESHOLDS ({self.tax_status}):")
            print(f"  Base: ${base_threshold:,.2f}")
            print(f"  Additional: ${additional_threshold:,.2f}")

            taxable_ss = calculate_taxable_social_security(Decimal(ss_income), agi_excl_ss, 0, self.tax_status)
            
            # Calculate how much would be taxable based on IRS rules
            if provisional_income <= base_threshold:
                taxable_portion = "0%"
            elif provisional_income <= additional_threshold:
                taxable_portion = f"50% of amount over ${base_threshold:,.2f}"
            else:
                taxable_portion = f"85% of amount over ${additional_threshold:,.2f} + 50% between thresholds"
            
            print(f"\nTAXABLE SOCIAL SECURITY CALCULATION:")
            print(f"  SS Benefits: ${ss_income:,.2f}")
            print(f"  Provisional Income: ${provisional_income:,.2f}")
            print(f"  Taxable Portion: {taxable_portion}")
            print(f"  Calculated Taxable SS: ${taxable_ss:,.2f}")
            print(f"  % of SS Taxable: {(taxable_ss / ss_income * 100) if ss_income > 0 else 0:.1f}%")

            taxable_income = agi_excl_ss + taxable_ss
            
            # Apply 2025 standard deduction if enabled
            if getattr(self.scenario, 'apply_standard_deduction', True):
                if self.tax_status in ["Single", "Married Filing Separately"]:
                    standard_deduction = Decimal('15000')
                elif self.tax_status == "Married Filing Jointly" or self.tax_status == "Qualifying Widow(er)":
                    standard_deduction = Decimal('30000')
                elif self.tax_status == "Head of Household":
                    standard_deduction = Decimal('22500')
                else:
                    standard_deduction = Decimal('15000')
                taxable_income = max(Decimal('0'), taxable_income - standard_deduction)
                print(f"\nSTANDARD DEDUCTION APPLIED: {standard_deduction} for {self.tax_status}. Taxable Income after deduction: ${taxable_income:,.2f}")

            print(f"\nTAXABLE INCOME CALCULATION:")
            print(f"  AGI excluding SS: ${agi_excl_ss:,.2f}")
            print(f"  + Taxable SS: ${taxable_ss:,.2f}")
            print(f"  = Taxable Income: ${taxable_income:,.2f}")

            # Calculate MAGI (Modified Adjusted Gross Income) for Medicare IRMAA determination
            # MAGI = AGI + Tax-exempt interest + excluded foreign income + other specific add-backs
            tax_exempt_interest = Decimal(getattr(self.scenario, 'tax_exempt_interest', 0) or 0)
            foreign_income_exclusion = Decimal('0')  # For future implementation
            
            # For retirement planning, MAGI is AGI plus tax-exempt interest and certain other income
            # AGI = income from all sources - specific deductions, but including taxable SS
            agi = agi_excl_ss + taxable_ss
            
            # Additional income sources for MAGI (these would be 0 in most cases but could be added in future)
            excluded_municipal_bond_interest = tax_exempt_interest  # Tax-exempt municipal bond interest
            excluded_series_ee_bond_interest = Decimal('0')  # Used for education expenses
            excluded_foreign_income = Decimal('0')
            qualified_adoption_expenses = Decimal('0')
            passive_income_loss = Decimal('0')
            student_loan_interest = Decimal('0')
            ira_contribution_deduction = Decimal('0')
            
            # The MAGI adjustment factors can be set based on tax situation
            # Traditionally there are several adjustments for MAGI, but for Medicare IRMAA purposes
            # the key additions are tax-exempt interest and excluded foreign income
            magi_adjustments = excluded_municipal_bond_interest + excluded_series_ee_bond_interest + \
                             excluded_foreign_income + ira_contribution_deduction
            
            magi = agi + magi_adjustments
            
            if magi == agi:
                print(f"\nMAGI CALCULATION: (Note: MAGI equals AGI because no MAGI adjustments are present)")
            else:
                print(f"\nMAGI CALCULATION: (MAGI is different from AGI due to adjustments)")
            
            print(f"  AGI (taxable income): ${agi:,.2f}")
            print(f"  + Tax-exempt interest: ${excluded_municipal_bond_interest:,.2f}")
            print(f"  + Foreign income exclusion: ${excluded_foreign_income:,.2f}")
            print(f"  + IRA contribution deduction: ${ira_contribution_deduction:,.2f}")
            print(f"  = MAGI: ${magi:,.2f}")

            # STEP 3: Taxable Income & MAGI Engine
            # Removed duplicate calculation

            # STEP 4: Federal Tax & AMT Engine
            federal_tax, tax_bracket = self._calculate_federal_tax_and_bracket(taxable_income)
            cumulative_federal_tax += federal_tax
            
            print(f"\nTAX CALCULATION:")
            print(f"  Taxable Income: ${taxable_income:,.2f}")
            print(f"  Federal Tax: ${federal_tax:,.2f}")
            print(f"  Cumulative Federal Tax: ${cumulative_federal_tax:,.2f}")

            # STEP 5: Medicare & IRMAA Engine (2-year lookback)
            # Note: In real-world scenarios, IRMAA is based on MAGI from 2 years prior
            # For projection purposes, we're using current year MAGI for simplicity
            medicare_base, irmaa, total_medicare, base_part_d, part_d_irmaa = self._calculate_medicare_costs(magi, year)
            total_medicare = Decimal(total_medicare)
            
            print(f"\nMEDICARE COSTS:")
            print(f"  Medicare Base: ${medicare_base:,.2f}")
            print(f"  IRMAA: ${irmaa:,.2f}")
            print(f"  Part D: ${base_part_d:,.2f}")
            print(f"  Part D IRMAA: ${part_d_irmaa:,.2f}")
            print(f"  Total Medicare: ${total_medicare:,.2f}")

            # STEP 6: Roth Conversion Module (Joint Household, Phase 1)
            roth_conversion_amount = self._calculate_roth_conversion(year)
            if roth_conversion_amount > 0:
                print(f"\nROTH CONVERSION:")
                print(f"  Conversion Amount: ${roth_conversion_amount:,.2f}")
                taxable_income += roth_conversion_amount
                print(f"  Updated Taxable Income: ${taxable_income:,.2f}")

            # STEP 7: Asset Spend-Down & Growth Engine
            self._calculate_asset_spend_down(year)

            net_income = gross_income + ss_income - federal_tax - total_medicare
            irmaa = irmaa + part_d_irmaa
            
            print(f"\nFINAL RESULTS FOR YEAR {year}:")
            print(f"  Gross Income: ${gross_income:,.2f}")
            print(f"  Taxable Income: ${taxable_income:,.2f}")
            print(f"  Federal Tax: ${federal_tax:,.2f}")
            print(f"  Total Medicare: ${total_medicare:,.2f}")
            print(f"  Net Income: ${net_income:,.2f}")
            print("--------------------------------------------")

            summary = {
                "year": year,
                "primary_age": primary_age if primary_alive else None,
                "spouse_age": spouse_age if spouse_alive else None,
                "gross_income": round(gross_income, 2),
                "ss_income": round(ss_income, 2),
                "taxable_ss": round(taxable_ss, 2),
                "agi": round(agi, 2),
                "magi": round(magi, 2),
                "taxable_income": round(taxable_income, 2),
                "roth_conversion": round(roth_conversion_amount, 2),
                "federal_tax": round(federal_tax, 2),
                "cumulative_federal_tax": round(cumulative_federal_tax, 2),
                "medicare_base": round(medicare_base, 2),
                "part_b": round(medicare_base, 2),
                "part_d": round(base_part_d, 2),
                "irmaa_surcharge": round(irmaa, 2),
                "total_medicare": round(total_medicare, 2),
                "net_income": round(net_income, 2),
                "tax_bracket": tax_bracket
            }

            for asset in self.assets:
                summary[f"{asset['income_type']}_balance"] = round(asset["current_asset_balance"], 2)

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
        monthly_contribution = Decimal(asset.get("monthly_contribution") or 0)

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
            self._log_debug(f"Year {year} - Current age {current_age} < withdrawal start age {start_age}, applying annual contribution: ${annual_contribution}")
        else:
            self._log_debug(f"Year {year} - Current age {current_age} >= withdrawal start age {start_age}, no contributions")

        # Get current year and check if this is the first time we're processing this asset
        current_year = datetime.datetime.now().year
        
        # If this is the first time we're processing this asset for this scenario run,
        # we need to calculate its value for the current processing year
        if "last_processed_year" not in asset:
            # Initialize the asset's tracking data
            asset["initial_asset_balance"] = asset.get("current_asset_balance", 0)
            asset["last_processed_year"] = current_year - 1  # Start from last year
            asset["previous_year_balance"] = asset.get("current_asset_balance", 0)
            
            # Calculate growth from initial entry year to current processing year
            years_to_grow = year - current_year
            
            self._log_debug(f"Year {year} - First time processing asset. Initial balance: {asset['initial_asset_balance']}")
            self._log_debug(f"Year {year} - Growing asset from current year {current_year} to processing year {year} ({years_to_grow} years)")
            
            # Grow the balance from current year to processing year
            if years_to_grow > 0:
                current_balance = asset["previous_year_balance"]
                for yr in range(years_to_grow):
                    # Check if we should apply contributions for this year
                    projection_year = current_year + yr
                    projection_age = projection_year - birthdate.year
                    
                    # Apply contributions only if before withdrawal age
                    if projection_age < start_age:
                        current_balance += annual_contribution
                        self._log_debug(f"Projection Year {projection_year} - Age {projection_age} < {start_age}, added contribution: ${annual_contribution}")
                    
                    # Apply growth
                    current_balance *= (1 + rate_of_return)
                    
                asset["previous_year_balance"] = current_balance
            
        # If we've already processed this asset but need to update for a new year
        elif asset["last_processed_year"] < year - 1:
            # Calculate how many years we need to catch up
            years_to_catch_up = year - asset["last_processed_year"] - 1
            current_balance = asset["previous_year_balance"]
            
            self._log_debug(f"Year {year} - Catching up asset growth for {years_to_catch_up} years from {asset['last_processed_year']} to {year-1}")
            
            # Process each missing year
            for i in range(years_to_catch_up):
                catch_up_year = asset["last_processed_year"] + i + 1
                catch_up_age = catch_up_year - birthdate.year
                
                # Apply contributions only if before withdrawal age
                if catch_up_age < start_age:
                    current_balance += annual_contribution
                    self._log_debug(f"Catch-up Year {catch_up_year} - Age {catch_up_age} < {start_age}, added contribution: ${annual_contribution}")
                
                # Apply growth
                current_balance *= (1 + rate_of_return)
            
            asset["previous_year_balance"] = current_balance
        
        # Now process the current year
        current_balance = asset["previous_year_balance"]
        
        # Apply contributions for current year if in contribution phase (before withdrawal age)
        if current_age < start_age:
            current_balance += annual_contribution
            self._log_debug(f"Year {year} - Added contribution: ${annual_contribution}")
        
        # Apply growth for current year
        current_balance *= (1 + rate_of_return)
        self._log_debug(f"Year {year} - Applied growth rate: {rate_of_return:.2%}")
        
        # Log the final balance for this year
        self._log_debug(f"Year {year} - Final balance: ${current_balance:,.2f}")
        
        # Update tracking information
        asset["last_processed_year"] = year
        asset["previous_year_balance"] = current_balance
        asset["current_asset_balance"] = current_balance
        
        return current_balance

    def _calculate_gross_income(self, year, primary_alive=True, spouse_alive=True):
        self._log_debug(f"Processing gross income for year {year}")
        income_total = 0
        for asset in self.assets:
            owner = asset.get("owned_by", "primary")
            if (owner == "primary" and not primary_alive) or (owner == "spouse" and not spouse_alive):
                continue
            self._update_asset_balance(asset, year)
            birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
            if not birthdate:
                continue
            current_age = year - birthdate.year
            start_age = asset.get("age_to_begin_withdrawal")
            end_age = asset.get("age_to_end_withdrawal")
            cola = Decimal(asset.get("cola", 0)) / 100
            if start_age is not None and end_age is not None and start_age <= current_age <= end_age:
                years_since_start = current_age - start_age
                monthly_amount = Decimal(asset.get("monthly_amount") or 0)
                inflated_amount = monthly_amount * (Decimal(1 + cola) ** years_since_start)
                annual_income = inflated_amount * 12
                if asset.get("income_type") == "Traditional_401k":
                    rmd_amount = self._calculate_rmd(asset, year)
                    if rmd_amount > annual_income:
                        annual_income = rmd_amount
                income_total += annual_income
        return income_total

    def _calculate_social_security(self, year, primary_alive=True, spouse_alive=True):
        self._log_debug(f"Processing social security income for year {year}")
        total_ss = 0
        for asset in self.assets:
            if asset.get("income_type") == "social_security":
                owner = asset.get("owned_by", "primary")
                if (owner == "primary" and not primary_alive) or (owner == "spouse" and not spouse_alive):
                    continue
                birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
                if not birthdate:
                    continue
                current_age = year - birthdate.year
                start_age = asset.get("age_to_begin_withdrawal")
                end_age = asset.get("age_to_end_withdrawal")
                cola = Decimal('0.02')
                if start_age is not None and end_age is not None and start_age <= current_age <= end_age:
                    years_since_start = current_age - start_age
                    monthly_amount = asset.get("monthly_amount", 0)
                    inflated_amount = monthly_amount * (Decimal(1 + cola) ** years_since_start)
                    annual_income = inflated_amount * 12
                    total_ss += annual_income
        self._log_debug(f"Total Social Security Income for year {year}: {total_ss}")
        return total_ss

    def _calculate_taxable_income(self, gross_income, ss_income):
        return gross_income + ss_income * Decimal("0.85")

    def _calculate_federal_tax_and_bracket(self, taxable_income):
        # 2025 IRS tax brackets (all rates as Decimal)
        brackets = {
            "single": [
                (11925, Decimal('0.10')),
                (48475, Decimal('0.12')),
                (103350, Decimal('0.22')),
                (197300, Decimal('0.24')),
                (250525, Decimal('0.32')),
                (626350, Decimal('0.35')),
                (Decimal('Infinity'), Decimal('0.37'))
            ],
            "married filing jointly": [
                (23850, Decimal('0.10')),
                (96950, Decimal('0.12')),
                (206700, Decimal('0.22')),
                (394600, Decimal('0.24')),
                (501050, Decimal('0.32')),
                (751600, Decimal('0.35')),
                (Decimal('Infinity'), Decimal('0.37'))
            ],
            "married filing separately": [
                (11925, Decimal('0.10')),
                (48475, Decimal('0.12')),
                (103350, Decimal('0.22')),
                (197300, Decimal('0.24')),
                (250525, Decimal('0.32')),
                (375800, Decimal('0.35')),
                (Decimal('Infinity'), Decimal('0.37'))
            ],
            "head of household": [
                (17000, Decimal('0.10')),
                (64850, Decimal('0.12')),
                (103350, Decimal('0.22')),
                (197300, Decimal('0.24')),
                (250500, Decimal('0.32')),
                (626350, Decimal('0.35')),
                (Decimal('Infinity'), Decimal('0.37'))
            ],
            "qualifying widow(er)": [
                (23850, Decimal('0.10')),
                (96950, Decimal('0.12')),
                (206700, Decimal('0.22')),
                (394600, Decimal('0.24')),
                (501050, Decimal('0.32')),
                (751600, Decimal('0.35')),
                (Decimal('Infinity'), Decimal('0.37'))
            ]
        }
        # Normalize tax status
        status = (self.tax_status or '').strip().lower()
        bracket_list = brackets.get(status, brackets["single"])
        tax = Decimal('0')
        last_cap = Decimal('0')
        marginal_rate = Decimal('0.10')
        taxable_income = Decimal(taxable_income)
        for cap, rate in bracket_list:
            cap = Decimal(cap)
            if taxable_income > cap:
                tax += (cap - last_cap) * marginal_rate
                last_cap = cap
                marginal_rate = rate
            else:
                tax += (taxable_income - last_cap) * marginal_rate
                break
        # Find the marginal bracket
        for cap, rate in bracket_list:
            cap = Decimal(cap)
            if taxable_income <= cap:
                bracket_str = f"{int(rate*100)}%"
                break
        else:
            bracket_str = f"{int(bracket_list[-1][1]*100)}%"
        return tax, bracket_str

    def _calculate_medicare_costs(self, magi, year):
        self._log_debug(f"Calculating Medicare costs based on MAGI: {magi}")
        base_part_b = 185  # Base monthly rate per person for Part B
        base_part_d = 71  # Base monthly rate for Part D
        irmaa = 0
        part_d_irmaa = 0

        # Determine IRMAA based on filing status and MAGI
        if self.tax_status == "Single":
            if magi > 500000:
                irmaa = 616
                part_d_irmaa = 85.80
            elif magi > 200000:
                irmaa = 581
                part_d_irmaa = 78.60
            elif magi > 167000:
                irmaa = 472.80
                part_d_irmaa = 57.00
            elif magi > 133000:
                irmaa = 364.90
                part_d_irmaa = 35.30
            elif magi > 106000:
                irmaa = 256.90
                part_d_irmaa = 13.70
            elif magi <= 106000:
                irmaa = 185.00
                part_d_irmaa = 0
        elif self.tax_status == "Married Filing Jointly":
            if magi > 750000:
                irmaa = 616
                part_d_irmaa = 85.80
            elif magi > 400000:
                irmaa = 581
                part_d_irmaa = 78.60
            elif magi > 334000:
                irmaa = 472.80
                part_d_irmaa = 57.00
            elif magi > 266000:
                irmaa = 364.90
                part_d_irmaa = 35.30
            elif magi > 212000:
                irmaa = 256.90
                part_d_irmaa = 13.70
            elif magi <= 212000:
                irmaa = 185.00
                part_d_irmaa = 0
            base_part_b *= 2  # Double the base for married couples
            base_part_d *= 2  # Double the base for married couples
        elif self.tax_status == "Married Filing Separately":
            if magi > 394000:
                irmaa = 443.90
                part_d_irmaa = 85.80
            elif magi > 106000:
                irmaa = 406.90
                part_d_irmaa = 78.60
            elif magi <= 106000:
                irmaa = 406.90
                part_d_irmaa = 0

        # Convert irmaa and part_d_irmaa to Decimal before applying the inflation rate
        irmaa = Decimal(irmaa)
        part_d_irmaa = Decimal(part_d_irmaa)

        # Retrieve inflation rates from the scenario
        part_b_inflation_rate = Decimal(self.scenario.part_b_inflation_rate) / 100
        part_d_inflation_rate = Decimal(self.scenario.part_d_inflation_rate) / 100

        # Calculate the number of years until the current year
        current_year = datetime.datetime.now().year
        years_until_current = year - current_year

        # Apply inflation for each year until the current year
        for _ in range(years_until_current):
            base_part_b *= (1 + part_b_inflation_rate)
            base_part_d *= (1 + part_d_inflation_rate)
            irmaa *= (1 + part_d_inflation_rate)
            part_d_irmaa *= (1 + part_d_inflation_rate)

        # Calculate the IRMAA cost separately
        irmaa_cost = irmaa - base_part_b

        if irmaa_cost < 0:
            irmaa_cost = 0

        # Calculate total Medicare cost
        total_medicare_monthly = base_part_b + irmaa_cost + base_part_d + part_d_irmaa

        # Log the adjusted values
        self._log_debug(f"Year {year} - Inflated Medicare Base Part B: {base_part_b}, Inflated IRMAA: {irmaa}, Base Part D: {base_part_d}, Part D IRMAA: {part_d_irmaa}, Total Medicare Monthly: {total_medicare_monthly}")

        total_medicare_annual = total_medicare_monthly * 12  # Calculate total annual cost
        self._log_debug(f"Adjusted Medicare Base Part B: {base_part_b}, Adjusted IRMAA: {irmaa}, Base Part D: {base_part_d}, Part D IRMAA: {part_d_irmaa}, Total Medicare Annual: {total_medicare_annual}")
        base_part_b_annual = base_part_b * 12
        base_part_d_annual = base_part_d * 12
        irmaa_cost_annual = irmaa_cost * 12
        
        return base_part_b_annual, irmaa_cost_annual, total_medicare_annual, base_part_d_annual, part_d_irmaa

    def _calculate_roth_conversion(self, year):
        """
        Implement the Roth Conversion Module (STEP 6)
        - Accept advisor-defined joint conversion schedule: start year, duration, annual conversion amount.
        - Apply pro-rata asset depletion across eligible balances (IRA, 401k, etc.).
        - Conversion amount treated as additional taxable income & MAGI.
        - Update Roth balances accordingly with growth.
        """
        roth_conversion_start_year = self.scenario.roth_conversion_start_year
        roth_conversion_duration = self.scenario.roth_conversion_duration
        roth_conversion_annual_amount = self.scenario.roth_conversion_annual_amount

        # Add error handling for None values
        if roth_conversion_start_year is None or roth_conversion_duration is None:
            self._log_debug(f"Roth conversion parameters are not set: start_year={roth_conversion_start_year}, duration={roth_conversion_duration}")
            return 0

        if year >= roth_conversion_start_year and year < roth_conversion_start_year + roth_conversion_duration:
            # Apply pro-rata asset depletion across eligible balances
            eligible_balances = [asset for asset in self.assets if asset["income_type"] in ["ira", "401k"]]
            total_eligible_balance = sum(asset["current_asset_balance"] for asset in eligible_balances)
            for asset in eligible_balances:
                depletion_ratio = asset["current_asset_balance"] / total_eligible_balance
                asset_conversion_amount = roth_conversion_annual_amount * depletion_ratio
                asset["current_asset_balance"] -= asset_conversion_amount
                asset["roth_conversion_amount"] = asset_conversion_amount

            # Add conversion amount to taxable income and MAGI
            return roth_conversion_annual_amount
        else:
            return 0

    def _calculate_asset_spend_down(self, year):
        """
        Implement the Asset Spend-Down & Growth Engine (STEP 7)
        - Apply monthly contributions until retirement age.
        - Apply growth rates annually.
        - Apply withdrawals after retirement start year.
        - Apply RMD override when applicable (IRS Uniform Lifetime Table).
        - Apply Roth conversions as account depletion & Roth growth.
        - Prevent negative balances.
        - Survivor rules handle tax filing transitions.
        """
        for asset in self.assets:
            self._update_asset_balance(asset, year)

            # Apply RMD override if calculated RMD > requested withdrawals
            rmd_amount = self._calculate_rmd(asset, year)
            withdrawal_amount = asset.get("withdrawal_amount", 0)
            if rmd_amount > withdrawal_amount:
                asset["withdrawal_amount"] = rmd_amount

            # Apply Roth conversion depletion and growth
            roth_conversion_amount = self._calculate_roth_conversion(year)
            asset["current_asset_balance"] = asset.get("current_asset_balance") or 0
            asset["current_asset_balance"] -= roth_conversion_amount

        # Prevent negative balances
        for asset in self.assets:
            if asset["current_asset_balance"] < 0:
                asset["current_asset_balance"] = 0

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
    
    # Detailed calculation explanation
    print(f"  DETAILED SS TAXATION CALCULATION:")
    print(f"    SS Benefits: ${ss_benefits:,.2f}")
    print(f"    AGI (excluding SS): ${agi:,.2f}")
    print(f"    Tax-exempt interest: ${tax_exempt_interest:,.2f}")
    print(f"    50% of SS: ${Decimal('0.5') * ss_benefits:,.2f}")
    print(f"    Provisional Income: ${provisional_income:,.2f}")

    # Determine the base and additional thresholds based on filing status
    if filing_status == "Single":
        base_threshold = Decimal('25000')
        additional_threshold = Decimal('34000')
    elif filing_status == "Married Filing Jointly":
        base_threshold = Decimal('32000')
        additional_threshold = Decimal('44000')
    else:
        raise ValueError("Unsupported filing status")
        
    print(f"    Filing Status: {filing_status}")
    print(f"    Base threshold: ${base_threshold:,.2f}")
    print(f"    Additional threshold: ${additional_threshold:,.2f}")

    # Calculate the taxable portion of Social Security benefits
    if provisional_income <= base_threshold:
        taxable_ss = Decimal('0')
        print(f"    Case: Provisional income <= base threshold")
        print(f"    Taxable SS: $0.00 (0% of benefits)")
    elif provisional_income <= additional_threshold:
        taxable_ss = min(Decimal('0.5') * (provisional_income - base_threshold), Decimal('0.5') * ss_benefits)
        print(f"    Case: Provisional income between thresholds")
        print(f"    Amount over base: ${provisional_income - base_threshold:,.2f}")
        print(f"    50% of amount over base: ${Decimal('0.5') * (provisional_income - base_threshold):,.2f}")
        print(f"    Maximum allowed (50% of SS): ${Decimal('0.5') * ss_benefits:,.2f}")
        print(f"    Taxable SS: ${taxable_ss:,.2f}")
    else:
        # For incomes above the additional threshold, the formula is more complex:
        # 50% of the amount between thresholds + 85% of the amount above additional threshold
        # But never more than 85% of total benefits
        amount_between_thresholds = additional_threshold - base_threshold
        amount_above_additional = provisional_income - additional_threshold
        
        taxable_portion_first_tier = Decimal('0.5') * amount_between_thresholds
        taxable_portion_second_tier = Decimal('0.85') * amount_above_additional
        
        calculated_taxable_ss = taxable_portion_first_tier + taxable_portion_second_tier
        max_taxable_ss = Decimal('0.85') * ss_benefits
        
        taxable_ss = min(calculated_taxable_ss, max_taxable_ss)
        
        print(f"    Case: Provisional income > additional threshold")
        print(f"    Amount between thresholds: ${amount_between_thresholds:,.2f}")
        print(f"    50% of amount between thresholds: ${taxable_portion_first_tier:,.2f}")
        print(f"    Amount above additional threshold: ${amount_above_additional:,.2f}")
        print(f"    85% of amount above additional: ${taxable_portion_second_tier:,.2f}")
        print(f"    Calculated taxable amount: ${calculated_taxable_ss:,.2f}")
        print(f"    Maximum allowed (85% of SS): ${max_taxable_ss:,.2f}")
        print(f"    Final Taxable SS: ${taxable_ss:,.2f} ({(taxable_ss / ss_benefits * 100):,.1f}% of benefits)")

    return taxable_ss

def calculate_asset_value_at_retirement(current_balance, monthly_contribution, annual_growth_rate, years_until_retirement, years_in_retirement):
    """
    Calculate the future value of an asset both at retirement and at the end of retirement.
    
    Parameters:
    - current_balance: Current value of the asset
    - monthly_contribution: Monthly contribution to the asset until retirement
    - annual_growth_rate: Annual rate of return (as a percentage, e.g., 7 for 7%)
    - years_until_retirement: Number of years until retirement begins
    - years_in_retirement: Number of years in retirement
    
    Returns:
    - future_value_at_end_of_retirement: The projected value at the end of retirement
    """
    # Convert to Decimal for precision
    current_balance = Decimal(str(current_balance))
    monthly_contribution = Decimal(str(monthly_contribution))
    annual_growth_rate = Decimal(str(annual_growth_rate))
    
    # Convert annual growth rate to decimal form (e.g., 7% -> 0.07)
    annual_rate_decimal = annual_growth_rate / Decimal('100')
    
    # Calculate the annual compounding factor
    annual_factor = Decimal('1') + annual_rate_decimal
    
    # Accumulation phase: calculate future value with contributions
    future_value = current_balance
    
    # Process each year until retirement - add contributions during this phase
    for _ in range(years_until_retirement):
        # Add annual contributions (12 months)
        annual_contribution = monthly_contribution * 12
        future_value += annual_contribution
        
        # Apply annual growth
        future_value *= annual_factor
    
    # Store the value at retirement - no more contributions after this point
    future_value_at_retirement = future_value
    
    # Decumulation phase: calculate future value without additional contributions
    # Just apply growth during retirement years
    for _ in range(years_in_retirement):
        future_value *= annual_factor
    
    future_value_at_end_of_retirement = future_value
    
    return future_value_at_end_of_retirement
