"""
Unit tests for the Roth Conversion Processor.
"""
import unittest
from decimal import Decimal
from datetime import datetime, date
import copy
import json
from django.test import TestCase
from ..roth_conversion_processor import RothConversionProcessor

class RothConversionProcessorTest(TestCase):
    """Test the RothConversionProcessor class."""
    
    def setUp(self):
        """Set up test data."""
        # Create a sample scenario
        self.scenario = {
            'retirement_age': 65,
            'mortality_age': 90,
            'part_b_inflation_rate': 3.0,
            'part_d_inflation_rate': 3.0,
        }
        
        # Create a sample client
        current_year = datetime.now().year
        self.client = {
            'birthdate': f"{current_year - 60}-01-01",  # 60 years old
            'tax_status': 'Single',
            'gender': 'M',
            'first_name': 'John',
            'last_name': 'Doe',
            'state': 'CA'
        }
        
        # No spouse for simplicity
        self.spouse = None
        
        # Create sample assets
        self.assets = [
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
        
        # Create sample conversion parameters
        current_year = datetime.now().year
        self.conversion_params = {
            'conversion_start_year': current_year + 1,
            'years_to_convert': 5,
            'pre_retirement_income': Decimal('100000'),
            'roth_growth_rate': 5.0,
            'max_annual_amount': Decimal('60000'),
            'roth_withdrawal_amount': Decimal('20000'),
            'roth_withdrawal_start_year': current_year + 10
        }
        
    def test_initialization(self):
        """Test that the processor initializes correctly."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        # Check that parameters were set correctly
        self.assertEqual(processor.conversion_start_year, self.conversion_params['conversion_start_year'])
        self.assertEqual(processor.years_to_convert, self.conversion_params['years_to_convert'])
        self.assertEqual(processor.pre_retirement_income, self.conversion_params['pre_retirement_income'])
        self.assertEqual(processor.roth_growth_rate, self.conversion_params['roth_growth_rate'])
        self.assertEqual(processor.max_annual_amount, self.conversion_params['max_annual_amount'])
        self.assertEqual(processor.roth_withdrawal_amount, self.conversion_params['roth_withdrawal_amount'])
        self.assertEqual(processor.roth_withdrawal_start_year, self.conversion_params['roth_withdrawal_start_year'])
        
    def test_prepare_assets_for_conversion(self):
        """Test that assets are prepared correctly for conversion."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        annual_conversion, total_conversion = processor._prepare_assets_for_conversion()
        
        # Check that the total conversion amount is correct
        expected_total = Decimal('300000')  # 200000 + 100000
        self.assertEqual(total_conversion, expected_total)
        
        # Check that the annual conversion is limited by max_annual_amount
        self.assertEqual(annual_conversion, Decimal('60000'))
        
        # Check that the years to convert was recalculated
        self.assertEqual(processor.years_to_convert, 5)
        
        # Check that a synthetic Roth asset was added
        self.assertEqual(len(processor.assets), 3)
        
        # Verify the synthetic Roth asset
        roth_asset = processor.assets[-1]
        self.assertEqual(roth_asset['income_type'], 'roth_ira')
        self.assertEqual(roth_asset['income_name'], 'Converted Roth IRA')
        self.assertEqual(roth_asset['current_asset_balance'], Decimal('0'))
        self.assertEqual(roth_asset['rate_of_return'], processor.roth_growth_rate)
        self.assertTrue(roth_asset.get('is_synthetic_roth', False))
        
    def test_prepare_baseline_scenario(self):
        """Test that the baseline scenario is prepared correctly."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        baseline_scenario = processor._prepare_baseline_scenario()
        
        # Check that Roth conversion fields are None/zero
        self.assertIsNone(baseline_scenario['roth_conversion_start_year'])
        self.assertIsNone(baseline_scenario['roth_conversion_duration'])
        self.assertIsNone(baseline_scenario['roth_conversion_annual_amount'])
        
        # Check that required fields are present
        self.assertEqual(baseline_scenario['part_b_inflation_rate'], 3.0)
        self.assertEqual(baseline_scenario['part_d_inflation_rate'], 3.0)
        self.assertEqual(baseline_scenario['retirement_age'], 65)
        self.assertEqual(baseline_scenario['mortality_age'], 90)
        
    def test_prepare_conversion_scenario(self):
        """Test that the conversion scenario is prepared correctly."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        # First prepare assets to set annual_conversion
        processor._prepare_assets_for_conversion()
        
        conversion_scenario = processor._prepare_conversion_scenario()
        
        # Check that Roth conversion fields are set
        self.assertEqual(conversion_scenario['roth_conversion_start_year'], processor.conversion_start_year)
        self.assertEqual(conversion_scenario['roth_conversion_duration'], processor.years_to_convert)
        self.assertEqual(conversion_scenario['roth_conversion_annual_amount'], processor.annual_conversion)
        
        # Check that pre-retirement income is set
        self.assertEqual(conversion_scenario['pre_retirement_income'], processor.pre_retirement_income)
        
    def test_extract_metrics(self):
        """Test that metrics are extracted correctly from results."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        # Create sample results
        results = [
            {
                'year': 2023,
                'federal_tax': 10000,
                'medicare_base': 2000,
                'irmaa_surcharge': 500,
                'asset1_rmd': 5000,
                'asset2_rmd': 3000,
                'net_income': 80000,
                'roth_ira_balance': 0
            },
            {
                'year': 2024,
                'federal_tax': 12000,
                'medicare_base': 2100,
                'irmaa_surcharge': 600,
                'asset1_rmd': 5500,
                'asset2_rmd': 3300,
                'net_income': 82000,
                'roth_ira_balance': 60000
            },
            {
                'year': 2025,
                'federal_tax': 14000,
                'medicare_base': 2200,
                'irmaa_surcharge': 700,
                'asset1_rmd': 6000,
                'asset2_rmd': 3600,
                'net_income': 84000,
                'roth_ira_balance': 123000
            }
        ]
        
        metrics = processor._extract_metrics(results)
        
        # Check that metrics were calculated correctly
        self.assertEqual(metrics['lifetime_tax'], 36000)
        self.assertEqual(metrics['lifetime_medicare'], 6300)
        self.assertEqual(metrics['total_irmaa'], 1800)
        self.assertEqual(metrics['total_rmds'], 26400)  # 5000 + 3000 + 5500 + 3300 + 6000 + 3600
        self.assertEqual(metrics['cumulative_net_income'], 246000)  # 80000 + 82000 + 84000
        self.assertEqual(metrics['final_roth'], 123000)  # Last year's Roth balance
        
    def test_compare_metrics(self):
        """Test that metrics comparison works correctly."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        # Create sample metrics
        baseline_metrics = {
            'lifetime_tax': 100000,
            'lifetime_medicare': 20000,
            'total_irmaa': 5000,
            'total_rmds': 200000,
            'cumulative_net_income': 800000,
            'final_roth': 0,
            'inheritance_tax': 50000
        }
        
        conversion_metrics = {
            'lifetime_tax': 120000,  # Higher due to conversions
            'lifetime_medicare': 18000,  # Lower due to less taxable income in retirement
            'total_irmaa': 4000,  # Lower due to less taxable income in retirement
            'total_rmds': 150000,  # Lower due to converted assets
            'cumulative_net_income': 820000,  # Higher due to tax-free Roth withdrawals
            'final_roth': 300000,  # Higher due to conversions
            'inheritance_tax': 30000  # Lower due to less taxable assets
        }
        
        comparison = processor._compare_metrics(baseline_metrics, conversion_metrics)
        
        # Check that comparison metrics were calculated correctly
        self.assertEqual(comparison['lifetime_tax']['baseline'], 100000)
        self.assertEqual(comparison['lifetime_tax']['conversion'], 120000)
        self.assertEqual(comparison['lifetime_tax']['difference'], 20000)
        self.assertEqual(comparison['lifetime_tax']['percent_change'], 20.0)
        
        self.assertEqual(comparison['lifetime_medicare']['baseline'], 20000)
        self.assertEqual(comparison['lifetime_medicare']['conversion'], 18000)
        self.assertEqual(comparison['lifetime_medicare']['difference'], -2000)
        self.assertEqual(comparison['lifetime_medicare']['percent_change'], -10.0)
        
        # Check total expenses
        baseline_expenses = 100000 + 20000 + 5000 + 50000  # 175000
        conversion_expenses = 120000 + 18000 + 4000 + 30000  # 172000
        
        self.assertEqual(comparison['total_expenses']['baseline'], baseline_expenses)
        self.assertEqual(comparison['total_expenses']['conversion'], conversion_expenses)
        self.assertEqual(comparison['total_expenses']['difference'], -3000)
        self.assertEqual(comparison['total_expenses']['percent_change'], -1.7142857142857142)
        
    def test_extract_asset_balances(self):
        """Test that asset balances are extracted correctly."""
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        # Create sample results
        baseline_results = [
            {
                'year': 2023,
                'asset1_balance': 500000,
                'asset2_balance': 300000,
                'roth_ira_balance': 0
            },
            {
                'year': 2024,
                'asset1_balance': 525000,
                'asset2_balance': 315000,
                'roth_ira_balance': 0
            }
        ]
        
        conversion_results = [
            {
                'year': 2023,
                'asset1_balance': 460000,  # Lower due to conversion
                'asset2_balance': 280000,  # Lower due to conversion
                'roth_ira_balance': 60000  # Higher due to conversion
            },
            {
                'year': 2024,
                'asset1_balance': 483000,  # Lower due to conversion
                'asset2_balance': 294000,  # Lower due to conversion
                'roth_ira_balance': 123000  # Higher due to conversion
            }
        ]
        
        asset_balances = processor._extract_asset_balances(baseline_results, conversion_results)
        
        # Check that asset balances were extracted correctly
        self.assertEqual(asset_balances['years'], [2023, 2024])
        
        # Check baseline balances
        self.assertEqual(asset_balances['baseline']['asset1'], [500000, 525000])
        self.assertEqual(asset_balances['baseline']['asset2'], [300000, 315000])
        self.assertEqual(asset_balances['baseline']['roth_ira'], [0, 0])
        
        # Check conversion balances
        self.assertEqual(asset_balances['conversion']['asset1'], [460000, 483000])
        self.assertEqual(asset_balances['conversion']['asset2'], [280000, 294000])
        self.assertEqual(asset_balances['conversion']['roth_ira'], [60000, 123000])
        
    def test_process(self):
        """Test the full processing flow."""
        # This is more of an integration test
        processor = RothConversionProcessor(
            scenario=self.scenario,
            client=self.client,
            spouse=self.spouse,
            assets=self.assets,
            conversion_params=self.conversion_params
        )
        
        # Mock the ScenarioProcessor.calculate method to avoid database calls
        def mock_calculate(self):
            # Return a simplified result set
            years = range(datetime.now().year, datetime.now().year + 30)
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
                    if asset.get('is_synthetic_roth', False) and hasattr(self, 'scenario') and self.scenario.get('roth_conversion_annual_amount'):
                        # Add conversion amount for the first N years
                        if years_passed < 5:  # Assuming 5 years of conversion
                            balance += float(self.scenario.get('roth_conversion_annual_amount', 0)) * (years_passed + 1)
                    
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
        
        # Apply the mock
        import types
        from ..scenario_processor import ScenarioProcessor
        original_calculate = ScenarioProcessor.calculate
        ScenarioProcessor.calculate = types.MethodType(mock_calculate, ScenarioProcessor)
        
        try:
            # Run the process method
            result = processor.process()
            
            # Check that the result has the expected structure
            self.assertIn('baseline_results', result)
            self.assertIn('conversion_results', result)
            self.assertIn('metrics', result)
            self.assertIn('asset_balances', result)
            self.assertIn('conversion_params', result)
            
            # Check that metrics were calculated
            self.assertIn('baseline', result['metrics'])
            self.assertIn('conversion', result['metrics'])
            self.assertIn('comparison', result['metrics'])
            
            # Check that asset balances were extracted
            self.assertIn('years', result['asset_balances'])
            self.assertIn('baseline', result['asset_balances'])
            self.assertIn('conversion', result['asset_balances'])
            
            # Check that conversion parameters were included
            self.assertEqual(result['conversion_params']['annual_conversion'], float(processor.annual_conversion))
            self.assertEqual(result['conversion_params']['total_conversion'], float(processor.total_conversion))
            self.assertEqual(result['conversion_params']['years_to_convert'], processor.years_to_convert)
            
        finally:
            # Restore the original method
            ScenarioProcessor.calculate = original_calculate

if __name__ == '__main__':
    unittest.main() 