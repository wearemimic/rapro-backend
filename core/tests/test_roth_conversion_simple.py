"""
Simple test script for the RothConversionProcessor.

This script tests the RothConversionProcessor without Django or database dependencies.
"""

import sys
import os
from decimal import Decimal
from datetime import datetime, date
import copy
import json

# Add the parent directory to the path so we can import the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# Create mock classes to replace Django dependencies
class ScenarioProcessor:
    @classmethod
    def from_dicts(cls, scenario, client, spouse, assets, debug=False):
        instance = cls()
        instance.scenario = scenario
        instance.client = client
        instance.spouse = spouse
        instance.assets = assets
        instance.debug = debug
        return instance
        
    def calculate(self):
        # Return a simplified result set
        current_year = datetime.now().year
        years = range(current_year, current_year + 30)
        results = []
        
        for year in years:
            row = {
                'year': year,
                'federal_tax': 10000 + (year - years[0]) * 500,
                'medicare_base': 2000 + (year - years[0]) * 100,
                'irmaa_surcharge': 500 + (year - years[0]) * 50,
                'net_income': 80000 + (year - years[0]) * 1000,
            }
            
            # Add asset balances
            for asset in self.assets:
                asset_id = asset.get('id') or asset.get('income_type')
                balance = float(asset.get('current_asset_balance', 0))
                
                # Simple growth model
                growth_rate = asset.get('rate_of_return', 5.0) / 100
                years_passed = year - years[0]
                
                # If this is a Roth asset in the conversion scenario
                if asset.get('is_synthetic_roth', False) and hasattr(self, 'scenario'):
                    # Add conversion amount for the first N years
                    if years_passed < 5:  # Assuming 5 years of conversion
                        conversion_amount = 0
                        if hasattr(self.scenario, 'roth_conversion_annual_amount'):
                            conversion_amount = float(self.scenario.roth_conversion_annual_amount or 0)
                        balance += conversion_amount * (years_passed + 1)
                
                # Apply growth
                balance *= (1 + growth_rate) ** years_passed
                
                # Add RMD if applicable
                rmd = 0
                if 'traditional' in asset.get('income_type', '').lower() and years_passed >= 12:  # RMD age
                    rmd = balance * 0.04  # Simplified RMD calculation
                    balance -= rmd
                    
                row[f"{asset_id}_balance"] = balance
                row[f"{asset_id}_rmd"] = rmd
            
            results.append(row)
            
        return results

# Define the RothConversionProcessor class with mocked dependencies
class RothConversionProcessor:
    """
    Process Roth conversion scenarios based on user inputs.
    
    This class extends ScenarioProcessor functionality to model the impact of
    Roth conversions on retirement scenarios, including tax implications,
    asset growth, and Medicare/IRMAA costs.
    """
    
    def __init__(self, scenario, client, spouse, assets, conversion_params):
        """
        Initialize the Roth Conversion Processor.
        
        Parameters:
        - scenario: Dictionary containing scenario data
        - client: Dictionary containing client data
        - spouse: Dictionary containing spouse data (or None)
        - assets: List of dictionaries containing asset data
        - conversion_params: Dictionary with conversion parameters:
            - conversion_start_year: Year to begin conversions
            - years_to_convert: Duration of conversion period
            - pre_retirement_income: Income before retirement
            - roth_growth_rate: Annual growth rate for Roth assets
            - max_annual_amount: Maximum annual conversion amount
            - roth_withdrawal_amount: Annual withdrawal from Roth
            - roth_withdrawal_start_year: Year to begin Roth withdrawals
            - asset_conversion_map: Dictionary mapping asset IDs to conversion amounts
        """
        self.scenario = scenario
        self.client = client
        self.spouse = spouse
        self.assets = copy.deepcopy(assets)  # Deep copy to avoid modifying original
        self.conversion_params = conversion_params
        
        # Extract conversion parameters
        self.conversion_start_year = int(conversion_params.get('conversion_start_year', datetime.now().year))
        self.years_to_convert = int(conversion_params.get('years_to_convert', 1))
        self.pre_retirement_income = Decimal(str(conversion_params.get('pre_retirement_income', '0')))
        self.roth_growth_rate = float(conversion_params.get('roth_growth_rate', 5.0))
        self.max_annual_amount = Decimal(str(conversion_params.get('max_annual_amount', '0')))
        self.roth_withdrawal_amount = Decimal(str(conversion_params.get('roth_withdrawal_amount', '0')))
        self.roth_withdrawal_start_year = int(conversion_params.get('roth_withdrawal_start_year', 0))
        
        # Calculate retirement year
        self.retirement_year = self._calculate_retirement_year()
        
        # Initialize baseline and conversion scenarios
        self.baseline_scenario = None
        self.conversion_scenario = None
        
        # Initialize results
        self.baseline_results = None
        self.conversion_results = None
        self.comparison = None
        
    def _calculate_retirement_year(self):
        """Calculate the retirement year based on client birthdate and retirement age."""
        try:
            retirement_age = int(self.scenario.get('retirement_age', 65))
            
            if isinstance(self.client.get('birthdate'), str):
                birth_year = datetime.strptime(self.client['birthdate'], '%Y-%m-%d').year
            else:
                birth_year = self.client.get('birthdate').year
                
            return birth_year + retirement_age
        except Exception as e:
            print(f"Error calculating retirement year: {e}")
            # Default to 5 years from now
            return datetime.now().year + 5
            
    def _prepare_assets_for_conversion(self):
        """
        Prepare assets for conversion by identifying convertible assets and
        applying the conversion amounts specified in the parameters.
        """
        # Identify Roth-convertible assets (IRA, 401k)
        convertible_assets = []
        for asset in self.assets:
            asset_type = asset.get('income_type', '').lower()
            if asset_type in ['traditional_401k', 'traditional_ira', 'ira', '401k']:
                convertible_assets.append(asset)
                
        # Calculate total conversion amount from asset_conversion_map
        total_conversion = Decimal('0')
        for asset in self.assets:
            asset_id = asset.get('id') or asset.get('income_type')
            max_to_convert = asset.get('max_to_convert', 0)
            
            if max_to_convert:
                try:
                    max_to_convert = Decimal(str(max_to_convert))
                    total_conversion += max_to_convert
                    # Store the conversion amount in the asset
                    asset['roth_conversion_total'] = max_to_convert
                except (ValueError, TypeError):
                    print(f"Warning: Invalid max_to_convert value: {max_to_convert}")
                    asset['roth_conversion_total'] = Decimal('0')
            else:
                asset['roth_conversion_total'] = Decimal('0')
                
        # Calculate annual conversion amount
        if self.years_to_convert > 0:
            annual_conversion = total_conversion / Decimal(str(self.years_to_convert))
            
            # Apply max_annual_amount constraint if specified
            if self.max_annual_amount > 0 and annual_conversion > self.max_annual_amount:
                annual_conversion = self.max_annual_amount
                # Recalculate years needed for conversion
                self.years_to_convert = int((total_conversion / annual_conversion).quantize(Decimal('1')))
        else:
            annual_conversion = Decimal('0')
            
        # Store annual conversion amount
        self.annual_conversion = annual_conversion
        self.total_conversion = total_conversion
        
        # Create synthetic Roth asset for tracking conversions
        roth_asset = {
            'income_type': 'roth_ira',
            'income_name': 'Converted Roth IRA',
            'owned_by': self.assets[0].get('owned_by', 'primary') if self.assets else 'primary',
            'current_asset_balance': Decimal('0'),
            'monthly_amount': Decimal('0'),
            'monthly_contribution': Decimal('0'),
            'age_to_begin_withdrawal': 0,  # Will be calculated based on withdrawal_start_year
            'age_to_end_withdrawal': 100,  # Arbitrary high age
            'rate_of_return': self.roth_growth_rate,
            'cola': 0,
            'exclusion_ratio': 0,
            'tax_rate': 0,
            'is_synthetic_roth': True  # Mark as synthetic for special handling
        }
        
        # Add synthetic Roth asset to assets list
        self.assets.append(roth_asset)
        
        return annual_conversion, total_conversion
        
    def _prepare_baseline_scenario(self):
        """Prepare the baseline scenario without Roth conversions."""
        baseline_scenario = copy.deepcopy(self.scenario)
        
        # Ensure Roth conversion fields are None/zero
        baseline_scenario['roth_conversion_start_year'] = None
        baseline_scenario['roth_conversion_duration'] = None
        baseline_scenario['roth_conversion_annual_amount'] = None
        
        # Ensure required fields are present
        if 'part_b_inflation_rate' not in baseline_scenario:
            baseline_scenario['part_b_inflation_rate'] = 3.0
        if 'part_d_inflation_rate' not in baseline_scenario:
            baseline_scenario['part_d_inflation_rate'] = 3.0
        if 'retirement_age' not in baseline_scenario:
            baseline_scenario['retirement_age'] = 65
        if 'mortality_age' not in baseline_scenario:
            baseline_scenario['mortality_age'] = 90
            
        return baseline_scenario
        
    def _prepare_conversion_scenario(self):
        """Prepare the scenario with Roth conversions."""
        conversion_scenario = copy.deepcopy(self.scenario)
        
        # Set Roth conversion parameters
        conversion_scenario['roth_conversion_start_year'] = self.conversion_start_year
        conversion_scenario['roth_conversion_duration'] = self.years_to_convert
        conversion_scenario['roth_conversion_annual_amount'] = self.annual_conversion
        
        # Add pre-retirement income if applicable
        if self.pre_retirement_income > 0:
            conversion_scenario['pre_retirement_income'] = self.pre_retirement_income
            
        # Ensure required fields are present
        if 'part_b_inflation_rate' not in conversion_scenario:
            conversion_scenario['part_b_inflation_rate'] = 3.0
        if 'part_d_inflation_rate' not in conversion_scenario:
            conversion_scenario['part_d_inflation_rate'] = 3.0
        if 'retirement_age' not in conversion_scenario:
            conversion_scenario['retirement_age'] = 65
        if 'mortality_age' not in conversion_scenario:
            conversion_scenario['mortality_age'] = 90
            
        return conversion_scenario
        
    def _extract_metrics(self, results):
        """
        Extract key metrics from scenario results.
        """
        if not results:
            return {}
            
        # Helper function to safely convert values to float
        def safe_float(value):
            try:
                if isinstance(value, Decimal):
                    return float(value)
                return float(value) if value is not None else 0.0
            except (ValueError, TypeError):
                return 0.0
                
        # Initialize metrics
        metrics = {
            'lifetime_tax': 0.0,
            'lifetime_medicare': 0.0,
            'total_irmaa': 0.0,
            'total_rmds': 0.0,
            'cumulative_net_income': 0.0,
            'final_roth': 0.0,
            'inheritance_tax': 0.0
        }
        
        # Sum up metrics from year-by-year results
        for row in results:
            metrics['lifetime_tax'] += safe_float(row.get('federal_tax', 0))
            metrics['lifetime_medicare'] += safe_float(row.get('medicare_base', 0))
            metrics['total_irmaa'] += safe_float(row.get('irmaa_surcharge', 0))
            
            # Sum up RMDs across all assets
            rmd_total = 0.0
            for key, value in row.items():
                if key.endswith('_rmd'):
                    rmd_total += safe_float(value)
            metrics['total_rmds'] += rmd_total
            
            # Track net income
            metrics['cumulative_net_income'] += safe_float(row.get('net_income', 0))
            
        # Get final Roth balance from the last year
        if results:
            final_year = results[-1]
            for key, value in final_year.items():
                if key.endswith('_balance') and 'roth' in key.lower():
                    metrics['final_roth'] += safe_float(value)
                    
        # Calculate inheritance tax
        metrics['inheritance_tax'] = self._calculate_inheritance_tax(results[-1] if results else {})
                    
        return metrics
    
    def _calculate_inheritance_tax(self, final_year_data):
        """
        Calculate estimated inheritance tax based on final year balances.
        
        This is a simplified calculation for demonstration purposes.
        """
        # Helper function to safely convert values to float
        def safe_float(value):
            try:
                if isinstance(value, Decimal):
                    return float(value)
                return float(value) if value is not None else 0.0
            except (ValueError, TypeError):
                return 0.0
                
        # Sum up all non-Roth balances
        taxable_inheritance = 0.0
        for key, value in final_year_data.items():
            if key.endswith('_balance') and 'roth' not in key.lower():
                taxable_inheritance += safe_float(value)
                
        # Apply a simplified inheritance tax rate (for demonstration)
        # In reality, this would depend on estate tax laws, state laws, etc.
        if taxable_inheritance > 12900000:  # 2023 federal estate tax exemption
            return (taxable_inheritance - 12900000) * 0.40  # 40% federal estate tax rate
        else:
            return 0.0
            
    def _compare_metrics(self, baseline, conversion):
        """
        Compare metrics between baseline and conversion scenarios.
        
        Returns a dictionary with the differences and percentages.
        """
        # Helper function to safely convert values to float
        def safe_float(value):
            try:
                if isinstance(value, Decimal):
                    return float(value)
                return float(value) if value is not None else 0.0
            except (ValueError, TypeError):
                return 0.0
                
        # Helper function to calculate percent change
        def percent_change(old, new):
            if old == 0:
                return 0.0 if new == 0 else 100.0
            return ((new - old) / abs(old)) * 100.0
                
        comparison = {}
        
        # Calculate differences and percentages for each metric
        for key in baseline.keys():
            baseline_val = safe_float(baseline.get(key, 0))
            conversion_val = safe_float(conversion.get(key, 0))
            
            difference = conversion_val - baseline_val
            pct_change = percent_change(baseline_val, conversion_val)
            
            comparison[key] = {
                'baseline': baseline_val,
                'conversion': conversion_val,
                'difference': difference,
                'percent_change': pct_change
            }
            
        # Calculate total expenses
        baseline_expenses = (
            safe_float(baseline.get('lifetime_tax', 0)) +
            safe_float(baseline.get('lifetime_medicare', 0)) +
            safe_float(baseline.get('total_irmaa', 0)) +
            safe_float(baseline.get('inheritance_tax', 0))
        )
        
        conversion_expenses = (
            safe_float(conversion.get('lifetime_tax', 0)) +
            safe_float(conversion.get('lifetime_medicare', 0)) +
            safe_float(conversion.get('total_irmaa', 0)) +
            safe_float(conversion.get('inheritance_tax', 0))
        )
        
        expense_difference = conversion_expenses - baseline_expenses
        expense_pct_change = percent_change(baseline_expenses, conversion_expenses)
        
        comparison['total_expenses'] = {
            'baseline': baseline_expenses,
            'conversion': conversion_expenses,
            'difference': expense_difference,
            'percent_change': expense_pct_change
        }
        
        return comparison
        
    def _extract_asset_balances(self, baseline_results, conversion_results):
        """
        Extract asset balance projections for visualization.
        
        Returns a dictionary with year-by-year asset balances for both scenarios.
        """
        # Initialize asset balance data
        asset_balances = {
            'years': [],
            'baseline': {},
            'conversion': {}
        }
        
        # Extract years and asset balances from baseline results
        for row in baseline_results:
            year = row.get('year')
            if year:
                asset_balances['years'].append(year)
                
                # Extract asset balances
                for key, value in row.items():
                    if key.endswith('_balance'):
                        asset_name = key.replace('_balance', '')
                        if asset_name not in asset_balances['baseline']:
                            asset_balances['baseline'][asset_name] = []
                        asset_balances['baseline'][asset_name].append(float(value) if value is not None else 0.0)
                        
        # Extract asset balances from conversion results
        for row in conversion_results:
            year = row.get('year')
            if year:
                # Extract asset balances
                for key, value in row.items():
                    if key.endswith('_balance'):
                        asset_name = key.replace('_balance', '')
                        if asset_name not in asset_balances['conversion']:
                            asset_balances['conversion'][asset_name] = []
                        asset_balances['conversion'][asset_name].append(float(value) if value is not None else 0.0)
                        
        return asset_balances
        
    def process(self):
        """
        Process the Roth conversion scenario and return the results.
        
        Returns a dictionary with:
        - baseline_results: Year-by-year results without conversion
        - conversion_results: Year-by-year results with conversion
        - metrics: Comparison of key metrics between scenarios
        - asset_balances: Asset balance projections for visualization
        """
        # Prepare assets for conversion
        annual_conversion, total_conversion = self._prepare_assets_for_conversion()
        
        # Prepare baseline and conversion scenarios
        baseline_scenario = self._prepare_baseline_scenario()
        conversion_scenario = self._prepare_conversion_scenario()
        
        # Create ScenarioProcessor instances for both scenarios
        baseline_processor = ScenarioProcessor.from_dicts(
            baseline_scenario,
            self.client,
            self.spouse,
            copy.deepcopy(self.assets),  # Use a copy to avoid modifications
            debug=False
        )
        
        conversion_processor = ScenarioProcessor.from_dicts(
            conversion_scenario,
            self.client,
            self.spouse,
            self.assets,  # Use the modified assets with Roth conversions
            debug=False
        )
        
        # Calculate results for both scenarios
        baseline_results = baseline_processor.calculate()
        conversion_results = conversion_processor.calculate()
        
        # Store results for reference
        self.baseline_results = baseline_results
        self.conversion_results = conversion_results
        
        # Extract metrics from results
        baseline_metrics = self._extract_metrics(baseline_results)
        conversion_metrics = self._extract_metrics(conversion_results)
        
        # Compare metrics
        comparison = self._compare_metrics(baseline_metrics, conversion_metrics)
        self.comparison = comparison
        
        # Extract asset balances for visualization
        asset_balances = self._extract_asset_balances(baseline_results, conversion_results)
        
        # Return the results
        return {
            'baseline_results': baseline_results,
            'conversion_results': conversion_results,
            'metrics': {
                'baseline': baseline_metrics,
                'conversion': conversion_metrics,
                'comparison': comparison
            },
            'asset_balances': asset_balances,
            'conversion_params': {
                'annual_conversion': float(annual_conversion),
                'total_conversion': float(total_conversion),
                'years_to_convert': self.years_to_convert,
                'conversion_start_year': self.conversion_start_year,
                'roth_withdrawal_start_year': self.roth_withdrawal_start_year,
                'roth_withdrawal_amount': float(self.roth_withdrawal_amount)
            }
        }

def decimal_default(obj):
    """Helper function to serialize Decimal objects to float for JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def main():
    """Run a simple test of the RothConversionProcessor."""
    print("Running simple test of RothConversionProcessor...")
    
    # Create test data
    current_year = datetime.now().year
    
    # Sample scenario
    scenario = {
        'retirement_age': 65,
        'mortality_age': 90,
        'part_b_inflation_rate': 3.0,
        'part_d_inflation_rate': 3.0,
    }
    
    # Sample client
    client = {
        'birthdate': f"{current_year - 60}-01-01",  # 60 years old
        'tax_status': 'Single',
        'gender': 'M',
        'first_name': 'John',
        'last_name': 'Doe',
        'state': 'CA'
    }
    
    # No spouse for simplicity
    spouse = None
    
    # Sample assets
    assets = [
        {
            'id': 'asset1',
            'income_type': 'traditional_ira',
            'income_name': 'Traditional IRA',
            'owned_by': 'primary',
            'current_asset_balance': Decimal('500000'),
            'monthly_amount': Decimal('0'),
            'monthly_contribution': Decimal('0'),
            'age_to_begin_withdrawal': 72,
            'age_to_end_withdrawal': 90,
            'rate_of_return': 5.0,
            'cola': 0,
            'exclusion_ratio': 0,
            'tax_rate': 0,
            'max_to_convert': Decimal('200000')  # Amount to convert
        },
        {
            'id': 'asset2',
            'income_type': 'traditional_401k',
            'income_name': 'Traditional 401(k)',
            'owned_by': 'primary',
            'current_asset_balance': Decimal('300000'),
            'monthly_amount': Decimal('0'),
            'monthly_contribution': Decimal('0'),
            'age_to_begin_withdrawal': 72,
            'age_to_end_withdrawal': 90,
            'rate_of_return': 5.0,
            'cola': 0,
            'exclusion_ratio': 0,
            'tax_rate': 0,
            'max_to_convert': Decimal('100000')  # Amount to convert
        }
    ]
    
    # Sample conversion parameters
    conversion_params = {
        'conversion_start_year': current_year + 1,
        'years_to_convert': 5,
        'pre_retirement_income': Decimal('100000'),
        'roth_growth_rate': 5.0,
        'max_annual_amount': Decimal('60000'),
        'roth_withdrawal_amount': Decimal('20000'),
        'roth_withdrawal_start_year': current_year + 10
    }
    
    # Create and process the Roth conversion
    processor = RothConversionProcessor(
        scenario=scenario,
        client=client,
        spouse=spouse,
        assets=assets,
        conversion_params=conversion_params
    )
    
    # Process the conversion and get results
    result = processor.process()
    
    # Print the results in a readable format
    print("\nRoth Conversion Results:")
    print("========================")
    
    # Print conversion parameters
    print("\nConversion Parameters:")
    print(f"  Start Year: {result['conversion_params']['conversion_start_year']}")
    print(f"  Years to Convert: {result['conversion_params']['years_to_convert']}")
    print(f"  Annual Conversion: ${result['conversion_params']['annual_conversion']:,.2f}")
    print(f"  Total Conversion: ${result['conversion_params']['total_conversion']:,.2f}")
    
    # Print metrics comparison
    print("\nMetrics Comparison:")
    comparison = result['metrics']['comparison']
    
    metrics_to_display = [
        ('lifetime_tax', 'Lifetime Taxes'),
        ('lifetime_medicare', 'Lifetime Medicare'),
        ('total_irmaa', 'Total IRMAA'),
        ('total_rmds', 'Total RMDs'),
        ('inheritance_tax', 'Inheritance Tax'),
        ('total_expenses', 'Total Expenses')
    ]
    
    print(f"{'Metric':<20} {'Baseline':<15} {'Conversion':<15} {'Difference':<15} {'% Change':<10}")
    print("-" * 75)
    
    for key, label in metrics_to_display:
        if key in comparison:
            baseline = comparison[key]['baseline']
            conversion = comparison[key]['conversion']
            difference = comparison[key]['difference']
            pct_change = comparison[key]['percent_change']
            
            print(f"{label:<20} ${baseline:>13,.2f} ${conversion:>13,.2f} ${difference:>13,.2f} {pct_change:>9.2f}%")
    
    # Print asset balances for the first and last year
    print("\nAsset Balances:")
    years = result['asset_balances']['years']
    first_year = years[0]
    last_year = years[-1]
    
    print(f"\nFirst Year ({first_year}):")
    print(f"{'Asset':<20} {'Baseline':<15} {'Conversion':<15} {'Difference':<15}")
    print("-" * 65)
    
    for asset_name in result['asset_balances']['baseline']:
        baseline_value = result['asset_balances']['baseline'][asset_name][0]
        conversion_value = result['asset_balances']['conversion'][asset_name][0]
        difference = conversion_value - baseline_value
        
        print(f"{asset_name:<20} ${baseline_value:>13,.2f} ${conversion_value:>13,.2f} ${difference:>13,.2f}")
    
    print(f"\nLast Year ({last_year}):")
    print(f"{'Asset':<20} {'Baseline':<15} {'Conversion':<15} {'Difference':<15}")
    print("-" * 65)
    
    for asset_name in result['asset_balances']['baseline']:
        baseline_value = result['asset_balances']['baseline'][asset_name][-1]
        conversion_value = result['asset_balances']['conversion'][asset_name][-1]
        difference = conversion_value - baseline_value
        
        print(f"{asset_name:<20} ${baseline_value:>13,.2f} ${conversion_value:>13,.2f} ${difference:>13,.2f}")
    
    # Save the full results to a JSON file for further analysis
    with open('roth_conversion_results.json', 'w') as f:
        json.dump(result, f, default=decimal_default, indent=2)
    
    print("\nFull results saved to 'roth_conversion_results.json'")

if __name__ == '__main__':
    main() 