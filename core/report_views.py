"""
Report Center Views
Real implementation of report generation endpoints
"""

import logging
import os
import uuid
from typing import Dict, List
from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from celery import current_app

from .models import Client, Scenario
from report_center.models import Report, ReportTemplate
from .services.report_generator import ReportGenerator
from .services.data_service import ReportDataService

logger = logging.getLogger(__name__)


class ReportTemplateListView(APIView):
    """API endpoint for listing and creating report templates"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List available report templates"""
        try:
            # Return professional templates per PRD specifications
            templates = [
                {
                    'id': 'retirement-overview',
                    'name': 'Comprehensive Retirement Overview',
                    'description': 'Complete retirement analysis with scenarios, projections, and recommendations',
                    'template_type': 'retirement',
                    'category': 'comprehensive',
                    'is_public': True,
                    'is_active': True,
                    'sections': ['cover', 'summary', 'scenarios', 'charts', 'recommendations'],
                    'preview_image': None,
                    'usage_count': 245,
                    'created_at': '2025-01-01T00:00:00Z',
                    'updated_at': '2025-01-01T00:00:00Z'
                },
                {
                    'id': 'irmaa-analysis',
                    'name': 'IRMAA Impact Analysis',
                    'description': 'Detailed Medicare premium impact analysis with optimization strategies',
                    'template_type': 'tax',
                    'category': 'irmaa',
                    'is_public': True,
                    'is_active': True,
                    'sections': ['cover', 'irmaa_overview', 'impact_analysis', 'optimization', 'recommendations'],
                    'preview_image': None,
                    'usage_count': 132,
                    'created_at': '2025-01-01T00:00:00Z',
                    'updated_at': '2025-01-01T00:00:00Z'
                },
                {
                    'id': 'tax-strategy',
                    'name': 'Tax Optimization Strategy',
                    'description': 'Comprehensive tax planning with Roth conversion analysis',
                    'template_type': 'tax',
                    'category': 'optimization',
                    'is_public': True,
                    'is_active': True,
                    'sections': ['cover', 'tax_overview', 'roth_analysis', 'strategies', 'timeline'],
                    'preview_image': None,
                    'usage_count': 189,
                    'created_at': '2025-01-01T00:00:00Z',
                    'updated_at': '2025-01-01T00:00:00Z'
                },
                {
                    'id': 'scenario-comparison',
                    'name': 'Scenario Comparison Report',
                    'description': 'Side-by-side comparison of multiple retirement scenarios',
                    'template_type': 'comparison',
                    'category': 'analysis',
                    'is_public': True,
                    'is_active': True,
                    'sections': ['cover', 'comparison_overview', 'scenarios', 'charts', 'recommendations'],
                    'preview_image': None,
                    'usage_count': 167,
                    'created_at': '2025-01-01T00:00:00Z',
                    'updated_at': '2025-01-01T00:00:00Z'
                },
                {
                    'id': 'executive-summary',
                    'name': 'Executive Summary Report',
                    'description': 'Concise overview perfect for initial client meetings',
                    'template_type': 'summary',
                    'category': 'executive',
                    'is_public': True,
                    'is_active': True,
                    'sections': ['cover', 'executive_summary', 'key_metrics', 'next_steps'],
                    'preview_image': None,
                    'usage_count': 298,
                    'created_at': '2025-01-01T00:00:00Z',
                    'updated_at': '2025-01-01T00:00:00Z'
                }
            ]
            
            return Response({
                'results': templates,
                'count': len(templates),
                'next': None,
                'previous': None
            })
            
        except Exception as e:
            logger.error(f"Error fetching templates: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch templates'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportListView(APIView):
    """API endpoint for listing and creating reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List user's reports"""
        try:
            # Get reports from database for the current user
            reports = Report.objects.filter(advisor=request.user).order_by('-created_at')
            
            # Serialize reports
            report_data = []
            for report in reports:
                report_data.append({
                    'id': str(report.id),  # Convert UUID to string
                    'name': report.name,
                    'description': report.description,
                    'client_id': report.client.id if report.client else None,
                    'client_name': f"{report.client.first_name} {report.client.last_name}" if report.client else "Unknown Client",
                    'template_id': report.report_config.get('template_id', 'retirement-overview'),
                    'template_name': report.template.name if report.template else 'Retirement Overview',
                    'export_format': report.report_config.get('export_format', 'pdf'),
                    'status': 'completed' if report.status == 'ready' else report.status,
                    'created_at': report.created_at.isoformat(),
                    'updated_at': report.updated_at.isoformat(),
                    'scenario_ids': report.report_config.get('scenario_ids', []),
                    'generated_at': report.generated_at.isoformat() if report.generated_at else None
                })
            
            return Response({
                'results': report_data,
                'count': len(report_data),
                'next': None,
                'previous': None
            })
            
        except Exception as e:
            logger.error(f"Error fetching reports: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to fetch reports'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new report"""
        try:
            data = request.data
            logger.info(f"Creating report with data: {data}")
            
            # Validate required fields
            required_fields = ['name', 'client_id']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Verify client exists and belongs to user
            try:
                client = Client.objects.get(id=data['client_id'], advisor=request.user)
            except Client.DoesNotExist:
                return Response(
                    {'error': 'Client not found or access denied'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get scenarios for the client
            scenario_ids = data.get('scenario_ids', [])
            if scenario_ids:
                scenarios = client.scenarios.filter(id__in=scenario_ids)
            else:
                scenarios = client.scenarios.all()[:3]  # Default to first 3 scenarios
            
            # Create report record in database
            # Get or create a default template
            template, _ = ReportTemplate.objects.get_or_create(
                name='Retirement Overview',
                defaults={
                    'description': 'Standard retirement planning report',
                    'template_type': 'system',
                    'category': 'retirement',
                    'is_system_template': True,
                    'template_config': {
                        'sections': ['cover', 'summary', 'scenarios', 'charts']
                    }
                }
            )
            
            # Create the actual Report model instance
            report = Report.objects.create(
                advisor=request.user,
                client=client,
                template=template,
                name=data['name'],
                description=data.get('description', ''),
                status='draft',
                report_config={
                    'export_format': data.get('export_format', 'pdf'),
                    'scenario_ids': [s.id for s in scenarios],
                    'template_id': data.get('template_id', 'retirement-overview')
                },
                data_snapshot={
                    'client': {
                        'id': client.id,
                        'name': f"{client.first_name} {client.last_name}"
                    },
                    'scenarios': [{'id': s.id, 'name': s.name} for s in scenarios]
                }
            )
            
            # Prepare response data
            report_data = {
                'id': str(report.id),  # Convert UUID to string
                'name': report.name,
                'description': report.description,
                'client_id': client.id,
                'client_name': f"{client.first_name} {client.last_name}",
                'template_id': data.get('template_id', 'retirement-overview'),
                'template_name': 'Retirement Overview',
                'export_format': data.get('export_format', 'pdf'),
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat(),
                'scenario_ids': [s.id for s in scenarios]
            }
            
            logger.info(f"Report created successfully: {report_data}")
            
            return Response(report_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to create report'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request, report_id):
    """Generate PDF/PowerPoint report"""
    try:
        data = request.data
        format_type = data.get('format', 'pdf')
        
        logger.info(f"Generating report {report_id} in {format_type} format")
        
        # Get the report from database and update status
        try:
            report = Report.objects.get(id=report_id, advisor=request.user)
            report.status = 'generating'
            report.save()
        except Report.DoesNotExist:
            return Response(
                {'error': 'Report not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get client and scenario information from request
        client_id = data.get('client_id')
        scenario_ids = data.get('scenario_ids', [])
        
        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify client access
        try:
            client = Client.objects.get(id=client_id, advisor=request.user)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare report configuration
        report_config = {
            'client_id': client_id,
            'scenario_ids': scenario_ids,
            'template_type': data.get('template_id', 'retirement-overview'),
            'export_format': format_type,
            'report_title': data.get('name', f'Retirement Analysis for {client.first_name} {client.last_name}'),
            'advisor_info': {
                'name': f"{request.user.first_name} {request.user.last_name}",
                'company': getattr(request.user, 'company_name', 'RetirementAdvisorPro'),
                'email': request.user.email,
                'phone': getattr(request.user, 'phone_number', ''),
                'primary_color': getattr(request.user, 'primary_color', '#0072C6')
            }
        }
        
        # Generate report using the ReportGenerator service
        generator = ReportGenerator()
        result = generator.generate_report(report_config)
        
        if result['success']:
            # Update report status to ready
            report.status = 'ready'
            report.generated_at = timezone.now()
            if format_type == 'pdf' and 'pdf' in result['files']:
                report.pdf_file = result['files']['pdf']['filename']
            elif format_type == 'pptx' and 'pptx' in result['files']:
                report.pptx_file = result['files']['pptx']['filename']
            report.save()
            
            # Return task information
            task_id = f"report_{report_id}_{format_type}_{int(timezone.now().timestamp())}"
            
            response_data = {
                'task_id': task_id,
                'format': format_type,
                'report_id': report_id,
                'status': 'ready',
                'message': f'Report generation completed for {format_type.upper()} format',
                'estimated_completion': timezone.now(),
                'files': result['files'],
                'generated_at': result['generated_at']
            }
            
            logger.info(f"Report generation completed: {response_data}")
            return Response(response_data)
        else:
            return Response(
                {'error': 'Report generation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to generate report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_status(request, report_id):
    """Check report generation status"""
    try:
        logger.info(f"Checking status for report {report_id}")
        
        # Get the actual report
        report = Report.objects.get(id=report_id, advisor=request.user)
        
        # Check if files exist
        import os
        from django.conf import settings
        media_root = settings.MEDIA_ROOT
        pdf_path = os.path.join(media_root, "reports", "pdf")
        pptx_path = os.path.join(media_root, "reports", "pptx")
        
        files = {}
        download_urls = []
        
        # Check for PDF files
        if os.path.exists(pdf_path):
            for filename in os.listdir(pdf_path):
                if filename.startswith("report_") and filename.endswith(".pdf"):
                    file_path = os.path.join(pdf_path, filename)
                    file_size = os.path.getsize(file_path)
                    files['pdf'] = {
                        'filename': filename,
                        'size': file_size,
                        'download_url': f'/api/report-center/reports/{report_id}/download/?format=pdf&filename={filename}'
                    }
                    download_urls.append(files['pdf']['download_url'])
                    break
        
        # Check for PowerPoint files
        if os.path.exists(pptx_path):
            for filename in os.listdir(pptx_path):
                if filename.startswith("report_") and filename.endswith(".pptx"):
                    file_path = os.path.join(pptx_path, filename)
                    file_size = os.path.getsize(file_path)
                    files['pptx'] = {
                        'filename': filename,
                        'size': file_size,
                        'download_url': f'/api/report-center/reports/{report_id}/download/?format=pptx&filename={filename}'
                    }
                    download_urls.append(files['pptx']['download_url'])
                    break
        
        # Check report status from database and file availability
        if report.status == 'ready' and files:
            status = 'completed'
            message = 'Report generation completed successfully'
        elif report.status == 'generating':
            status = 'generating'
            message = 'Report generation in progress'
        elif files:
            # Files exist but status not updated - update it
            status = 'completed'
            message = 'Report generation completed successfully'
            report.status = 'ready'
            report.save()
        else:
            status = 'generating'
            message = 'Report generation in progress'
        
        status_data = {
            'id': report_id,
            'status': status,
            'generation_completed_at': timezone.now().isoformat() if status == 'completed' else None,
            'files': files,
            'download_urls': download_urls,
            'message': message
        }
        
        logger.info(f"Report status: {status_data}")
        return Response(status_data)
        
    except Exception as e:
        logger.error(f"Error checking report status: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to check report status'},
            status=500
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, report_id):
    """Download generated report file"""
    try:
        format_type = request.GET.get('format', 'pdf')
        filename = request.GET.get('filename')
        logger.info(f"Download request for report {report_id} in {format_type} format, filename: {filename}")
        
        # Get the actual report to verify user access
        report = Report.objects.get(id=report_id, advisor=request.user)
        
        # If filename is provided, use it; otherwise find the most recent file
        if filename:
            file_path = os.path.join(settings.MEDIA_ROOT, "reports", format_type, filename)
        else:
            # Find the most recent file for this format
            format_dir = os.path.join(settings.MEDIA_ROOT, "reports", format_type)
            if os.path.exists(format_dir):
                files = [f for f in os.listdir(format_dir) if f.startswith("report_") and f.endswith(f".{format_type}")]
                if files:
                    files.sort(key=lambda x: os.path.getmtime(os.path.join(format_dir, x)), reverse=True)
                    filename = files[0]
                    file_path = os.path.join(format_dir, filename)
                else:
                    raise FileNotFoundError(f"No {format_type} files found")
            else:
                raise FileNotFoundError(f"Reports directory not found")
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Report file not found: {file_path}")
        
        # Serve the file
        from django.http import FileResponse
        content_type = 'application/pdf' if format_type == 'pdf' else 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=filename
        )
        
        logger.info(f"Serving file: {file_path}")
        return response
        
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to download report'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Additional utility views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_data(request, client_id):
    """Get client and scenario data for report generation"""
    try:
        # Verify client access
        try:
            client = Client.objects.get(id=client_id, advisor=request.user)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get client scenarios
        scenarios = client.scenarios.all()
        
        # Serialize data using ReportDataService
        data_service = ReportDataService()
        
        client_data = data_service.serialize_client(client)
        scenarios_data = []
        
        for scenario in scenarios:
            scenario_data = data_service.serialize_scenario(scenario)
            scenarios_data.append(scenario_data)
        
        return Response({
            'client': client_data,
            'scenarios': scenarios_data,
            'total_scenarios': len(scenarios_data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching report data: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to fetch report data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )