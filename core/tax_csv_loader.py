"""
CSV-Based Tax Configuration Loader

This module loads tax data from CSV files, making it easy to update
tax rates, brackets, and thresholds annually without code changes.
"""

import csv
import os
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any

class TaxCSVLoader:
    """Loads tax configuration data from CSV files."""
    
    def __init__(self, tax_year=2025):
        self.tax_year = tax_year
        self.data_dir = Path(__file__).parent / 'tax_data'
        self._cache = {}
    
    def _load_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Load CSV file and return list of dictionaries."""
        cache_key = f"{filename}_{self.tax_year}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Tax data file not found: {file_path}")
        
        data = []
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert numeric fields to Decimal
                converted_row = {}
                for key, value in row.items():
                    if key in ['min_income', 'max_income', 'tax_rate', 'deduction_amount', 
                              'magi_threshold', 'part_b_surcharge', 'part_d_surcharge',
                              'monthly_rate', 'base_threshold', 'additional_threshold',
                              'income_tax_rate', 'inflation_rate']:
                        try:
                            converted_row[key] = Decimal(value)
                        except:
                            converted_row[key] = value
                    elif key in ['ss_taxed']:
                        converted_row[key] = value.lower() == 'true'
                    elif key == 'retirement_income_exempt':
                        # Keep as string: 'true', 'false', or 'partial'
                        converted_row[key] = value.lower()
                    else:
                        converted_row[key] = value
                data.append(converted_row)
        
        self._cache[cache_key] = data
        return data
    
    def get_federal_tax_brackets(self, filing_status: str = "Single") -> List[Dict[str, Any]]:
        """Get federal tax brackets for filing status."""
        filename = f"federal_tax_brackets_{self.tax_year}.csv"
        data = self._load_csv(filename)
        
        # Filter by filing status
        brackets = [row for row in data if row['filing_status'].lower() == filing_status.lower()]
        
        # Sort by min_income
        brackets.sort(key=lambda x: x['min_income'])
        
        return brackets
    
    def get_standard_deduction(self, filing_status: str = "Single") -> Decimal:
        """Get standard deduction for filing status."""
        filename = f"standard_deductions_{self.tax_year}.csv"
        data = self._load_csv(filename)
        
        for row in data:
            if row['filing_status'].lower() == filing_status.lower():
                return row['deduction_amount']
        
        # Default to Single if not found
        for row in data:
            if row['filing_status'].lower() == 'single':
                return row['deduction_amount']
        
        return Decimal('15000')  # Fallback
    
    def get_irmaa_thresholds(self, filing_status: str = "Single") -> List[Dict[str, Any]]:
        """Get IRMAA thresholds for filing status."""
        filename = f"irmaa_thresholds_{self.tax_year}.csv"
        data = self._load_csv(filename)
        
        # Filter by filing status
        thresholds = [row for row in data if row['filing_status'].lower() == filing_status.lower()]
        
        # Sort by MAGI threshold
        thresholds.sort(key=lambda x: x['magi_threshold'])
        
        return thresholds
    
    def get_medicare_base_rates(self) -> Dict[str, Decimal]:
        """Get Medicare base rates."""
        filename = f"medicare_base_rates_{self.tax_year}.csv"
        data = self._load_csv(filename)
        
        rates = {}
        for row in data:
            # Convert coverage type to lowercase key
            key = row['coverage_type'].lower().replace(' ', '_')
            rates[key] = row['monthly_rate']
        
        return rates
    
    def get_social_security_thresholds(self, filing_status: str = "Single") -> Dict[str, Decimal]:
        """Get Social Security taxation thresholds."""
        filename = f"social_security_thresholds_{self.tax_year}.csv"
        data = self._load_csv(filename)
        
        for row in data:
            if row['filing_status'].lower() == filing_status.lower():
                return {
                    'base': row['base_threshold'],
                    'additional': row['additional_threshold']
                }
        
        # Default to Single if not found
        for row in data:
            if row['filing_status'].lower() == 'single':
                return {
                    'base': row['base_threshold'],
                    'additional': row['additional_threshold']
                }
        
        return {'base': Decimal('25000'), 'additional': Decimal('34000')}  # Fallback
    
    def get_inflation_rates(self) -> Dict[str, Decimal]:
        """Get inflation rates from configuration."""
        filename = "inflation_config.csv"
        data = self._load_csv(filename)
        
        rates = {}
        for row in data:
            rates[row['item']] = row['inflation_rate']
        
        return rates
    
    def get_inflated_irmaa_thresholds(self, filing_status: str, target_year: int, part_b_inflation_rate: Decimal = None, part_d_inflation_rate: Decimal = None) -> List[Dict[str, Any]]:
        """Get IRMAA thresholds inflated to target year."""
        base_thresholds = self.get_irmaa_thresholds(filing_status)
        inflation_rates = self.get_inflation_rates()

        # Get IRMAA threshold inflation rate (default 1% if not found)
        irmaa_inflation_rate = inflation_rates.get('irmaa_thresholds', Decimal('1.0')) / 100

        # Calculate years to inflate from base year to target year
        years_to_inflate = target_year - self.tax_year

        if years_to_inflate <= 0:
            return base_thresholds

        # Use provided inflation rates or default to 5% medical inflation
        if part_b_inflation_rate is None:
            part_b_inflation_rate = Decimal('0.05')
        if part_d_inflation_rate is None:
            part_d_inflation_rate = Decimal('0.05')

        inflated_thresholds = []
        for threshold in base_thresholds:
            inflated_threshold = threshold.copy()

            # Inflate the MAGI threshold (income levels) using IRMAA-specific inflation
            original_magi = threshold['magi_threshold']
            inflated_magi = original_magi * ((1 + irmaa_inflation_rate) ** years_to_inflate)
            inflated_threshold['magi_threshold'] = inflated_magi

            # Inflate the IRMAA surcharge amounts using provided inflation rates
            original_part_b = threshold['part_b_surcharge']
            original_part_d = threshold['part_d_surcharge']
            inflated_part_b = original_part_b * ((1 + part_b_inflation_rate) ** years_to_inflate)
            inflated_part_d = original_part_d * ((1 + part_d_inflation_rate) ** years_to_inflate)
            inflated_threshold['part_b_surcharge'] = inflated_part_b
            inflated_threshold['part_d_surcharge'] = inflated_part_d

            inflated_thresholds.append(inflated_threshold)

        return inflated_thresholds
    
    def calculate_irmaa_with_inflation(self, magi: Decimal, filing_status: str, target_year: int, part_b_inflation_rate: Decimal = None, part_d_inflation_rate: Decimal = None) -> tuple[Decimal, Decimal]:
        """Calculate IRMAA surcharges using inflated thresholds for target year."""
        thresholds = self.get_inflated_irmaa_thresholds(filing_status, target_year, part_b_inflation_rate, part_d_inflation_rate)

        part_b_surcharge = Decimal('0')
        part_d_surcharge = Decimal('0')

        for threshold in reversed(thresholds):  # Start from highest
            if magi > threshold['magi_threshold']:
                part_b_surcharge = threshold['part_b_surcharge']
                part_d_surcharge = threshold['part_d_surcharge']
                break

        return part_b_surcharge, part_d_surcharge
    
    def get_state_tax_info(self, state_code: str) -> Dict[str, Any]:
        """Get state tax information."""
        filename = f"state_tax_rates_{self.tax_year}.csv"
        data = self._load_csv(filename)
        
        for row in data:
            if row['state_code'].upper() == state_code.upper():
                return row
        
        # Default to no state tax if not found
        return {
            'state': 'Unknown',
            'state_code': state_code.upper(),
            'income_tax_rate': Decimal('0'),
            'retirement_income_exempt': 'true',
            'ss_taxed': False,
            'description': 'State not found'
        }
    
    def calculate_federal_tax(self, taxable_income: Decimal, filing_status: str = "Single") -> tuple[Decimal, str]:
        """Calculate federal tax using bracket data."""
        brackets = self.get_federal_tax_brackets(filing_status)
        
        tax = Decimal('0')
        previous_max = Decimal('0')
        current_bracket_rate = Decimal('0.10')
        
        for bracket in brackets:
            bracket_min = bracket['min_income']
            bracket_max = bracket['max_income']
            rate = bracket['tax_rate']
            
            # Handle the case where max_income is very large (representing infinity)
            if bracket_max >= Decimal('999999999'):
                bracket_max = taxable_income
            
            if taxable_income <= bracket_min:
                break
            
            # Calculate tax for this bracket
            taxable_in_bracket = min(taxable_income, bracket_max) - bracket_min
            if taxable_in_bracket > 0:
                tax += taxable_in_bracket * rate
                current_bracket_rate = rate
            
            if taxable_income <= bracket_max:
                break
        
        # Format bracket as percentage
        bracket_str = f"{int(current_bracket_rate * 100)}%"
        
        return tax, bracket_str
    
    def calculate_irmaa(self, magi: Decimal, filing_status: str = "Single") -> tuple[Decimal, Decimal]:
        """Calculate IRMAA surcharges based on MAGI."""
        thresholds = self.get_irmaa_thresholds(filing_status)
        
        part_b_surcharge = Decimal('0')
        part_d_surcharge = Decimal('0')
        
        for threshold in reversed(thresholds):  # Start from highest
            if magi > threshold['magi_threshold']:
                part_b_surcharge = threshold['part_b_surcharge']
                part_d_surcharge = threshold['part_d_surcharge']
                break
        
        return part_b_surcharge, part_d_surcharge
    
    def get_available_tax_years(self) -> List[int]:
        """Get list of available tax years based on CSV files."""
        years = set()

        for file in self.data_dir.glob("*.csv"):
            # Extract year from filename
            parts = file.stem.split('_')
            for part in parts:
                if part.isdigit() and len(part) == 4:
                    years.add(int(part))

        return sorted(list(years))

    def get_estate_tax_brackets(self) -> List[Dict[str, Any]]:
        """Get federal estate tax brackets."""
        # Try data dir first, then fall back to core/data directory
        filename = f"federal_estate_tax_brackets_{self.tax_year}.csv"

        # Try tax_data directory first
        file_path = self.data_dir / filename

        # Fall back to core/data directory
        if not file_path.exists():
            file_path = Path(__file__).parent / 'data' / filename

        if not file_path.exists():
            # Return default brackets if file not found
            return [{
                'income_min': Decimal('0'),
                'income_max': Decimal('13610000'),
                'tax_rate': Decimal('0.00'),
                'base_tax': Decimal('0')
            }, {
                'income_min': Decimal('13610000'),
                'income_max': Decimal('99999999999'),
                'tax_rate': Decimal('0.40'),
                'base_tax': Decimal('0')
            }]

        data = []
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append({
                    'income_min': Decimal(row['income_min']),
                    'income_max': Decimal(row['income_max']),
                    'tax_rate': Decimal(row['tax_rate']),
                    'base_tax': Decimal(row['base_tax'])
                })

        # Sort by min income
        data.sort(key=lambda x: x['income_min'])
        return data

    def calculate_estate_tax(self, total_estate_value: Decimal) -> Decimal:
        """Calculate federal estate tax on total estate value."""
        brackets = self.get_estate_tax_brackets()

        # Estate is below exemption threshold
        if not brackets:
            return Decimal('0')

        tax = Decimal('0')

        for bracket in brackets:
            bracket_min = bracket['income_min']
            bracket_max = bracket['income_max']
            rate = bracket['tax_rate']
            base_tax = bracket['base_tax']

            # If estate is below this bracket, no tax
            if total_estate_value <= bracket_min:
                break

            # If estate is in this bracket
            if total_estate_value > bracket_min:
                # Calculate amount subject to this bracket's rate
                taxable_amount = min(total_estate_value - bracket_min, bracket_max - bracket_min)
                tax = base_tax + (taxable_amount * rate)

                # If estate is within this bracket, we're done
                if total_estate_value <= bracket_max:
                    break

        return tax


# Convenience functions for current year
_current_loader = None

def get_tax_loader(tax_year=2025):
    """Get cached tax loader for specified year."""
    global _current_loader
    if _current_loader is None or _current_loader.tax_year != tax_year:
        _current_loader = TaxCSVLoader(tax_year)
    return _current_loader

def get_current_federal_brackets(filing_status="Single"):
    """Get current year federal tax brackets."""
    return get_tax_loader().get_federal_tax_brackets(filing_status)

def get_current_standard_deduction(filing_status="Single"):
    """Get current year standard deduction."""
    return get_tax_loader().get_standard_deduction(filing_status)

def get_current_irmaa_thresholds(filing_status="Single"):
    """Get current year IRMAA thresholds."""
    return get_tax_loader().get_irmaa_thresholds(filing_status)

def get_current_medicare_rates():
    """Get current year Medicare base rates."""
    return get_tax_loader().get_medicare_base_rates()

def get_current_ss_thresholds(filing_status="Single"):
    """Get current year Social Security taxation thresholds."""
    return get_tax_loader().get_social_security_thresholds(filing_status)

def calculate_current_federal_tax(taxable_income, filing_status="Single"):
    """Calculate federal tax using current year data."""
    return get_tax_loader().calculate_federal_tax(taxable_income, filing_status)

def calculate_current_irmaa(magi, filing_status="Single"):
    """Calculate IRMAA using current year data."""
    return get_tax_loader().calculate_irmaa(magi, filing_status)