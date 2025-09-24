"""
PDF Generation Module using Pdfcrowd
Generates PDF reports for retirement scenarios by capturing multiple tab views
"""

import os
import logging
import tempfile
from typing import List, Dict, Any
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json

logger = logging.getLogger(__name__)

# Pdfcrowd configuration
PDFCROWD_USERNAME = os.environ.get('PDFCROWD_USERNAME', '')
PDFCROWD_API_KEY = os.environ.get('PDFCROWD_API_KEY', '')
PDFCROWD_ENABLED = bool(PDFCROWD_USERNAME and PDFCROWD_API_KEY)

if PDFCROWD_ENABLED:
    try:
        import pdfcrowd
    except ImportError:
        logger.error("pdfcrowd library not installed. Please run: pip install pdfcrowd")
        PDFCROWD_ENABLED = False


class ScenarioPDFGenerator:
    """
    Generates PDF reports for retirement scenarios using Pdfcrowd API
    """
    
    def __init__(self):
        if not PDFCROWD_ENABLED:
            raise ValueError("Pdfcrowd is not configured. Please set PDFCROWD_USERNAME and PDFCROWD_API_KEY environment variables.")
        
        self.client = pdfcrowd.HtmlToPdfClient(PDFCROWD_USERNAME, PDFCROWD_API_KEY)
        self._configure_client()
    
    def _configure_client(self):
        """Configure Pdfcrowd client with optimal settings"""
        # Page setup
        self.client.setPageSize("Letter")
        self.client.setOrientation("portrait")
        self.client.setMarginTop("0.75in")
        self.client.setMarginBottom("0.75in")
        self.client.setMarginLeft("0.75in")
        self.client.setMarginRight("0.75in")
        
        # Quality settings - using correct pdfcrowd API methods
        # Don't set delay here - we'll set it per request
        # self.client.setLoadImages(True)  # Not available in this API version
        # self.client.setEnableJavascript(True)  # JavaScript is enabled by default
        self.client.setNoBackground(False)
        
        # Header and footer
        self.client.setHeaderHeight("0.5in")
        self.client.setFooterHeight("0.5in")
        
        # Add custom HTTP header to skip ngrok warning page
        self.client.setCustomHttpHeader("ngrok-skip-browser-warning: true")
        
    def generate_scenario_pdf_from_url(self, client_id: int, scenario_id: int, tabs: List[str], auth_token: str = None) -> bytes:
        """
        Generate PDF by capturing the actual page
        
        Args:
            client_id: Client ID
            scenario_id: Scenario ID
            tabs: List of tab names to include in PDF
            auth_token: Authentication token for accessing the pages
            
        Returns:
            PDF content as bytes
        """
        try:
            # Get the frontend URL from environment or use default
            import os
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            
            # Build the actual URL to the page with PDF mode parameter
            # This will tell the frontend to hide navigation elements
            # Also pass the token as a URL parameter for the frontend to use
            url = f"{frontend_url}/clients/{client_id}/scenarios/detail/{scenario_id}?pdf=true"
            if auth_token:
                url += f"&pdfToken={auth_token}"
            
            logger.info(f"Converting URL to PDF: {url}")
            
            # Also set authentication cookie as a backup
            if auth_token:
                # Set the token cookie that the frontend will check
                cookie_string = f"token={auth_token}"
                self.client.setCookies(cookie_string)
                logger.info(f"Set authentication cookie for PDF generation")
            
            # Wait for specific elements that indicate data has loaded
            # Let's try simpler selectors first
            # Just wait for any table with data
            wait_selector = "table"  # Just wait for ANY table to appear
            self.client.setWaitForElement(wait_selector)
            logger.info(f"Waiting for element: {wait_selector}")
            
            # Also set JavaScript delay as a fallback (max is 2000ms)
            # This runs AFTER the element is found
            self.client.setJavascriptDelay(2000)  # 2 seconds max allowed
            
            # Set a longer max loading time (in seconds, range 10-30)
            # This is the overall timeout for the page load
            self.client.setMaxLoadingTime(30)
            
            # Run JavaScript after load to check what's on the page
            self.client.setOnLoadJavascript("""
                // Debug: Check if we have localStorage token
                var token = localStorage.getItem('token');
                console.log('Token in localStorage:', token ? 'Present' : 'Missing');
                
                // Debug: Check for Vue app
                var vueApp = document.getElementById('app');
                console.log('Vue app element:', vueApp ? 'Found' : 'Not found');
                
                // Debug: Count tables on page
                var tables = document.querySelectorAll('table');
                console.log('Number of tables found:', tables.length);
                
                // Debug: Check for any error messages
                var errors = document.querySelectorAll('.error, .alert-danger');
                console.log('Error messages found:', errors.length);
                
                // Try to wait for Vue to mount
                setTimeout(function() {
                    // Check again after delay
                    var tablesAfter = document.querySelectorAll('table');
                    console.log('Tables after delay:', tablesAfter.length);
                    
                    // Add a visible marker to the page for debugging
                    var marker = document.createElement('div');
                    marker.innerHTML = 'PDF Generation Debug - Tables: ' + tablesAfter.length;
                    marker.style.cssText = 'position:fixed;top:0;left:0;background:red;color:white;padding:10px;z-index:9999';
                    document.body.appendChild(marker);
                    
                    // Scroll to trigger lazy loading
                    window.scrollTo(0, document.body.scrollHeight);
                    window.scrollTo(0, 0);
                }, 1500);
            """)
            
            # Convert the actual page to PDF
            pdf_content = self.client.convertUrl(url)
            
            return pdf_content
            
        except pdfcrowd.Error as e:
            logger.error(f"Pdfcrowd error: {str(e)}")
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def generate_scenario_pdf(self, client_id: int, scenario_id: int, tabs: List[str], auth_token: str = None) -> bytes:
        """
        Generate PDF with actual data from backend (server-side rendering)
        
        Args:
            client_id: Client ID
            scenario_id: Scenario ID
            tabs: List of tab names to include in PDF
            auth_token: Authentication token (not needed for server-side)
            
        Returns:
            PDF content as bytes
        """
        try:
            # Get the scenario and client data
            from .models import Scenario, Client
            scenario = Scenario.objects.get(id=scenario_id)
            client = Client.objects.get(id=client_id)
            
            # Calculate scenario results using the processor directly
            from .scenario_processor import ScenarioProcessor
            processor = ScenarioProcessor(scenario.id)  # Pass the ID, not the object
            scenario_results = processor.calculate()
            
            # Generate HTML with actual data
            html_content = self._generate_html_with_charts(scenario, client, scenario_results, tabs)
            
            logger.info(f"Converting HTML to PDF for scenario {scenario_id}")
            
            # Convert HTML to PDF
            pdf_content = self.client.convertString(html_content)
            
            return pdf_content
            
        except pdfcrowd.Error as e:
            logger.error(f"Pdfcrowd error: {str(e)}")
            raise Exception(f"Failed to generate PDF: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _generate_html_with_charts(self, scenario, client, results, tabs):
        """Generate HTML with embedded Chart.js charts matching the frontend"""
        import json
        import base64
        import os
        
        html = []
        
        # Get logo - either advisor's custom logo or default company logo
        logo_base64 = None
        logo_path = None
        
        # Check if the client's advisor has a custom logo
        if hasattr(client, 'advisor') and client.advisor and hasattr(client.advisor, 'logo') and client.advisor.logo:
            logo_path = client.advisor.logo.path
        # If no custom logo, use default company logo
        elif os.path.exists('/app/frontend/public/assets/img/logo.png'):
            logo_path = '/app/frontend/public/assets/img/logo.png'
        elif os.path.exists('/tmp/logo.png'):  # Fallback for existing setup
            logo_path = '/tmp/logo.png'
        elif os.path.exists('frontend/public/assets/img/logo.png'):
            logo_path = 'frontend/public/assets/img/logo.png'
        
        # Convert logo to base64 for embedding in HTML
        if logo_path and os.path.exists(logo_path):
            try:
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                    logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                    logger.info(f"Logo loaded from: {logo_path}")
            except Exception as e:
                logger.warning(f"Could not load logo from {logo_path}: {e}")
        
        # Prepare data matching the frontend structure
        # Convert Decimal to float for JSON serialization
        years = [str(r['year']) for r in results]
        gross_income = [float(r.get('gross_income', 0)) for r in results]
        federal_tax = [float(r.get('federal_tax', 0)) for r in results]
        total_medicare = [float(r.get('total_medicare', 0)) for r in results]
        net_income_values = [
            float(r.get('gross_income', 0)) - float(r.get('federal_tax', 0)) - float(r.get('total_medicare', 0))
            for r in results
        ]
        agi = [float(r.get('agi', 0)) for r in results]
        magi = [float(r.get('magi', 0)) for r in results]
        
        html.append('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Retirement Scenario Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 20px;
            color: #333;
        }
        h1 { 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        h2 { 
            color: #34495e; 
            margin-top: 40px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        .page-break { page-break-after: always; }
        .summary-box { 
            background: #f8f9fa;
            color: #333;
            padding: 30px;
            margin: 20px 0;
            border-radius: 10px;
            border: 2px solid #dee2e6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .title-page {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 90vh;
            text-align: center;
        }
        .title-page h1 {
            font-size: 42px;
            color: #2c3e50;
            margin-bottom: 40px;
            border: none;
        }
        .title-page h2 {
            color: #495057;
            border: none;
            font-size: 28px;
            margin-bottom: 15px;
        }
        .metrics-row {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin: 30px 0;
            gap: 15px;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            text-align: center;
            flex: 1;
            min-width: 140px;
        }
        .metric-value { 
            font-size: 32px; 
            font-weight: bold; 
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .metric-label { 
            color: #7f8c8d; 
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        th { 
            background: #f8f9fa;
            color: #495057;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }
        td { 
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .title-page-logo {
            max-width: 300px;
            max-height: 120px;
            margin-bottom: 40px;
        }
    </style>
</head>
<body>
''')
        
        # Don't add a global logo header - we'll add it per page instead
        
        # Title Page - wrap in container to isolate it
        html.append('<div style="position: relative; min-height: 100vh; page-break-after: always;">')
        html.append('<div class="title-page">')
        
        # Add large logo to title page only
        if logo_base64:
            html.append(f'<img src="data:image/png;base64,{logo_base64}" alt="Company Logo" class="title-page-logo" />')
        
        html.append('<h1>Retirement Scenario Report</h1>')
        html.append('<div class="summary-box" style="width: 80%; max-width: 600px;">')
        html.append(f'<h2>Client: {client.first_name} {client.last_name}</h2>')
        html.append(f'<p style="font-size: 20px; margin: 15px 0; color: #6c757d;"><strong>Scenario:</strong> {scenario.name}</p>')
        html.append(f'<p style="font-size: 16px; color: #6c757d;"><strong>Generated:</strong> {scenario.created_at.strftime("%B %d, %Y")}</p>')
        html.append('</div>')
        html.append('</div>')
        html.append('</div>')  # Close the title page container
        
        # Page break is handled by the container above, no need for explicit page break
        
        # Financial Overview - starts on page 2
        if 'overview' in tabs:
            # Start a new page container (page break already handled by title page)
            html.append('<div style="min-height: 100vh;">')
            
            # Add small logo to all pages except first
            if logo_base64:
                html.append(f'''
                    <div style="float: right; margin: 5px 10px 10px 10px;">
                        <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="max-height: 30px; width: auto;" />
                    </div>
                ''')
            
            # Add the h2 after the floated logo
            html.append('<h2 style="margin-top: 0; padding-top: 5px; clear: left;">Financial Overview</h2>')
            
            # Key metrics matching frontend
            html.append('<div class="metrics-row">')
            html.append(f'<div class="metric-card"><div class="metric-value">{scenario.retirement_age}</div><div class="metric-label">Retirement Age</div></div>')
            html.append(f'<div class="metric-card"><div class="metric-value">{scenario.mortality_age}</div><div class="metric-label">Life Expectancy</div></div>')
            if results:
                # Calculate totals matching frontend (convert Decimal to float)
                lifetime_gross_income = sum(float(r.get('gross_income', 0)) for r in results)
                lifetime_federal_tax = sum(float(r.get('federal_tax', 0)) for r in results)
                lifetime_medicare = sum(float(r.get('total_medicare', 0)) for r in results)
                lifetime_net = lifetime_gross_income - lifetime_federal_tax - lifetime_medicare
                
                html.append(f'<div class="metric-card"><div class="metric-value">${lifetime_gross_income:,.0f}</div><div class="metric-label">Total Gross Income</div></div>')
                html.append(f'<div class="metric-card"><div class="metric-value">${lifetime_federal_tax:,.0f}</div><div class="metric-label">Total Federal Tax</div></div>')
                html.append(f'<div class="metric-card"><div class="metric-value">${lifetime_medicare:,.0f}</div><div class="metric-label">Total Medicare</div></div>')
                html.append(f'<div class="metric-card"><div class="metric-value">${lifetime_net:,.0f}</div><div class="metric-label">Net Income</div></div>')
            html.append('</div>')
            
            # Financial Overview Chart - matching frontend
            html.append('<div class="chart-container">')
            html.append('<canvas id="financialChart"></canvas>')
            html.append('</div>')
            
            html.append(f'''
<script>
const ctx1 = document.getElementById('financialChart').getContext('2d');
new Chart(ctx1, {{
    type: 'bar',
    data: {{
        labels: {json.dumps(years[:30])},
        datasets: [{{
            type: 'line',
            label: 'Gross Income',
            data: {json.dumps(gross_income[:30])},
            borderColor: '#4285f4',
            backgroundColor: 'transparent',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: '#4285f4',
            order: 1,
            fill: false
        }}, {{
            type: 'line',
            label: 'Net Income',
            data: {json.dumps(net_income_values[:30])},
            borderColor: '#34a853',
            backgroundColor: 'transparent',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: '#34a853',
            order: 1,
            fill: false
        }}, {{
            type: 'bar',
            label: 'Federal Tax',
            data: {json.dumps(federal_tax[:30])},
            backgroundColor: '#ea4335',
            stack: 'Stack 0',
            order: 2
        }}, {{
            type: 'bar',
            label: 'Medicare',
            data: {json.dumps(total_medicare[:30])},
            backgroundColor: '#fbbc05',
            stack: 'Stack 0',
            order: 2
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            title: {{
                display: true,
                text: 'Financial Overview',
                font: {{ size: 16 }}
            }},
            legend: {{
                display: true,
                position: 'bottom'
            }}
        }},
        scales: {{
            x: {{
                title: {{
                    display: true,
                    text: 'Year'
                }}
            }},
            y: {{
                beginAtZero: true,
                title: {{
                    display: true,
                    text: 'Amount ($)'
                }},
                ticks: {{
                    callback: function(value) {{
                        return '$' + value.toLocaleString();
                    }}
                }}
            }}
        }}
    }}
}});
</script>
''')
            
            # Close the page container
            html.append('</div>')
        
        # Add Financial Overview Table matching the frontend
        if 'financial' in tabs and results:
            html.append('<div class="page-break"></div>')
            
            # Start a new page container
            html.append('<div style="min-height: 100vh;">')
            
            # Add small logo to all pages except first
            if logo_base64:
                html.append(f'''
                    <div style="float: right; margin: 5px 10px 10px 10px;">
                        <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="max-height: 30px; width: auto;" />
                    </div>
                ''')
            
            # Add content
            html.append('<h2 style="padding-top: 5px; clear: left;">Financial Overview Table</h2>')
            
            # Calculate totals (convert Decimal to float)
            total_federal_tax = sum(float(r.get('federal_tax', 0)) for r in results)
            total_medicare_sum = sum(float(r.get('total_medicare', 0)) for r in results)
            
            # Financial Overview Table matching frontend
            html.append('<table>')
            html.append('<thead><tr>')
            html.append('<th>Year</th>')
            html.append('<th>Primary Age</th>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append('<th>Spouse Age</th>')
            html.append('<th>Gross Income</th>')
            html.append('<th>AGI</th>')
            html.append('<th>MAGI</th>')
            html.append('<th>Tax Bracket</th>')
            html.append('<th>Federal Tax</th>')
            html.append('<th>Total Medicare</th>')
            html.append('<th>Remaining Income</th>')
            html.append('</tr></thead>')
            html.append('<tbody>')
            
            for year_data in results[:20]:  # Show first 20 years
                html.append('<tr>')
                html.append(f'<td>{year_data.get("year", "")}</td>')
                html.append(f'<td>{year_data.get("primary_age", year_data.get("age", ""))}</td>')
                if hasattr(client, 'spouse') and client.spouse:
                    html.append(f'<td>{year_data.get("spouse_age", "")}</td>')
                
                gross = year_data.get("gross_income", 0)
                fed_tax = year_data.get("federal_tax", 0)
                medicare = year_data.get("total_medicare", 0)
                remaining = gross - fed_tax - medicare
                
                html.append(f'<td>${gross:,.0f}</td>')
                html.append(f'<td>${year_data.get("agi", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("magi", 0):,.0f}</td>')
                html.append(f'<td>{year_data.get("tax_bracket", "")}</td>')
                html.append(f'<td>${fed_tax:,.0f}</td>')
                html.append(f'<td>${medicare:,.0f}</td>')
                html.append(f'<td>${remaining:,.0f}</td>')
                html.append('</tr>')
            
            # Add totals row
            html.append('<tr style="font-weight: bold;">')
            html.append('<td>Total</td>')
            html.append('<td></td>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append('<td></td>')
            html.append('<td></td>')
            html.append('<td></td>')
            html.append('<td></td>')
            html.append('<td></td>')
            html.append(f'<td>${total_federal_tax:,.0f}</td>')
            html.append(f'<td>${total_medicare_sum:,.0f}</td>')
            html.append('<td></td>')
            html.append('</tr>')
            html.append('</tbody></table>')
            
            # Close the page container
            html.append('</div>')
        
        # Social Security Overview Section
        if 'socialSecurity' in tabs and results:
            html.append('<div class="page-break"></div>')
            
            # Start a new page container
            html.append('<div style="min-height: 100vh;">')
            
            # Add small logo to all pages except first
            if logo_base64:
                html.append(f'''
                    <div style="float: right; margin: 5px 10px 10px 10px;">
                        <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="max-height: 30px; width: auto;" />
                    </div>
                ''')
            
            # Add content
            html.append('<h2 style="margin-top: 0; padding-top: 5px; clear: left;">Social Security Overview</h2>')
            
            # Prepare SS data for chart - filter for rows with SS income
            ss_filtered_results = [r for r in results if float(r.get('ss_income_primary_gross', 0)) > 0 or float(r.get('ss_income_spouse_gross', 0)) > 0][:30]
            ss_years = [str(r['year']) for r in ss_filtered_results]
            ss_primary = [float(r.get('ss_income_primary_gross', 0)) for r in ss_filtered_results]
            ss_spouse = [float(r.get('ss_income_spouse_gross', 0)) for r in ss_filtered_results]
            medicare_expense = [float(r.get('total_medicare', 0)) for r in ss_filtered_results]
            
            # Calculate remaining SSI correctly
            ss_remaining = []
            for r in ss_filtered_results:
                primary = float(r.get('ss_income_primary_gross', 0))
                spouse = float(r.get('ss_income_spouse_gross', 0))
                medicare = float(r.get('total_medicare', 0))
                taxed = float(r.get('ssi_taxed', 0))
                remaining = primary + spouse - medicare - taxed
                ss_remaining.append(remaining)
            
            # Social Security Chart - matching frontend
            html.append('<div class="chart-container">')
            html.append('<canvas id="ssChart"></canvas>')
            html.append('</div>')
            
            html.append(f'''
<script>
const ctxSS = document.getElementById('ssChart').getContext('2d');
new Chart(ctxSS, {{
    type: 'bar',  // Base type is bar for mixed chart
    data: {{
        labels: {json.dumps(ss_years)},
        datasets: [{{
            type: 'line',
            label: 'Primary SSI Benefit',
            data: {json.dumps(ss_primary)},
            borderColor: '#377dff',
            backgroundColor: 'transparent',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: '#377dff',
            fill: false,
            order: 1
        }}, {{
            type: 'line',
            label: 'Spouse SSI Benefit',
            data: {json.dumps(ss_spouse)},
            borderColor: '#9b59b6',
            backgroundColor: 'transparent',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: '#9b59b6',
            fill: false,
            order: 1
        }}, {{
            type: 'line',
            label: 'Remaining SSI Benefit',
            data: {json.dumps(ss_remaining)},
            borderColor: '#00c9db',
            backgroundColor: 'transparent',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: '#00c9db',
            fill: false,
            order: 1
        }}, {{
            type: 'bar',
            label: 'Medicare Expense',
            data: {json.dumps(medicare_expense)},
            backgroundColor: '#ffc107',
            stack: 'Stack 0',
            order: 2
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            title: {{
                display: true,
                text: 'Social Security Benefits Overview'
            }},
            legend: {{
                display: true,
                position: 'bottom'
            }},
            tooltip: {{
                mode: 'index',
                intersect: false
            }}
        }},
        scales: {{
            x: {{
                title: {{
                    display: true,
                    text: 'Year'
                }}
            }},
            y: {{
                beginAtZero: true,
                title: {{
                    display: true,
                    text: 'Amount ($)'
                }},
                ticks: {{
                    callback: function(value) {{
                        return '$' + value.toLocaleString();
                    }}
                }}
            }}
        }}
    }}
}});
</script>
''')
            
            # Social Security Table
            html.append('<h3 style="margin-top: 30px;">Social Security Details</h3>')
            html.append('<table>')
            html.append('<thead><tr>')
            html.append('<th>Year</th>')
            html.append('<th>Primary Age</th>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append('<th>Spouse Age</th>')
            html.append('<th>Primary SSI</th>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append('<th>Spouse SSI</th>')
            html.append('<th>Total Medicare</th>')
            html.append('<th>SSI Taxed</th>')
            html.append('<th>Remaining SSI</th>')
            html.append('</tr></thead>')
            html.append('<tbody>')
            
            for year_data in results[:20]:
                if year_data.get('ss_income_primary_gross', 0) > 0 or year_data.get('ss_income_spouse_gross', 0) > 0:
                    html.append('<tr>')
                    html.append(f'<td>{year_data.get("year", "")}</td>')
                    html.append(f'<td>{year_data.get("primary_age", year_data.get("age", ""))}</td>')
                    if hasattr(client, 'spouse') and client.spouse:
                        html.append(f'<td>{year_data.get("spouse_age", "")}</td>')
                    
                    ss_primary = float(year_data.get("ss_income_primary_gross", 0))
                    ss_spouse = float(year_data.get("ss_income_spouse_gross", 0))
                    medicare = float(year_data.get("total_medicare", 0))
                    ssi_taxed = float(year_data.get("ssi_taxed", 0))
                    remaining_ssi = ss_primary + ss_spouse - medicare - ssi_taxed
                    
                    html.append(f'<td>${ss_primary:,.2f}</td>')
                    if hasattr(client, 'spouse') and client.spouse:
                        html.append(f'<td>${ss_spouse:,.2f}</td>')
                    html.append(f'<td>${medicare:,.2f}</td>')
                    html.append(f'<td>${ssi_taxed:,.2f}</td>')
                    html.append(f'<td>${remaining_ssi:,.2f}</td>')
                    html.append('</tr>')
            
            html.append('</tbody></table>')
            
            # Close the page container
            html.append('</div>')
        
        # Medicare Overview Section
        if 'medicare' in tabs and results:
            html.append('<div class="page-break"></div>')
            
            # Start a new page container
            html.append('<div style="min-height: 100vh;">')
            
            # Add small logo to all pages except first
            if logo_base64:
                html.append(f'''
                    <div style="float: right; margin: 5px 10px 10px 10px;">
                        <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="max-height: 30px; width: auto;" />
                    </div>
                ''')
            
            # Add content
            html.append('<h2 style="margin-top: 0; padding-top: 5px; clear: left;">Medicare Overview</h2>')
            
            # Calculate Medicare totals
            total_part_b = sum(float(r.get('part_b', 0)) for r in results)
            total_part_d = sum(float(r.get('part_d', 0)) for r in results)
            total_irmaa = sum(float(r.get('irmaa_surcharge', 0)) for r in results)
            total_medicare_cost = sum(float(r.get('total_medicare', 0)) for r in results)
            
            # Medicare metrics
            html.append('<div class="metrics-row">')
            html.append(f'<div class="metric-card"><div class="metric-value">${total_medicare_cost:,.0f}</div><div class="metric-label">Total Medicare Cost</div></div>')
            html.append(f'<div class="metric-card"><div class="metric-value">${total_part_b:,.0f}</div><div class="metric-label">Total Part B</div></div>')
            html.append(f'<div class="metric-card"><div class="metric-value">${total_part_d:,.0f}</div><div class="metric-label">Total Part D</div></div>')
            html.append(f'<div class="metric-card"><div class="metric-value">${total_irmaa:,.0f}</div><div class="metric-label">Total IRMAA</div></div>')
            html.append('</div>')
            
            # Prepare Medicare data for chart
            medicare_years = [str(r['year']) for r in results if float(r.get('total_medicare', 0)) > 0][:30]
            part_b_data = [float(r.get('part_b', 0)) for r in results if float(r.get('total_medicare', 0)) > 0][:30]
            part_d_data = [float(r.get('part_d', 0)) for r in results if float(r.get('total_medicare', 0)) > 0][:30]
            irmaa_data = [float(r.get('irmaa_surcharge', 0)) for r in results if float(r.get('total_medicare', 0)) > 0][:30]
            
            # Medicare Chart
            html.append('<div class="chart-container">')
            html.append('<canvas id="medicareChart"></canvas>')
            html.append('</div>')
            
            html.append(f'''
<script>
const ctxMedicare = document.getElementById('medicareChart').getContext('2d');
new Chart(ctxMedicare, {{
    type: 'bar',
    data: {{
        labels: {json.dumps(medicare_years)},
        datasets: [{{
            label: 'Part B',
            data: {json.dumps(part_b_data)},
            backgroundColor: '#4285f4',
            stack: 'Stack 0'
        }}, {{
            label: 'Part D',
            data: {json.dumps(part_d_data)},
            backgroundColor: '#0f9d58',
            stack: 'Stack 0'
        }}, {{
            label: 'IRMAA Surcharge',
            data: {json.dumps(irmaa_data)},
            backgroundColor: '#ea4335',
            stack: 'Stack 0'
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            title: {{
                display: true,
                text: 'Medicare Costs Breakdown'
            }},
            legend: {{
                display: true,
                position: 'bottom'
            }}
        }},
        scales: {{
            x: {{
                stacked: true
            }},
            y: {{
                stacked: true,
                beginAtZero: true,
                ticks: {{
                    callback: function(value) {{
                        return '$' + value.toLocaleString();
                    }}
                }}
            }}
        }}
    }}
}});
</script>
''')
            
            # Medicare Table
            html.append('<h3 style="margin-top: 30px;">Medicare Costs Details</h3>')
            html.append('<table>')
            html.append('<thead><tr>')
            html.append('<th>Year</th>')
            html.append('<th>Primary Age</th>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append('<th>Spouse Age</th>')
            html.append('<th>Part B</th>')
            html.append('<th>Part D</th>')
            html.append('<th>IRMAA Surcharge</th>')
            html.append('<th>Total Medicare</th>')
            html.append('</tr></thead>')
            html.append('<tbody>')
            
            for year_data in results[:20]:
                if float(year_data.get('total_medicare', 0)) > 0:
                    html.append('<tr>')
                    html.append(f'<td>{year_data.get("year", "")}</td>')
                    html.append(f'<td>{year_data.get("primary_age", year_data.get("age", ""))}</td>')
                    if hasattr(client, 'spouse') and client.spouse:
                        html.append(f'<td>{year_data.get("spouse_age", "")}</td>')
                    
                    part_b = float(year_data.get("part_b", 0))
                    part_d = float(year_data.get("part_d", 0))
                    irmaa = float(year_data.get("irmaa_surcharge", 0))
                    total_med = float(year_data.get("total_medicare", 0))
                    
                    html.append(f'<td>${part_b:,.2f}</td>')
                    html.append(f'<td>${part_d:,.2f}</td>')
                    html.append(f'<td>${irmaa:,.2f}</td>')
                    html.append(f'<td>${total_med:,.2f}</td>')
                    html.append('</tr>')
            
            # Add totals row
            html.append('<tr style="font-weight: bold;">')
            html.append('<td>Total</td>')
            html.append('<td></td>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append('<td></td>')
            html.append(f'<td>${total_part_b:,.2f}</td>')
            html.append(f'<td>${total_part_d:,.2f}</td>')
            html.append(f'<td>${total_irmaa:,.2f}</td>')
            html.append(f'<td>${total_medicare_cost:,.2f}</td>')
            html.append('</tr>')
            
            html.append('</tbody></table>')
            
            # Close the Medicare page container
            html.append('</div>')
        
        html.append('</body></html>')
        return ''.join(html)
    
    def _generate_report_html(self, scenario, client, results, tabs):
        """Generate HTML report with scenario data"""
        html = []
        
        # HTML header with styling
        html.append('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Retirement Scenario Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .page-break { page-break-after: always; }
        .summary-box { background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .metric { display: inline-block; margin-right: 30px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { color: #6c757d; font-size: 14px; }
    </style>
</head>
<body>
''')
        
        # Report header
        html.append(f'<h1>Retirement Scenario Report</h1>')
        html.append(f'<div class="summary-box">')
        html.append(f'<p><strong>Client:</strong> {client.first_name} {client.last_name}</p>')
        html.append(f'<p><strong>Scenario:</strong> {scenario.name}</p>')
        html.append(f'<p><strong>Generated:</strong> {scenario.created_at.strftime("%B %d, %Y")}</p>')
        html.append(f'</div>')
        
        # Overview section
        if 'overview' in tabs:
            html.append('<h2>Scenario Overview</h2>')
            html.append('<div class="summary-box">')
            html.append(f'<div class="metric"><div class="metric-value">{scenario.retirement_age}</div><div class="metric-label">Retirement Age</div></div>')
            html.append(f'<div class="metric"><div class="metric-value">{scenario.mortality_age}</div><div class="metric-label">Life Expectancy</div></div>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append(f'<div class="metric"><div class="metric-value">{scenario.spouse_retirement_age}</div><div class="metric-label">Spouse Retirement Age</div></div>')
            html.append('</div>')
            
            if results:
                total_income = sum(r.get('total_income', 0) for r in results)
                total_expenses = sum(r.get('total_expenses', 0) for r in results)
                total_taxes = sum(r.get('federal_tax', 0) + r.get('state_tax', 0) for r in results)
                
                html.append('<div class="summary-box">')
                html.append(f'<div class="metric"><div class="metric-value">${total_income:,.0f}</div><div class="metric-label">Lifetime Income</div></div>')
                html.append(f'<div class="metric"><div class="metric-value">${total_expenses:,.0f}</div><div class="metric-label">Lifetime Expenses</div></div>')
                html.append(f'<div class="metric"><div class="metric-value">${total_taxes:,.0f}</div><div class="metric-label">Lifetime Taxes</div></div>')
                html.append('</div>')
        
        # Financial Overview section
        if 'financial' in tabs and results:
            html.append('<div class="page-break"></div>')
            html.append('<h2>Financial Overview</h2>')
            html.append('<table>')
            html.append('<thead><tr><th>Year</th><th>Age</th><th>Total Income</th><th>Total Expenses</th><th>Federal Tax</th><th>State Tax</th><th>Net Income</th></tr></thead>')
            html.append('<tbody>')
            
            for year_data in results[:15]:  # Show first 15 years
                html.append('<tr>')
                html.append(f'<td>{year_data.get("year", "")}</td>')
                html.append(f'<td>{year_data.get("age", "")}</td>')
                html.append(f'<td>${year_data.get("total_income", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("total_expenses", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("federal_tax", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("state_tax", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("net_income", 0):,.0f}</td>')
                html.append('</tr>')
            
            html.append('</tbody></table>')
            if len(results) > 15:
                html.append(f'<p><em>Showing first 15 years of {len(results)} total years</em></p>')
        
        # Social Security section
        if 'socialSecurity' in tabs:
            html.append('<div class="page-break"></div>')
            html.append('<h2>Social Security Analysis</h2>')
            html.append('<div class="summary-box">')
            html.append(f'<div class="metric"><div class="metric-value">{scenario.primary_ss_claiming_age or "Not Set"}</div><div class="metric-label">Primary Claiming Age</div></div>')
            if hasattr(client, 'spouse') and client.spouse:
                html.append(f'<div class="metric"><div class="metric-value">{scenario.spouse_ss_claiming_age or "Not Set"}</div><div class="metric-label">Spouse Claiming Age</div></div>')
            html.append('</div>')
            
            # Show SS benefits table
            if results:
                ss_years = [y for y in results if y.get('social_security_income', 0) > 0][:10]
                if ss_years:
                    html.append('<table>')
                    html.append('<thead><tr><th>Year</th><th>Age</th><th>SS Income</th><th>Taxable SS</th></tr></thead>')
                    html.append('<tbody>')
                    for year_data in ss_years:
                        html.append('<tr>')
                        html.append(f'<td>{year_data.get("year", "")}</td>')
                        html.append(f'<td>{year_data.get("age", "")}</td>')
                        html.append(f'<td>${year_data.get("social_security_income", 0):,.0f}</td>')
                        html.append(f'<td>${year_data.get("taxable_social_security", 0):,.0f}</td>')
                        html.append('</tr>')
                    html.append('</tbody></table>')
        
        # Medicare section
        if 'medicare' in tabs:
            html.append('<div class="page-break"></div>')
            html.append('<h2>Medicare Planning</h2>')
            html.append('<div class="summary-box">')
            html.append(f'<div class="metric"><div class="metric-value">{scenario.medicare_age}</div><div class="metric-label">Medicare Start Age</div></div>')
            html.append(f'<div class="metric"><div class="metric-value">{scenario.part_b_inflation_rate}%</div><div class="metric-label">Part B Inflation</div></div>')
            html.append(f'<div class="metric"><div class="metric-value">{scenario.part_d_inflation_rate}%</div><div class="metric-label">Part D Inflation</div></div>')
            html.append('</div>')
            
            # Show Medicare costs table
            if results:
                medicare_years = [y for y in results if y.get('medicare_part_b', 0) > 0][:10]
                if medicare_years:
                    html.append('<table>')
                    html.append('<thead><tr><th>Year</th><th>Age</th><th>Part B</th><th>Part D</th><th>IRMAA</th></tr></thead>')
                    html.append('<tbody>')
                    for year_data in medicare_years:
                        html.append('<tr>')
                        html.append(f'<td>{year_data.get("year", "")}</td>')
                        html.append(f'<td>{year_data.get("age", "")}</td>')
                        html.append(f'<td>${year_data.get("medicare_part_b", 0):,.0f}</td>')
                        html.append(f'<td>${year_data.get("medicare_part_d", 0):,.0f}</td>')
                        html.append(f'<td>${year_data.get("irmaa_adjustment", 0):,.0f}</td>')
                        html.append('</tr>')
                    html.append('</tbody></table>')
        
        html.append('</body></html>')
        return ''.join(html)
    
    def _build_html_with_data(self, client, scenario, scenario_data, tabs: List[str]) -> str:
        """
        Build HTML content with actual scenario data
        """
        client_name = f"{client.first_name} {client.last_name}"
        scenario_name = scenario.name
        date_str = scenario.created_at.strftime('%B %d, %Y')
        
        html_parts = []
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html>')
        html_parts.append('<head>')
        html_parts.append('<meta charset="utf-8">')
        html_parts.append('<title>Retirement Scenario Report</title>')
        html_parts.append('<style>')
        html_parts.append('body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 100%; margin: 0; padding: 20px; }')
        html_parts.append('.header { border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }')
        html_parts.append('.page-break { page-break-after: always; }')
        html_parts.append('.tab-content { margin-bottom: 30px; }')
        html_parts.append('.tab-title { font-size: 24px; font-weight: bold; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }')
        html_parts.append('table { width: 100%; border-collapse: collapse; margin: 20px 0; }')
        html_parts.append('th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }')
        html_parts.append('th { background-color: #f8f9fa; font-weight: 600; }')
        html_parts.append('.metric-card { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }')
        html_parts.append('.metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }')
        html_parts.append('.metric-label { color: #6c757d; font-size: 14px; }')
        html_parts.append('</style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('<div class="header">')
        html_parts.append('<h1>Retirement Scenario Report</h1>')
        html_parts.append(f'<p><strong>Client:</strong> {client_name}</p>')
        html_parts.append(f'<p><strong>Scenario:</strong> {scenario_name}</p>')
        html_parts.append(f'<p><strong>Date:</strong> {date_str}</p>')
        html_parts.append('</div>')
        
        # Add content for each tab
        tab_titles = {
            'overview': 'Scenario Overview',
            'financial': 'Financial Overview',
            'socialSecurity': 'Social Security Analysis',
            'medicare': 'Medicare Planning'
        }
        
        for i, tab in enumerate(tabs):
            if tab not in tab_titles:
                continue
                
            # Add page break between sections (except for the first one)
            if i > 0:
                html_parts.append('<div class="page-break"></div>')
            
            html_parts.append(f'<div class="tab-content">')
            html_parts.append(f'<h2 class="tab-title">{tab_titles[tab]}</h2>')
            
            # Add content based on tab type
            if tab == 'overview':
                html_parts.append(self._build_overview_section(scenario, scenario_data))
            elif tab == 'financial':
                html_parts.append(self._build_financial_section(scenario, scenario_data))
            elif tab == 'socialSecurity':
                html_parts.append(self._build_social_security_section(scenario, scenario_data))
            elif tab == 'medicare':
                html_parts.append(self._build_medicare_section(scenario, scenario_data))
            
            html_parts.append('</div>')
        
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return ''.join(html_parts)
    
    def _build_overview_section(self, scenario, scenario_data):
        """Build overview section HTML"""
        html = []
        
        # Key metrics
        html.append('<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">')
        html.append('<div class="metric-card">')
        html.append(f'<div class="metric-value">{scenario.retirement_age}</div>')
        html.append('<div class="metric-label">Retirement Age</div>')
        html.append('</div>')
        
        if hasattr(scenario.client, 'spouse') and scenario.client.spouse:
            html.append('<div class="metric-card">')
            html.append(f'<div class="metric-value">{scenario.spouse_retirement_age}</div>')
            html.append('<div class="metric-label">Spouse Retirement Age</div>')
            html.append('</div>')
        
        html.append('<div class="metric-card">')
        html.append(f'<div class="metric-value">{scenario.mortality_age}</div>')
        html.append('<div class="metric-label">Life Expectancy</div>')
        html.append('</div>')
        
        # Add financial summary if data available
        if scenario_data and isinstance(scenario_data, list) and len(scenario_data) > 0:
            # Calculate totals
            total_lifetime_income = sum(y.get('total_income', 0) for y in scenario_data)
            total_lifetime_expenses = sum(y.get('total_expenses', 0) for y in scenario_data)
            total_lifetime_taxes = sum(y.get('federal_tax', 0) + y.get('state_tax', 0) for y in scenario_data)
            
            html.append('<div class="metric-card">')
            html.append(f'<div class="metric-value">${total_lifetime_income:,.0f}</div>')
            html.append('<div class="metric-label">Lifetime Income</div>')
            html.append('</div>')
            
            html.append('<div class="metric-card">')
            html.append(f'<div class="metric-value">${total_lifetime_expenses:,.0f}</div>')
            html.append('<div class="metric-label">Lifetime Expenses</div>')
            html.append('</div>')
            
            html.append('<div class="metric-card">')
            html.append(f'<div class="metric-value">${total_lifetime_taxes:,.0f}</div>')
            html.append('<div class="metric-label">Lifetime Taxes</div>')
            html.append('</div>')
        
        html.append('</div>')
        
        # Scenario details
        if scenario.description:
            html.append(f'<p><strong>Description:</strong> {scenario.description}</p>')
        
        # Income sources summary
        income_sources = scenario.income_sources.all()
        if income_sources:
            html.append('<h3>Income Sources</h3>')
            html.append('<ul>')
            for source in income_sources:
                balance = source.current_asset_balance or 0
                html.append(f'<li>{source.income_name}: ${balance:,.0f}</li>')
            html.append('</ul>')
        
        # Expense categories summary  
        expenses = scenario.expenses.all()
        if expenses:
            html.append('<h3>Expense Categories</h3>')
            html.append('<ul>')
            for expense in expenses[:5]:  # Show first 5 expenses
                amount = expense.current_monthly_expense or 0
                html.append(f'<li>{expense.expense_name}: ${amount:,.0f}/month</li>')
            html.append('</ul>')
        
        return ''.join(html)
    
    def _build_financial_section(self, scenario, scenario_data):
        """Build financial section HTML"""
        html = []
        
        if scenario_data and isinstance(scenario_data, list) and len(scenario_data) > 0:
            # Create a summary table
            html.append('<table>')
            html.append('<thead><tr><th>Year</th><th>Age</th><th>Total Income</th><th>Total Expenses</th><th>Net Income</th><th>Fed Tax</th><th>State Tax</th></tr></thead>')
            html.append('<tbody>')
            
            for year_data in scenario_data[:10]:  # Show first 10 years
                html.append('<tr>')
                html.append(f'<td>{year_data.get("year", "")}</td>')
                html.append(f'<td>{year_data.get("age", "")}</td>')
                html.append(f'<td>${year_data.get("total_income", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("total_expenses", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("net_income", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("federal_tax", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("state_tax", 0):,.0f}</td>')
                html.append('</tr>')
            
            html.append('</tbody></table>')
            
            if len(scenario_data) > 10:
                html.append(f'<p><em>Showing first 10 years of {len(scenario_data)} total years</em></p>')
        else:
            html.append('<p>No financial data available</p>')
        
        return ''.join(html)
    
    def _build_social_security_section(self, scenario, scenario_data):
        """Build Social Security section HTML"""
        html = []
        
        # Display claiming ages
        html.append('<div style="display: flex; gap: 20px; margin-bottom: 20px;">')
        html.append('<div class="metric-card">')
        html.append(f'<div class="metric-value">{scenario.primary_ss_claiming_age or "Not Set"}</div>')
        html.append('<div class="metric-label">Primary SS Claiming Age</div>')
        html.append('</div>')
        
        if hasattr(scenario.client, 'spouse') and scenario.client.spouse:
            html.append('<div class="metric-card">')
            html.append(f'<div class="metric-value">{scenario.spouse_ss_claiming_age or "Not Set"}</div>')
            html.append('<div class="metric-label">Spouse SS Claiming Age</div>')
            html.append('</div>')
        html.append('</div>')
        
        # Show Social Security income data if available
        if scenario_data and isinstance(scenario_data, list) and len(scenario_data) > 0:
            html.append('<h3>Social Security Benefits Over Time</h3>')
            html.append('<table>')
            html.append('<thead><tr><th>Year</th><th>Age</th><th>Primary SS</th>')
            if hasattr(scenario.client, 'spouse') and scenario.client.spouse:
                html.append('<th>Spouse SS</th>')
            html.append('<th>Total SS</th><th>Taxable SS</th></tr></thead>')
            html.append('<tbody>')
            
            # Show years where SS is received
            ss_years = [y for y in scenario_data if y.get('social_security_income', 0) > 0][:10]
            for year_data in ss_years:
                html.append('<tr>')
                html.append(f'<td>{year_data.get("year", "")}</td>')
                html.append(f'<td>{year_data.get("age", "")}</td>')
                html.append(f'<td>${year_data.get("social_security_primary", 0):,.0f}</td>')
                if hasattr(scenario.client, 'spouse') and scenario.client.spouse:
                    html.append(f'<td>${year_data.get("social_security_spouse", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("social_security_income", 0):,.0f}</td>')
                html.append(f'<td>${year_data.get("taxable_social_security", 0):,.0f}</td>')
                html.append('</tr>')
            
            html.append('</tbody></table>')
        
        return ''.join(html)
    
    def _build_medicare_section(self, scenario, scenario_data):
        """Build Medicare section HTML"""
        html = []
        
        # Display Medicare configuration
        html.append('<div style="display: flex; gap: 20px; margin-bottom: 20px;">')
        html.append('<div class="metric-card">')
        html.append(f'<div class="metric-value">{scenario.medicare_age}</div>')
        html.append('<div class="metric-label">Medicare Start Age</div>')
        html.append('</div>')
        
        html.append('<div class="metric-card">')
        html.append(f'<div class="metric-value">{scenario.part_b_inflation_rate}%</div>')
        html.append('<div class="metric-label">Part B Inflation Rate</div>')
        html.append('</div>')
        
        html.append('<div class="metric-card">')
        html.append(f'<div class="metric-value">{scenario.part_d_inflation_rate}%</div>')
        html.append('<div class="metric-label">Part D Inflation Rate</div>')
        html.append('</div>')
        html.append('</div>')
        
        # Show Medicare costs over time if available
        if scenario_data and isinstance(scenario_data, list) and len(scenario_data) > 0:
            # Filter for years with Medicare
            medicare_years = [y for y in scenario_data if y.get('medicare_part_b', 0) > 0 or y.get('medicare_part_d', 0) > 0][:10]
            
            if medicare_years:
                html.append('<h3>Medicare Costs Over Time</h3>')
                html.append('<table>')
                html.append('<thead><tr><th>Year</th><th>Age</th><th>Part B</th><th>Part D</th><th>IRMAA</th><th>Total Medicare</th></tr></thead>')
                html.append('<tbody>')
                
                for year_data in medicare_years:
                    html.append('<tr>')
                    html.append(f'<td>{year_data.get("year", "")}</td>')
                    html.append(f'<td>{year_data.get("age", "")}</td>')
                    html.append(f'<td>${year_data.get("medicare_part_b", 0):,.0f}</td>')
                    html.append(f'<td>${year_data.get("medicare_part_d", 0):,.0f}</td>')
                    html.append(f'<td>${year_data.get("irmaa_adjustment", 0):,.0f}</td>')
                    html.append(f'<td>${year_data.get("total_medicare", 0):,.0f}</td>')
                    html.append('</tr>')
                
                html.append('</tbody></table>')
        
        return ''.join(html)
    
    def _build_html_content(self, base_url: str, client_id: int, scenario_id: int, tabs: List[str], auth_token: str) -> str:
        """
        Build HTML content that combines multiple tab views
        """
        html_parts = ["""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Retirement Scenario Report</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 100%;
                    margin: 0;
                    padding: 0;
                }
                .page-break {
                    page-break-after: always;
                }
                .tab-content {
                    padding: 20px;
                    margin-bottom: 30px;
                }
                .tab-title {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                iframe {
                    width: 100%;
                    min-height: 1000px;
                    border: none;
                }
            </style>
        </head>
        <body>
        """]
        
        # Add content for each tab
        tab_titles = {
            'overview': 'Scenario Overview',
            'financial': 'Financial Overview',
            'socialSecurity': 'Social Security Analysis',
            'medicare': 'Medicare Planning'
        }
        
        for i, tab in enumerate(tabs):
            if tab not in tab_titles:
                continue
                
            tab_url = f"{base_url}/clients/{client_id}/scenarios/detail/{scenario_id}?tab={tab}"
            
            # Add page break between sections (except for the first one)
            if i > 0:
                html_parts.append('<div class="page-break"></div>')
            
            html_parts.append(f"""
            <div class="tab-content">
                <h1 class="tab-title">{tab_titles[tab]}</h1>
                <iframe src="{tab_url}" data-auth-token="{auth_token}"></iframe>
            </div>
            """)
        
        html_parts.append("""
        </body>
        </html>
        """)
        
        return ''.join(html_parts)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_scenario_pdf_view(request, scenario_id):
    """
    API endpoint to generate PDF for a scenario
    
    POST /api/scenarios/<scenario_id>/generate-pdf/
    Body: {
        "client_id": 123,
        "tabs": ["overview", "financial", "socialSecurity", "medicare"]
    }
    """
    try:
        # Validate user has access to this scenario
        from .models import Scenario
        try:
            scenario = Scenario.objects.get(id=scenario_id)
        except Scenario.DoesNotExist:
            return JsonResponse({'error': 'Scenario not found'}, status=404)
        
        # Get request data
        data = json.loads(request.body) if request.body else {}
        client_id = data.get('client_id', scenario.client_id)
        tabs = data.get('tabs', ['overview', 'financial', 'socialSecurity', 'medicare'])
        
        # Check if Pdfcrowd is enabled
        if not PDFCROWD_ENABLED:
            # Fallback: Return a simple message if Pdfcrowd is not configured
            logger.warning("Pdfcrowd not configured. Using fallback PDF generation.")
            return _generate_fallback_pdf(scenario, tabs)
        
        # Generate PDF using Pdfcrowd
        generator = ScenarioPDFGenerator()
        
        # Get the auth token from the request header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        auth_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        pdf_content = generator.generate_scenario_pdf(
            client_id=client_id,
            scenario_id=scenario_id,
            tabs=tabs,
            auth_token=auth_token
        )
        
        # Return PDF as response
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="scenario_{scenario_id}_report.pdf"'
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF for scenario {scenario_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def _generate_fallback_pdf(scenario, tabs):
    """
    Generate a simple fallback PDF when Pdfcrowd is not available
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        from io import BytesIO
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"Retirement Scenario Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Scenario info
        info_text = f"""
        <b>Client:</b> {scenario.client.first_name} {scenario.client.last_name}<br/>
        <b>Scenario:</b> {scenario.name}<br/>
        <b>Created:</b> {scenario.created_at.strftime('%Y-%m-%d')}<br/>
        """
        info = Paragraph(info_text, styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 0.5*inch))
        
        # Add section for each tab
        tab_titles = {
            'overview': 'Scenario Overview',
            'financial': 'Financial Overview',
            'socialSecurity': 'Social Security Analysis',
            'medicare': 'Medicare Planning'
        }
        
        for tab in tabs:
            if tab in tab_titles:
                story.append(PageBreak())
                section_title = Paragraph(tab_titles[tab], styles['Heading1'])
                story.append(section_title)
                story.append(Spacer(1, 0.3*inch))
                
                # Add placeholder content
                content = Paragraph(
                    f"Please visit the web application to view detailed {tab_titles[tab]} information.",
                    styles['Normal']
                )
                story.append(content)
        
        # Build PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="scenario_{scenario.id}_report.pdf"'
        return response
        
    except ImportError:
        # If even reportlab is not available, return error
        return JsonResponse({
            'error': 'PDF generation is not configured. Please install pdfcrowd or reportlab.'
        }, status=503)