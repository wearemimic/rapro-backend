"""
Report Center Celery Tasks
Handles background processing for report generation and template operations
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import ContentFile

from celery import shared_task
from retirementadvisorpro.celery import AnalyticsTask

from .models import Report, ReportTemplate, ReportGeneration, TemplateAnalytics, ReportSection
from core.models import Client, Scenario

User = get_user_model()
logger = logging.getLogger(__name__)

# =============================================================================
# REPORT GENERATION TASKS
# =============================================================================

@shared_task(base=AnalyticsTask, bind=True, max_retries=3)
def generate_report_pdf(self, report_id: str) -> Dict:
    """
    Generate PDF report from template and scenario data
    """
    try:
        # Get report object
        try:
            report = Report.objects.select_related(
                'template', 'client', 'scenario', 'created_by'
            ).get(id=report_id)
        except Report.DoesNotExist:
            logger.error(f"Report {report_id} not found")
            return {'status': 'error', 'error': f'Report {report_id} not found'}
        
        # Update generation record
        generation_record = ReportGeneration.objects.filter(report=report).last()
        if generation_record:
            generation_record.generation_status = 'processing'
            generation_record.save()
        
        # Update report status
        report.status = 'generating'
        report.generation_started_at = timezone.now()
        report.save()
        
        try:
            # Import report generator service
            from .services.report_generator import ReportGeneratorService
            
            # Initialize report generator
            generator = ReportGeneratorService()
            
            # Generate the report
            result = generator.generate_pdf_report(report)
            
            if result['success']:
                # Update report with successful generation
                report.status = 'completed'
                report.generation_completed_at = timezone.now()
                report.file_path = result['file_path']
                report.save()
                
                # Update generation record
                if generation_record:
                    generation_record.generation_status = 'completed'
                    generation_record.completed_at = timezone.now()
                    generation_record.file_size = result.get('file_size', 0)
                    generation_record.processing_time = (
                        generation_record.completed_at - generation_record.started_at
                    ).total_seconds() if generation_record.started_at else 0
                    generation_record.save()
                
                # Update template analytics
                update_template_usage_stats.delay(report.template.id)
                
                logger.info(f"PDF report generated successfully for report {report_id}")
                return {
                    'status': 'success',
                    'report_id': str(report_id),
                    'file_path': result['file_path'],
                    'file_size': result.get('file_size', 0),
                    'processing_time': generation_record.processing_time if generation_record else 0
                }
            else:
                # Handle generation failure
                error_message = result.get('error', 'Unknown error during PDF generation')
                logger.error(f"PDF generation failed for report {report_id}: {error_message}")
                
                # Update report status
                report.status = 'failed'
                report.save()
                
                # Update generation record
                if generation_record:
                    generation_record.generation_status = 'failed'
                    generation_record.error_message = error_message
                    generation_record.completed_at = timezone.now()
                    generation_record.save()
                
                return {'status': 'error', 'error': error_message}
                
        except ImportError:
            error_message = "Report generator service not available"
            logger.error(f"Import error for report {report_id}: {error_message}")
            
            # Update statuses
            report.status = 'failed'
            report.save()
            
            if generation_record:
                generation_record.generation_status = 'failed'
                generation_record.error_message = error_message
                generation_record.completed_at = timezone.now()
                generation_record.save()
            
            return {'status': 'error', 'error': error_message}
            
    except Exception as e:
        logger.error(f"Report generation task failed for {report_id}: {str(e)}")
        
        # Update report status to failed
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            report.save()
            
            # Update generation record
            generation_record = ReportGeneration.objects.filter(report=report).last()
            if generation_record:
                generation_record.generation_status = 'failed'
                generation_record.error_message = str(e)
                generation_record.completed_at = timezone.now()
                generation_record.save()
        except:
            pass
        
        # Retry logic with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 120 * (2 ** self.request.retries)  # 2min, 4min, 8min
            logger.info(f"Retrying report generation {report_id} in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {
            'status': 'failed',
            'error': str(e),
            'retries_exhausted': True,
            'report_id': str(report_id)
        }


@shared_task(base=AnalyticsTask, bind=True, max_retries=3)
def generate_report_pptx(self, report_id: str) -> Dict:
    """
    Generate PowerPoint report from template and scenario data
    """
    try:
        # Get report object
        try:
            report = Report.objects.select_related(
                'template', 'client', 'scenario', 'created_by'
            ).get(id=report_id)
        except Report.DoesNotExist:
            logger.error(f"Report {report_id} not found")
            return {'status': 'error', 'error': f'Report {report_id} not found'}
        
        # Update generation record
        generation_record = ReportGeneration.objects.filter(report=report).last()
        if generation_record:
            generation_record.generation_status = 'processing'
            generation_record.save()
        
        # Update report status
        report.status = 'generating'
        report.generation_started_at = timezone.now()
        report.save()
        
        try:
            # Import report generator service
            from .services.report_generator import ReportGeneratorService
            
            # Initialize report generator
            generator = ReportGeneratorService()
            
            # Generate the PowerPoint report
            result = generator.generate_pptx_report(report)
            
            if result['success']:
                # Update report with successful generation
                report.status = 'completed'
                report.generation_completed_at = timezone.now()
                report.file_path = result['file_path']
                report.save()
                
                # Update generation record
                if generation_record:
                    generation_record.generation_status = 'completed'
                    generation_record.completed_at = timezone.now()
                    generation_record.file_size = result.get('file_size', 0)
                    generation_record.processing_time = (
                        generation_record.completed_at - generation_record.started_at
                    ).total_seconds() if generation_record.started_at else 0
                    generation_record.save()
                
                # Update template analytics
                update_template_usage_stats.delay(report.template.id)
                
                logger.info(f"PowerPoint report generated successfully for report {report_id}")
                return {
                    'status': 'success',
                    'report_id': str(report_id),
                    'file_path': result['file_path'],
                    'file_size': result.get('file_size', 0),
                    'processing_time': generation_record.processing_time if generation_record else 0
                }
            else:
                # Handle generation failure
                error_message = result.get('error', 'Unknown error during PowerPoint generation')
                logger.error(f"PowerPoint generation failed for report {report_id}: {error_message}")
                
                # Update report status
                report.status = 'failed'
                report.save()
                
                # Update generation record
                if generation_record:
                    generation_record.generation_status = 'failed'
                    generation_record.error_message = error_message
                    generation_record.completed_at = timezone.now()
                    generation_record.save()
                
                return {'status': 'error', 'error': error_message}
                
        except ImportError:
            error_message = "Report generator service not available"
            logger.error(f"Import error for report {report_id}: {error_message}")
            
            # Update statuses
            report.status = 'failed'
            report.save()
            
            if generation_record:
                generation_record.generation_status = 'failed'
                generation_record.error_message = error_message
                generation_record.completed_at = timezone.now()
                generation_record.save()
            
            return {'status': 'error', 'error': error_message}
            
    except Exception as e:
        logger.error(f"PowerPoint generation task failed for {report_id}: {str(e)}")
        
        # Update report status to failed
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            report.save()
            
            # Update generation record
            generation_record = ReportGeneration.objects.filter(report=report).last()
            if generation_record:
                generation_record.generation_status = 'failed'
                generation_record.error_message = str(e)
                generation_record.completed_at = timezone.now()
                generation_record.save()
        except:
            pass
        
        # Retry logic with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 120 * (2 ** self.request.retries)  # 2min, 4min, 8min
            logger.info(f"Retrying PowerPoint generation {report_id} in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {
            'status': 'failed',
            'error': str(e),
            'retries_exhausted': True,
            'report_id': str(report_id)
        }


@shared_task
def batch_generate_reports(report_ids: List[str], format_type: str = 'pdf') -> Dict:
    """
    Generate multiple reports in batch
    """
    results = {
        'total': len(report_ids),
        'queued': 0,
        'task_ids': [],
        'format': format_type
    }
    
    # Choose the appropriate task based on format
    generation_task = generate_report_pdf if format_type == 'pdf' else generate_report_pptx
    queue_name = 'analytics'  # Use analytics queue for report generation
    
    for report_id in report_ids:
        try:
            # Queue individual generation task
            task = generation_task.apply_async(
                args=[report_id],
                queue=queue_name
            )
            results['task_ids'].append(task.id)
            results['queued'] += 1
        except Exception as e:
            logger.error(f"Failed to queue report {report_id} for generation: {str(e)}")
    
    logger.info(f"Queued {results['queued']} reports for {format_type.upper()} generation")
    return results


# =============================================================================
# TEMPLATE ANALYTICS TASKS
# =============================================================================

@shared_task
def update_template_usage_stats(template_id: str) -> Dict:
    """
    Update usage statistics for a template after report generation
    """
    try:
        template = ReportTemplate.objects.get(id=template_id)
        
        # Get or create analytics record
        analytics, created = TemplateAnalytics.objects.get_or_create(
            template=template,
            defaults={
                'usage_count': 0,
                'average_generation_time': 0,
                'last_used': timezone.now()
            }
        )
        
        # Calculate new stats
        completed_reports = Report.objects.filter(
            template=template,
            status='completed',
            generation_completed_at__isnull=False
        )
        
        usage_count = completed_reports.count()
        
        if usage_count > 0:
            # Calculate average generation time
            total_time = 0
            valid_reports = 0
            
            for report in completed_reports:
                if report.generation_started_at and report.generation_completed_at:
                    generation_time = (
                        report.generation_completed_at - report.generation_started_at
                    ).total_seconds()
                    total_time += generation_time
                    valid_reports += 1
            
            if valid_reports > 0:
                average_time = total_time / valid_reports
            else:
                average_time = analytics.average_generation_time
        else:
            average_time = 0
        
        # Update analytics
        analytics.usage_count = usage_count
        analytics.average_generation_time = average_time
        analytics.last_used = timezone.now()
        analytics.save()
        
        logger.info(f"Updated analytics for template {template_id}: {usage_count} uses, {average_time:.1f}s avg time")
        return {
            'status': 'success',
            'template_id': str(template_id),
            'usage_count': usage_count,
            'average_generation_time': average_time
        }
        
    except ReportTemplate.DoesNotExist:
        logger.error(f"Template {template_id} not found")
        return {'status': 'error', 'error': 'Template not found'}
    except Exception as e:
        logger.error(f"Failed to update template analytics for {template_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def generate_template_preview(template_id: str) -> Dict:
    """
    Generate preview image for a template
    """
    try:
        template = ReportTemplate.objects.get(id=template_id)
        
        try:
            from .services.template_preview_service import TemplatePreviewService
            
            # Generate preview
            preview_service = TemplatePreviewService()
            result = preview_service.generate_preview(template)
            
            if result['success']:
                # Update template with preview
                template.preview_image = result['preview_path']
                template.save()
                
                logger.info(f"Generated preview for template {template_id}")
                return {
                    'status': 'success',
                    'template_id': str(template_id),
                    'preview_path': result['preview_path']
                }
            else:
                logger.error(f"Preview generation failed for template {template_id}: {result.get('error')}")
                return {'status': 'error', 'error': result.get('error', 'Unknown error')}
                
        except ImportError:
            logger.error(f"Template preview service not available for template {template_id}")
            return {'status': 'error', 'error': 'Preview service not available'}
            
    except ReportTemplate.DoesNotExist:
        logger.error(f"Template {template_id} not found")
        return {'status': 'error', 'error': 'Template not found'}
    except Exception as e:
        logger.error(f"Template preview generation failed for {template_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}


# =============================================================================
# CLEANUP AND MAINTENANCE TASKS
# =============================================================================

@shared_task
def cleanup_old_report_files() -> Dict:
    """
    Clean up old report files and failed generations
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=30)  # Keep files for 30 days
        
        # Find old completed reports
        old_reports = Report.objects.filter(
            status='completed',
            generation_completed_at__lt=cutoff_date
        )
        
        files_deleted = 0
        reports_cleaned = 0
        
        for report in old_reports:
            if report.file_path and os.path.exists(report.file_path):
                try:
                    os.remove(report.file_path)
                    files_deleted += 1
                except OSError:
                    pass
            
            # Clear file path but keep report record
            report.file_path = None
            report.save()
            reports_cleaned += 1
        
        # Clean up failed report generations older than 7 days
        failed_cutoff = timezone.now() - timedelta(days=7)
        failed_generations = ReportGeneration.objects.filter(
            generation_status='failed',
            completed_at__lt=failed_cutoff
        )
        
        failed_deleted = failed_generations.delete()[0]
        
        logger.info(f"Cleaned up {files_deleted} old report files, {reports_cleaned} report records, "
                   f"and {failed_deleted} failed generation records")
        
        return {
            'status': 'success',
            'files_deleted': files_deleted,
            'reports_cleaned': reports_cleaned,
            'failed_generations_deleted': failed_deleted
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old report files: {str(e)}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def update_all_template_analytics() -> Dict:
    """
    Update analytics for all active templates
    """
    try:
        active_templates = ReportTemplate.objects.filter(is_active=True)
        
        results = {
            'total_templates': active_templates.count(),
            'updated': 0,
            'failed': 0
        }
        
        for template in active_templates:
            try:
                result = update_template_usage_stats.delay(str(template.id))
                results['updated'] += 1
            except Exception as e:
                logger.error(f"Failed to queue analytics update for template {template.id}: {str(e)}")
                results['failed'] += 1
        
        logger.info(f"Queued analytics updates for {results['updated']} templates")
        return results
        
    except Exception as e:
        logger.error(f"Failed to update all template analytics: {str(e)}")
        return {'status': 'error', 'error': str(e)}


# =============================================================================
# MONITORING AND HEALTH CHECKS
# =============================================================================

@shared_task
def report_center_health_check() -> Dict:
    """
    Health check for Report Center components
    """
    try:
        health_status = {
            'timestamp': timezone.now().isoformat(),
            'database': 'healthy',
            'file_storage': 'healthy',
            'services': {}
        }
        
        # Check database connectivity
        try:
            ReportTemplate.objects.count()
            Report.objects.count()
        except Exception as e:
            health_status['database'] = f'error: {str(e)}'
        
        # Check file storage paths
        storage_paths = getattr(settings, 'REPORT_CENTER_STORAGE', {})
        for path_name, path_value in storage_paths.items():
            try:
                if not os.path.exists(path_value):
                    os.makedirs(path_value, exist_ok=True)
                health_status['services'][path_name] = 'accessible'
            except Exception as e:
                health_status['services'][path_name] = f'error: {str(e)}'
        
        # Check for stuck report generations (longer than 1 hour)
        stuck_cutoff = timezone.now() - timedelta(hours=1)
        stuck_reports = Report.objects.filter(
            status='generating',
            generation_started_at__lt=stuck_cutoff
        ).count()
        
        if stuck_reports > 0:
            health_status['stuck_reports'] = stuck_reports
            logger.warning(f"Found {stuck_reports} stuck report generations")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Report center health check failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }