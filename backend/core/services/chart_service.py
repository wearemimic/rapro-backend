"""
Report Chart Service
Handles chart data preparation and visualization for reports
"""

import logging
from typing import Dict, List, Optional
import json

from ..models import Scenario

logger = logging.getLogger(__name__)


class ReportChartService:
    """Service for preparing chart data for various visualizations"""
    
    def prepare_chart_data(self, scenarios: List[Scenario]) -> Dict:
        """
        Prepare chart data for various visualizations
        
        Args:
            scenarios: List of Scenario model instances
            
        Returns:
            Dictionary containing chart configurations and data
        """
        try:
            logger.info(f"Preparing chart data for {len(scenarios)} scenarios")
            
            charts = {}
            
            # Monte Carlo Success Rate Charts
            charts['monte_carlo'] = self._prepare_monte_carlo_chart(scenarios)
            
            # Asset Allocation Charts  
            charts['asset_allocation'] = self._prepare_asset_allocation_chart(scenarios)
            
            # Income Timeline Charts
            charts['income_timeline'] = self._prepare_income_timeline_chart(scenarios)
            
            # Tax Impact Analysis
            charts['tax_analysis'] = self._prepare_tax_analysis_chart(scenarios)
            
            # IRMAA Impact Visualization
            charts['irmaa_impact'] = self._prepare_irmaa_chart(scenarios)
            
            # Portfolio Growth Chart
            charts['portfolio_growth'] = self._prepare_portfolio_growth_chart(scenarios)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error preparing chart data: {str(e)}", exc_info=True)
            return {}
    
    def _prepare_monte_carlo_chart(self, scenarios: List[Scenario]) -> Dict:
        """Prepare Monte Carlo simulation chart data"""
        try:
            chart_data = {
                'type': 'line',
                'title': 'Portfolio Success Rate Analysis',
                'subtitle': 'Monte Carlo Simulation Results',
                'data': {
                    'labels': [],
                    'datasets': []
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'top'},
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.dataset.label + ": " + context.parsed.y + "%"; }'
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'max': 100,
                            'ticks': {'callback': 'function(value) { return value + "%"; }'}
                        }
                    }
                }
            }
            
            # Generate years for x-axis (retirement years)
            years = list(range(65, 96))  # Ages 65-95
            chart_data['data']['labels'] = [str(year) for year in years]
            
            # Generate simulation data for each scenario
            colors = ['#0072C6', '#28A745', '#DC3545', '#FFC107', '#6F42C1']
            
            for i, scenario in enumerate(scenarios[:5]):  # Limit to 5 scenarios
                success_rates = self._generate_mock_success_rates(scenario, years)
                
                chart_data['data']['datasets'].append({
                    'label': scenario.name,
                    'data': success_rates,
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': colors[i % len(colors)] + '20',  # Add transparency
                    'tension': 0.4,
                    'fill': False
                })
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing Monte Carlo chart: {str(e)}")
            return {}
    
    def _prepare_asset_allocation_chart(self, scenarios: List[Scenario]) -> Dict:
        """Prepare asset allocation pie chart"""
        try:
            # Use the first scenario for allocation display
            scenario = scenarios[0] if scenarios else None
            
            if not scenario:
                return {}
            
            chart_data = {
                'type': 'pie',
                'title': 'Current Asset Allocation',
                'subtitle': f'Portfolio Distribution for {scenario.name}',
                'data': {
                    'labels': ['Stocks', 'Bonds', 'Cash', 'Real Estate', 'Other'],
                    'datasets': [{
                        'label': 'Asset Allocation',
                        'data': [60, 25, 5, 7, 3],  # Mock percentages
                        'backgroundColor': [
                            '#0072C6',  # Stocks - Blue
                            '#28A745',  # Bonds - Green  
                            '#FFC107',  # Cash - Yellow
                            '#DC3545',  # Real Estate - Red
                            '#6C757D'   # Other - Gray
                        ],
                        'borderWidth': 2,
                        'borderColor': '#FFFFFF'
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {
                            'position': 'right'
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.label + ": " + context.parsed + "%"; }'
                            }
                        }
                    }
                }
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing asset allocation chart: {str(e)}")
            return {}
    
    def _prepare_income_timeline_chart(self, scenarios: List[Scenario]) -> Dict:
        """Prepare income timeline chart"""
        try:
            chart_data = {
                'type': 'bar',
                'title': 'Retirement Income Timeline',
                'subtitle': 'Projected Annual Income by Source',
                'data': {
                    'labels': [],
                    'datasets': []
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'x': {
                            'stacked': True
                        },
                        'y': {
                            'stacked': True,
                            'ticks': {
                                'callback': 'function(value) { return "$" + (value/1000) + "K"; }'
                            }
                        }
                    },
                    'plugins': {
                        'legend': {
                            'position': 'top'
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.dataset.label + ": $" + context.parsed.y.toLocaleString(); }'
                            }
                        }
                    }
                }
            }
            
            # Generate timeline years  
            years = list(range(65, 81))  # Ages 65-80
            chart_data['data']['labels'] = [f'Age {year}' for year in years]
            
            # Income sources
            income_sources = [
                {'name': 'Social Security', 'color': '#0072C6', 'amounts': [30000] * len(years)},
                {'name': '401k/IRA Withdrawals', 'color': '#28A745', 'amounts': [40000] * len(years)},  
                {'name': 'Pension', 'color': '#FFC107', 'amounts': [15000] * len(years)},
                {'name': 'Other Income', 'color': '#DC3545', 'amounts': [10000] * len(years)}
            ]
            
            for source in income_sources:
                chart_data['data']['datasets'].append({
                    'label': source['name'],
                    'data': source['amounts'],
                    'backgroundColor': source['color'],
                    'borderColor': source['color'],
                    'borderWidth': 1
                })
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing income timeline chart: {str(e)}")
            return {}
    
    def _prepare_tax_analysis_chart(self, scenarios: List[Scenario]) -> Dict:
        """Prepare tax impact analysis chart"""
        try:
            chart_data = {
                'type': 'line',
                'title': 'Tax Impact Analysis',
                'subtitle': 'Federal and State Tax Projections',
                'data': {
                    'labels': [],
                    'datasets': []
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return "$" + (value/1000) + "K"; }'
                            }
                        }
                    },
                    'plugins': {
                        'legend': {
                            'position': 'top'
                        }
                    }
                }
            }
            
            # Generate years
            years = list(range(65, 81))  # Ages 65-80
            chart_data['data']['labels'] = [f'Age {year}' for year in years]
            
            # Tax data for first scenario
            if scenarios:
                scenario = scenarios[0]
                
                # Mock tax data - would be calculated from scenario processor
                federal_taxes = [8000 + (year - 65) * 200 for year in years]
                state_taxes = [2000 + (year - 65) * 50 for year in years]
                
                chart_data['data']['datasets'] = [
                    {
                        'label': 'Federal Tax',
                        'data': federal_taxes,
                        'borderColor': '#DC3545',
                        'backgroundColor': '#DC354520',
                        'tension': 0.4,
                        'fill': False
                    },
                    {
                        'label': 'State Tax',
                        'data': state_taxes,
                        'borderColor': '#28A745',
                        'backgroundColor': '#28A74520',
                        'tension': 0.4,
                        'fill': False
                    }
                ]
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing tax analysis chart: {str(e)}")
            return {}
    
    def _prepare_irmaa_chart(self, scenarios: List[Scenario]) -> Dict:
        """Prepare IRMAA impact visualization"""
        try:
            chart_data = {
                'type': 'line',
                'title': 'IRMAA Impact Analysis',
                'subtitle': 'Medicare Premium Adjustments',
                'data': {
                    'labels': [],
                    'datasets': []
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return "$" + value.toLocaleString(); }'
                            }
                        }
                    },
                    'plugins': {
                        'legend': {
                            'position': 'top'
                        }
                    }
                }
            }
            
            # Generate years (Medicare eligible years)
            years = list(range(65, 81))  # Ages 65-80  
            chart_data['data']['labels'] = [f'Age {year}' for year in years]
            
            # IRMAA surcharge data for first scenario
            if scenarios:
                scenario = scenarios[0]
                
                # Mock IRMAA data - would be calculated from scenario processor
                base_premium = [148] * len(years)  # Base Medicare Part B premium
                irmaa_surcharge = []
                
                for year in years:
                    # Mock logic: higher surcharge after age 70
                    if year > 70:
                        irmaa_surcharge.append(238)  # High income surcharge
                    elif year > 67:
                        irmaa_surcharge.append(59)   # Medium income surcharge
                    else:
                        irmaa_surcharge.append(0)    # No surcharge
                
                chart_data['data']['datasets'] = [
                    {
                        'label': 'Base Medicare Premium',
                        'data': base_premium,
                        'borderColor': '#0072C6',
                        'backgroundColor': '#0072C620',
                        'tension': 0.4,
                        'fill': False
                    },
                    {
                        'label': 'IRMAA Surcharge',
                        'data': irmaa_surcharge,
                        'borderColor': '#DC3545',
                        'backgroundColor': '#DC354520',
                        'tension': 0.4,
                        'fill': False
                    }
                ]
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing IRMAA chart: {str(e)}")
            return {}
    
    def _prepare_portfolio_growth_chart(self, scenarios: List[Scenario]) -> Dict:
        """Prepare portfolio growth projection chart"""
        try:
            chart_data = {
                'type': 'area',
                'title': 'Portfolio Value Projection',
                'subtitle': 'Asset Growth Over Time',
                'data': {
                    'labels': [],
                    'datasets': []
                },
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return "$" + (value/1000000).toFixed(1) + "M"; }'
                            }
                        }
                    },
                    'plugins': {
                        'legend': {
                            'position': 'top'
                        },
                        'filler': {
                            'propagate': True
                        }
                    },
                    'elements': {
                        'line': {
                            'tension': 0.4
                        }
                    }
                }
            }
            
            # Generate years
            years = list(range(65, 96))  # Ages 65-95
            chart_data['data']['labels'] = [f'Age {year}' for year in years]
            
            # Generate portfolio values for scenarios
            colors = ['#0072C6', '#28A745', '#DC3545']
            
            for i, scenario in enumerate(scenarios[:3]):  # Limit to 3 scenarios
                portfolio_values = self._generate_portfolio_values(scenario, years)
                
                chart_data['data']['datasets'].append({
                    'label': scenario.name,
                    'data': portfolio_values,
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': colors[i % len(colors)] + '30',
                    'fill': True,
                    'tension': 0.4
                })
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing portfolio growth chart: {str(e)}")
            return {}
    
    def _generate_mock_success_rates(self, scenario: Scenario, years: List[int]) -> List[float]:
        """Generate mock Monte Carlo success rates"""
        try:
            # Base success rate starts high and decreases with age
            base_rate = 95.0
            rates = []
            
            for i, year in enumerate(years):
                # Decrease success rate over time
                decline_rate = i * 0.8  # Gradual decline
                success_rate = max(base_rate - decline_rate, 20.0)  # Minimum 20%
                rates.append(round(success_rate, 1))
            
            return rates
            
        except Exception as e:
            logger.error(f"Error generating success rates: {str(e)}")
            return [85.0] * len(years)  # Default flat rate
    
    def _generate_portfolio_values(self, scenario: Scenario, years: List[int]) -> List[float]:
        """Generate portfolio value projections"""
        try:
            # Start with initial portfolio value
            initial_value = 1000000  # $1M default
            values = []
            
            # Mock portfolio growth/decline
            for i, year in enumerate(years):
                # Simple model: growth early, decline later
                if i < 10:  # First 10 years: modest growth
                    value = initial_value * (1.04 ** i)  # 4% annual growth
                else:  # Later years: withdrawal phase
                    withdraw_years = i - 10
                    value = initial_value * (1.04 ** 10) * (0.95 ** withdraw_years)  # 5% annual decline
                
                values.append(max(value, 0))  # Ensure non-negative
            
            return values
            
        except Exception as e:
            logger.error(f"Error generating portfolio values: {str(e)}")
            return [1000000] * len(years)  # Default flat value
    
    def get_chart_for_export(self, chart_config: Dict, format: str = 'png') -> Optional[bytes]:
        """
        Generate chart image for export to PDF/PowerPoint
        This would integrate with a charting library like matplotlib or plotly
        """
        try:
            # This would generate actual chart images
            # For now, return None (charts will be represented as text in exports)
            logger.info(f"Chart export requested for format: {format}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating chart for export: {str(e)}")
            return None