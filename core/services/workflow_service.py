# core/services/workflow_service.py
"""
Automated workflow service for common admin tasks
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .cache_service import CacheService
from .notification_service import NotificationService

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Main workflow engine for executing automated tasks
    """
    
    def __init__(self):
        self.workflows = {}
        self.active_workflows = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default workflow definitions"""
        # User onboarding workflow
        self.register_workflow('user_onboarding', {
            'name': 'User Onboarding',
            'description': 'Automated onboarding process for new users',
            'triggers': ['user_created'],
            'steps': [
                {'action': 'send_welcome_email', 'delay': 0},
                {'action': 'create_sample_data', 'delay': 300},  # 5 minutes
                {'action': 'send_getting_started_guide', 'delay': 1800},  # 30 minutes
                {'action': 'schedule_onboarding_followup', 'delay': 86400}  # 24 hours
            ]
        })
        
        # Billing issue resolution workflow
        self.register_workflow('billing_issue_resolution', {
            'name': 'Billing Issue Resolution',
            'description': 'Automated handling of billing-related issues',
            'triggers': ['payment_failed', 'subscription_expired'],
            'steps': [
                {'action': 'notify_billing_team', 'delay': 0},
                {'action': 'send_payment_reminder', 'delay': 3600},  # 1 hour
                {'action': 'attempt_payment_retry', 'delay': 86400},  # 24 hours
                {'action': 'suspend_account_warning', 'delay': 259200},  # 3 days
                {'action': 'suspend_account', 'delay': 604800}  # 7 days
            ],
            'conditions': {
                'max_retry_attempts': 3,
                'grace_period_days': 7
            }
        })
        
        # System health monitoring workflow
        self.register_workflow('system_health_monitoring', {
            'name': 'System Health Monitoring',
            'description': 'Continuous system health checks and alerts',
            'triggers': ['scheduled'],
            'schedule': '*/5 * * * *',  # Every 5 minutes
            'steps': [
                {'action': 'check_system_resources', 'delay': 0},
                {'action': 'check_database_performance', 'delay': 30},
                {'action': 'check_api_response_times', 'delay': 60},
                {'action': 'generate_health_report', 'delay': 90}
            ],
            'conditions': {
                'cpu_threshold': 80,
                'memory_threshold': 85,
                'response_time_threshold': 2000
            }
        })
        
        # Support ticket auto-routing workflow
        self.register_workflow('support_ticket_routing', {
            'name': 'Support Ticket Auto-Routing',
            'description': 'Automatically route support tickets to appropriate teams',
            'triggers': ['support_ticket_created'],
            'steps': [
                {'action': 'analyze_ticket_content', 'delay': 0},
                {'action': 'assign_to_team', 'delay': 60},
                {'action': 'set_priority_level', 'delay': 120},
                {'action': 'send_acknowledgment', 'delay': 180}
            ],
            'conditions': {
                'auto_assignment_rules': {
                    'billing': ['payment', 'subscription', 'invoice'],
                    'technical': ['bug', 'error', 'performance'],
                    'general': ['feature', 'question', 'help']
                }
            }
        })
        
        # Data cleanup workflow
        self.register_workflow('data_cleanup', {
            'name': 'Data Cleanup',
            'description': 'Regular cleanup of old data and logs',
            'triggers': ['scheduled'],
            'schedule': '0 2 * * 0',  # Weekly at 2 AM on Sunday
            'steps': [
                {'action': 'cleanup_old_logs', 'delay': 0},
                {'action': 'cleanup_expired_sessions', 'delay': 300},
                {'action': 'cleanup_temp_files', 'delay': 600},
                {'action': 'optimize_database', 'delay': 900},
                {'action': 'generate_cleanup_report', 'delay': 1200}
            ],
            'conditions': {
                'log_retention_days': 90,
                'session_retention_days': 30,
                'temp_file_retention_hours': 24
            }
        })
    
    def register_workflow(self, workflow_id: str, definition: Dict):
        """Register a new workflow definition"""
        self.workflows[workflow_id] = definition
        logger.info(f"Registered workflow: {workflow_id}")
    
    def trigger_workflow(self, workflow_id: str, context: Dict = None, user_id: int = None):
        """Trigger a workflow execution"""
        if workflow_id not in self.workflows:
            logger.error(f"Workflow not found: {workflow_id}")
            return None
        
        workflow_instance = WorkflowInstance(
            workflow_id=workflow_id,
            definition=self.workflows[workflow_id],
            context=context or {},
            user_id=user_id
        )
        
        # Start workflow execution
        instance_id = workflow_instance.start()
        self.active_workflows[instance_id] = workflow_instance
        
        logger.info(f"Started workflow {workflow_id} with instance ID: {instance_id}")
        return instance_id
    
    def get_workflow_status(self, instance_id: str) -> Dict:
        """Get the status of a workflow instance"""
        if instance_id in self.active_workflows:
            return self.active_workflows[instance_id].get_status()
        
        # Check completed workflows in cache/database
        cached_status = CacheService.get(f"workflow_status:{instance_id}")
        return cached_status or {'status': 'not_found'}
    
    def list_active_workflows(self) -> List[Dict]:
        """List all active workflow instances"""
        return [
            {
                'instance_id': instance_id,
                'workflow_id': instance.workflow_id,
                'status': instance.get_status(),
                'started_at': instance.started_at
            }
            for instance_id, instance in self.active_workflows.items()
        ]


class WorkflowInstance:
    """
    Individual workflow instance execution
    """
    
    def __init__(self, workflow_id: str, definition: Dict, context: Dict, user_id: int = None):
        self.workflow_id = workflow_id
        self.definition = definition
        self.context = context
        self.user_id = user_id
        self.instance_id = f"{workflow_id}_{int(timezone.now().timestamp())}"
        self.status = 'initialized'
        self.started_at = None
        self.completed_at = None
        self.current_step = 0
        self.step_results = []
        self.error_count = 0
        self.max_errors = 3
    
    def start(self) -> str:
        """Start workflow execution"""
        self.status = 'running'
        self.started_at = timezone.now()
        
        # Schedule first step
        self._schedule_next_step()
        
        return self.instance_id
    
    def _schedule_next_step(self):
        """Schedule the next workflow step"""
        if self.current_step >= len(self.definition['steps']):
            self._complete_workflow()
            return
        
        step = self.definition['steps'][self.current_step]
        delay = step.get('delay', 0)
        
        # Schedule step execution
        execute_workflow_step.apply_async(
            args=[self.instance_id, self.current_step],
            countdown=delay
        )
    
    def execute_step(self, step_index: int):
        """Execute a specific workflow step"""
        if step_index != self.current_step:
            logger.warning(f"Step index mismatch in workflow {self.instance_id}")
            return
        
        step = self.definition['steps'][step_index]
        action = step['action']
        
        try:
            # Execute step action
            result = self._execute_action(action, step)
            
            # Record result
            self.step_results.append({
                'step': step_index,
                'action': action,
                'status': 'completed',
                'result': result,
                'executed_at': timezone.now()
            })
            
            # Move to next step
            self.current_step += 1
            self._schedule_next_step()
            
        except Exception as e:
            logger.error(f"Step {step_index} failed in workflow {self.instance_id}: {str(e)}")
            self._handle_step_error(step_index, str(e))
    
    def _execute_action(self, action: str, step: Dict) -> Any:
        """Execute a workflow action"""
        action_handler = getattr(self, f"_action_{action}", None)
        
        if not action_handler:
            # Try to find action in workflow actions registry
            from .workflow_actions import get_action_handler
            action_handler = get_action_handler(action)
        
        if not action_handler:
            raise ValueError(f"Unknown action: {action}")
        
        return action_handler(self.context, step, self.definition.get('conditions', {}))
    
    def _handle_step_error(self, step_index: int, error_message: str):
        """Handle step execution error"""
        self.error_count += 1
        
        self.step_results.append({
            'step': step_index,
            'action': self.definition['steps'][step_index]['action'],
            'status': 'failed',
            'error': error_message,
            'executed_at': timezone.now()
        })
        
        if self.error_count >= self.max_errors:
            self._fail_workflow(f"Maximum errors exceeded: {error_message}")
        else:
            # Retry step after delay
            retry_delay = min(60 * (2 ** self.error_count), 300)  # Exponential backoff
            execute_workflow_step.apply_async(
                args=[self.instance_id, step_index],
                countdown=retry_delay
            )
    
    def _complete_workflow(self):
        """Mark workflow as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        # Cache final status
        CacheService.set(
            f"workflow_status:{self.instance_id}",
            self.get_status(),
            'default'
        )
        
        logger.info(f"Workflow {self.instance_id} completed successfully")
    
    def _fail_workflow(self, error_message: str):
        """Mark workflow as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        
        # Cache final status
        CacheService.set(
            f"workflow_status:{self.instance_id}",
            self.get_status(),
            'default'
        )
        
        logger.error(f"Workflow {self.instance_id} failed: {error_message}")
    
    def get_status(self) -> Dict:
        """Get current workflow status"""
        return {
            'instance_id': self.instance_id,
            'workflow_id': self.workflow_id,
            'status': self.status,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'current_step': self.current_step,
            'total_steps': len(self.definition['steps']),
            'progress': (self.current_step / len(self.definition['steps'])) * 100,
            'step_results': self.step_results,
            'error_count': self.error_count
        }
    
    # Built-in workflow actions
    def _action_send_welcome_email(self, context: Dict, step: Dict, conditions: Dict):
        """Send welcome email to new user"""
        user_id = context.get('user_id')
        if not user_id:
            raise ValueError("User ID required for welcome email")
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            
            send_mail(
                subject='Welcome to RetirementAdvisorPro!',
                message=f'Welcome {user.first_name}! We\'re excited to have you on board.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return {'email_sent': True, 'recipient': user.email}
            
        except User.DoesNotExist:
            raise ValueError(f"User {user_id} not found")
    
    def _action_create_sample_data(self, context: Dict, step: Dict, conditions: Dict):
        """Create sample data for new user"""
        user_id = context.get('user_id')
        if not user_id:
            return {'sample_data_created': False, 'reason': 'No user ID'}
        
        # Create sample client and scenario
        from ..models import Client, Scenario
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        with transaction.atomic():
            # Create sample client
            sample_client = Client.objects.create(
                advisor=user,
                first_name='John',
                last_name='Sample',
                email='john.sample@example.com',
                date_of_birth='1965-01-01'
            )
            
            # Create sample scenario
            sample_scenario = Scenario.objects.create(
                client=sample_client,
                scenario_name='Sample Retirement Plan',
                description='This is a sample scenario to help you get started',
                retirement_age=65,
                life_expectancy_male=85,
                life_expectancy_female=88
            )
        
        return {
            'sample_data_created': True,
            'client_id': sample_client.id,
            'scenario_id': sample_scenario.id
        }
    
    def _action_notify_billing_team(self, context: Dict, step: Dict, conditions: Dict):
        """Notify billing team of payment issue"""
        issue_type = context.get('issue_type', 'unknown')
        user_id = context.get('user_id')
        
        notification_service = NotificationService()
        
        notification_service.send_admin_notification(
            type='billing_issue',
            title=f'Billing Issue: {issue_type}',
            message=f'User {user_id} has a billing issue: {issue_type}',
            priority='high',
            metadata={'user_id': user_id, 'issue_type': issue_type}
        )
        
        return {'notification_sent': True, 'issue_type': issue_type}
    
    def _action_check_system_resources(self, context: Dict, step: Dict, conditions: Dict):
        """Check system resource usage"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check thresholds
            alerts = []
            if cpu_percent > conditions.get('cpu_threshold', 80):
                alerts.append(f'High CPU usage: {cpu_percent}%')
            
            if memory.percent > conditions.get('memory_threshold', 85):
                alerts.append(f'High memory usage: {memory.percent}%')
            
            if disk.percent > conditions.get('disk_threshold', 90):
                alerts.append(f'High disk usage: {disk.percent}%')
            
            # Send alerts if any
            if alerts:
                notification_service = NotificationService()
                notification_service.send_admin_notification(
                    type='system_alert',
                    title='System Resource Alert',
                    message='; '.join(alerts),
                    priority='critical'
                )
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'alerts': alerts
            }
            
        except ImportError:
            return {'error': 'psutil not available'}


@shared_task
def execute_workflow_step(instance_id: str, step_index: int):
    """Celery task to execute a workflow step"""
    workflow_engine = WorkflowEngine()
    
    if instance_id in workflow_engine.active_workflows:
        instance = workflow_engine.active_workflows[instance_id]
        instance.execute_step(step_index)
    else:
        logger.warning(f"Workflow instance {instance_id} not found in active workflows")


class WorkflowScheduler:
    """
    Scheduler for recurring workflows
    """
    
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
    
    def setup_scheduled_workflows(self):
        """Setup scheduled workflows"""
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        import json
        
        for workflow_id, definition in self.workflow_engine.workflows.items():
            if 'schedule' in definition:
                schedule_expr = definition['schedule']
                
                # Parse cron schedule
                parts = schedule_expr.split()
                if len(parts) == 5:
                    minute, hour, day_of_month, month, day_of_week = parts
                    
                    schedule, _ = CrontabSchedule.objects.get_or_create(
                        minute=minute,
                        hour=hour,
                        day_of_month=day_of_month,
                        month_of_year=month,
                        day_of_week=day_of_week
                    )
                    
                    # Create or update periodic task
                    task_name = f"workflow_{workflow_id}"
                    PeriodicTask.objects.update_or_create(
                        name=task_name,
                        defaults={
                            'task': 'core.services.workflow_service.execute_scheduled_workflow',
                            'crontab': schedule,
                            'args': json.dumps([workflow_id]),
                            'enabled': True
                        }
                    )


@shared_task
def execute_scheduled_workflow(workflow_id: str):
    """Execute a scheduled workflow"""
    workflow_engine = WorkflowEngine()
    return workflow_engine.trigger_workflow(workflow_id, {'trigger': 'scheduled'})


# Global workflow engine instance
workflow_engine = WorkflowEngine()
workflow_scheduler = WorkflowScheduler()