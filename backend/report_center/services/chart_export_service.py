"""
Chart Export Service
Handles exporting Chart.js visualizations for inclusion in PDF and PowerPoint reports
"""

import os
import json
import logging
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg

logger = logging.getLogger(__name__)


class ChartExportService:
    """
    Service for converting Chart.js configurations and data into static images
    for inclusion in PDF and PowerPoint reports
    """
    
    def __init__(self):
        self.chart_storage = getattr(settings, 'REPORT_CENTER_STORAGE', {}).get(
            'CHART_EXPORTS', 
            os.path.join(settings.MEDIA_ROOT, 'report_center/chart_exports/')
        )
        os.makedirs(self.chart_storage, exist_ok=True)
        
        # Set matplotlib style for professional charts
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 11,
            'figure.figsize': (10, 6),
            'figure.dpi': 150,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.facecolor': 'white'
        })
    
    def export_scenario_chart(self, scenario_data: Dict, chart_type: str, chart_id: str) -> Dict[str, Any]:
        """
        Export scenario visualization chart based on RetirementAdvisorPro data
        """
        try:
            if chart_type == 'asset_timeline':
                return self._create_asset_timeline_chart(scenario_data, chart_id)
            elif chart_type == 'income_projection':
                return self._create_income_projection_chart(scenario_data, chart_id)
            elif chart_type == 'tax_analysis':
                return self._create_tax_analysis_chart(scenario_data, chart_id)
            elif chart_type == 'monte_carlo':
                return self._create_monte_carlo_chart(scenario_data, chart_id)
            elif chart_type == 'roth_conversion':
                return self._create_roth_conversion_chart(scenario_data, chart_id)
            else:
                return self._create_generic_chart(scenario_data, chart_id)
                
        except Exception as e:
            logger.error(f"Chart export failed for {chart_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'chart_id': chart_id
            }
    
    def _create_asset_timeline_chart(self, data: Dict, chart_id: str) -> Dict[str, Any]:
        """Create asset timeline chart showing portfolio value over time"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract data from scenario results
        years = data.get('years', list(range(2024, 2050)))
        asset_values = data.get('asset_values', [1000000 + i * 50000 for i in range(len(years))])
        
        # Create the main asset line
        ax.plot(years, asset_values, linewidth=3, color='#3498db', label='Total Assets')
        
        # Add retirement marker
        retirement_year = data.get('retirement_year', 2034)
        if retirement_year in years:
            retirement_idx = years.index(retirement_year)
            ax.axvline(x=retirement_year, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.7)
            ax.annotate('Retirement', xy=(retirement_year, asset_values[retirement_idx]), 
                       xytext=(retirement_year + 2, asset_values[retirement_idx] + 100000),
                       arrowprops=dict(arrowstyle='->', color='#e74c3c'))
        
        # Formatting
        ax.set_title('Asset Growth Projection', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('Portfolio Value ($)', fontsize=14)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # Add grid and styling
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'asset_timeline_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'asset_timeline'
        }
    
    def _create_income_projection_chart(self, data: Dict, chart_id: str) -> Dict[str, Any]:
        """Create income vs expenses projection chart"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract data
        years = data.get('years', list(range(2024, 2050)))
        income_values = data.get('income_values', [85000 + i * 1000 for i in range(len(years))])
        expense_values = data.get('expense_values', [75000 + i * 1500 for i in range(len(years))])
        
        # Create the lines
        ax.plot(years, income_values, linewidth=3, color='#27ae60', label='Total Income', marker='o', markersize=4)
        ax.plot(years, expense_values, linewidth=3, color='#e74c3c', label='Total Expenses', marker='s', markersize=4)
        
        # Fill area between lines
        ax.fill_between(years, income_values, expense_values, 
                       where=[i >= e for i, e in zip(income_values, expense_values)],
                       interpolate=True, alpha=0.3, color='#27ae60', label='Surplus')
        
        # Formatting
        ax.set_title('Annual Income vs Expenses Projection', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('Annual Amount ($)', fontsize=14)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'income_projection_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'income_projection'
        }
    
    def _create_monte_carlo_chart(self, data: Dict, chart_id: str) -> Dict[str, Any]:
        """Create Monte Carlo simulation results chart"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract Monte Carlo data
        years = data.get('years', list(range(2024, 2050)))
        percentiles = data.get('percentiles', {
            '10': [900000 + i * 20000 for i in range(len(years))],
            '25': [1000000 + i * 25000 for i in range(len(years))],
            '50': [1100000 + i * 30000 for i in range(len(years))],
            '75': [1200000 + i * 35000 for i in range(len(years))],
            '90': [1300000 + i * 40000 for i in range(len(years))]
        })
        
        # Plot percentile bands
        ax.fill_between(years, percentiles['10'], percentiles['90'], alpha=0.2, color='#3498db', label='80% Confidence Band')
        ax.fill_between(years, percentiles['25'], percentiles['75'], alpha=0.3, color='#3498db', label='50% Confidence Band')
        
        # Plot median line
        ax.plot(years, percentiles['50'], linewidth=3, color='#2c3e50', label='Median Outcome')
        
        # Formatting
        ax.set_title('Monte Carlo Simulation Results', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('Portfolio Value ($)', fontsize=14)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'monte_carlo_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'monte_carlo'
        }
    
    def _create_tax_analysis_chart(self, data: Dict, chart_id: str) -> Dict[str, Any]:
        """Create tax analysis chart showing tax burden over time"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract tax data
        years = data.get('years', list(range(2024, 2050)))
        federal_tax = data.get('federal_tax', [15000 + i * 200 for i in range(len(years))])
        state_tax = data.get('state_tax', [4000 + i * 100 for i in range(len(years))])
        irmaa_charges = data.get('irmaa_charges', [0 if i < 10 else 1680 for i in range(len(years))])
        
        # Create stacked bar chart
        width = 0.6
        ax.bar(years, federal_tax, width, label='Federal Tax', color='#e74c3c')
        ax.bar(years, state_tax, width, bottom=federal_tax, label='State Tax', color='#f39c12')
        
        # Add IRMAA as separate bars
        bottom_values = [f + s for f, s in zip(federal_tax, state_tax)]
        ax.bar(years, irmaa_charges, width, bottom=bottom_values, label='IRMAA Surcharge', color='#9b59b6')
        
        # Formatting
        ax.set_title('Annual Tax Burden Analysis', fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('Tax Amount ($)', fontsize=14)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'tax_analysis_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'tax_analysis'
        }
    
    def _create_roth_conversion_chart(self, data: Dict, chart_id: str) -> Dict[str, Any]:
        """Create Roth conversion optimization chart"""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Top chart: Conversion amounts by year
        conversion_years = data.get('conversion_years', list(range(2024, 2034)))
        conversion_amounts = data.get('conversion_amounts', [50000, 60000, 45000, 55000, 70000, 40000, 35000, 30000, 25000, 20000])
        
        bars = ax1.bar(conversion_years, conversion_amounts, color='#9b59b6', alpha=0.7)
        ax1.set_title('Recommended Roth Conversion Amounts', fontsize=16, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Conversion Amount ($)', fontsize=12)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, amount in zip(bars, conversion_amounts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1000,
                    f'${amount/1000:.0f}K', ha='center', va='bottom', fontsize=10)
        
        # Bottom chart: Tax savings over time
        years_extended = list(range(2024, 2050))
        tax_savings = data.get('cumulative_tax_savings', [i * 5000 + i**2 * 100 for i in range(len(years_extended))])
        
        ax2.plot(years_extended, tax_savings, linewidth=3, color='#27ae60', marker='o', markersize=4)
        ax2.fill_between(years_extended, 0, tax_savings, alpha=0.3, color='#27ae60')
        ax2.set_title('Cumulative Tax Savings from Roth Conversions', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Cumulative Savings ($)', fontsize=12)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'roth_conversion_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'roth_conversion'
        }
    
    def _create_generic_chart(self, data: Dict, chart_id: str) -> Dict[str, Any]:
        """Create generic chart for unknown chart types"""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract generic x/y data
        x_data = data.get('x_data', list(range(10)))
        y_data = data.get('y_data', [i * 1000 + np.random.randint(-500, 500) for i in x_data])
        chart_title = data.get('title', 'Financial Data')
        x_label = data.get('x_label', 'Time')
        y_label = data.get('y_label', 'Value')
        
        # Create line chart
        ax.plot(x_data, y_data, linewidth=2, color='#3498db', marker='o', markersize=6)
        
        # Formatting
        ax.set_title(chart_title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'generic_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'generic'
        }
    
    def convert_chartjs_config(self, chartjs_config: Dict, chart_id: str) -> Dict[str, Any]:
        """
        Convert Chart.js configuration to matplotlib chart
        """
        try:
            chart_type = chartjs_config.get('type', 'line')
            chart_data = chartjs_config.get('data', {})
            chart_options = chartjs_config.get('options', {})
            
            if chart_type == 'line':
                return self._convert_line_chart(chart_data, chart_options, chart_id)
            elif chart_type == 'bar':
                return self._convert_bar_chart(chart_data, chart_options, chart_id)
            elif chart_type == 'pie':
                return self._convert_pie_chart(chart_data, chart_options, chart_id)
            else:
                # Fallback to generic chart
                return self._create_generic_chart({
                    'title': chart_options.get('plugins', {}).get('title', {}).get('text', 'Chart'),
                    'x_data': list(range(len(chart_data.get('labels', [])))),
                    'y_data': chart_data.get('datasets', [{}])[0].get('data', [])
                }, chart_id)
                
        except Exception as e:
            logger.error(f"Chart.js conversion failed for {chart_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'chart_id': chart_id
            }
    
    def _convert_line_chart(self, data: Dict, options: Dict, chart_id: str) -> Dict[str, Any]:
        """Convert Chart.js line chart to matplotlib"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        colors_list = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6']
        
        for i, dataset in enumerate(datasets):
            label = dataset.get('label', f'Dataset {i+1}')
            values = dataset.get('data', [])
            color = colors_list[i % len(colors_list)]
            
            ax.plot(labels, values, linewidth=2, color=color, label=label, marker='o', markersize=4)
        
        # Get title from options
        title_config = options.get('plugins', {}).get('title', {})
        title = title_config.get('text', 'Line Chart') if title_config.get('display') else 'Line Chart'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        if len(datasets) > 1:
            ax.legend()
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'line_chart_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'line'
        }
    
    def _convert_bar_chart(self, data: Dict, options: Dict, chart_id: str) -> Dict[str, Any]:
        """Convert Chart.js bar chart to matplotlib"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        if not datasets:
            raise ValueError("No datasets found in chart data")
        
        colors_list = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6']
        bar_width = 0.8 / len(datasets) if len(datasets) > 1 else 0.8
        
        for i, dataset in enumerate(datasets):
            dataset_label = dataset.get('label', f'Dataset {i+1}')
            values = dataset.get('data', [])
            color = colors_list[i % len(colors_list)]
            
            # Calculate x positions for grouped bars
            x_positions = [j + (i - len(datasets)/2 + 0.5) * bar_width for j in range(len(labels))]
            
            ax.bar(x_positions, values, bar_width, label=dataset_label, color=color, alpha=0.8)
        
        # Set x-axis labels
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)
        
        # Get title from options
        title_config = options.get('plugins', {}).get('title', {})
        title = title_config.get('text', 'Bar Chart') if title_config.get('display') else 'Bar Chart'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        if len(datasets) > 1:
            ax.legend()
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'bar_chart_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'bar'
        }
    
    def _convert_pie_chart(self, data: Dict, options: Dict, chart_id: str) -> Dict[str, Any]:
        """Convert Chart.js pie chart to matplotlib"""
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        if not datasets:
            raise ValueError("No datasets found in pie chart data")
        
        values = datasets[0].get('data', [])
        colors_list = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            colors=colors_list[:len(values)],
            autopct='%1.1f%%',
            startangle=90
        )
        
        # Enhance text formatting
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Get title from options
        title_config = options.get('plugins', {}).get('title', {})
        title = title_config.get('text', 'Pie Chart') if title_config.get('display') else 'Pie Chart'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Save chart
        chart_path = os.path.join(self.chart_storage, f'pie_chart_{chart_id}.png')
        plt.savefig(chart_path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return {
            'success': True,
            'image_path': chart_path,
            'chart_id': chart_id,
            'chart_type': 'pie'
        }
    
    def export_multiple_charts(self, charts_config: List[Dict], report_id: str) -> Dict[str, Any]:
        """
        Export multiple charts for a single report
        """
        try:
            results = {
                'success': True,
                'charts': [],
                'failed_charts': [],
                'report_id': report_id
            }
            
            for i, chart_config in enumerate(charts_config):
                chart_id = f"{report_id}_chart_{i}"
                
                if 'chartjs_config' in chart_config:
                    # Convert Chart.js config
                    result = self.convert_chartjs_config(chart_config['chartjs_config'], chart_id)
                else:
                    # Use scenario data
                    chart_type = chart_config.get('type', 'generic')
                    scenario_data = chart_config.get('data', {})
                    result = self.export_scenario_chart(scenario_data, chart_type, chart_id)
                
                if result['success']:
                    results['charts'].append(result)
                else:
                    results['failed_charts'].append({
                        'chart_id': chart_id,
                        'error': result['error']
                    })
            
            # Mark as failed if no charts succeeded
            if not results['charts'] and results['failed_charts']:
                results['success'] = False
                results['error'] = f"All {len(results['failed_charts'])} charts failed to export"
            
            logger.info(f"Chart export completed for report {report_id}: "
                       f"{len(results['charts'])} successful, {len(results['failed_charts'])} failed")
            
            return results
            
        except Exception as e:
            logger.error(f"Multiple chart export failed for report {report_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'report_id': report_id
            }
    
    def cleanup_chart_files(self, chart_ids: List[str]) -> Dict[str, Any]:
        """
        Clean up temporary chart files after report generation
        """
        try:
            deleted_count = 0
            errors = []
            
            for chart_id in chart_ids:
                # Find all chart files with this ID
                for filename in os.listdir(self.chart_storage):
                    if chart_id in filename and filename.endswith('.png'):
                        file_path = os.path.join(self.chart_storage, filename)
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except OSError as e:
                            errors.append(f"Failed to delete {filename}: {str(e)}")
            
            return {
                'success': len(errors) == 0,
                'deleted_count': deleted_count,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Chart cleanup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }