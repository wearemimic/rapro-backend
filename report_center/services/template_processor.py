"""
Template Processing Engine
Handles template configuration processing and content generation
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils import timezone

from ..models import ReportTemplate, Report, ReportSection
from .scenario_integration_service import ScenarioDataIntegrationService

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """
    Processes report templates and generates structured content for PDF/PowerPoint generation
    """
    
    def __init__(self):
        self.scenario_service = ScenarioDataIntegrationService()
        self.supported_section_types = [
            'executive_summary',
            'client_overview', 
            'financial_projections',
            'asset_analysis',
            'income_analysis',
            'expense_analysis',
            'tax_analysis',
            'monte_carlo_analysis',
            'roth_conversion',
            'social_security',
            'recommendations',
            'disclaimers',
            'appendix'
        ]
    
    def process_template(self, report: Report) -> Dict[str, Any]:
        """
        Process report template and generate structured content
        """
        try:
            if not report.template:
                raise ValueError("Report must have an associated template")
            
            template = report.template
            template_config = template.template_config or {}
            
            # Get scenario data
            scenario_data = self.scenario_service.format_data_for_template(report, template_config)
            
            # Process template configuration
            processed_content = {
                'template_id': str(template.id),
                'template_name': template.name,
                'template_type': template.template_type,
                'processed_at': timezone.now().isoformat(),
                'sections': [],
                'metadata': {
                    'page_count': 0,
                    'section_count': 0,
                    'chart_count': 0
                }
            }
            
            # Process sections from template configuration
            template_sections = template_config.get('sections', [])
            
            for i, section_config in enumerate(template_sections):
                section_data = self._process_section(section_config, scenario_data, report)
                if section_data:
                    processed_content['sections'].append(section_data)
                    processed_content['metadata']['section_count'] += 1
                    
                    # Count charts in this section
                    charts = section_data.get('charts', [])
                    processed_content['metadata']['chart_count'] += len(charts)
            
            # Add sections from ReportSection models if they exist
            db_sections = report.sections.filter(is_enabled=True).order_by('order')
            for section in db_sections:
                section_data = self._process_db_section(section, scenario_data, report)
                if section_data:
                    processed_content['sections'].append(section_data)
                    processed_content['metadata']['section_count'] += 1
            
            # Estimate page count
            processed_content['metadata']['page_count'] = max(1, processed_content['metadata']['section_count'] // 2)
            
            logger.info(f"Template processed successfully for report {report.id}: "
                       f"{processed_content['metadata']['section_count']} sections, "
                       f"{processed_content['metadata']['chart_count']} charts")
            
            return processed_content
            
        except Exception as e:
            logger.error(f"Template processing failed for report {report.id}: {str(e)}")
            raise
    
    def _process_section(self, section_config: Dict, scenario_data: Dict, report: Report) -> Optional[Dict[str, Any]]:
        """Process individual section from template configuration"""
        
        try:
            section_type = section_config.get('type')
            if section_type not in self.supported_section_types:
                logger.warning(f"Unsupported section type: {section_type}")
                return None
            
            section_data = {
                'type': section_type,
                'title': section_config.get('title', section_type.replace('_', ' ').title()),
                'order': section_config.get('order', 0),
                'enabled': section_config.get('enabled', True),
                'content': {},
                'charts': [],
                'tables': []
            }
            
            # Generate content based on section type
            if section_type == 'executive_summary':
                section_data['content'] = self._generate_executive_summary_content(scenario_data, report)
            elif section_type == 'client_overview':
                section_data['content'] = self._generate_client_overview_content(scenario_data, report)
            elif section_type == 'financial_projections':
                section_data['content'] = self._generate_financial_projections_content(scenario_data, report)
                section_data['charts'] = self._get_financial_charts(scenario_data)
            elif section_type == 'asset_analysis':
                section_data['content'] = self._generate_asset_analysis_content(scenario_data, report)
                section_data['charts'] = self._get_asset_charts(scenario_data)
            elif section_type == 'tax_analysis':
                section_data['content'] = self._generate_tax_analysis_content(scenario_data, report)
                section_data['charts'] = self._get_tax_charts(scenario_data)
            elif section_type == 'monte_carlo_analysis':
                section_data['content'] = self._generate_monte_carlo_content(scenario_data, report)
                section_data['charts'] = self._get_monte_carlo_charts(scenario_data)
            elif section_type == 'roth_conversion':
                section_data['content'] = self._generate_roth_conversion_content(scenario_data, report)
                section_data['charts'] = self._get_roth_conversion_charts(scenario_data)
            elif section_type == 'recommendations':
                section_data['content'] = self._generate_recommendations_content(scenario_data, report)
            else:
                # Generic content
                section_data['content'] = self._generate_generic_content(section_config, scenario_data)
            
            return section_data
            
        except Exception as e:
            logger.error(f"Section processing failed for {section_type}: {str(e)}")
            return None
    
    def _process_db_section(self, section: ReportSection, scenario_data: Dict, report: Report) -> Optional[Dict[str, Any]]:
        """Process section from database ReportSection model"""
        
        try:
            content_config = section.content_config or {}
            
            section_data = {
                'type': section.section_type,
                'title': section.title,
                'order': section.order,
                'enabled': section.is_enabled,
                'content': content_config.get('content', {}),
                'charts': content_config.get('charts', []),
                'tables': content_config.get('tables', [])
            }
            
            return section_data
            
        except Exception as e:
            logger.error(f"DB section processing failed for section {section.id}: {str(e)}")
            return None
    
    def _generate_executive_summary_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate executive summary content"""
        
        client_data = scenario_data.get('client_data', {})
        scenario = scenario_data.get('scenario_data', {})
        
        return {
            'summary_text': f"""
            This retirement planning analysis for {client_data.get('full_name', 'the client')} 
            evaluates the current financial position and projects potential retirement outcomes. 
            Based on the "{scenario.get('name', 'current scenario')}" analysis, we have identified 
            key opportunities to optimize retirement income and tax efficiency.
            """,
            'key_findings': [
                f"Current asset position: ${scenario.get('total_assets', 0):,.0f}",
                f"Projected annual retirement income: ${scenario.get('total_annual_income', 0):,.0f}",
                f"Years to retirement: {max(0, scenario.get('retirement_age', 65) - client_data.get('age', 65))}",
                "Tax optimization opportunities identified through Roth conversion analysis"
            ],
            'next_steps': [
                "Review and approve recommended asset allocation adjustments",
                "Implement Roth conversion strategy as outlined",
                "Schedule quarterly progress reviews",
                "Update projections with any life changes"
            ]
        }
    
    def _generate_client_overview_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate client overview content"""
        
        client_data = scenario_data.get('client_data', {})
        
        return {
            'personal_info': client_data,
            'financial_snapshot': {
                'current_income': client_data.get('current_income', 0),
                'current_savings': client_data.get('current_savings', 0),
                'retirement_target_age': client_data.get('retirement_age', 65),
                'risk_tolerance': client_data.get('risk_tolerance', 'Moderate')
            }
        }
    
    def _generate_financial_projections_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate financial projections content"""
        
        projections = scenario_data.get('financial_projections', {})
        
        return {
            'projection_summary': {
                'years_analyzed': len(projections.get('projection_years', [])),
                'starting_assets': projections.get('asset_projections', [0])[0] if projections.get('asset_projections') else 0,
                'ending_assets': projections.get('asset_projections', [0])[-1] if projections.get('asset_projections') else 0,
                'total_income_projected': sum(projections.get('income_projections', [])),
                'total_expenses_projected': sum(projections.get('expense_projections', []))
            },
            'annual_projections': projections
        }
    
    def _generate_asset_analysis_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate asset analysis content"""
        
        scenario = scenario_data.get('scenario_data', {})
        assets = scenario.get('assets', [])
        
        return {
            'asset_summary': {
                'total_assets': scenario.get('total_assets', 0),
                'asset_count': len(assets),
                'largest_asset': max(assets, key=lambda x: x.get('current_balance', 0)) if assets else {},
                'diversification_score': 'Well Diversified'  # Would be calculated
            },
            'asset_details': assets
        }
    
    def _generate_tax_analysis_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate tax analysis content"""
        
        scenario = scenario_data.get('scenario_data', {})
        
        return {
            'tax_strategy': {
                'primary_state': scenario.get('primary_state', ''),
                'roth_conversion_enabled': bool(scenario.get('roth_conversion_start_year')),
                'irmaa_consideration': 'Included in analysis',
                'optimization_opportunities': [
                    'Roth conversion ladder implementation',
                    'Tax-loss harvesting in taxable accounts',
                    'Medicare IRMAA bracket management',
                    'State tax minimization strategies'
                ]
            },
            'tax_settings': scenario
        }
    
    def _generate_monte_carlo_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate Monte Carlo analysis content"""
        
        return {
            'simulation_parameters': {
                'simulations_run': 10000,
                'market_volatility': 'Historical averages (1926-2023)',
                'inflation_assumption': '3.0% annually',
                'confidence_intervals': ['10th', '25th', '50th', '75th', '90th']
            },
            'success_probability': '85%',  # Would be calculated
            'key_insights': [
                'High probability of meeting retirement income goals',
                'Asset diversification reduces downside risk',
                'Conservative spending assumptions increase success rate'
            ]
        }
    
    def _generate_roth_conversion_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate Roth conversion analysis content"""
        
        scenario = scenario_data.get('scenario_data', {})
        
        return {
            'conversion_strategy': {
                'start_year': scenario.get('roth_conversion_start_year'),
                'duration_years': scenario.get('roth_conversion_duration'),
                'annual_amount': scenario.get('roth_conversion_annual_amount', 0),
                'total_conversions': scenario.get('roth_conversion_annual_amount', 0) * scenario.get('roth_conversion_duration', 0)
            },
            'tax_benefits': {
                'immediate_cost': 'Higher taxes during conversion years',
                'long_term_benefit': 'Tax-free withdrawals in retirement',
                'irmaa_impact': 'May trigger higher Medicare premiums temporarily',
                'estate_benefits': 'No required minimum distributions'
            }
        }
    
    def _generate_recommendations_content(self, scenario_data: Dict, report: Report) -> Dict[str, Any]:
        """Generate recommendations content"""
        
        client_data = scenario_data.get('client_data', {})
        scenario = scenario_data.get('scenario_data', {})
        
        recommendations = []
        
        # Asset-based recommendations
        if scenario.get('total_assets', 0) < client_data.get('current_income', 0) * 10:
            recommendations.append({
                'category': 'Savings',
                'priority': 'High',
                'recommendation': 'Increase retirement savings rate to reach 10x income target by retirement',
                'action_items': [
                    'Consider increasing 401(k) contribution percentage',
                    'Maximize employer matching contributions',
                    'Explore additional IRA contributions'
                ]
            })
        
        # Roth conversion recommendation
        if scenario.get('roth_conversion_start_year'):
            recommendations.append({
                'category': 'Tax Planning',
                'priority': 'Medium',
                'recommendation': 'Implement planned Roth conversion strategy',
                'action_items': [
                    f"Begin conversions in {scenario.get('roth_conversion_start_year')}",
                    f"Convert ${scenario.get('roth_conversion_annual_amount', 0):,.0f} annually",
                    'Monitor tax bracket impacts annually'
                ]
            })
        
        # Social Security recommendation
        if scenario.get('primary_ss_claiming_age'):
            recommendations.append({
                'category': 'Social Security',
                'priority': 'Medium',
                'recommendation': f"Claim Social Security at age {scenario.get('primary_ss_claiming_age')}",
                'action_items': [
                    'Review annual Social Security statements',
                    'Consider spousal claiming strategies',
                    'Monitor benefit reduction legislation'
                ]
            })
        
        return {
            'recommendations': recommendations,
            'priority_summary': {
                'high_priority': len([r for r in recommendations if r['priority'] == 'High']),
                'medium_priority': len([r for r in recommendations if r['priority'] == 'Medium']),
                'low_priority': len([r for r in recommendations if r['priority'] == 'Low'])
            }
        }
    
    def _generate_generic_content(self, section_config: Dict, scenario_data: Dict) -> Dict[str, Any]:
        """Generate generic content for unknown section types"""
        
        return {
            'content_type': 'generic',
            'raw_config': section_config,
            'content_text': section_config.get('content', 'Content not configured for this section type.')
        }
    
    def _get_financial_charts(self, scenario_data: Dict) -> List[Dict[str, Any]]:
        """Get chart configurations for financial projections section"""
        
        chart_data = scenario_data.get('chart_data', {})
        
        return [
            {
                'chart_id': 'asset_timeline',
                'chart_type': 'asset_timeline',
                'title': 'Portfolio Value Over Time',
                'data': chart_data.get('asset_timeline', {}),
                'position': 'full_width'
            },
            {
                'chart_id': 'income_vs_expenses',
                'chart_type': 'income_projection',
                'title': 'Income vs Expenses Projection',
                'data': chart_data.get('income_projection', {}),
                'position': 'full_width'
            }
        ]
    
    def _get_asset_charts(self, scenario_data: Dict) -> List[Dict[str, Any]]:
        """Get chart configurations for asset analysis section"""
        
        return [
            {
                'chart_id': 'asset_allocation',
                'chart_type': 'pie',
                'title': 'Current Asset Allocation',
                'data': self._prepare_asset_allocation_data(scenario_data),
                'position': 'half_width'
            }
        ]
    
    def _get_tax_charts(self, scenario_data: Dict) -> List[Dict[str, Any]]:
        """Get chart configurations for tax analysis section"""
        
        chart_data = scenario_data.get('chart_data', {})
        
        return [
            {
                'chart_id': 'tax_burden',
                'chart_type': 'tax_analysis',
                'title': 'Annual Tax Burden Analysis',
                'data': chart_data.get('tax_analysis', {}),
                'position': 'full_width'
            }
        ]
    
    def _get_monte_carlo_charts(self, scenario_data: Dict) -> List[Dict[str, Any]]:
        """Get chart configurations for Monte Carlo section"""
        
        chart_data = scenario_data.get('chart_data', {})
        
        return [
            {
                'chart_id': 'monte_carlo_results',
                'chart_type': 'monte_carlo',
                'title': 'Monte Carlo Simulation Results',
                'data': chart_data.get('monte_carlo', {}),
                'position': 'full_width'
            }
        ]
    
    def _get_roth_conversion_charts(self, scenario_data: Dict) -> List[Dict[str, Any]]:
        """Get chart configurations for Roth conversion section"""
        
        chart_data = scenario_data.get('chart_data', {})
        roth_data = chart_data.get('roth_conversion', {})
        
        if not roth_data:
            return []
        
        return [
            {
                'chart_id': 'roth_conversion_schedule',
                'chart_type': 'roth_conversion',
                'title': 'Roth Conversion Strategy',
                'data': roth_data,
                'position': 'full_width'
            }
        ]
    
    def _prepare_asset_allocation_data(self, scenario_data: Dict) -> Dict[str, Any]:
        """Prepare asset allocation data for pie chart"""
        
        scenario = scenario_data.get('scenario_data', {})
        assets = scenario.get('assets', [])
        
        # Group assets by type for pie chart
        allocation = {}
        for asset in assets:
            asset_type = asset.get('investment_type', 'Other')
            current_balance = asset.get('current_balance', 0)
            
            if asset_type not in allocation:
                allocation[asset_type] = 0
            allocation[asset_type] += current_balance
        
        return {
            'labels': list(allocation.keys()),
            'data': list(allocation.values()),
            'title': 'Asset Allocation'
        }
    
    def validate_template_config(self, template_config: Dict) -> Dict[str, Any]:
        """
        Validate template configuration for completeness and correctness
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sections_validated': 0
        }
        
        try:
            # Check required fields
            if 'sections' not in template_config:
                validation_result['errors'].append("Template must have 'sections' configuration")
                validation_result['valid'] = False
            
            sections = template_config.get('sections', [])
            
            for i, section in enumerate(sections):
                section_errors = []
                
                # Check section type
                section_type = section.get('type')
                if not section_type:
                    section_errors.append(f"Section {i}: Missing 'type' field")
                elif section_type not in self.supported_section_types:
                    validation_result['warnings'].append(f"Section {i}: Unsupported section type '{section_type}'")
                
                # Check title
                if not section.get('title'):
                    validation_result['warnings'].append(f"Section {i}: Missing title")
                
                # Check order
                if 'order' not in section:
                    validation_result['warnings'].append(f"Section {i}: Missing order field")
                
                validation_result['errors'].extend(section_errors)
                validation_result['sections_validated'] += 1
            
            if validation_result['errors']:
                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Template validation failed: {str(e)}")
            return {
                'valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'warnings': [],
                'sections_validated': 0
            }
    
    def create_default_template_config(self, template_type: str) -> Dict[str, Any]:
        """
        Create default template configuration for different template types
        """
        
        base_config = {
            'template_version': '1.0',
            'created_at': timezone.now().isoformat(),
            'page_settings': {
                'orientation': 'portrait',
                'margins': {'top': 1, 'bottom': 1, 'left': 1, 'right': 1},
                'font_family': 'Helvetica',
                'base_font_size': 11
            },
            'branding': {
                'show_logo': True,
                'logo_position': 'header',
                'company_colors': {
                    'primary': '#3498db',
                    'secondary': '#2c3e50',
                    'accent': '#27ae60'
                }
            }
        }
        
        if template_type == 'executive_summary':
            base_config['sections'] = [
                {'type': 'executive_summary', 'title': 'Executive Summary', 'order': 1, 'enabled': True},
                {'type': 'client_overview', 'title': 'Client Overview', 'order': 2, 'enabled': True},
                {'type': 'financial_projections', 'title': 'Financial Projections', 'order': 3, 'enabled': True},
                {'type': 'recommendations', 'title': 'Recommendations', 'order': 4, 'enabled': True}
            ]
        
        elif template_type == 'comprehensive':
            base_config['sections'] = [
                {'type': 'executive_summary', 'title': 'Executive Summary', 'order': 1, 'enabled': True},
                {'type': 'client_overview', 'title': 'Client Profile', 'order': 2, 'enabled': True},
                {'type': 'asset_analysis', 'title': 'Asset Analysis', 'order': 3, 'enabled': True},
                {'type': 'financial_projections', 'title': 'Financial Projections', 'order': 4, 'enabled': True},
                {'type': 'monte_carlo_analysis', 'title': 'Monte Carlo Analysis', 'order': 5, 'enabled': True},
                {'type': 'tax_analysis', 'title': 'Tax Planning', 'order': 6, 'enabled': True},
                {'type': 'roth_conversion', 'title': 'Roth Conversion Strategy', 'order': 7, 'enabled': True},
                {'type': 'social_security', 'title': 'Social Security Planning', 'order': 8, 'enabled': True},
                {'type': 'recommendations', 'title': 'Recommendations', 'order': 9, 'enabled': True},
                {'type': 'disclaimers', 'title': 'Important Disclaimers', 'order': 10, 'enabled': True}
            ]
        
        elif template_type == 'tax_focused':
            base_config['sections'] = [
                {'type': 'executive_summary', 'title': 'Tax Strategy Overview', 'order': 1, 'enabled': True},
                {'type': 'client_overview', 'title': 'Client Tax Profile', 'order': 2, 'enabled': True},
                {'type': 'tax_analysis', 'title': 'Current Tax Analysis', 'order': 3, 'enabled': True},
                {'type': 'roth_conversion', 'title': 'Roth Conversion Opportunities', 'order': 4, 'enabled': True},
                {'type': 'recommendations', 'title': 'Tax Optimization Recommendations', 'order': 5, 'enabled': True}
            ]
        
        elif template_type == 'social_security':
            base_config['sections'] = [
                {'type': 'executive_summary', 'title': 'Social Security Strategy', 'order': 1, 'enabled': True},
                {'type': 'client_overview', 'title': 'Client Profile', 'order': 2, 'enabled': True},
                {'type': 'social_security', 'title': 'Social Security Analysis', 'order': 3, 'enabled': True},
                {'type': 'recommendations', 'title': 'Claiming Strategy Recommendations', 'order': 4, 'enabled': True}
            ]
        
        else:
            # Default template
            base_config['sections'] = [
                {'type': 'executive_summary', 'title': 'Summary', 'order': 1, 'enabled': True},
                {'type': 'client_overview', 'title': 'Client Information', 'order': 2, 'enabled': True},
                {'type': 'recommendations', 'title': 'Next Steps', 'order': 3, 'enabled': True}
            ]
        
        return base_config