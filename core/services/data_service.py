"""
Report Data Service
Handles data preparation and serialization for report generation
"""

import logging
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from ..models import Client, Scenario, IncomeSource
from ..scenario_processor import ScenarioProcessor

logger = logging.getLogger(__name__)


class ReportDataService:
    """Service for preparing and serializing data for report generation"""
    
    def __init__(self):
        # Don't initialize ScenarioProcessor here since it requires a scenario_id
        pass
    
    def get_scenario_data(self, scenario: Scenario) -> Dict:
        """
        Get comprehensive scenario data for reporting
        
        Args:
            scenario: Scenario model instance
            
        Returns:
            Dictionary containing scenario data, calculations, and analysis
        """
        try:
            logger.info(f"Processing scenario data for scenario ID: {scenario.id}")
            
            # Get basic scenario data
            scenario_dict = self.serialize_scenario(scenario)
            
            # Create ScenarioProcessor for this specific scenario
            scenario_processor = ScenarioProcessor(scenario.id)
            
            # Process scenario calculations using calculate method
            yearly_results = scenario_processor.calculate()
            
            # Calculate summary metrics
            summary = self._calculate_scenario_summary(scenario, yearly_results)
            
            # Get IRMAA analysis
            irmaa_analysis = self._get_irmaa_analysis(scenario, yearly_results)
            
            # Get tax analysis
            tax_analysis = self._get_tax_analysis(scenario, yearly_results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scenario, yearly_results)
            
            return {
                'scenario': scenario_dict,
                'yearly_results': yearly_results,
                'summary': summary,
                'irmaa_analysis': irmaa_analysis,
                'tax_analysis': tax_analysis,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error processing scenario data: {str(e)}", exc_info=True)
            return {
                'scenario': self.serialize_scenario(scenario),
                'yearly_results': [],
                'summary': {},
                'irmaa_analysis': {},
                'tax_analysis': {},
                'recommendations': []
            }
    
    def serialize_client(self, client: Client) -> Dict:
        """Serialize client data for reports"""
        try:
            return {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'full_name': f"{client.first_name} {client.last_name}",
                'email': client.email or '',
                'birthdate': client.birthdate.isoformat() if client.birthdate else None,
                'age': self._calculate_age(client.birthdate) if client.birthdate else None,
                'tax_status': client.tax_status if hasattr(client, 'tax_status') else 'single',
                'spouse': self._serialize_spouse(client) if hasattr(client, 'spouse') else None,
                'created_at': client.created_at.isoformat() if client.created_at else None
            }
        except Exception as e:
            logger.error(f"Error serializing client: {str(e)}")
            return {
                'id': getattr(client, 'id', 0),
                'first_name': getattr(client, 'first_name', 'Unknown'),
                'last_name': getattr(client, 'last_name', 'Client'),
                'full_name': f"{getattr(client, 'first_name', 'Unknown')} {getattr(client, 'last_name', 'Client')}",
                'email': '',
                'age': None,
                'tax_status': 'single',
                'spouse': None
            }
    
    def serialize_scenario(self, scenario: Scenario) -> Dict:
        """Serialize scenario data for reports"""
        try:
            return {
                'id': scenario.id,
                'name': scenario.name,
                'description': scenario.description,
                'retirement_age': scenario.retirement_age,
                'mortality_age': scenario.mortality_age,
                'spouse_mortality_age': scenario.spouse_mortality_age,
                'retirement_year': scenario.retirement_year,
                'total_assets': self._calculate_total_assets(scenario),
                'annual_income': self._calculate_annual_income(scenario),
                'created_at': scenario.created_at.isoformat() if scenario.created_at else None,
                'updated_at': scenario.updated_at.isoformat() if scenario.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error serializing scenario: {str(e)}")
            return {
                'id': getattr(scenario, 'id', 0),
                'name': getattr(scenario, 'name', 'Unknown Scenario'),
                'description': getattr(scenario, 'description', ''),
                'retirement_age': getattr(scenario, 'retirement_age', 65),
                'mortality_age': getattr(scenario, 'mortality_age', 90),
                'total_assets': 0.0,
                'annual_income': 0.0
            }
    
    def serialize_advisor(self, advisor) -> Dict:
        """Serialize advisor data for reports"""
        try:
            return {
                'name': f"{getattr(advisor, 'first_name', '')} {getattr(advisor, 'last_name', '')}".strip(),
                'company': getattr(advisor, 'company_name', ''),
                'email': getattr(advisor, 'email', ''),
                'phone': getattr(advisor, 'phone_number', ''),
                'website': getattr(advisor, 'website_url', ''),
                'address': {
                    'street': getattr(advisor, 'address', ''),
                    'city': getattr(advisor, 'city', ''),
                    'state': getattr(advisor, 'state', ''),
                    'zip': getattr(advisor, 'zip_code', '')
                },
                'branding': {
                    'logo_url': advisor.logo.url if hasattr(advisor, 'logo') and advisor.logo else None,
                    'primary_color': getattr(advisor, 'primary_color', '#0072C6'),
                    'company_name': getattr(advisor, 'white_label_company_name', '') or getattr(advisor, 'company_name', ''),
                    'support_email': getattr(advisor, 'white_label_support_email', ''),
                    'custom_disclosure': getattr(advisor, 'custom_disclosure', '')
                }
            }
        except Exception as e:
            logger.error(f"Error serializing advisor: {str(e)}")
            return {
                'name': 'RetirementAdvisorPro',
                'company': 'RetirementAdvisorPro',
                'email': '',
                'phone': '',
                'website': '',
                'address': {},
                'branding': {
                    'primary_color': '#0072C6',
                    'company_name': 'RetirementAdvisorPro'
                }
            }
    
    def _serialize_spouse(self, client: Client) -> Optional[Dict]:
        """Serialize spouse data if available"""
        try:
            if hasattr(client, 'spouse') and client.spouse:
                spouse = client.spouse
                return {
                    'first_name': spouse.first_name,
                    'last_name': spouse.last_name,
                    'full_name': f"{spouse.first_name} {spouse.last_name}",
                    'birthdate': spouse.birthdate.isoformat() if spouse.birthdate else None,
                    'age': self._calculate_age(spouse.birthdate) if spouse.birthdate else None
                }
        except Exception as e:
            logger.error(f"Error serializing spouse: {str(e)}")
        
        return None
    
    def _calculate_age(self, birthdate) -> Optional[int]:
        """Calculate age from birthdate"""
        try:
            if not birthdate:
                return None
            today = datetime.now().date()
            return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        except Exception as e:
            logger.error(f"Error calculating age: {str(e)}")
            return None
    
    def _calculate_total_assets(self, scenario: Scenario) -> float:
        """Calculate total assets for a scenario"""
        try:
            total = 0.0
            
            # Get all assets related to the scenario/client
            if hasattr(scenario, 'assets'):
                for asset in scenario.assets.all():
                    if hasattr(asset, 'current_balance'):
                        total += float(asset.current_balance or 0)
            
            return total
        except Exception as e:
            logger.error(f"Error calculating total assets: {str(e)}")
            return 0.0
    
    def _calculate_annual_income(self, scenario: Scenario) -> float:
        """Calculate projected annual income for a scenario"""
        try:
            total = 0.0
            
            # Get income sources
            if hasattr(scenario, 'income_sources'):
                for income in scenario.income_sources.all():
                    if hasattr(income, 'monthly_amount'):
                        total += float(income.monthly_amount or 0) * 12
            
            return total
        except Exception as e:
            logger.error(f"Error calculating annual income: {str(e)}")
            return 0.0
    
    def _calculate_scenario_summary(self, scenario: Scenario, yearly_results: List) -> Dict:
        """Calculate summary metrics for scenario"""
        try:
            if not yearly_results:
                return {
                    'success_rate': 0.0,
                    'total_assets': self._calculate_total_assets(scenario),
                    'retirement_income': self._calculate_annual_income(scenario),
                    'years_analyzed': 0
                }
            
            # Calculate summary from yearly results
            final_year = yearly_results[-1] if yearly_results else {}
            
            return {
                'success_rate': 85.0,  # Mock success rate - would be calculated from Monte Carlo
                'total_assets': self._calculate_total_assets(scenario),
                'retirement_income': self._calculate_annual_income(scenario),
                'years_analyzed': len(yearly_results),
                'final_portfolio_value': final_year.get('total_assets', 0),
                'average_annual_withdrawal': sum(yr.get('total_expenses', 0) for yr in yearly_results) / len(yearly_results) if yearly_results else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating scenario summary: {str(e)}")
            return {
                'success_rate': 0.0,
                'total_assets': 0.0,
                'retirement_income': 0.0,
                'years_analyzed': 0
            }
    
    def _get_irmaa_analysis(self, scenario: Scenario, yearly_results: List) -> Dict:
        """Get IRMAA analysis for scenario"""
        try:
            # Check if any years hit IRMAA thresholds
            irmaa_years = []
            total_irmaa_cost = 0.0
            
            for year_data in yearly_results:
                if year_data.get('irmaa_surcharge', 0) > 0:
                    irmaa_years.append({
                        'year': year_data.get('year'),
                        'magi': year_data.get('magi', 0),
                        'surcharge': year_data.get('irmaa_surcharge', 0),
                        'bracket': year_data.get('irmaa_bracket_number', 0)
                    })
                    total_irmaa_cost += float(year_data.get('irmaa_surcharge', 0))
            
            return {
                'reaches_threshold': len(irmaa_years) > 0,
                'affected_years': len(irmaa_years),
                'total_additional_cost': total_irmaa_cost,
                'irmaa_years': irmaa_years[:5],  # Limit to first 5 years
                'recommendations': self._get_irmaa_recommendations(irmaa_years)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing IRMAA: {str(e)}")
            return {
                'reaches_threshold': False,
                'affected_years': 0,
                'total_additional_cost': 0.0,
                'irmaa_years': [],
                'recommendations': []
            }
    
    def _get_tax_analysis(self, scenario: Scenario, yearly_results: List) -> Dict:
        """Get tax analysis for scenario"""
        try:
            total_taxes = 0.0
            tax_years = []
            
            for year_data in yearly_results:
                year_taxes = year_data.get('total_taxes', 0)
                total_taxes += float(year_taxes)
                
                if year_taxes > 0:
                    tax_years.append({
                        'year': year_data.get('year'),
                        'federal_tax': year_data.get('federal_tax', 0),
                        'state_tax': year_data.get('state_tax', 0),
                        'total_tax': year_taxes,
                        'effective_rate': year_data.get('effective_tax_rate', 0)
                    })
            
            average_tax_rate = (total_taxes / sum(yr.get('total_income', 1) for yr in yearly_results)) * 100 if yearly_results else 0
            
            return {
                'total_lifetime_taxes': total_taxes,
                'average_tax_rate': average_tax_rate,
                'years_analyzed': len(tax_years),
                'tax_optimization_opportunities': self._identify_tax_opportunities(tax_years)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing taxes: {str(e)}")
            return {
                'total_lifetime_taxes': 0.0,
                'average_tax_rate': 0.0,
                'years_analyzed': 0,
                'tax_optimization_opportunities': []
            }
    
    def _generate_recommendations(self, scenario: Scenario, yearly_results: List) -> List[str]:
        """Generate recommendations based on scenario analysis"""
        recommendations = []
        
        try:
            # Asset-based recommendations
            total_assets = self._calculate_total_assets(scenario)
            if total_assets < 500000:
                recommendations.append("Consider increasing retirement contributions to build adequate savings")
            elif total_assets > 2000000:
                recommendations.append("Explore advanced tax planning strategies for high-net-worth individuals")
            
            # IRMAA-based recommendations  
            irmaa_analysis = self._get_irmaa_analysis(scenario, yearly_results)
            if irmaa_analysis['reaches_threshold']:
                recommendations.append("Consider Roth conversion strategies to manage IRMAA exposure")
            
            # Age-based recommendations
            if scenario.retirement_age < 62:
                recommendations.append("Plan for healthcare coverage bridge until Medicare eligibility")
            elif scenario.retirement_age > 67:
                recommendations.append("Maximize delayed retirement credits for Social Security")
            
            # Default recommendations
            if not recommendations:
                recommendations = [
                    "Review and rebalance portfolio allocation annually",
                    "Consider tax-loss harvesting opportunities",
                    "Monitor Required Minimum Distribution (RMD) planning",
                    "Evaluate long-term care insurance needs"
                ]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            recommendations = ["Consult with your financial advisor for personalized recommendations"]
        
        return recommendations
    
    def _get_irmaa_recommendations(self, irmaa_years: List) -> List[str]:
        """Get specific IRMAA recommendations"""
        if not irmaa_years:
            return []
        
        recommendations = [
            "Consider Roth conversions in low-income years to reduce future MAGI",
            "Explore tax-loss harvesting to offset capital gains",
            "Review withdrawal sequencing from different account types"
        ]
        
        if len(irmaa_years) > 5:
            recommendations.append("Develop multi-year tax planning strategy to minimize IRMAA exposure")
        
        return recommendations
    
    def _identify_tax_opportunities(self, tax_years: List) -> List[str]:
        """Identify tax optimization opportunities"""
        opportunities = []
        
        if not tax_years:
            return opportunities
        
        # Check for high tax years
        high_tax_years = [yr for yr in tax_years if yr.get('effective_rate', 0) > 25]
        if high_tax_years:
            opportunities.append("Consider income smoothing strategies")
        
        # Check for varying tax rates
        tax_rates = [yr.get('effective_rate', 0) for yr in tax_years]
        if max(tax_rates) - min(tax_rates) > 10:
            opportunities.append("Optimize withdrawal timing based on tax brackets")
        
        return opportunities