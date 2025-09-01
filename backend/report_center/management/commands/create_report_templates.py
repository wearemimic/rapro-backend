"""
Django management command to create the 5 professional report templates
required for Phase 1 deliverables of the Report Center.
"""
from django.core.management.base import BaseCommand
from report_center.models import ReportTemplate, ReportSection
import json


class Command(BaseCommand):
    help = 'Creates the 5 professional report templates for Report Center Phase 1'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Delete existing templates and recreate them',
        )

    def handle(self, *args, **options):
        if options['recreate']:
            self.stdout.write('Deleting existing system templates...')
            ReportTemplate.objects.filter(is_system_template=True).delete()

        templates_created = 0
        
        # Template 1: Retirement Overview
        retirement_overview = self._create_retirement_overview_template()
        if retirement_overview:
            templates_created += 1
            
        # Template 2: IRMAA Analysis
        irmaa_analysis = self._create_irmaa_analysis_template()
        if irmaa_analysis:
            templates_created += 1
            
        # Template 3: Tax Strategy
        tax_strategy = self._create_tax_strategy_template()
        if tax_strategy:
            templates_created += 1
            
        # Template 4: Scenario Comparison
        scenario_comparison = self._create_scenario_comparison_template()
        if scenario_comparison:
            templates_created += 1
            
        # Template 5: Executive Summary
        executive_summary = self._create_executive_summary_template()
        if executive_summary:
            templates_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {templates_created} report templates')
        )

    def _create_retirement_overview_template(self):
        """Create comprehensive retirement planning overview template"""
        template, created = ReportTemplate.objects.get_or_create(
            name='Comprehensive Retirement Overview',
            template_type='system',
            defaults={
                'description': 'Complete retirement planning analysis including assets, income projections, tax implications, and strategic recommendations.',
                'category': 'retirement',
                'is_active': True,
                'is_system_template': True,
                'template_config': {
                    'theme': 'professional',
                    'color_scheme': 'blue',
                    'page_orientation': 'portrait',
                    'include_charts': True,
                    'include_disclosures': True,
                    'branding': {
                        'logo_placement': 'header',
                        'footer_text': True,
                        'color_customizable': True
                    }
                },
                'tags': ['retirement', 'comprehensive', 'overview', 'professional']
            }
        )
        
        if created:
            # Create sections for this template
            sections_data = [
                {
                    'section_type': 'cover',
                    'name': 'Cover Page',
                    'description': 'Professional cover page with advisor branding and client information',
                    'order_index': 1,
                    'is_required': True,
                    'section_config': {
                        'include_logo': True,
                        'include_date': True,
                        'include_client_name': True,
                        'template_style': 'professional'
                    }
                },
                {
                    'section_type': 'summary',
                    'name': 'Executive Summary',
                    'description': 'High-level overview of current situation and key recommendations',
                    'order_index': 2,
                    'is_required': True,
                    'section_config': {
                        'include_key_metrics': True,
                        'include_recommendations': True,
                        'highlight_concerns': True
                    }
                },
                {
                    'section_type': 'charts',
                    'name': 'Current Financial Position',
                    'description': 'Visual representation of current assets, income, and expenses',
                    'order_index': 3,
                    'is_required': True,
                    'section_config': {
                        'chart_types': ['pie', 'bar', 'timeline'],
                        'include_asset_allocation': True,
                        'include_cash_flow': True
                    }
                },
                {
                    'section_type': 'scenarios',
                    'name': 'Retirement Projections',
                    'description': 'Detailed retirement income and asset projections over time',
                    'order_index': 4,
                    'is_required': True,
                    'section_config': {
                        'projection_years': 30,
                        'include_inflation': True,
                        'show_success_probability': True,
                        'include_monte_carlo': True
                    }
                },
                {
                    'section_type': 'tax_strategy',
                    'name': 'Tax Planning Analysis',
                    'description': 'Tax implications and optimization strategies for retirement',
                    'order_index': 5,
                    'is_required': False,
                    'section_config': {
                        'include_brackets': True,
                        'show_irmaa_impact': True,
                        'roth_conversion_analysis': True
                    }
                },
                {
                    'section_type': 'recommendations',
                    'name': 'Strategic Recommendations',
                    'description': 'Actionable recommendations and next steps',
                    'order_index': 6,
                    'is_required': True,
                    'section_config': {
                        'prioritize_actions': True,
                        'include_timeline': True,
                        'implementation_notes': True
                    }
                }
            ]
            
            for section_data in sections_data:
                ReportSection.objects.create(
                    template=template,
                    **section_data
                )
            
            self.stdout.write(f'✓ Created: {template.name}')
            return template
        else:
            self.stdout.write(f'- Exists: {template.name}')
            return None

    def _create_irmaa_analysis_template(self):
        """Create IRMAA-focused analysis template"""
        template, created = ReportTemplate.objects.get_or_create(
            name='IRMAA Impact Analysis',
            template_type='system',
            defaults={
                'description': 'Specialized analysis of Medicare Income-Related Monthly Adjustment Amounts and optimization strategies.',
                'category': 'irmaa',
                'is_active': True,
                'is_system_template': True,
                'template_config': {
                    'theme': 'healthcare',
                    'color_scheme': 'green',
                    'page_orientation': 'portrait',
                    'focus_areas': ['irmaa', 'medicare', 'tax_optimization'],
                    'advanced_calculations': True
                },
                'tags': ['irmaa', 'medicare', 'tax', 'healthcare', 'optimization']
            }
        )
        
        if created:
            sections_data = [
                {
                    'section_type': 'cover',
                    'name': 'Cover Page',
                    'description': 'IRMAA analysis report cover',
                    'order_index': 1,
                    'is_required': True,
                    'section_config': {'report_type': 'IRMAA Analysis'}
                },
                {
                    'section_type': 'summary',
                    'name': 'IRMAA Overview',
                    'description': 'Explanation of IRMAA and current client situation',
                    'order_index': 2,
                    'is_required': True,
                    'section_config': {
                        'explain_irmaa': True,
                        'current_bracket': True,
                        'premium_impact': True
                    }
                },
                {
                    'section_type': 'irmaa',
                    'name': 'Bracket Analysis',
                    'description': 'Detailed IRMAA bracket analysis and projections',
                    'order_index': 3,
                    'is_required': True,
                    'section_config': {
                        'show_thresholds': True,
                        'bracket_progression': True,
                        'inflation_adjusted': True,
                        'yearly_projections': True
                    }
                },
                {
                    'section_type': 'charts',
                    'name': 'IRMAA Impact Visualizations',
                    'description': 'Charts showing IRMAA impact over time',
                    'order_index': 4,
                    'is_required': True,
                    'section_config': {
                        'chart_types': ['line', 'bar'],
                        'show_crossover_points': True,
                        'premium_projections': True
                    }
                },
                {
                    'section_type': 'recommendations',
                    'name': 'IRMAA Optimization Strategies',
                    'description': 'Specific strategies to minimize IRMAA impact',
                    'order_index': 5,
                    'is_required': True,
                    'section_config': {
                        'roth_conversion_timing': True,
                        'income_management': True,
                        'asset_positioning': True
                    }
                }
            ]
            
            for section_data in sections_data:
                ReportSection.objects.create(template=template, **section_data)
            
            self.stdout.write(f'✓ Created: {template.name}')
            return template
        else:
            self.stdout.write(f'- Exists: {template.name}')
            return None

    def _create_tax_strategy_template(self):
        """Create tax optimization strategy template"""
        template, created = ReportTemplate.objects.get_or_create(
            name='Tax Optimization Strategy',
            template_type='system',
            defaults={
                'description': 'Comprehensive tax planning strategies including Roth conversions, tax-loss harvesting, and income timing.',
                'category': 'tax',
                'is_active': True,
                'is_system_template': True,
                'template_config': {
                    'theme': 'financial',
                    'color_scheme': 'orange',
                    'page_orientation': 'portrait',
                    'tax_complexity': 'advanced',
                    'include_state_taxes': True
                },
                'tags': ['tax', 'strategy', 'optimization', 'roth', 'planning']
            }
        )
        
        if created:
            sections_data = [
                {
                    'section_type': 'cover',
                    'name': 'Cover Page',
                    'description': 'Tax strategy report cover',
                    'order_index': 1,
                    'is_required': True,
                    'section_config': {'report_type': 'Tax Strategy'}
                },
                {
                    'section_type': 'summary',
                    'name': 'Tax Situation Overview',
                    'description': 'Current tax situation and optimization opportunities',
                    'order_index': 2,
                    'is_required': True,
                    'section_config': {
                        'current_brackets': True,
                        'effective_rate': True,
                        'optimization_potential': True
                    }
                },
                {
                    'section_type': 'tax_strategy',
                    'name': 'Federal Tax Analysis',
                    'description': 'Federal tax bracket analysis and projections',
                    'order_index': 3,
                    'is_required': True,
                    'section_config': {
                        'bracket_management': True,
                        'standard_deduction': True,
                        'marginal_rates': True
                    }
                },
                {
                    'section_type': 'roth',
                    'name': 'Roth Conversion Strategy',
                    'description': 'Roth conversion analysis and recommendations',
                    'order_index': 4,
                    'is_required': True,
                    'section_config': {
                        'conversion_ladder': True,
                        'tax_cost_analysis': True,
                        'breakeven_analysis': True,
                        'optimal_timing': True
                    }
                },
                {
                    'section_type': 'charts',
                    'name': 'Tax Impact Projections',
                    'description': 'Visual projections of tax strategies over time',
                    'order_index': 5,
                    'is_required': True,
                    'section_config': {
                        'chart_types': ['line', 'area', 'bar'],
                        'before_after_comparison': True,
                        'cumulative_savings': True
                    }
                },
                {
                    'section_type': 'recommendations',
                    'name': 'Implementation Plan',
                    'description': 'Step-by-step tax optimization implementation',
                    'order_index': 6,
                    'is_required': True,
                    'section_config': {
                        'annual_actions': True,
                        'review_schedule': True,
                        'coordination_notes': True
                    }
                }
            ]
            
            for section_data in sections_data:
                ReportSection.objects.create(template=template, **section_data)
            
            self.stdout.write(f'✓ Created: {template.name}')
            return template
        else:
            self.stdout.write(f'- Exists: {template.name}')
            return None

    def _create_scenario_comparison_template(self):
        """Create scenario comparison template"""
        template, created = ReportTemplate.objects.get_or_create(
            name='Scenario Comparison Analysis',
            template_type='system',
            defaults={
                'description': 'Side-by-side comparison of multiple retirement scenarios with detailed analysis of trade-offs and recommendations.',
                'category': 'comparison',
                'is_active': True,
                'is_system_template': True,
                'template_config': {
                    'theme': 'comparison',
                    'color_scheme': 'purple',
                    'page_orientation': 'landscape',
                    'max_scenarios': 3,
                    'side_by_side': True
                },
                'tags': ['comparison', 'scenarios', 'analysis', 'side-by-side']
            }
        )
        
        if created:
            sections_data = [
                {
                    'section_type': 'cover',
                    'name': 'Cover Page',
                    'description': 'Scenario comparison report cover',
                    'order_index': 1,
                    'is_required': True,
                    'section_config': {'report_type': 'Scenario Comparison'}
                },
                {
                    'section_type': 'summary',
                    'name': 'Scenarios Overview',
                    'description': 'Summary of scenarios being compared',
                    'order_index': 2,
                    'is_required': True,
                    'section_config': {
                        'scenario_descriptions': True,
                        'key_differences': True,
                        'comparison_criteria': True
                    }
                },
                {
                    'section_type': 'data_table',
                    'name': 'Key Metrics Comparison',
                    'description': 'Side-by-side comparison of key financial metrics',
                    'order_index': 3,
                    'is_required': True,
                    'section_config': {
                        'table_format': 'comparison',
                        'highlight_differences': True,
                        'include_percentages': True
                    }
                },
                {
                    'section_type': 'charts',
                    'name': 'Visual Comparisons',
                    'description': 'Charts comparing scenarios across multiple dimensions',
                    'order_index': 4,
                    'is_required': True,
                    'section_config': {
                        'chart_types': ['grouped_bar', 'line', 'area'],
                        'overlay_scenarios': True,
                        'highlight_crossovers': True
                    }
                },
                {
                    'section_type': 'scenarios',
                    'name': 'Detailed Scenario Analysis',
                    'description': 'In-depth analysis of each scenario',
                    'order_index': 5,
                    'is_required': True,
                    'section_config': {
                        'individual_analysis': True,
                        'pros_and_cons': True,
                        'risk_assessment': True
                    }
                },
                {
                    'section_type': 'recommendations',
                    'name': 'Recommendation & Decision Framework',
                    'description': 'Recommended scenario with decision-making framework',
                    'order_index': 6,
                    'is_required': True,
                    'section_config': {
                        'recommended_scenario': True,
                        'decision_factors': True,
                        'implementation_priority': True
                    }
                }
            ]
            
            for section_data in sections_data:
                ReportSection.objects.create(template=template, **section_data)
            
            self.stdout.write(f'✓ Created: {template.name}')
            return template
        else:
            self.stdout.write(f'- Exists: {template.name}')
            return None

    def _create_executive_summary_template(self):
        """Create executive summary template"""
        template, created = ReportTemplate.objects.get_or_create(
            name='Executive Summary Report',
            template_type='system',
            defaults={
                'description': 'Concise executive summary highlighting key findings, recommendations, and action items for busy clients.',
                'category': 'general',
                'is_active': True,
                'is_system_template': True,
                'template_config': {
                    'theme': 'executive',
                    'color_scheme': 'navy',
                    'page_orientation': 'portrait',
                    'page_limit': 4,
                    'concise_format': True
                },
                'tags': ['executive', 'summary', 'concise', 'highlights']
            }
        )
        
        if created:
            sections_data = [
                {
                    'section_type': 'cover',
                    'name': 'Executive Cover',
                    'description': 'Executive-style cover page',
                    'order_index': 1,
                    'is_required': True,
                    'section_config': {
                        'report_type': 'Executive Summary',
                        'executive_layout': True
                    }
                },
                {
                    'section_type': 'summary',
                    'name': 'Key Findings',
                    'description': 'Most important findings and insights',
                    'order_index': 2,
                    'is_required': True,
                    'section_config': {
                        'bullet_format': True,
                        'highlight_critical': True,
                        'quantify_impact': True,
                        'limit_points': 5
                    }
                },
                {
                    'section_type': 'charts',
                    'name': 'Essential Metrics',
                    'description': 'Key charts and visualizations only',
                    'order_index': 3,
                    'is_required': True,
                    'section_config': {
                        'chart_types': ['summary_dashboard'],
                        'limit_charts': 3,
                        'high_impact_only': True
                    }
                },
                {
                    'section_type': 'recommendations',
                    'name': 'Priority Actions',
                    'description': 'Top 3-5 priority recommendations with timeline',
                    'order_index': 4,
                    'is_required': True,
                    'section_config': {
                        'limit_recommendations': 5,
                        'priority_ranking': True,
                        'timeline_included': True,
                        'action_oriented': True
                    }
                }
            ]
            
            for section_data in sections_data:
                ReportSection.objects.create(template=template, **section_data)
            
            self.stdout.write(f'✓ Created: {template.name}')
            return template
        else:
            self.stdout.write(f'- Exists: {template.name}')
            return None