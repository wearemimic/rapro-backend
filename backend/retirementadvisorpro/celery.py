"""
Celery Configuration for RetirementAdvisorPro
Handles background task processing with multiple queues
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retirementadvisorpro.settings')

# Create Celery application
app = Celery('retirementadvisorpro')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Task routing configuration - Route tasks to specific queues
app.conf.task_routes = {
    # AI Processing Queue - High CPU, moderate priority
    'core.tasks.process_email_with_ai': {'queue': 'ai_processing'},
    'core.tasks.batch_process_communications': {'queue': 'ai_processing'},
    'core.tasks.analyze_communication_async': {'queue': 'ai_processing'},
    'core.tasks.generate_ai_response': {'queue': 'ai_processing'},
    
    # Email Sync Queue - I/O intensive, high priority
    'core.tasks.sync_emails_batch': {'queue': 'email_sync'},
    'core.tasks.sync_single_email_account': {'queue': 'email_sync'},
    'core.tasks.send_email_via_provider': {'queue': 'email_sync'},
    'core.tasks.process_email_webhook': {'queue': 'email_sync'},
    
    # SMS Processing Queue - Time sensitive, high priority
    'core.tasks.send_sms_batch': {'queue': 'sms_processing'},
    'core.tasks.process_sms_webhook': {'queue': 'sms_processing'},
    'core.tasks.send_automated_sms': {'queue': 'sms_processing'},
    
    # Analytics & Reporting Queue - Low priority, scheduled
    'core.tasks.update_lead_scoring': {'queue': 'analytics'},
    'core.tasks.generate_daily_reports': {'queue': 'analytics'},
    'core.tasks.calculate_campaign_roi': {'queue': 'analytics'},
    'core.tasks.update_client_relationship_scores': {'queue': 'analytics'},
    
    # Default queue for miscellaneous tasks
    'core.tasks.cleanup_old_task_results': {'queue': 'default'},
    'core.tasks.health_check_task': {'queue': 'default'},
}

# Task configuration
app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],  # Ignore other content types
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Prevent worker from prefetching too many tasks
    task_acks_late=True,  # Acknowledge tasks after completion (not before processing)
    worker_max_tasks_per_child=100,  # Restart worker after N tasks to prevent memory leaks
    
    # Task execution limits
    task_soft_time_limit=300,  # 5 minute soft limit (task can catch this and cleanup)
    task_time_limit=600,  # 10 minute hard limit (task will be killed)
    
    # Default queue
    task_default_queue='default',
    
    # Queue configuration with different priorities
    task_queues={
        'default': {
            'routing_key': 'default',
        },
        'ai_processing': {
            'routing_key': 'ai_processing',
            'priority': 5,  # Medium priority
        },
        'email_sync': {
            'routing_key': 'email_sync',
            'priority': 8,  # High priority
        },
        'sms_processing': {
            'routing_key': 'sms_processing',
            'priority': 9,  # Highest priority (time sensitive)
        },
        'analytics': {
            'routing_key': 'analytics',
            'priority': 3,  # Low priority
        },
    },
    
    # Result backend configuration
    result_expires=86400,  # Results expire after 24 hours
    result_persistent=True,  # Store results persistently
    
    # Beat scheduler configuration
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    beat_schedule_filename='celerybeat-schedule',
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,  # We want to track task results
    
    # Advanced configuration
    worker_disable_rate_limits=False,
    task_compression='gzip',  # Compress task messages
    result_compression='gzip',  # Compress results
    
    # Monitoring
    worker_send_task_events=True,  # Send task events for monitoring
    task_send_sent_event=True,  # Send task sent events
)

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Additional queue-specific worker configurations
# This can be used to run workers with different configurations for different queues
@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration"""
    print(f'Request: {self.request!r}')
    return f'Celery is working! Task ID: {self.request.id}'

# Custom task base classes for different queue types
class AIProcessingTask(app.Task):
    """Base task class for AI processing tasks"""
    soft_time_limit = 300  # 5 minutes
    time_limit = 600      # 10 minutes
    max_retries = 3
    default_retry_delay = 60  # 1 minute base retry delay

class EmailSyncTask(app.Task):
    """Base task class for email sync tasks"""
    soft_time_limit = 180  # 3 minutes
    time_limit = 360      # 6 minutes
    max_retries = 5
    default_retry_delay = 30  # 30 second base retry delay

class SMSProcessingTask(app.Task):
    """Base task class for SMS processing tasks"""
    soft_time_limit = 60   # 1 minute
    time_limit = 120      # 2 minutes
    max_retries = 3
    default_retry_delay = 10  # 10 second base retry delay

class AnalyticsTask(app.Task):
    """Base task class for analytics tasks"""
    soft_time_limit = 600  # 10 minutes
    time_limit = 1200     # 20 minutes
    max_retries = 2
    default_retry_delay = 300  # 5 minute base retry delay

# Health check function
def celery_health_check():
    """Check if Celery workers are responsive"""
    try:
        # Send a simple task to test if workers are running
        result = debug_task.apply_async(expires=10)  # 10 second timeout
        result.get(timeout=10)  # Wait max 10 seconds for result
        return True
    except Exception as e:
        print(f"Celery health check failed: {e}")
        return False

# Periodic tasks configuration (will be moved to Django admin via django-celery-beat)
app.conf.beat_schedule = {
    'cleanup-old-results': {
        'task': 'core.tasks.cleanup_old_task_results',
        'schedule': 86400.0,  # Run daily
        'options': {'queue': 'default'}
    },
    'sync-all-email-accounts': {
        'task': 'core.tasks.sync_all_email_accounts',
        'schedule': 3600.0,  # Run hourly
        'options': {'queue': 'email_sync'}
    },
    'analyze-new-emails': {
        'task': 'core.tasks.analyze_new_inbound_emails',
        'schedule': 1800.0,  # Run every 30 minutes
        'options': {'queue': 'ai_processing'}
    },
    'generate-ai-usage-report': {
        'task': 'core.tasks.generate_ai_usage_report',
        'schedule': 86400.0,  # Run daily
        'options': {'queue': 'analytics'}
    },
}

# Celery signal handlers for monitoring and logging
from celery.signals import task_prerun, task_postrun, task_failure
import logging

logger = logging.getLogger('celery.tasks')

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Log when a task starts"""
    logger.info(f'Task {task.name}[{task_id}] starting')

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Log when a task completes"""
    logger.info(f'Task {task.name}[{task_id}] completed with state: {state}')

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Log when a task fails"""
    logger.error(f'Task {sender.name}[{task_id}] failed: {exception}')
    # Here you could add additional error reporting (e.g., Sentry, email notifications)

# Queue monitoring utilities
def get_queue_stats():
    """Get statistics for all queues"""
    inspect = app.control.inspect()
    stats = {}
    
    try:
        # Get active tasks by queue
        active = inspect.active()
        if active:
            for worker, tasks in active.items():
                for task in tasks:
                    queue = task.get('delivery_info', {}).get('routing_key', 'unknown')
                    if queue not in stats:
                        stats[queue] = {'active': 0, 'scheduled': 0}
                    stats[queue]['active'] += 1
        
        # Get scheduled tasks
        scheduled = inspect.scheduled()
        if scheduled:
            for worker, tasks in scheduled.items():
                for task in tasks:
                    queue = task.get('delivery_info', {}).get('routing_key', 'unknown')
                    if queue not in stats:
                        stats[queue] = {'active': 0, 'scheduled': 0}
                    stats[queue]['scheduled'] += 1
                    
    except Exception as e:
        logger.error(f"Failed to get queue stats: {e}")
    
    return stats

def get_worker_status():
    """Get status of all workers"""
    inspect = app.control.inspect()
    try:
        return {
            'stats': inspect.stats(),
            'active_queues': inspect.active_queues(),
            'registered': inspect.registered(),
        }
    except Exception as e:
        logger.error(f"Failed to get worker status: {e}")
        return {'error': str(e)}