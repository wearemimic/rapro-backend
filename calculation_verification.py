#!/usr/bin/env python
"""
Comprehensive Year-by-Year Calculation Verification System
===========================================================

This script independently verifies retirement planning calculations against the application's results.
It performs complete calculations from current year through mortality age and compares results
year-by-year to identify any discrepancies.

Usage:
    python calculation_verification.py <client_id> <scenario_id>

Example:
    python calculation_verification.py 4 6
"""

import os
import sys
import django
from decimal import Decimal, ROUND_HALF_UP
import datetime
from typing import Dict, List, Any, Tuple, Optional
import requests
import json
from dataclasses import dataclass

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')
django.setup()

from core.models import Client, Scenario, IncomeSource, Spouse
from core.tax_csv_loader import get_tax_loader
from core.scenario_processor import RMD_TABLE

@dataclass
class VerificationResult:
    """Class to hold verification results for a single year."""
    year: int
    my_gross_income: Decimal
    app_gross_income: Decimal
    my_federal_tax: Decimal
    app_federal_tax: Decimal
    my_medicare: Decimal
    app_medicare: Decimal
    my_net_income: Decimal
    app_net_income: Decimal
    gross_diff: Decimal
    tax_diff: Decimal
    medicare_diff: Decimal
    net_diff: Decimal
    status: str
    notes: str = ""

class RetirementCalculationVerifier:
    """Independent retirement calculation verifier."""
    
    def __init__(self, client_id: int, scenario_id: int):
        self.client_id = client_id
        self.scenario_id = scenario_id
        self.tax_loader = get_tax_loader()
        self.tolerance = Decimal('100')  # $100 tolerance
        self.percentage_tolerance = Decimal('0.01')  # 1% tolerance
        
        # Load data from database
        self._load_scenario_data()
        
    def _load_scenario_data(self):
        """Load complete scenario data from database."""
        try:
            self.client = Client.objects.get(id=self.client_id)
            self.scenario = Scenario.objects.get(id=self.scenario_id, client=self.client)
            self.income_sources = list(self.scenario.income_sources.all())
            self.spouse = getattr(self.client, 'spouse', None)
            
            print(f"✅ Loaded scenario data:")
            print(f"   Client: {self.client.first_name} {self.client.last_name}")
            print(f"   Scenario: {self.scenario.name}")
            print(f"   Income Sources: {len(self.income_sources)}")
            print(f"   Tax Status: {self.client.tax_status}")
            print(f"   Birth Date: {self.client.birthdate}")
            if self.spouse:
                print(f"   Spouse Birth Date: {self.spouse.birthdate}")
                
        except Exception as e:
            print(f"❌ Error loading scenario data: {e}")
            sys.exit(1)
    
    def _calculate_current_age(self, birthdate: datetime.date, year: int) -> int:
        """Calculate age for given year."""
        return year - birthdate.year
    
    def _calculate_social_security_cola_adjusted(self, base_amount: Decimal, start_year: int, current_year: int, cola: float = 0.025) -> Decimal:
        """Calculate Social Security with COLA adjustments."""
        if current_year < start_year:
            return Decimal('0')
        
        years_elapsed = current_year - start_year
        adjustment_factor = Decimal(str((1 + cola) ** years_elapsed))
        return base_amount * adjustment_factor
    
    def _calculate_taxable_social_security(self, ss_income: Decimal, agi_excl_ss: Decimal, filing_status: str) -> Decimal:
        """Calculate taxable portion of Social Security benefits."""
        if ss_income <= 0:
            return Decimal('0')
            
        provisional_income = agi_excl_ss + (ss_income * Decimal('0.5'))
        
        # Get thresholds based on filing status
        if filing_status == "Single":
            base_threshold = Decimal('25000')
            additional_threshold = Decimal('34000')
        else:  # Married Filing Jointly
            base_threshold = Decimal('32000')
            additional_threshold = Decimal('44000')
        
        if provisional_income <= base_threshold:
            return Decimal('0')
        elif provisional_income <= additional_threshold:
            # 50% of amount over base threshold, capped at 50% of benefits
            taxable_amount = (provisional_income - base_threshold) * Decimal('0.5')
            return min(taxable_amount, ss_income * Decimal('0.5'))
        else:
            # 85% of amount over additional threshold + 50% between thresholds, capped at 85% of benefits
            amount_over_additional = provisional_income - additional_threshold
            amount_between_thresholds = additional_threshold - base_threshold
            taxable_amount = (amount_over_additional * Decimal('0.85')) + (amount_between_thresholds * Decimal('0.5'))
            return min(taxable_amount, ss_income * Decimal('0.85'))
    
    def _calculate_federal_tax(self, taxable_income: Decimal, filing_status: str) -> Tuple[Decimal, str]:
        """Calculate federal tax using progressive brackets from CSV."""
        if taxable_income <= 0:
            return Decimal('0'), "0%"
            
        brackets = self.tax_loader.get_federal_tax_brackets(filing_status)
        tax = Decimal('0')
        top_bracket = "0%"
        
        for bracket in brackets:
            min_income = bracket['min_income']
            max_income = bracket.get('max_income')
            rate = bracket['tax_rate'] / 100  # Convert percentage to decimal
            
            if taxable_income <= min_income:
                break
                
            # Calculate tax for this bracket
            if max_income is None or taxable_income > max_income:
                # Tax the full bracket
                bracket_income = max_income - min_income if max_income else taxable_income - min_income
                top_bracket = f"{bracket['tax_rate']}%"
            else:
                # Partial bracket
                bracket_income = taxable_income - min_income
                top_bracket = f"{bracket['tax_rate']}%"
                
            bracket_tax = bracket_income * rate
            tax += bracket_tax
            
            if max_income and taxable_income <= max_income:
                break
                
        return tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), top_bracket
    
    def _calculate_medicare_costs(self, magi: Decimal, filing_status: str) -> Tuple[Decimal, Decimal]:
        """Calculate Medicare Part B and Part D costs including IRMAA."""
        base_rates = self.tax_loader.get_medicare_base_rates()
        part_b_base = base_rates['part_b_monthly']
        part_d_base = base_rates['part_d_monthly']
        
        # Get IRMAA thresholds
        irmaa_thresholds = self.tax_loader.get_irmaa_thresholds(filing_status)
        
        part_b_surcharge = Decimal('0')
        part_d_surcharge = Decimal('0')
        
        for threshold in reversed(irmaa_thresholds):
            if magi >= threshold['magi_threshold']:
                part_b_surcharge = threshold['part_b_surcharge']
                part_d_surcharge = threshold['part_d_surcharge']
                break
        
        total_part_b = (part_b_base + part_b_surcharge) * 12
        total_part_d = (part_d_base + part_d_surcharge) * 12
        
        return total_part_b, total_part_d
    
    def _calculate_asset_value_and_withdrawal(self, asset_data: Dict, year: int, owner_age: int) -> Tuple[Decimal, Decimal]:
        """Calculate asset value and withdrawal for a given year."""
        # Get asset parameters
        current_balance = Decimal(str(asset_data.get('current_asset_balance', 0)))
        rate_of_return = Decimal(str(asset_data.get('rate_of_return', 0))) / 100
        monthly_amount = Decimal(str(asset_data.get('monthly_amount', 0)))
        monthly_contribution = Decimal(str(asset_data.get('monthly_contribution', 0)))
        age_begin = asset_data.get('age_to_begin_withdrawal', 65)
        age_end = asset_data.get('age_to_end_withdrawal', 90)
        is_contributing = asset_data.get('is_contributing', False)
        age_last_contribution = asset_data.get('age_last_contribution', 65)
        
        # Calculate years elapsed from current year
        current_year = datetime.datetime.now().year
        years_elapsed = year - current_year
        
        # Apply growth and contributions to get current year balance
        projected_balance = current_balance
        
        # Apply growth and contributions for each year
        for i in range(years_elapsed):
            # Apply growth
            projected_balance = projected_balance * (1 + rate_of_return)
            
            # Add contributions if still contributing
            contribution_age = owner_age - years_elapsed + i
            if is_contributing and contribution_age <= age_last_contribution and monthly_contribution > 0:
                annual_contribution = monthly_contribution * 12
                projected_balance += annual_contribution
        
        # Calculate withdrawal
        withdrawal = Decimal('0')
        if age_begin <= owner_age <= age_end:
            if monthly_amount > 0:
                withdrawal = monthly_amount * 12
            else:
                # Check for RMD if applicable
                income_type = asset_data.get('income_type', '').lower()
                if 'qualified' in income_type or '401' in income_type or 'traditional' in income_type:
                    if owner_age >= 72:  # RMD age
                        rmd_divisor = RMD_TABLE.get(owner_age, 1)
                        withdrawal = projected_balance / Decimal(str(rmd_divisor))
        
        return projected_balance, withdrawal
    
    def _calculate_gross_income_for_year(self, year: int) -> Tuple[Decimal, Decimal, Decimal]:
        """Calculate gross income, Social Security income, and other income for a year."""
        primary_age = self._calculate_current_age(self.client.birthdate, year)
        spouse_age = self._calculate_current_age(self.spouse.birthdate, year) if self.spouse else None
        
        total_income = Decimal('0')
        ss_income_total = Decimal('0')
        ss_income_primary = Decimal('0')
        ss_income_spouse = Decimal('0')
        
        # Process each income source
        for income_source in self.income_sources:
            owner = income_source.owned_by
            owner_age = primary_age if owner == 'primary' else spouse_age
            
            if owner_age is None:
                continue
                
            income_type = income_source.income_type.lower()
            
            # Handle Social Security separately
            if 'social security' in income_type:
                monthly_amount = income_source.monthly_amount or Decimal('0')
                age_begin = income_source.age_to_begin_withdrawal or 65
                
                if owner_age >= age_begin:
                    # Apply COLA adjustment
                    start_year = (self.client.birthdate.year if owner == 'primary' else self.spouse.birthdate.year) + age_begin
                    cola_rate = income_source.cola or 0.025
                    annual_ss = self._calculate_social_security_cola_adjusted(monthly_amount * 12, start_year, year, cola_rate)
                    
                    ss_income_total += annual_ss
                    if owner == 'primary':
                        ss_income_primary += annual_ss
                    else:
                        ss_income_spouse += annual_ss
                        
            else:
                # Handle investment accounts and other income
                projected_balance, withdrawal = self._calculate_asset_value_and_withdrawal({
                    'current_asset_balance': income_source.current_asset_balance or 0,
                    'rate_of_return': income_source.rate_of_return or 0,
                    'monthly_amount': income_source.monthly_amount or 0,
                    'monthly_contribution': income_source.monthly_contribution or 0,
                    'age_to_begin_withdrawal': income_source.age_to_begin_withdrawal,
                    'age_to_end_withdrawal': income_source.age_to_end_withdrawal,
                    'is_contributing': income_source.is_contributing,
                    'age_last_contribution': income_source.age_last_contribution,
                    'income_type': income_source.income_type
                }, year, owner_age)
                
                total_income += withdrawal
        
        # Add Social Security to total income
        total_income += ss_income_total
        
        return total_income, ss_income_total, ss_income_primary + ss_income_spouse
    
    def calculate_year_independently(self, year: int) -> Dict[str, Any]:
        """Calculate all financial metrics for a single year independently."""
        primary_age = self._calculate_current_age(self.client.birthdate, year)
        spouse_age = self._calculate_current_age(self.spouse.birthdate, year) if self.spouse else None
        
        # Calculate gross income
        gross_income, ss_income, ss_breakdown = self._calculate_gross_income_for_year(year)
        
        # Calculate AGI excluding Social Security
        agi_excl_ss = gross_income - ss_income
        
        # Calculate taxable Social Security
        taxable_ss = self._calculate_taxable_social_security(ss_income, agi_excl_ss, self.client.tax_status)
        
        # Calculate taxable income
        taxable_income = agi_excl_ss + taxable_ss
        
        # Apply standard deduction if enabled
        if getattr(self.scenario, 'apply_standard_deduction', True):
            standard_deduction = self.tax_loader.get_standard_deduction(self.client.tax_status)
            taxable_income = max(Decimal('0'), taxable_income - standard_deduction)
        
        # Calculate federal tax
        federal_tax, tax_bracket = self._calculate_federal_tax(taxable_income, self.client.tax_status)
        
        # Calculate Medicare costs (use gross income as MAGI approximation)
        part_b_cost, part_d_cost = self._calculate_medicare_costs(gross_income, self.client.tax_status)
        total_medicare = part_b_cost + part_d_cost
        
        # Calculate net income
        net_income = gross_income - federal_tax - total_medicare
        
        return {
            'year': year,
            'primary_age': primary_age,
            'spouse_age': spouse_age,
            'gross_income': gross_income,
            'ss_income': ss_income,
            'agi_excl_ss': agi_excl_ss,
            'taxable_ss': taxable_ss,
            'taxable_income_before_deduction': agi_excl_ss + taxable_ss,
            'taxable_income_after_deduction': taxable_income,
            'federal_tax': federal_tax,
            'tax_bracket': tax_bracket,
            'medicare_part_b': part_b_cost,
            'medicare_part_d': part_d_cost,
            'total_medicare': total_medicare,
            'net_income': net_income
        }
    
    def get_application_results(self) -> List[Dict[str, Any]]:
        """Get calculation results from the application API."""
        try:
            # Note: In a real implementation, you'd make an HTTP request to the API
            # For this verification, we'll import the scenario processor directly
            from core.scenario_processor import ScenarioProcessor
            
            processor = ScenarioProcessor(self.scenario_id)
            results = processor.calculate()
            
            return results
        except Exception as e:
            print(f"❌ Error getting application results: {e}")
            return []
    
    def compare_results(self, my_result: Dict[str, Any], app_result: Dict[str, Any]) -> VerificationResult:
        """Compare my calculations with application results."""
        year = my_result['year']
        
        # Extract values with safe defaults
        my_gross = my_result.get('gross_income', Decimal('0'))
        app_gross = Decimal(str(app_result.get('gross_income', 0)))
        
        my_tax = my_result.get('federal_tax', Decimal('0'))
        app_tax = Decimal(str(app_result.get('federal_tax', 0)))
        
        my_medicare = my_result.get('total_medicare', Decimal('0'))
        app_medicare = Decimal(str(app_result.get('total_medicare', 0)))
        
        my_net = my_result.get('net_income', Decimal('0'))
        app_net = Decimal(str(app_result.get('net_income', 0)))
        
        # Calculate differences
        gross_diff = abs(my_gross - app_gross)
        tax_diff = abs(my_tax - app_tax)
        medicare_diff = abs(my_medicare - app_medicare)
        net_diff = abs(my_net - app_net)
        
        # Determine status
        status = "✅"
        notes = ""
        
        # Check for significant differences
        if (gross_diff > self.tolerance or 
            tax_diff > self.tolerance or 
            medicare_diff > self.tolerance or 
            net_diff > self.tolerance):
            status = "❌"
            
            # Add specific notes about what differs
            if gross_diff > self.tolerance:
                notes += f"Gross income differs by ${gross_diff:,.2f}. "
            if tax_diff > self.tolerance:
                notes += f"Federal tax differs by ${tax_diff:,.2f}. "
            if medicare_diff > self.tolerance:
                notes += f"Medicare costs differ by ${medicare_diff:,.2f}. "
        
        return VerificationResult(
            year=year,
            my_gross_income=my_gross,
            app_gross_income=app_gross,
            my_federal_tax=my_tax,
            app_federal_tax=app_tax,
            my_medicare=my_medicare,
            app_medicare=app_medicare,
            my_net_income=my_net,
            app_net_income=app_net,
            gross_diff=gross_diff,
            tax_diff=tax_diff,
            medicare_diff=medicare_diff,
            net_diff=net_diff,
            status=status,
            notes=notes.strip()
        )
    
    def run_verification(self) -> List[VerificationResult]:
        """Run complete verification process."""
        print("\n" + "="*80)
        print("RETIREMENT CALCULATION VERIFICATION")
        print("="*80)
        
        print(f"\nCONFIGURATION SUMMARY:")
        print(f"Client: {self.client.first_name} {self.client.last_name}")
        print(f"Scenario: {self.scenario.name}")
        print(f"Birth Date: {self.client.birthdate}")
        print(f"Tax Status: {self.client.tax_status}")
        print(f"Retirement Age: {self.scenario.retirement_age}")
        print(f"Mortality Age: {self.scenario.mortality_age}")
        if self.spouse:
            print(f"Spouse Birth Date: {self.spouse.birthdate}")
            print(f"Spouse Retirement Age: {self.scenario.spouse_retirement_age}")
            print(f"Spouse Mortality Age: {self.scenario.spouse_mortality_age}")
        
        print(f"\nINCOME SOURCES ({len(self.income_sources)}):")
        for i, source in enumerate(self.income_sources, 1):
            print(f"{i}. {source.income_type} ({source.owned_by})")
            if source.monthly_amount:
                print(f"   Monthly Amount: ${source.monthly_amount:,.2f}")
            if source.current_asset_balance:
                print(f"   Current Balance: ${source.current_asset_balance:,.2f}")
            print(f"   Withdrawal Ages: {source.age_to_begin_withdrawal}-{source.age_to_end_withdrawal}")
        
        # Get application results
        print(f"\n📊 Getting application calculation results...")
        app_results = self.get_application_results()
        
        if not app_results:
            print("❌ No application results available for comparison")
            return []
        
        print(f"✅ Retrieved {len(app_results)} years of application data")
        
        # Calculate years to verify
        current_year = datetime.datetime.now().year
        end_year = self.client.birthdate.year + self.scenario.mortality_age
        
        results = []
        
        print(f"\n🔍 Performing year-by-year verification from {current_year} to {end_year}...")
        
        for year in range(current_year, end_year + 1):
            # Find corresponding application result
            app_result = next((r for r in app_results if r.get('year') == year), None)
            
            if not app_result:
                print(f"⚠️  No application data for year {year}")
                continue
            
            # Calculate independently
            my_result = self.calculate_year_independently(year)
            
            # Compare results
            comparison = self.compare_results(my_result, app_result)
            results.append(comparison)
        
        return results
    
    def print_verification_report(self, results: List[VerificationResult]):
        """Print comprehensive verification report."""
        print("\n" + "="*120)
        print("YEAR-BY-YEAR COMPARISON REPORT")
        print("="*120)
        
        # Print header
        print(f"{'Year':<6} {'My Gross':<12} {'App Gross':<12} {'My Tax':<10} {'App Tax':<10} {'My Medicare':<12} {'App Medicare':<12} {'Net Diff':<10} {'Status':<6}")
        print("-" * 120)
        
        discrepancy_count = 0
        total_years = len(results)
        
        # Print each year
        for result in results:
            if result.status == "❌":
                discrepancy_count += 1
                
            print(f"{result.year:<6} "
                  f"${result.my_gross_income:<11,.0f} "
                  f"${result.app_gross_income:<11,.0f} "
                  f"${result.my_federal_tax:<9,.0f} "
                  f"${result.app_federal_tax:<9,.0f} "
                  f"${result.my_medicare:<11,.0f} "
                  f"${result.app_medicare:<11,.0f} "
                  f"${result.net_diff:<9,.0f} "
                  f"{result.status:<6}")
        
        print("-" * 120)
        
        # Print summary
        print(f"\nVERIFICATION SUMMARY:")
        print(f"Total Years Verified: {total_years}")
        print(f"Years with Discrepancies: {discrepancy_count}")
        print(f"Accuracy Rate: {((total_years - discrepancy_count) / total_years * 100):.1f}%" if total_years > 0 else "N/A")
        
        # Print discrepancy details
        if discrepancy_count > 0:
            print(f"\n🚨 DISCREPANCIES FOUND:")
            for result in results:
                if result.status == "❌":
                    print(f"\nYear {result.year}:")
                    print(f"  {result.notes}")
                    print(f"  Gross Income: My ${result.my_gross_income:,.2f} vs App ${result.app_gross_income:,.2f} (${result.gross_diff:,.2f} diff)")
                    print(f"  Federal Tax:  My ${result.my_federal_tax:,.2f} vs App ${result.app_federal_tax:,.2f} (${result.tax_diff:,.2f} diff)")
                    print(f"  Medicare:     My ${result.my_medicare:,.2f} vs App ${result.app_medicare:,.2f} (${result.medicare_diff:,.2f} diff)")
        
        # Print recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if discrepancy_count == 0:
            print("✅ All calculations verified successfully! No issues found.")
        else:
            print("❌ Calculation discrepancies found. Recommend:")
            print("   1. Review asset growth calculations")
            print("   2. Verify Social Security COLA adjustments")
            print("   3. Check tax bracket application")
            print("   4. Validate Medicare IRMAA calculations")
            print("   5. Review RMD calculations for qualified accounts")


def main():
    """Main entry point for the verification script."""
    if len(sys.argv) != 3:
        print("Usage: python calculation_verification.py <client_id> <scenario_id>")
        print("Example: python calculation_verification.py 4 6")
        sys.exit(1)
    
    try:
        client_id = int(sys.argv[1])
        scenario_id = int(sys.argv[2])
    except ValueError:
        print("❌ Client ID and Scenario ID must be integers")
        sys.exit(1)
    
    # Create verifier and run verification
    verifier = RetirementCalculationVerifier(client_id, scenario_id)
    results = verifier.run_verification()
    verifier.print_verification_report(results)


if __name__ == "__main__":
    main()