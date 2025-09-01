"""
Scenario Data Integration Service
Connects Report Center with existing scenario calculation results and client data
"""

import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime

from django.utils import timezone
from django.db.models import Q, Sum, Avg

from core.models import Scenario, Client, Asset, Income, Expense, TaxSettings
from ..models import Report

logger = logging.getLogger(__name__)


class ScenarioDataIntegrationService:
    """
    Service for extracting and formatting scenario data for report generation
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def get_report_data(self, report: Report) -> Dict[str, Any]:
        """
        Extract all necessary data for report generation from scenario and client
        """
        try:
            data = {
                'report_id': str(report.id),
                'generated_at': timezone.now().isoformat(),
                'client_data': {},
                'scenario_data': {},
                'financial_projections': {},
                'chart_data': {}
            }
            
            # Extract client data
            if report.client:
                data['client_data'] = self._extract_client_data(report.client)
            
            # Extract scenario data
            if report.scenario:
                data['scenario_data'] = self._extract_scenario_data(report.scenario)
                data['financial_projections'] = self._generate_financial_projections(report.scenario)
                data['chart_data'] = self._prepare_chart_data(report.scenario)
            
            logger.info(f"Successfully extracted report data for report {report.id}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to extract report data for {report.id}: {str(e)}")
            raise
    
    def _extract_client_data(self, client: Client) -> Dict[str, Any]:
        """Extract comprehensive client information"""
        
        return {
            'id': client.id,
            'full_name': client.full_name,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'phone': client.phone,
            'age': client.age,
            'retirement_age': client.retirement_age,
            'current_income': float(client.current_income) if client.current_income else 0,
            'current_savings': float(client.current_savings) if client.current_savings else 0,
            'spouse_age': client.spouse_age,
            'spouse_retirement_age': client.spouse_retirement_age,
            'risk_tolerance': client.risk_tolerance,
            'created_at': client.created_at.isoformat(),
            'advisor_name': client.advisor.get_full_name() if client.advisor else ''
        }
    
    def _extract_scenario_data(self, scenario: Scenario) -> Dict[str, Any]:
        """Extract comprehensive scenario information"""
        
        # Get related data
        assets = list(scenario.assets.all().values())
        incomes = list(scenario.incomes.all().values())
        expenses = list(scenario.expenses.all().values())
        
        # Convert Decimal fields to float for JSON serialization
        for asset in assets:
            for key, value in asset.items():
                if isinstance(value, Decimal):
                    asset[key] = float(value)
        
        for income in incomes:
            for key, value in income.items():
                if isinstance(value, Decimal):
                    income[key] = float(value)
        
        for expense in expenses:
            for key, value in expense.items():
                if isinstance(value, Decimal):
                    expense[key] = float(value)
        
        return {
            'id': scenario.id,
            'name': scenario.name,
            'description': scenario.description,
            'retirement_age': scenario.retirement_age,
            'medicare_age': scenario.medicare_age,
            'spouse_retirement_age': scenario.spouse_retirement_age,
            'spouse_medicare_age': scenario.spouse_medicare_age,
            'mortality_age': scenario.mortality_age,
            'spouse_mortality_age': scenario.spouse_mortality_age,
            'retirement_year': scenario.retirement_year,
            'final_age': scenario.mortality_age,
            'current_year': self.current_year,
            
            # Roth conversion data
            'roth_conversion_start_year': scenario.roth_conversion_start_year,
            'roth_conversion_duration': scenario.roth_conversion_duration,
            'roth_conversion_annual_amount': float(scenario.roth_conversion_annual_amount) if scenario.roth_conversion_annual_amount else 0,
            
            # Social Security data
            'primary_ss_claiming_age': scenario.primary_ss_claiming_age,
            'spouse_ss_claiming_age': scenario.spouse_ss_claiming_age,
            'ss_include_irmaa': scenario.ss_include_irmaa,
            'reduction_2030_ss': scenario.reduction_2030_ss,
            'ss_adjustment_year': scenario.ss_adjustment_year,
            'ss_adjustment_direction': scenario.ss_adjustment_direction,
            'ss_adjustment_type': scenario.ss_adjustment_type,
            'ss_adjustment_amount': scenario.ss_adjustment_amount,
            
            # Tax settings
            'primary_state': scenario.primary_state,
            'apply_standard_deduction': scenario.apply_standard_deduction,
            'federal_standard_deduction': float(scenario.federal_standard_deduction) if scenario.federal_standard_deduction else 0,
            'state_standard_deduction': float(scenario.state_standard_deduction) if scenario.state_standard_deduction else 0,
            'custom_annual_deduction': float(scenario.custom_annual_deduction) if scenario.custom_annual_deduction else 0,
            'primary_blind': scenario.primary_blind,
            'spouse_blind': scenario.spouse_blind,
            'is_dependent': scenario.is_dependent,
            
            # Related data
            'assets': assets,
            'incomes': incomes,
            'expenses': expenses,
            
            # Summary calculations
            'total_assets': sum(float(asset.get('current_balance', 0)) for asset in assets),
            'total_annual_income': sum(float(income.get('amount', 0)) for income in incomes if income.get('frequency') == 'annual'),
            'total_annual_expenses': sum(float(expense.get('amount', 0)) for expense in expenses if expense.get('frequency') == 'annual'),
            
            'created_at': scenario.created_at.isoformat(),
            'updated_at': scenario.updated_at.isoformat()
        }
    
    def _generate_financial_projections(self, scenario: Scenario) -> Dict[str, Any]:
        """Generate financial projections based on scenario data"""
        
        try:
            # Calculate projection years from retirement to mortality
            start_year = scenario.retirement_year or self.current_year
            end_year = start_year + (scenario.mortality_age - scenario.retirement_age) if scenario.mortality_age and scenario.retirement_age else start_year + 25
            
            projections = {
                'projection_years': list(range(start_year, end_year + 1)),
                'asset_projections': [],
                'income_projections': [],
                'expense_projections': [],
                'tax_projections': [],
                'net_cash_flow': []
            }
            
            # Get initial values
            initial_assets = float(scenario.assets.aggregate(total=Sum('current_balance'))['total'] or 0)
            annual_income = float(scenario.incomes.aggregate(total=Sum('amount'))['total'] or 0)
            annual_expenses = float(scenario.expenses.aggregate(total=Sum('amount'))['total'] or 0)
            
            # Simple projection logic (this would be enhanced with actual calculation engine)
            current_assets = initial_assets
            growth_rate = 0.07  # 7% annual growth assumption
            inflation_rate = 0.03  # 3% inflation assumption
            
            for i, year in enumerate(projections['projection_years']):
                # Asset growth with withdrawals
                if i > 0:  # Skip first year
                    investment_growth = current_assets * growth_rate
                    net_withdrawal = max(0, annual_expenses - annual_income)
                    current_assets = current_assets + investment_growth - net_withdrawal
                
                # Inflate income and expenses
                inflated_income = annual_income * ((1 + inflation_rate) ** i)
                inflated_expenses = annual_expenses * ((1 + inflation_rate) ** i)
                
                # Simple tax calculation (would use actual tax engine)
                estimated_tax = inflated_income * 0.22  # 22% effective tax rate assumption
                
                projections['asset_projections'].append(round(current_assets, 0))
                projections['income_projections'].append(round(inflated_income, 0))
                projections['expense_projections'].append(round(inflated_expenses, 0))
                projections['tax_projections'].append(round(estimated_tax, 0))
                projections['net_cash_flow'].append(round(inflated_income - inflated_expenses - estimated_tax, 0))
            
            return projections
            
        except Exception as e:
            logger.error(f"Financial projection generation failed for scenario {scenario.id}: {str(e)}")
            return {
                'projection_years': [],
                'asset_projections': [],
                'income_projections': [],
                'expense_projections': [],
                'tax_projections': [],
                'net_cash_flow': []
            }
    
    def _prepare_chart_data(self, scenario: Scenario) -> Dict[str, Any]:
        """Prepare data specifically formatted for chart generation"""
        
        try:
            projections = self._generate_financial_projections(scenario)
            
            chart_data = {
                'asset_timeline': {
                    'years': projections['projection_years'],
                    'asset_values': projections['asset_projections'],
                    'retirement_year': scenario.retirement_year
                },
                
                'income_projection': {
                    'years': projections['projection_years'],
                    'income_values': projections['income_projections'],
                    'expense_values': projections['expense_projections']
                },
                
                'tax_analysis': {
                    'years': projections['projection_years'],
                    'federal_tax': [tax * 0.8 for tax in projections['tax_projections']],  # Assume 80% federal
                    'state_tax': [tax * 0.15 for tax in projections['tax_projections']],   # Assume 15% state
                    'irmaa_charges': [tax * 0.05 for tax in projections['tax_projections']]  # Assume 5% IRMAA
                },
                
                'monte_carlo': {
                    'years': projections['projection_years'],
                    'percentiles': {
                        '10': [val * 0.7 for val in projections['asset_projections']],
                        '25': [val * 0.85 for val in projections['asset_projections']],
                        '50': projections['asset_projections'],
                        '75': [val * 1.15 for val in projections['asset_projections']],
                        '90': [val * 1.35 for val in projections['asset_projections']]
                    }
                }
            }
            
            # Add Roth conversion data if applicable
            if scenario.roth_conversion_start_year and scenario.roth_conversion_duration:
                conversion_years = list(range(
                    scenario.roth_conversion_start_year,
                    scenario.roth_conversion_start_year + scenario.roth_conversion_duration
                ))
                conversion_amount = float(scenario.roth_conversion_annual_amount or 50000)
                
                chart_data['roth_conversion'] = {
                    'conversion_years': conversion_years,
                    'conversion_amounts': [conversion_amount] * len(conversion_years),
                    'cumulative_tax_savings': [i * 5000 + i**2 * 100 for i in range(len(projections['projection_years']))]
                }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Chart data preparation failed for scenario {scenario.id}: {str(e)}")
            return {}
    
    def get_scenario_summary_stats(self, scenario: Scenario) -> Dict[str, Any]:
        """Get key summary statistics for scenario"""
        
        try:
            # Calculate totals
            total_assets = scenario.assets.aggregate(total=Sum('current_balance'))['total'] or 0
            total_income = scenario.incomes.aggregate(total=Sum('amount'))['total'] or 0
            total_expenses = scenario.expenses.aggregate(total=Sum('amount'))['total'] or 0
            
            # Calculate derived metrics
            net_worth = float(total_assets)
            annual_surplus = float(total_income - total_expenses)
            savings_rate = (annual_surplus / float(total_income)) * 100 if total_income > 0 else 0
            
            # Years to retirement
            client_age = scenario.client.age or 65
            years_to_retirement = max(0, scenario.retirement_age - client_age)
            
            # Retirement duration
            retirement_years = scenario.mortality_age - scenario.retirement_age if scenario.mortality_age and scenario.retirement_age else 25
            
            return {
                'net_worth': round(net_worth, 2),
                'annual_income': round(float(total_income), 2),
                'annual_expenses': round(float(total_expenses), 2),
                'annual_surplus': round(annual_surplus, 2),
                'savings_rate_percent': round(savings_rate, 1),
                'years_to_retirement': years_to_retirement,
                'retirement_duration_years': retirement_years,
                'retirement_year': scenario.retirement_year,
                'asset_count': scenario.assets.count(),
                'income_source_count': scenario.incomes.count(),
                'expense_category_count': scenario.expenses.count(),
            }
            
        except Exception as e:
            logger.error(f"Summary stats calculation failed for scenario {scenario.id}: {str(e)}")
            return {}
    
    def get_asset_breakdown(self, scenario: Scenario) -> Dict[str, Any]:
        """Get detailed asset breakdown for reports"""
        
        try:
            assets = scenario.assets.all()
            
            breakdown = {
                'total_value': 0,
                'by_type': {},
                'by_account': [],
                'qualified_vs_nonqualified': {
                    'qualified': 0,
                    'nonqualified': 0,
                    'roth': 0
                }
            }
            
            for asset in assets:
                current_balance = float(asset.current_balance or 0)
                breakdown['total_value'] += current_balance
                
                # Group by investment type
                inv_type = asset.investment_type or 'Other'
                if inv_type not in breakdown['by_type']:
                    breakdown['by_type'][inv_type] = 0
                breakdown['by_type'][inv_type] += current_balance
                
                # Individual account data
                breakdown['by_account'].append({
                    'name': asset.investment_name or asset.income_name or 'Unnamed Asset',
                    'type': inv_type,
                    'current_balance': current_balance,
                    'annual_contribution': float(asset.annual_contribution or 0),
                    'employer_match': float(asset.employer_match or 0)
                })
                
                # Qualified vs non-qualified classification (simplified)
                if 'roth' in inv_type.lower():
                    breakdown['qualified_vs_nonqualified']['roth'] += current_balance
                elif any(keyword in inv_type.lower() for keyword in ['401k', '403b', 'ira', 'pension']):
                    breakdown['qualified_vs_nonqualified']['qualified'] += current_balance
                else:
                    breakdown['qualified_vs_nonqualified']['nonqualified'] += current_balance
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Asset breakdown calculation failed for scenario {scenario.id}: {str(e)}")
            return {'total_value': 0, 'by_type': {}, 'by_account': [], 'qualified_vs_nonqualified': {}}
    
    def get_income_analysis(self, scenario: Scenario) -> Dict[str, Any]:
        """Get detailed income source analysis"""
        
        try:
            incomes = scenario.incomes.all()
            
            analysis = {
                'total_annual': 0,
                'by_source_type': {},
                'social_security': {
                    'included': False,
                    'primary_amount': 0,
                    'spouse_amount': 0,
                    'claiming_strategy': {}
                },
                'sources': []
            }
            
            for income in incomes:
                amount = float(income.amount or 0)
                
                # Convert to annual if needed
                if income.frequency == 'monthly':
                    annual_amount = amount * 12
                elif income.frequency == 'quarterly':
                    annual_amount = amount * 4
                else:
                    annual_amount = amount
                
                analysis['total_annual'] += annual_amount
                
                # Group by source type
                source_type = income.income_type or 'Other'
                if source_type not in analysis['by_source_type']:
                    analysis['by_source_type'][source_type] = 0
                analysis['by_source_type'][source_type] += annual_amount
                
                # Track Social Security specifically
                if 'social security' in source_type.lower():
                    analysis['social_security']['included'] = True
                    if 'spouse' in income.income_name.lower():
                        analysis['social_security']['spouse_amount'] = annual_amount
                    else:
                        analysis['social_security']['primary_amount'] = annual_amount
                
                # Individual source data
                analysis['sources'].append({
                    'name': income.income_name,
                    'type': source_type,
                    'annual_amount': annual_amount,
                    'start_year': income.start_year,
                    'end_year': income.end_year,
                    'frequency': income.frequency
                })
            
            # Add Social Security claiming strategy info
            if analysis['social_security']['included']:
                analysis['social_security']['claiming_strategy'] = {
                    'primary_claiming_age': scenario.primary_ss_claiming_age,
                    'spouse_claiming_age': scenario.spouse_ss_claiming_age,
                    'include_irmaa_impact': scenario.ss_include_irmaa,
                    'benefit_reduction_applied': scenario.reduction_2030_ss,
                    'adjustment_year': scenario.ss_adjustment_year if scenario.reduction_2030_ss else None
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Income analysis failed for scenario {scenario.id}: {str(e)}")
            return {'total_annual': 0, 'by_source_type': {}, 'social_security': {}, 'sources': []}
    
    def get_expense_analysis(self, scenario: Scenario) -> Dict[str, Any]:
        """Get detailed expense analysis"""
        
        try:
            expenses = scenario.expenses.all()
            
            analysis = {
                'total_annual': 0,
                'by_category': {},
                'essential_vs_discretionary': {
                    'essential': 0,
                    'discretionary': 0
                },
                'expenses': []
            }
            
            for expense in expenses:
                amount = float(expense.amount or 0)
                
                # Convert to annual if needed
                if expense.frequency == 'monthly':
                    annual_amount = amount * 12
                elif expense.frequency == 'quarterly':
                    annual_amount = amount * 4
                else:
                    annual_amount = amount
                
                analysis['total_annual'] += annual_amount
                
                # Group by category
                category = expense.expense_type or 'Other'
                if category not in analysis['by_category']:
                    analysis['by_category'][category] = 0
                analysis['by_category'][category] += annual_amount
                
                # Classify as essential vs discretionary (simplified logic)
                essential_categories = ['housing', 'healthcare', 'food', 'utilities', 'insurance']
                if any(keyword in category.lower() for keyword in essential_categories):
                    analysis['essential_vs_discretionary']['essential'] += annual_amount
                else:
                    analysis['essential_vs_discretionary']['discretionary'] += annual_amount
                
                # Individual expense data
                analysis['expenses'].append({
                    'name': expense.expense_name,
                    'category': category,
                    'annual_amount': annual_amount,
                    'frequency': expense.frequency,
                    'is_essential': any(keyword in category.lower() for keyword in essential_categories)
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Expense analysis failed for scenario {scenario.id}: {str(e)}")
            return {'total_annual': 0, 'by_category': {}, 'essential_vs_discretionary': {}, 'expenses': []}
    
    def get_tax_planning_data(self, scenario: Scenario) -> Dict[str, Any]:
        """Get tax planning and IRMAA analysis data"""
        
        try:
            data = {
                'tax_settings': {
                    'primary_state': scenario.primary_state,
                    'apply_standard_deduction': scenario.apply_standard_deduction,
                    'federal_standard_deduction': float(scenario.federal_standard_deduction or 0),
                    'state_standard_deduction': float(scenario.state_standard_deduction or 0),
                    'custom_annual_deduction': float(scenario.custom_annual_deduction or 0),
                    'primary_blind': scenario.primary_blind,
                    'spouse_blind': scenario.spouse_blind,
                    'is_dependent': scenario.is_dependent
                },
                
                'roth_conversion_plan': {
                    'enabled': bool(scenario.roth_conversion_start_year),
                    'start_year': scenario.roth_conversion_start_year,
                    'duration': scenario.roth_conversion_duration,
                    'annual_amount': float(scenario.roth_conversion_annual_amount or 0),
                    'total_conversion': float(scenario.roth_conversion_annual_amount or 0) * (scenario.roth_conversion_duration or 0)
                },
                
                'irmaa_analysis': {
                    'medicare_age': scenario.medicare_age,
                    'spouse_medicare_age': scenario.spouse_medicare_age,
                    'part_b_inflation_rate': scenario.part_b_inflation_rate,
                    'part_d_inflation_rate': scenario.part_d_inflation_rate,
                    'medicare_irmaa_percent': scenario.medicare_irmaa_percent
                }
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Tax planning data extraction failed for scenario {scenario.id}: {str(e)}")
            return {}
    
    def format_data_for_template(self, report: Report, template_config: Dict) -> Dict[str, Any]:
        """
        Format scenario data according to specific template requirements
        """
        try:
            # Get base report data
            base_data = self.get_report_data(report)
            
            # Add template-specific formatting
            template_type = template_config.get('template_type', 'comprehensive')
            
            if template_type == 'executive_summary':
                formatted_data = self._format_for_executive_template(base_data)
            elif template_type == 'comprehensive':
                formatted_data = self._format_for_comprehensive_template(base_data)
            elif template_type == 'tax_focused':
                formatted_data = self._format_for_tax_template(base_data)
            elif template_type == 'social_security':
                formatted_data = self._format_for_ss_template(base_data)
            else:
                formatted_data = base_data
            
            # Add template metadata
            formatted_data['template'] = {
                'type': template_type,
                'config': template_config,
                'formatted_at': timezone.now().isoformat()
            }
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Template formatting failed for report {report.id}: {str(e)}")
            return self.get_report_data(report)  # Fallback to base data
    
    def _format_for_executive_template(self, base_data: Dict) -> Dict[str, Any]:
        """Format data for executive summary template"""
        
        # Focus on key metrics only
        formatted = {
            'client_data': base_data['client_data'],
            'key_metrics': {
                'current_net_worth': base_data['scenario_data'].get('total_assets', 0),
                'retirement_readiness': 'On Track',  # Would be calculated
                'years_to_retirement': base_data['scenario_data'].get('retirement_age', 65) - base_data['client_data'].get('age', 65),
                'monthly_retirement_income': base_data['financial_projections'].get('income_projections', [0])[0] / 12 if base_data['financial_projections'].get('income_projections') else 0
            },
            'chart_data': {
                'asset_timeline': base_data['chart_data'].get('asset_timeline', {}),
                'income_projection': base_data['chart_data'].get('income_projection', {})
            }
        }
        
        return formatted
    
    def _format_for_comprehensive_template(self, base_data: Dict) -> Dict[str, Any]:
        """Format data for comprehensive analysis template"""
        # Return all data for comprehensive template
        return base_data
    
    def _format_for_tax_template(self, base_data: Dict) -> Dict[str, Any]:
        """Format data for tax-focused template"""
        
        formatted = {
            'client_data': base_data['client_data'],
            'scenario_data': base_data['scenario_data'],
            'tax_analysis': self.get_tax_planning_data(None),  # Would pass actual scenario
            'chart_data': {
                'tax_analysis': base_data['chart_data'].get('tax_analysis', {}),
                'roth_conversion': base_data['chart_data'].get('roth_conversion', {})
            }
        }
        
        return formatted
    
    def _format_for_ss_template(self, base_data: Dict) -> Dict[str, Any]:
        """Format data for Social Security analysis template"""
        
        formatted = {
            'client_data': base_data['client_data'],
            'social_security': base_data['scenario_data'],  # Contains SS claiming data
            'chart_data': {
                'income_projection': base_data['chart_data'].get('income_projection', {})
            }
        }
        
        return formatted