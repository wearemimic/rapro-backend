import datetime
from decimal import Decimal, InvalidOperation
from core.models import Scenario, Client, Spouse, IncomeSource
from core.tax_csv_loader import get_tax_loader

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
        
    @classmethod
    def from_dicts(cls, scenario, client, spouse, assets, debug=False):
        """
        Create a ScenarioProcessor instance from dictionaries instead of database objects.
        
        Parameters:
        - scenario: Dictionary containing scenario data
        - client: Dictionary containing client data
        - spouse: Dictionary containing spouse data (or None)
        - assets: List of dictionaries containing asset data
        - debug: Boolean to enable debug logging
        
        Returns:
        - ScenarioProcessor instance initialized with the provided data
        """
        instance = cls.__new__(cls)
        instance.debug = debug
        
        # Log input data for debugging
        if debug:
            print(f"ScenarioProcessor.from_dicts() called with:")
            print(f"Scenario: {scenario}")
            print(f"Client: {client}")
            print(f"Spouse: {spouse}")
            print(f"Assets count: {len(assets) if assets else 0}")
        
        # Validate client data
        if not client:
            raise ValueError("Client data is required")
            
        # Ensure required client fields exist
        required_client_fields = {
            'tax_status': 'Single',
            'gender': 'M',
            'birthdate': None,  # Will be handled separately
            'first_name': 'Client',
            'last_name': '',
            'email': '',
            'state': 'CA'
        }
        
        for field, default_value in required_client_fields.items():
            if field not in client or client[field] is None:
                if field == 'birthdate':  # Skip birthdate as it's handled separately
                    continue
                print(f"WARNING: Client missing required field '{field}', using default: {default_value}")
                client[field] = default_value
        
        # Ensure all required scenario fields are present with defaults
        required_scenario_fields = {
            'reduction_2030_ss': False,
            'ss_adjustment_year': 2030,
            'ss_adjustment_direction': 'decrease',
            'ss_adjustment_type': 'percentage',
            'ss_adjustment_amount': 23.0,
            'apply_standard_deduction': True,
        }
        
        for field, default_value in required_scenario_fields.items():
            if field not in scenario or scenario[field] is None:
                if instance.debug:
                    print(f"WARNING: Scenario missing field '{field}', using default: {default_value}")
                scenario[field] = default_value
        
        # Set scenario attributes directly from the dictionary
        instance.scenario = type('obj', (object,), scenario)
        
        # Set client attributes
        instance.client = type('obj', (object,), client)
        
        # Set spouse attributes if provided
        if spouse:
            instance.spouse = type('obj', (object,), spouse)
        else:
            instance.spouse = None
        
        # Set birthdate attributes with proper error handling
        try:
            if isinstance(client.get('birthdate'), str):
                instance.primary_birthdate = datetime.datetime.strptime(client['birthdate'], '%Y-%m-%d').date()
            else:
                instance.primary_birthdate = client.get('birthdate')
            
            if not instance.primary_birthdate:
                # If birthdate is missing, use a default (current year - 65)
                current_year = datetime.datetime.now().year
                instance.primary_birthdate = datetime.date(current_year - 65, 1, 1)
                print(f"WARNING: Client birthdate missing, using default: {instance.primary_birthdate}")
                # Update the client dictionary with the default birthdate
                client['birthdate'] = instance.primary_birthdate.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"ERROR parsing client birthdate: {e}")
            # Default to 65 years ago
            current_year = datetime.datetime.now().year
            instance.primary_birthdate = datetime.date(current_year - 65, 1, 1)
            # Update the client dictionary with the default birthdate
            client['birthdate'] = instance.primary_birthdate.strftime('%Y-%m-%d')
        
        # Handle spouse birthdate
        instance.spouse_birthdate = None
        if spouse and 'birthdate' in spouse and spouse['birthdate']:
            try:
                if isinstance(spouse['birthdate'], str):
                    instance.spouse_birthdate = datetime.datetime.strptime(spouse['birthdate'], '%Y-%m-%d').date()
                else:
                    instance.spouse_birthdate = spouse['birthdate']
            except Exception as e:
                print(f"ERROR parsing spouse birthdate: {e}")
        
        # Set tax status with default
        instance.tax_status = client.get('tax_status', 'Single')
        
        # Set assets with validation
        if not assets:
            print("WARNING: No assets provided, using empty list")
            instance.assets = []
        else:
            # Validate each asset has required fields
            validated_assets = []
            for asset in assets:
                # Ensure each asset has the minimum required fields
                if 'income_type' not in asset:
                    print(f"WARNING: Asset missing income_type, skipping: {asset}")
                    continue
                
                # Ensure numeric fields are properly set
                for field in ['current_asset_balance', 'monthly_amount', 'monthly_contribution', 'rate_of_return']:
                    if field not in asset or asset[field] is None:
                        asset[field] = 0
                
                # Ensure age fields are set
                if 'age_to_begin_withdrawal' not in asset or asset['age_to_begin_withdrawal'] is None:
                    asset['age_to_begin_withdrawal'] = 65
                if 'age_to_end_withdrawal' not in asset or asset['age_to_end_withdrawal'] is None:
                    asset['age_to_end_withdrawal'] = 90
                
                validated_assets.append(asset)
            
            instance.assets = validated_assets
        
        # Log initialization
        instance._log_debug(f"Initialized from dictionaries with {len(instance.assets)} assets")
        
        # STEP 1: Scenario Initialization
        current_year = datetime.datetime.now().year
        
        # Get scenario parameters with defaults
        retirement_age_primary = getattr(instance.scenario, 'retirement_age', 65)
        retirement_age_spouse = getattr(instance.scenario, 'spouse_retirement_age', 65)
        mortality_age_primary = getattr(instance.scenario, 'mortality_age', 90)
        mortality_age_spouse = getattr(instance.scenario, 'spouse_mortality_age', mortality_age_primary)
        
        # Add required inflation rates if missing
        if not hasattr(instance.scenario, 'part_b_inflation_rate'):
            setattr(instance.scenario, 'part_b_inflation_rate', 3.0)
        if not hasattr(instance.scenario, 'part_d_inflation_rate'):
            setattr(instance.scenario, 'part_d_inflation_rate', 3.0)
        
        # Calculate current ages
        current_age_primary = current_year - instance.primary_birthdate.year
        if instance.spouse_birthdate:
            current_age_spouse = current_year - instance.spouse_birthdate.year
        else:
            current_age_spouse = None
            
        # Calculate start year based on retirement
        if instance.tax_status == "Single" or not instance.spouse_birthdate:
            years_until_retirement = retirement_age_primary - current_age_primary
            instance.start_year = current_year + max(years_until_retirement, 0)
        else:
            years_until_retirement_primary = retirement_age_primary - current_age_primary
            years_until_retirement_spouse = retirement_age_spouse - current_age_spouse
            start_year_primary = current_year + max(years_until_retirement_primary, 0)
            start_year_spouse = current_year + max(years_until_retirement_spouse, 0)
            instance.start_year = min(start_year_primary, start_year_spouse)
            
        # Calculate end years based on mortality
        end_year_primary = instance.primary_birthdate.year + mortality_age_primary
        end_year_spouse = instance.spouse_birthdate.year + mortality_age_spouse if instance.spouse_birthdate else end_year_primary
        
        max_end_year = max(end_year_primary, end_year_spouse)
        
        # Check asset end years
        for asset in instance.assets:
            start_age = asset.get("age_to_begin_withdrawal")
            end_age = asset.get("age_to_end_withdrawal")
            owner = asset.get("owned_by", "primary")
            birthdate = instance.primary_birthdate if owner == "primary" else instance.spouse_birthdate
            if birthdate and end_age is not None:
                asset_end_year = birthdate.year + end_age
                if asset_end_year > max_end_year:
                    max_end_year = asset_end_year
                    
        instance.end_year = max_end_year
        
        # Set Roth conversion parameters
        if hasattr(instance.scenario, 'roth_conversion_start_year') and hasattr(instance.scenario, 'roth_conversion_duration'):
            instance._log_debug(f"Roth conversion parameters: start_year={instance.scenario.roth_conversion_start_year}, duration={instance.scenario.roth_conversion_duration}")
        else:
            instance._log_debug("No Roth conversion parameters set")
        
        return instance

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

        # --- NEW LOGIC: Determine table start year ---
        retirement_year = self.primary_birthdate.year + (self.scenario.retirement_age or 65)
        conversion_start_year = getattr(self.scenario, 'roth_conversion_start_year', None)
        if conversion_start_year is None:
            table_start_year = retirement_year
        else:
            table_start_year = min(retirement_year, int(conversion_start_year))
            
        print(f"DEBUG: retirement_year={retirement_year}, conversion_start_year={conversion_start_year}, table_start_year={table_start_year}")

        pre_retirement_income = getattr(self.scenario, 'pre_retirement_income', 0)

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
            ss_decrease_applied = False
            ss_decrease_amount_actual = 0
            ss_income_primary_gross = 0
            ss_income_spouse_gross = 0
            if primary_alive or spouse_alive:
                gross_income = self._calculate_gross_income(year, primary_alive, spouse_alive)
                ss_income, ss_income_primary, ss_income_spouse = self._calculate_social_security(year, primary_alive, spouse_alive)
                
                # Check if SS decrease is applied this year and calculate actual amount
                if (self.scenario.reduction_2030_ss and 
                    year >= self.scenario.ss_adjustment_year and 
                    self.scenario.ss_adjustment_direction == 'decrease' and 
                    ss_income > 0):
                    
                    ss_decrease_applied = True
                    # Calculate what the SS income would have been without the decrease
                    ss_income_without_decrease, ss_income_primary_gross, ss_income_spouse_gross = self._calculate_social_security_without_decrease(year, primary_alive, spouse_alive)
                    ss_decrease_amount_actual = float(ss_income_without_decrease - ss_income)
                else:
                    # No reduction applied - gross amounts are the same as net amounts
                    _, ss_income_primary_gross, ss_income_spouse_gross = self._calculate_social_security_without_decrease(year, primary_alive, spouse_alive)
                
                # Add pre-retirement income if we're before retirement year
                if year < retirement_year and pre_retirement_income:
                    pre_retirement_income_decimal = Decimal(str(pre_retirement_income))
                    gross_income += pre_retirement_income_decimal
                    print(f"  Adding pre-retirement income: ${pre_retirement_income_decimal:,.2f}")
                    
            agi_excl_ss = Decimal(gross_income)
            taxable_ss = calculate_taxable_social_security(Decimal(ss_income), agi_excl_ss, 0, self.tax_status)

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
            
            # Apply standard deduction from CSV data if enabled
            if getattr(self.scenario, 'apply_standard_deduction', True):
                tax_loader = get_tax_loader()
                
                # Normalize tax status for CSV lookup
                status_mapping = {
                    'single': 'Single',
                    'married filing jointly': 'Married Filing Jointly',
                    'married filing separately': 'Married Filing Separately', 
                    'head of household': 'Head of Household',
                    'qualifying widow(er)': 'Qualifying Widow(er)'
                }
                
                normalized_status = (self.tax_status or '').strip().lower()
                filing_status = status_mapping.get(normalized_status, 'Single')
                
                standard_deduction = tax_loader.get_standard_deduction(filing_status)
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
            # For Medicare IRMAA purposes, MAGI includes ALL Social Security benefits (not just taxable portion)
            # plus tax-exempt interest and excluded foreign income
            untaxed_ss = Decimal(ss_income) - taxable_ss  # The portion of SS not included in AGI
            magi_adjustments = excluded_municipal_bond_interest + excluded_series_ee_bond_interest + \
                             excluded_foreign_income + ira_contribution_deduction + untaxed_ss
            
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
            medicare_base, irmaa, total_medicare, base_part_d, part_d_irmaa, first_irmaa_threshold, current_irmaa_bracket, irmaa_bracket_number = self._calculate_medicare_costs(magi, year)
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

            # STEP 8: Apply Hold Harmless Act if applicable
            # IMPORTANT: Hold Harmless reduces Medicare deductions to maintain previous year's net SS
            # It does NOT change SS income used for tax/IRMAA calculations
            hold_harmless_protected = False
            hold_harmless_amount = 0
            original_remaining_ss = ss_income - total_medicare
            effective_medicare = total_medicare  # This is what's actually deducted (may be reduced by Hold Harmless)
            
            if (ss_income > 0 and irmaa_bracket_number == 0):  # Eligible for Hold Harmless
                if len(results) > 0:  # Not the first year
                    previous_year_result = results[-1]
                    previous_remaining_ss = previous_year_result.get('remaining_ss', 0)
                    
                    # If Medicare increases would reduce net SS, apply Hold Harmless
                    if original_remaining_ss < previous_remaining_ss:
                        hold_harmless_protected = True
                        hold_harmless_amount = previous_remaining_ss - original_remaining_ss
                        # Reduce Medicare deduction to maintain previous year's remaining amount
                        effective_medicare = total_medicare - hold_harmless_amount
                        print(f"\nHOLD HARMLESS PROTECTION APPLIED:")
                        print(f"  SS income (unchanged): ${ss_income:,.2f}")
                        print(f"  Full Medicare cost: ${total_medicare:,.2f}")
                        print(f"  Effective Medicare deduction: ${effective_medicare:,.2f}")
                        print(f"  Previous year remaining SS: ${previous_remaining_ss:,.2f}")
                        print(f"  Current calculated remaining: ${original_remaining_ss:,.2f}")
                        print(f"  Hold Harmless protection: ${hold_harmless_amount:,.2f}")

            net_income = gross_income + ss_income - federal_tax - effective_medicare
            remaining_ss = ss_income - effective_medicare
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
                "gross_income": round(gross_income + ss_income, 2),
                "ss_income": round(ss_income, 2),
                "ss_income_primary": round(ss_income_primary, 2),
                "ss_income_spouse": round(ss_income_spouse, 2),
                "ss_income_primary_gross": round(ss_income_primary_gross, 2),
                "ss_income_spouse_gross": round(ss_income_spouse_gross, 2),
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
                "irmaa_threshold": first_irmaa_threshold,
                "irmaa_bracket_number": irmaa_bracket_number,
                "irmaa_bracket_threshold": float(current_irmaa_bracket['magi_threshold']) if current_irmaa_bracket else None,
                "total_medicare": round(total_medicare, 2),
                "effective_medicare": round(effective_medicare, 2),
                "net_income": round(net_income, 2),
                "remaining_ss": round(remaining_ss, 2),
                "tax_bracket": tax_bracket,
                "ss_decrease_applied": ss_decrease_applied,
                "ss_decrease_amount": ss_decrease_amount_actual,
                "hold_harmless_protected": hold_harmless_protected,
                "hold_harmless_amount": round(hold_harmless_amount, 2),
                "original_remaining_ss": round(original_remaining_ss, 2)
            }

            # Add asset balances to summary with safe rounding
            def safe_round(val, ndigits=2):
                try:
                    return round(Decimal(val), ndigits)
                except (InvalidOperation, TypeError, ValueError):
                    return Decimal('0.00')
            for asset in self.assets:
                summary[f"{asset['income_type']}_balance"] = safe_round(asset.get("current_asset_balance", 0))

            self._log_debug(f"Year {year}: {summary}")
            results.append(summary)
        return results

    def _requires_rmd(self, asset):
        """
        Determine if an asset type requires RMD calculations.
        Only the new asset types that are traditional/qualified accounts require RMD.
        """
        income_type = asset.get("income_type", "")
        
        # New asset types that require RMD
        rmd_asset_types = [
            "Qualified",  # Traditional tax-deferred accounts
            "Inherited Traditional Spouse",
            "Inherited Traditional Non-Spouse"
        ]
        
        return income_type in rmd_asset_types

    def _get_rmd_start_age(self, asset, owner_birthdate):
        """
        Get the RMD start age based on current IRS rules and birth year.
        """
        if not owner_birthdate:
            return 73  # Default to current rule
            
        birth_year = owner_birthdate.year
        asset_type = asset.get("income_type", "")
        
        # Inherited accounts have different rules
        if "Inherited" in asset_type:
            if "Non-Spouse" in asset_type:
                # Inherited non-spouse: 10-year rule (no annual RMD required until year 10)
                return None  # Special handling needed
            else:
                # Inherited spouse: can use their own life expectancy, starts immediately
                return 0  # Can start RMDs immediately
        
        # Regular accounts - based on birth year
        if birth_year <= 1950:
            return 72  # Old rule for those already subject to it
        elif birth_year <= 1959:
            return 73  # Current rule (2023+)
        else:
            return 75  # Future rule (2033+) for those born 1960+

    def _calculate_rmd(self, asset, year):
        """
        Calculate the Required Minimum Distribution (RMD) for a given asset in a specific year.
        Uses current IRS rules including different start ages and inherited account rules.
        """
        # Skip RMD calculation for fully converted assets
        if asset.get("fully_converted_to_roth", False):
            self._log_debug(f"Year {year} - Asset {asset.get('investment_name', 'Unknown')} fully converted, no RMD required")
            return Decimal('0')
        
        # Check if this asset type requires RMD
        if not self._requires_rmd(asset):
            return 0
            
        owner = asset.get("owned_by", "primary")
        birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
        if not birthdate:
            self._log_debug(f"Year {year} - No birthdate found for owner {owner}")
            return 0

        current_age = year - birthdate.year
        asset_type = asset.get("income_type", "")
        rmd_start_age = self._get_rmd_start_age(asset, birthdate)
        
        # Handle inherited non-spouse accounts (10-year rule)
        if asset_type == "Inherited Traditional Non-Spouse":
            # For inherited non-spouse, must deplete by end of 10th year
            # No annual RMDs required, but account must be empty by year 10
            inheritance_year = asset.get("inheritance_year", year - 1)  # Default to previous year
            years_since_inheritance = year - inheritance_year
            
            if years_since_inheritance >= 10:
                # Must withdraw entire remaining balance in year 10
                return Decimal(str(asset.get("current_asset_balance", 0)))
            else:
                # No required distribution in years 1-9 (but beneficiary can take distributions)
                return Decimal('0')
        
        # Handle regular and inherited spouse accounts
        if rmd_start_age is None or current_age < rmd_start_age:
            self._log_debug(f"Year {year} - Owner age {current_age} below RMD start age {rmd_start_age}")
            return 0

        # Calculate standard RMD using IRS Uniform Lifetime Table
        self._log_debug(f"Year {year} - Current age of owner: {current_age}, RMD start age: {rmd_start_age}")

        previous_year_balance = asset.get("previous_year_balance", 0)
        self._log_debug(f"Year {year} - Previous Year Balance: {previous_year_balance}")

        # Fetch the life expectancy factor from the RMD table
        life_expectancy_factor = RMD_TABLE.get(current_age, None)
        if life_expectancy_factor is None:
            self._log_debug(f"Year {year} - No RMD factor found for age {current_age}")
            return 0

        # Convert life expectancy factor to Decimal for division
        life_expectancy_factor = Decimal(life_expectancy_factor)
        rmd_amount = Decimal(str(previous_year_balance)) / life_expectancy_factor

        # Calculate RMD percentage for debugging
        rmd_percentage = 100 / life_expectancy_factor
        
        self._log_debug(f"Year {year} - Asset type: {asset_type}")
        self._log_debug(f"Year {year} - RMD percentage: {rmd_percentage:.2f}%")
        self._log_debug(f"Year {year} - Calculated RMD amount: {rmd_amount}")

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
        # Only update previous_year_balance if not fully converted
        if not asset.get("fully_converted_to_roth", False):
            asset["previous_year_balance"] = current_balance
        else:
            # If fully converted, set previous year balance to 0
            asset["previous_year_balance"] = Decimal('0')
        asset["current_asset_balance"] = current_balance
        
        return current_balance

    def _calculate_gross_income(self, year, primary_alive=True, spouse_alive=True):
        self._log_debug(f"Processing gross income for year {year}")
        income_total = 0
        for asset in self.assets:
            # Skip Social Security assets - they are handled separately
            if asset.get("income_type") == "social_security":
                continue
                
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
                # Apply RMD override for qualifying asset types
                rmd_amount = self._calculate_rmd(asset, year)
                if rmd_amount > annual_income:
                    annual_income = rmd_amount
                income_total += annual_income
        return income_total

    def _calculate_social_security(self, year, primary_alive=True, spouse_alive=True):
        self._log_debug(f"Processing social security income for year {year}")
        total_ss = 0
        primary_ss = 0
        spouse_ss = 0
        
        # First pass - calculate raw SS benefits without adjustments
        ss_assets = []
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
                    
                    ss_assets.append({
                        'owner': owner,
                        'annual_income': annual_income
                    })
                    
                    # Track primary vs spouse separately (before adjustments)
                    if owner == "primary":
                        primary_ss += annual_income
                    else:
                        spouse_ss += annual_income
        
        # Apply SS decrease adjustment only if enabled and conditions are met
        if (self.scenario.reduction_2030_ss and 
            year >= self.scenario.ss_adjustment_year and 
            self.scenario.ss_adjustment_direction == 'decrease' and
            ss_assets):  # Only apply if there are SS benefits
            
            adjustment_amount = Decimal(str(self.scenario.ss_adjustment_amount))
            
            # Check who has SS benefits and if they're alive
            has_primary_ss = any(asset['owner'] == 'primary' for asset in ss_assets) and primary_alive
            has_spouse_ss = any(asset['owner'] == 'spouse' for asset in ss_assets) and spouse_alive
            
            primary_raw_ss = sum(asset['annual_income'] for asset in ss_assets if asset['owner'] == 'primary')
            spouse_raw_ss = sum(asset['annual_income'] for asset in ss_assets if asset['owner'] == 'spouse')
            
            # Check if this is a couple scenario
            is_couple = self.tax_status and 'married' in self.tax_status.lower()
            
            # Determine reduction strategy based on who's alive and receiving benefits:
            # 1. If both spouses are alive and receiving SS → Double the reduction, apply to both
            # 2. If only one spouse is alive/receiving SS → Single reduction, apply to that person
            both_receiving_ss = has_primary_ss and has_spouse_ss and primary_alive and spouse_alive
            
            if both_receiving_ss and is_couple:
                # Double the reduction when both are retired and receiving benefits
                if self.scenario.ss_adjustment_type == 'percentage':
                    # Apply percentage to each person's benefits
                    reduction_multiplier = adjustment_amount / 100
                    primary_adjustment = primary_raw_ss * reduction_multiplier
                    spouse_adjustment = spouse_raw_ss * reduction_multiplier
                    total_adjustment = primary_adjustment + spouse_adjustment
                else:
                    # Double the flat amount (apply to both)
                    monthly_adjustment = adjustment_amount * 2
                    total_adjustment = monthly_adjustment * 12
            else:
                # Single person reduction
                # Determine who to apply it to
                apply_to_primary = has_primary_ss and primary_raw_ss > 0 and primary_alive
                apply_to_spouse = has_spouse_ss and spouse_raw_ss > 0 and spouse_alive and not apply_to_primary
                
                target_ss_amount = 0
                if apply_to_primary:
                    target_ss_amount = primary_raw_ss
                elif apply_to_spouse:
                    target_ss_amount = spouse_raw_ss
                
                total_adjustment = 0
                if target_ss_amount > 0:
                    if self.scenario.ss_adjustment_type == 'percentage':
                        # Apply percentage to target person's SS income
                        reduction_multiplier = adjustment_amount / 100
                        total_adjustment = target_ss_amount * reduction_multiplier
                    else:
                        # Apply flat amount to target person
                        total_adjustment = adjustment_amount * 12
            
            # Apply the adjustment based on the scenario
            if total_adjustment > 0:
                primary_ss = 0
                spouse_ss = 0
                
                if both_receiving_ss and is_couple:
                    # Apply reduction to both spouses proportionally to their benefits
                    for asset in ss_assets:
                        if asset['owner'] == "primary" and primary_raw_ss > 0:
                            # Apply reduction proportionally to primary's SS assets
                            proportion = asset['annual_income'] / primary_raw_ss
                            if self.scenario.ss_adjustment_type == 'percentage':
                                reduction_multiplier = adjustment_amount / 100
                                asset_adjustment = asset['annual_income'] * reduction_multiplier
                            else:
                                # For flat amount, distribute proportionally among primary's assets
                                monthly_per_person = adjustment_amount
                                annual_per_person = monthly_per_person * 12
                                asset_adjustment = annual_per_person * proportion
                            adjusted_income = max(0, asset['annual_income'] - asset_adjustment)
                            primary_ss += adjusted_income
                        elif asset['owner'] == "spouse" and spouse_raw_ss > 0:
                            # Apply reduction proportionally to spouse's SS assets
                            proportion = asset['annual_income'] / spouse_raw_ss
                            if self.scenario.ss_adjustment_type == 'percentage':
                                reduction_multiplier = adjustment_amount / 100
                                asset_adjustment = asset['annual_income'] * reduction_multiplier
                            else:
                                # For flat amount, distribute proportionally among spouse's assets
                                monthly_per_person = adjustment_amount
                                annual_per_person = monthly_per_person * 12
                                asset_adjustment = annual_per_person * proportion
                            adjusted_income = max(0, asset['annual_income'] - asset_adjustment)
                            spouse_ss += adjusted_income
                        else:
                            # Asset owner is not alive, no income
                            pass
                else:
                    # Single person reduction - apply to whoever is receiving benefits
                    apply_to_primary = has_primary_ss and primary_raw_ss > 0 and primary_alive
                    apply_to_spouse = has_spouse_ss and spouse_raw_ss > 0 and spouse_alive and not apply_to_primary
                    
                    for asset in ss_assets:
                        if apply_to_primary and asset['owner'] == "primary":
                            # Apply reduction proportionally to primary's SS assets
                            proportion = asset['annual_income'] / primary_raw_ss
                            asset_adjustment = total_adjustment * proportion
                            adjusted_income = max(0, asset['annual_income'] - asset_adjustment)
                            primary_ss += adjusted_income
                        elif apply_to_spouse and asset['owner'] == "spouse":
                            # Apply reduction proportionally to spouse's SS assets
                            proportion = asset['annual_income'] / spouse_raw_ss
                            asset_adjustment = total_adjustment * proportion
                            adjusted_income = max(0, asset['annual_income'] - asset_adjustment)
                            spouse_ss += adjusted_income
                        else:
                            # No reduction applied to this asset
                            if asset['owner'] == "primary":
                                primary_ss += asset['annual_income']
                            else:
                                spouse_ss += asset['annual_income']
                    
                total_ss = primary_ss + spouse_ss
            else:
                # No adjustment applied - use raw values
                total_ss = primary_ss + spouse_ss
        else:
            # No adjustment - use raw values
            total_ss = primary_ss + spouse_ss
                        
        self._log_debug(f"Total Social Security Income for year {year}: {total_ss} (Primary: {primary_ss}, Spouse: {spouse_ss})")
        return total_ss, primary_ss, spouse_ss
    
    def _calculate_social_security_without_decrease(self, year, primary_alive=True, spouse_alive=True):
        """Calculate Social Security income as if no decrease was applied - for comparison purposes."""
        total_ss = 0
        primary_ss = 0
        spouse_ss = 0
        
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
                    
                    # NO SS decrease applied - this is the raw amount
                    total_ss += annual_income
                    
                    # Track primary vs spouse separately
                    if owner == "primary":
                        primary_ss += annual_income
                    else:
                        spouse_ss += annual_income
                        
        return total_ss, primary_ss, spouse_ss
    
    def _get_ss_decrease_amount(self):
        """Get the annual SS decrease amount, doubled for couples."""
        if not self.scenario.reduction_2030_ss:
            return 0
            
        adjustment_amount = Decimal(str(self.scenario.ss_adjustment_amount))
        
        # Double the reduction for couples (married filing jointly)
        is_couple = self.tax_status and 'married' in self.tax_status.lower()
        if is_couple:
            adjustment_amount = adjustment_amount * 2
        
        if self.scenario.ss_adjustment_type == 'percentage':
            # For percentage, we'd need to know the base SS amount
            # This is a simplified approach - return 0 for now for percentage type
            # In a real implementation, this would calculate based on actual SS amounts
            return 0
        else:
            # Flat monthly amount - convert to annual
            return float(adjustment_amount * 12)

    def _calculate_taxable_income(self, gross_income, ss_income):
        return gross_income + ss_income * Decimal("0.85")

    def _calculate_federal_tax_and_bracket(self, taxable_income):
        """Calculate federal tax using CSV-based tax bracket data."""
        tax_loader = get_tax_loader()
        
        # Normalize tax status for CSV lookup
        status_mapping = {
            'single': 'Single',
            'married filing jointly': 'Married Filing Jointly',
            'married filing separately': 'Married Filing Separately', 
            'head of household': 'Head of Household',
            'qualifying widow(er)': 'Qualifying Widow(er)'
        }
        
        normalized_status = (self.tax_status or '').strip().lower()
        filing_status = status_mapping.get(normalized_status, 'Single')
        
        # Use CSV loader to calculate tax
        tax, bracket_str = tax_loader.calculate_federal_tax(Decimal(taxable_income), filing_status)
        
        return tax, bracket_str

    def _calculate_medicare_costs(self, magi, year):
        """Calculate Medicare costs using CSV-based rates and IRMAA thresholds."""
        self._log_debug(f"Calculating Medicare costs based on MAGI: {magi}")
        
        tax_loader = get_tax_loader()
        
        # Get base Medicare rates from CSV
        medicare_rates = tax_loader.get_medicare_base_rates()
        base_part_b = medicare_rates.get('part_b', Decimal('185'))
        base_part_d = medicare_rates.get('part_d', Decimal('71'))
        
        # Normalize tax status for CSV lookup
        status_mapping = {
            'single': 'Single',
            'married filing jointly': 'Married Filing Jointly',
            'married filing separately': 'Married Filing Separately'
        }
        
        normalized_status = (self.tax_status or '').strip().lower()
        filing_status = status_mapping.get(normalized_status, 'Single')
        
        # Calculate IRMAA surcharges using inflated thresholds for the target year
        part_b_surcharge, part_d_irmaa = tax_loader.calculate_irmaa_with_inflation(Decimal(magi), filing_status, year)
        
        # Get the inflated IRMAA thresholds for this year to include in results
        irmaa_thresholds_for_year = tax_loader.get_inflated_irmaa_thresholds(filing_status, year)
        
        # Find which IRMAA bracket we're in
        current_irmaa_bracket = None
        irmaa_bracket_number = 0
        first_irmaa_threshold = None
        
        # Sort thresholds by MAGI amount
        sorted_thresholds = sorted([t for t in irmaa_thresholds_for_year if t['magi_threshold'] > 0], 
                                 key=lambda x: x['magi_threshold'])
        
        if sorted_thresholds:
            first_irmaa_threshold = float(sorted_thresholds[0]['magi_threshold'])
            
            # Find the current bracket
            for i, threshold in enumerate(sorted_thresholds):
                if Decimal(magi) >= threshold['magi_threshold']:
                    current_irmaa_bracket = threshold
                    irmaa_bracket_number = i + 1
                else:
                    break
        
        # For married filing jointly, double the base rates
        if filing_status == "Married Filing Jointly":
            base_part_b *= 2
            base_part_d *= 2
        
        # Total IRMAA (base + surcharge)
        irmaa = base_part_b + part_b_surcharge

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
        
        return base_part_b_annual, irmaa_cost_annual, total_medicare_annual, base_part_d_annual, part_d_irmaa, first_irmaa_threshold, current_irmaa_bracket, irmaa_bracket_number

    def _calculate_roth_conversion(self, year):
        """
        Calculate Roth conversion amounts for the year without modifying balances.
        Returns total conversion amount and stores per-asset conversion amounts.
        Balance modifications happen in _apply_roth_conversions().
        """
        roth_conversion_start_year = self.scenario.roth_conversion_start_year
        roth_conversion_duration = self.scenario.roth_conversion_duration
        roth_conversion_annual_amount = getattr(self.scenario, 'roth_conversion_annual_amount', 0)
        
        # Convert to Decimal if it's not already
        if not isinstance(roth_conversion_annual_amount, Decimal):
            try:
                roth_conversion_annual_amount = Decimal(str(roth_conversion_annual_amount))
            except:
                roth_conversion_annual_amount = Decimal('0')

        # Add error handling for None values
        if roth_conversion_start_year is None or roth_conversion_duration is None:
            self._log_debug(f"Roth conversion parameters are not set: start_year={roth_conversion_start_year}, duration={roth_conversion_duration}")
            return Decimal('0')

        if year >= roth_conversion_start_year and year < roth_conversion_start_year + roth_conversion_duration:
            # Calculate pro-rata distribution WITHOUT modifying balances
            eligible_assets = [asset for asset in self.assets if 
                             asset["income_type"] in ["Qualified", "Inherited Traditional Spouse", "Inherited Traditional Non-Spouse"]
                             and asset.get("current_asset_balance", 0) > 0]
            
            if not eligible_assets:
                self._log_debug(f"Year {year} - No eligible assets for Roth conversion")
                return Decimal('0')
            
            total_eligible_balance = sum(Decimal(str(asset.get("current_asset_balance", 0))) for asset in eligible_assets)
            
            if total_eligible_balance == 0:
                self._log_debug(f"Year {year} - Total eligible balance is 0, no conversion possible")
                return Decimal('0')
            
            # Store conversion amounts for each asset (will be applied later)
            for asset in eligible_assets:
                asset_balance = Decimal(str(asset.get("current_asset_balance", 0)))
                depletion_ratio = asset_balance / total_eligible_balance
                asset_conversion_amount = roth_conversion_annual_amount * depletion_ratio
                # Store but don't apply yet
                asset["pending_roth_conversion"] = min(asset_conversion_amount, asset_balance)
            
            # Return total conversion amount for tax calculations
            return roth_conversion_annual_amount
        else:
            # Clear any pending conversions outside conversion window
            for asset in self.assets:
                asset["pending_roth_conversion"] = Decimal('0')
            return Decimal('0')

    def _calculate_asset_spend_down(self, year):
        """
        Implement the Asset Spend-Down & Growth Engine (STEP 7)
        Following IRS rules: RMDs must be taken before Roth conversions
        Order of operations:
        1. Update asset balances (growth, contributions)
        2. Calculate and apply RMDs 
        3. Apply Roth conversions
        4. Prevent negative balances
        """
        # Step 1: Update all asset balances (growth, contributions, regular withdrawals)
        for asset in self.assets:
            self._update_asset_balance(asset, year)
        
        # Step 2: Calculate and apply RMDs (must be done before conversions per IRS rules)
        for asset in self.assets:
            # Only calculate RMDs for assets that haven't been fully converted
            if asset.get("fully_converted_to_roth", False):
                asset["withdrawal_amount"] = Decimal('0')
                continue
                
            rmd_amount = self._calculate_rmd(asset, year)
            withdrawal_amount = Decimal(str(asset.get("withdrawal_amount", 0)))
            if rmd_amount > withdrawal_amount:
                asset["withdrawal_amount"] = rmd_amount
                # Actually withdraw the RMD
                asset["current_asset_balance"] = max(
                    Decimal('0'), 
                    Decimal(str(asset.get("current_asset_balance", 0))) - rmd_amount
                )
        
        # Step 3: Calculate Roth conversions (this just calculates, doesn't apply)
        total_conversion = self._calculate_roth_conversion(year)
        
        # Step 4: Apply the Roth conversions that were calculated
        if total_conversion > 0:
            self._apply_roth_conversions(year)
        
        # Step 5: Prevent negative balances
        for asset in self.assets:
            if asset.get("current_asset_balance", 0) < 0:
                asset["current_asset_balance"] = Decimal('0')

    def _apply_roth_conversions(self, year):
        """
        Apply Roth conversions that were calculated earlier.
        This method:
        1. Depletes traditional account balances
        2. Creates or updates Roth account balances
        3. Marks fully converted accounts
        """
        # Find or create a Roth account to receive conversions
        roth_account = None
        for asset in self.assets:
            if asset.get("income_type") == "Roth":
                roth_account = asset
                break
        
        # If no Roth account exists, create one
        if roth_account is None:
            roth_account = {
                "income_type": "Roth",
                "investment_name": "Roth IRA (Converted)",
                "current_asset_balance": Decimal('0'),
                "previous_year_balance": Decimal('0'),
                "rate_of_return": Decimal('0.06'),  # Default 6% growth
                "owned_by": "primary",
                "is_converted_roth": True
            }
            self.assets.append(roth_account)
            self._log_debug(f"Year {year} - Created new Roth account for conversions")
        
        # Apply conversions from each eligible asset
        total_converted = Decimal('0')
        for asset in self.assets:
            if asset.get("pending_roth_conversion", 0) > 0:
                conversion_amount = Decimal(str(asset["pending_roth_conversion"]))
                current_balance = Decimal(str(asset.get("current_asset_balance", 0)))
                
                # Can't convert more than available balance
                actual_conversion = min(conversion_amount, current_balance)
                
                # Deplete the traditional account
                asset["current_asset_balance"] = current_balance - actual_conversion
                
                # Add to Roth account
                roth_account["current_asset_balance"] = Decimal(str(roth_account.get("current_asset_balance", 0))) + actual_conversion
                
                # Track the conversion
                asset["roth_conversion_amount"] = actual_conversion
                total_converted += actual_conversion
                
                # Mark as fully converted if balance is now zero
                if asset["current_asset_balance"] <= Decimal('0.01'):  # Allow for rounding
                    asset["fully_converted_to_roth"] = True
                    asset["current_asset_balance"] = Decimal('0')
                    self._log_debug(f"Year {year} - Asset {asset.get('investment_name', 'Unknown')} fully converted to Roth")
                
                # Clear pending conversion
                asset["pending_roth_conversion"] = Decimal('0')
                
                self._log_debug(f"Year {year} - Converted ${actual_conversion:,.2f} from {asset.get('investment_name', 'Unknown')}")
        
        self._log_debug(f"Year {year} - Total Roth conversion: ${total_converted:,.2f}")
        return total_converted

    def _log_debug(self, message):
        if self.debug:
            print(f"🔍 Debug: {message}")

    def _calculate_inheritance_tax(self, final_year_data):
        """
        Calculate estimated inheritance tax based on remaining balances.
        This is a simplified model that can be enhanced with more specific tax rules.
        """
        # Get tax status for inheritance tax calculation
        tax_status = getattr(self.client, 'tax_status', 'Single').lower()
        
        # Extract traditional (taxable) and Roth (non-taxable) balances
        traditional_balances = Decimal('0')
        roth_balances = Decimal('0')
        
        # Look for any asset balance in the final year data
        for key, value in final_year_data.items():
            if key.endswith('_balance'):
                try:
                    balance = Decimal(str(value))
                    if 'roth' in key.lower():
                        roth_balances += balance
                    else:
                        traditional_balances += balance
                except (ValueError, TypeError):
                    pass
        
        # Apply simplified inheritance tax model
        # Traditional assets are subject to income tax for beneficiaries
        # Roth assets pass tax-free
        if tax_status in ['married filing jointly', 'qualifying widow(er)']:
            # Higher exemption for married couples
            tax_rate = Decimal('0.24')  # Simplified average tax rate for beneficiaries
        else:
            tax_rate = Decimal('0.22')  # Simplified average tax rate for beneficiaries
        
        inheritance_tax = traditional_balances * tax_rate
        
        self._log_debug(f"Inheritance tax calculation: Traditional balances: {traditional_balances}, Roth balances: {roth_balances}, Tax rate: {tax_rate}, Inheritance tax: {inheritance_tax}")
        
        return inheritance_tax


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
        # Avoid division by zero when calculating percentage
        if ss_benefits > 0:
            percentage = (taxable_ss / ss_benefits * 100)
            print(f"    Final Taxable SS: ${taxable_ss:,.2f} ({percentage:.1f}% of benefits)")
        else:
            print(f"    Final Taxable SS: ${taxable_ss:,.2f} (no SS benefits)")

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
