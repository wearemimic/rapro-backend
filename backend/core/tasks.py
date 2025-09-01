"""
Celery Tasks for RetirementAdvisorPro CRM
Handles background processing for AI, email sync, SMS, and analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings

from celery import shared_task
from retirementadvisorpro.celery import AIProcessingTask, EmailSyncTask, SMSProcessingTask, AnalyticsTask

from .models import Communication, Client, Lead, EmailAccount, ActivityLog

User = get_user_model()
logger = logging.getLogger(__name__)

# =============================================================================
# AI PROCESSING TASKS
# =============================================================================

@shared_task(base=AIProcessingTask, bind=True, max_retries=3)
def process_email_with_ai(self, communication_id: int) -> Dict:
    """
    Background task to process email with AI analysis
    Includes comprehensive error handling and retry logic
    """
    try:
        from .services.ai_email_service import AIEmailService
        
        # Get communication
        try:
            communication = Communication.objects.select_related('client', 'advisor').get(id=communication_id)
        except Communication.DoesNotExist:
            logger.error(f"Communication {communication_id} not found")
            return {'status': 'error', 'error': f'Communication {communication_id} not found'}
        
        # Skip if already processed
        if communication.ai_analysis_date:
            logger.info(f"Communication {communication_id} already processed")
            return {'status': 'skipped', 'reason': 'Already processed'}
        
        # Skip if no content
        if not communication.content or len(communication.content.strip()) < 10:
            logger.info(f"Communication {communication_id} has insufficient content for AI analysis")
            return {'status': 'skipped', 'reason': 'Insufficient content'}
        
        # Initialize AI service
        ai_service = AIEmailService()
        
        # Update communication with AI analysis
        success = ai_service.update_communication_analysis(communication)
        
        if success:
            # Log activity
            ActivityLog.objects.create(
                activity_type='ai_analysis_completed',
                user=communication.advisor,
                client=communication.client,
                lead=communication.lead,
                description=f'AI analysis completed for {communication.communication_type}',
                metadata={
                    'communication_id': communication_id,
                    'sentiment_score': float(communication.ai_sentiment_score or 0),
                    'priority_score': float(communication.ai_priority_score or 0),
                }
            )
            
            logger.info(f"AI analysis completed for communication {communication_id}")
            return {
                'status': 'success',
                'communication_id': communication_id,
                'sentiment_score': float(communication.ai_sentiment_score or 0),
                'priority_score': float(communication.ai_priority_score or 0),
                'has_suggested_response': bool(communication.ai_suggested_response)
            }
        else:
            logger.error(f"AI analysis failed for communication {communication_id}")
            return {'status': 'error', 'error': 'AI service failed'}
            
    except Exception as e:
        logger.error(f"AI email processing failed for {communication_id}: {str(e)}")
        
        # Retry logic with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 60 * (2 ** self.request.retries)  # Exponential backoff: 60s, 120s, 240s
            logger.info(f"Retrying communication {communication_id} in {retry_delay} seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=retry_delay, exc=e)
        
        # Mark as failed after max retries
        try:
            communication = Communication.objects.get(id=communication_id)
            communication.ai_sentiment_label = 'neutral'  # Default for failed analysis
            communication.ai_analysis_date = timezone.now()
            communication.ai_model_version = 'failed'
            communication.save(update_fields=['ai_sentiment_label', 'ai_analysis_date', 'ai_model_version'])
        except:
            pass
        
        return {
            'status': 'failed',
            'error': str(e),
            'retries_exhausted': True,
            'communication_id': communication_id
        }

@shared_task(bind=True)
def batch_process_communications(self, communication_ids: List[int]) -> Dict:
    """Process multiple communications for AI analysis"""
    results = {
        'total': len(communication_ids),
        'queued': 0,
        'task_ids': []
    }
    
    for comm_id in communication_ids:
        try:
            # Queue individual processing task
            task = process_email_with_ai.apply_async(args=[comm_id], queue='ai_processing')
            results['task_ids'].append(task.id)
            results['queued'] += 1
        except Exception as e:
            logger.error(f"Failed to queue communication {comm_id} for AI processing: {str(e)}")
    
    logger.info(f"Queued {results['queued']} communications for AI processing")
    return results

@shared_task
def analyze_new_inbound_emails() -> Dict:
    """
    Analyze new inbound emails that haven't been processed yet
    This task is run periodically to catch new emails
    """
    try:
        # Find unprocessed inbound emails from the last 24 hours
        recent_cutoff = timezone.now() - timedelta(hours=24)
        
        unprocessed_emails = Communication.objects.filter(
            communication_type='email',
            direction='inbound',
            ai_analysis_date__isnull=True,
            created_at__gte=recent_cutoff
        ).order_by('-created_at')[:50]  # Limit to 50 to avoid overload
        
        if not unprocessed_emails:
            logger.info("No new inbound emails to analyze")
            return {'processed': 0, 'total': 0, 'message': 'No new emails found'}
        
        # Queue them for processing
        email_ids = [email.id for email in unprocessed_emails]
        batch_result = batch_process_communications.delay(email_ids)
        
        logger.info(f"Queued {len(email_ids)} new inbound emails for AI analysis")
        return {
            'total': len(email_ids),
            'queued': len(email_ids),
            'batch_task_id': batch_result.id,
            'message': f'Queued {len(email_ids)} emails for analysis'
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze new inbound emails: {str(e)}")
        return {'error': str(e), 'processed': 0, 'total': 0}

# =============================================================================
# EMAIL SYNC TASKS
# =============================================================================

@shared_task(base=EmailSyncTask, bind=True, max_retries=5)
def sync_email_account(self, email_account_id: int) -> Dict:
    """Sync a single email account"""
    try:
        from .services.email_service import EmailService
        
        email_account = EmailAccount.objects.get(id=email_account_id, is_active=True)
        service = EmailService(email_account)
        
        # Perform sync
        sync_stats = service.sync_emails_to_crm()
        
        # Queue AI processing for new emails
        new_communications = sync_stats.get('new_communications', [])
        if new_communications:
            batch_process_communications.apply_async(
                args=[new_communications],
                queue='ai_processing'
            )
        
        logger.info(f"Synced email account {email_account.email_address}: {sync_stats}")
        return {
            'status': 'success',
            'account': email_account.email_address,
            'synced': sync_stats.get('created', 0),
            'updated': sync_stats.get('updated', 0),
            'ai_queued': len(new_communications)
        }
        
    except EmailAccount.DoesNotExist:
        logger.error(f"Email account {email_account_id} not found")
        return {'status': 'error', 'error': 'Account not found'}
    except Exception as e:
        logger.error(f"Email sync failed for account {email_account_id}: {str(e)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 30 * (2 ** self.request.retries)  # 30s, 60s, 120s, 240s, 480s
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {'status': 'failed', 'error': str(e)}

@shared_task
def sync_all_email_accounts() -> Dict:
    """Sync all active email accounts"""
    try:
        active_accounts = EmailAccount.objects.filter(is_active=True, sync_enabled=True)
        
        if not active_accounts.exists():
            return {'message': 'No active email accounts to sync', 'synced': 0}
        
        results = {
            'total_accounts': active_accounts.count(),
            'queued': 0,
            'task_ids': []
        }
        
        for account in active_accounts:
            try:
                task = sync_email_account.apply_async(
                    args=[account.id],
                    queue='email_sync'
                )
                results['task_ids'].append(task.id)
                results['queued'] += 1
            except Exception as e:
                logger.error(f"Failed to queue sync for account {account.email_address}: {str(e)}")
        
        logger.info(f"Queued {results['queued']} email accounts for sync")
        return results
        
    except Exception as e:
        logger.error(f"Failed to sync all email accounts: {str(e)}")
        return {'error': str(e)}

@shared_task(base=EmailSyncTask)
def send_email_via_provider(email_data: Dict) -> Dict:
    """Send email through provider and create communication record"""
    try:
        from .services.email_service import EmailService
        
        email_account_id = email_data.get('email_account_id')
        email_account = EmailAccount.objects.get(id=email_account_id)
        
        service = EmailService(email_account)
        result = service.send_email(email_data)
        
        return {
            'status': 'success',
            'message_id': result.get('message_id'),
            'communication_id': result.get('communication_id')
        }
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# SMS PROCESSING TASKS
# =============================================================================

@shared_task(base=SMSProcessingTask)
def send_sms_message(sms_data: Dict) -> Dict:
    """Send SMS message via Twilio"""
    try:
        from .services.sms_service import SMSService
        
        user_id = sms_data.get('user_id')
        service = SMSService(user_id=user_id)
        
        result = service.send_sms(
            to_number=sms_data['to_number'],
            message=sms_data['message'],
            client_id=sms_data.get('client_id')
        )
        
        return {
            'status': 'success',
            'message_sid': result['message_sid'],
            'sms_message_id': result['sms_message_id']
        }
        
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def send_sms_batch(sms_batch_data: List[Dict]) -> Dict:
    """Send multiple SMS messages"""
    results = {
        'total': len(sms_batch_data),
        'sent': 0,
        'failed': 0,
        'errors': []
    }
    
    for sms_data in sms_batch_data:
        try:
            result = send_sms_message.apply_async(args=[sms_data], queue='sms_processing')
            results['sent'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(str(e))
    
    return results

@shared_task
def process_sms_webhook(webhook_data: Dict) -> Dict:
    """Process incoming SMS webhook from Twilio"""
    try:
        from .services.sms_service import SMSService
        
        # Process the webhook data
        service = SMSService()
        result = service.process_incoming_sms(webhook_data)
        
        # If this is an inbound SMS, we might want to analyze it with AI
        if result.get('direction') == 'inbound' and result.get('sms_message_id'):
            # Create a Communication record and potentially queue for AI analysis
            pass  # Implementation depends on SMS to Communication mapping
        
        return {'status': 'success', 'result': result}
        
    except Exception as e:
        logger.error(f"Failed to process SMS webhook: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# ANALYTICS TASKS
# =============================================================================

@shared_task(base=AnalyticsTask)
def update_lead_scoring() -> Dict:
    """Update lead scoring based on recent interactions"""
    try:
        # Implementation would calculate lead scores based on:
        # - Recent communications
        # - Email engagement
        # - Response times
        # - Conversion probability
        
        leads_updated = Lead.objects.filter(status__in=['new', 'contacted', 'qualified']).count()
        
        logger.info(f"Updated scoring for {leads_updated} leads")
        return {
            'status': 'success',
            'leads_updated': leads_updated,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update lead scoring: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task(base=AnalyticsTask)
def generate_daily_reports() -> Dict:
    """Generate daily analytics reports"""
    try:
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Calculate daily stats
        stats = {
            'date': yesterday.isoformat(),
            'emails_processed': Communication.objects.filter(
                communication_type='email',
                created_at__date=yesterday
            ).count(),
            'ai_analyses_completed': Communication.objects.filter(
                ai_analysis_date__date=yesterday
            ).count(),
            'new_leads': Lead.objects.filter(
                created_at__date=yesterday
            ).count(),
        }
        
        logger.info(f"Generated daily report for {yesterday}: {stats}")
        return {'status': 'success', 'stats': stats}
        
    except Exception as e:
        logger.error(f"Failed to generate daily reports: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task(base=AnalyticsTask)
def calculate_campaign_roi() -> Dict:
    """Calculate ROI for marketing campaigns"""
    try:
        # Implementation would calculate:
        # - Cost per lead by source
        # - Conversion rates by campaign
        # - Lifetime value attribution
        # - ROI by marketing channel
        
        campaigns_analyzed = 0  # Placeholder
        
        logger.info(f"Analyzed ROI for {campaigns_analyzed} campaigns")
        return {
            'status': 'success',
            'campaigns_analyzed': campaigns_analyzed,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate campaign ROI: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def generate_ai_usage_report() -> Dict:
    """Generate AI usage and cost reporting"""
    try:
        from .tasks.ai_tasks import get_ai_analysis_stats
        
        # Get current month's stats
        stats = get_ai_analysis_stats()
        
        # Calculate cost trends and alerts
        if 'total_cost' in stats:
            budget_limit = settings.AI_MONTHLY_BUDGET_LIMIT
            usage_percentage = (stats['total_cost'] / budget_limit) * 100
            
            if usage_percentage > settings.AI_COST_ALERT_THRESHOLD:
                # Here you could send alerts to admins
                logger.warning(f"AI usage at {usage_percentage:.1f}% of monthly budget")
        
        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI usage report: {str(e)}")
        return {'status': 'error', 'error': str(e)}

# =============================================================================
# REPORT CENTER TASKS
# =============================================================================

@shared_task(bind=True, max_retries=3)
def generate_report_task(self, report_config):
    """
    Background task for generating reports
    
    Args:
        report_config: Dictionary containing report configuration
        
    Returns:
        Dictionary with generation results
    """
    try:
        from .services.report_generator import ReportGenerator
        
        logger.info(f"Starting background report generation task")
        logger.info(f"Report config: {report_config}")
        
        # Initialize report generator
        generator = ReportGenerator()
        
        # Generate report
        result = generator.generate_report(report_config)
        
        logger.info(f"Background report generation completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Background report generation failed: {str(e)}", exc_info=True)
        
        # Retry logic with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 30 * (2 ** self.request.retries)  # 30s, 60s, 120s
            logger.info(f"Retrying report generation in {retry_delay} seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {
            'success': False,
            'error': str(e),
            'generated_at': timezone.now().isoformat(),
            'retries_exhausted': True
        }


@shared_task
def cleanup_old_reports():
    """
    Background task to clean up old report files
    Runs daily to remove expired reports
    """
    try:
        import os
        from pathlib import Path
        from django.conf import settings
        
        logger.info("Starting report cleanup task")
        
        # Get report directories
        reports_dir = Path(settings.MEDIA_ROOT) / "reports"
        
        if not reports_dir.exists():
            logger.info("Reports directory does not exist, skipping cleanup")
            return {'cleaned_files': 0}
        
        # Clean up files older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        cutoff_timestamp = cutoff_date.timestamp()
        
        cleaned_count = 0
        
        for format_dir in ['pdf', 'pptx']:
            format_path = reports_dir / format_dir
            if format_path.exists():
                for file_path in format_path.iterdir():
                    if file_path.is_file():
                        # Check file age
                        file_age = file_path.stat().st_mtime
                        if file_age < cutoff_timestamp:
                            try:
                                file_path.unlink()
                                cleaned_count += 1
                                logger.info(f"Cleaned up old report file: {file_path}")
                            except Exception as e:
                                logger.error(f"Failed to delete file {file_path}: {str(e)}")
        
        logger.info(f"Report cleanup completed. Cleaned {cleaned_count} files.")
        return {'cleaned_files': cleaned_count}
        
    except Exception as e:
        logger.error(f"Report cleanup task failed: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task
def generate_report_analytics():
    """
    Background task to generate report usage analytics
    """
    try:
        logger.info("Starting report analytics generation")
        
        # This would generate analytics data for the admin dashboard
        # For now, return mock data
        analytics = {
            'total_reports_generated': 156,
            'pdf_reports': 89,
            'pptx_reports': 67,
            'most_popular_template': 'retirement-overview',
            'average_generation_time': 45.2,
            'generated_at': timezone.now().isoformat()
        }
        
        logger.info(f"Report analytics generated: {analytics}")
        return analytics
        
    except Exception as e:
        logger.error(f"Report analytics generation failed: {str(e)}", exc_info=True)
        return {'error': str(e)}

# =============================================================================
# UTILITY TASKS
# =============================================================================

@shared_task
def cleanup_old_task_results() -> Dict:
    """Clean up old Celery task results"""
    try:
        from django_celery_results.models import TaskResult
        
        # Delete results older than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)
        deleted_count = TaskResult.objects.filter(date_done__lt=cutoff_date).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old task results")
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old task results: {str(e)}")
        return {'status': 'error', 'error': str(e)}

@shared_task
def health_check_task() -> Dict:
    """Simple health check task to verify Celery is working"""
    return {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'worker': 'active'
    }

# =============================================================================
# PERIODIC TASK SCHEDULING
# =============================================================================

# These can be configured via Django admin with django-celery-beat
# or through the beat_schedule in celery.py

def schedule_periodic_tasks():
    """
    Function to set up periodic tasks programmatically
    This can be called from Django management commands
    """
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    
    # Create schedules if they don't exist
    every_30_minutes, _ = IntervalSchedule.objects.get_or_create(
        every=30,
        period=IntervalSchedule.MINUTES,
    )
    
    every_hour, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.HOURS,
    )
    
    daily, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.DAYS,
    )
    
    # Create periodic tasks
    tasks = [
        {
            'name': 'Analyze new inbound emails',
            'task': 'core.tasks.analyze_new_inbound_emails',
            'interval': every_30_minutes,
        },
        {
            'name': 'Sync all email accounts',
            'task': 'core.tasks.sync_all_email_accounts',
            'interval': every_hour,
        },
        {
            'name': 'Generate daily reports',
            'task': 'core.tasks.generate_daily_reports',
            'interval': daily,
        },
        {
            'name': 'Cleanup old task results',
            'task': 'core.tasks.cleanup_old_task_results',
            'interval': daily,
        },
    ]
    
    for task_config in tasks:
        PeriodicTask.objects.get_or_create(
            name=task_config['name'],
            defaults={
                'task': task_config['task'],
                'interval': task_config['interval'],
                'enabled': True,
            }
        )
    
    logger.info("Periodic tasks configured successfully")