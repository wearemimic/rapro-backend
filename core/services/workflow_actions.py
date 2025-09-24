# core/services/workflow_actions.py
"""
Workflow action handlers for automated tasks
"""

import logging
from typing import Dict, Any, Callable
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# Global registry of workflow actions
ACTION_REGISTRY: Dict[str, Callable] = {}


def register_action(action_name: str):
    """Decorator to register workflow actions"""
    def decorator(func: Callable) -> Callable:
        ACTION_REGISTRY[action_name] = func
        return func
    return decorator


def get_action_handler(action_name: str) -> Callable:
    """Get action handler by name"""
    return ACTION_REGISTRY.get(action_name)


# User Management Actions
@register_action('send_welcome_email')
def send_welcome_email(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Send welcome email to new user"""
    user_id = context.get('user_id')
    if not user_id:
        raise ValueError("User ID required for welcome email")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        # Use email template if available
        from django.template.loader import render_to_string
        
        try:
            html_message = render_to_string('emails/welcome_email.html', {
                'user': user,
                'platform_name': 'RetirementAdvisorPro'
            })
            
            send_mail(
                subject='Welcome to RetirementAdvisorPro!',
                message='',
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
        except:
            # Fallback to plain text
            send_mail(
                subject='Welcome to RetirementAdvisorPro!',
                message=f'Welcome {user.first_name}! We\'re excited to have you join our platform.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
        
        return {'email_sent': True, 'recipient': user.email}
        
    except User.DoesNotExist:
        raise ValueError(f"User {user_id} not found")


@register_action('send_getting_started_guide')
def send_getting_started_guide(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Send getting started guide to user"""
    user_id = context.get('user_id')
    if not user_id:
        return {'guide_sent': False, 'reason': 'No user ID'}
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        send_mail(
            subject='Getting Started with RetirementAdvisorPro',
            message=f'''Hi {user.first_name},

Here are some quick steps to get started:

1. Create your first client
2. Set up a retirement scenario
3. Run Monte Carlo simulations
4. Generate reports

Need help? Our support team is here for you!

Best regards,
The RetirementAdvisorPro Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return {'guide_sent': True, 'recipient': user.email}
        
    except User.DoesNotExist:
        return {'guide_sent': False, 'reason': 'User not found'}


@register_action('schedule_onboarding_followup')
def schedule_onboarding_followup(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Schedule follow-up for onboarding completion"""
    user_id = context.get('user_id')
    if not user_id:
        return {'followup_scheduled': False}
    
    # Schedule follow-up task
    from .workflow_service import execute_workflow_step
    
    # Check if user has completed onboarding actions
    followup_delay = conditions.get('followup_delay', 259200)  # 3 days
    
    execute_workflow_step.apply_async(
        args=['onboarding_followup', user_id],
        countdown=followup_delay
    )
    
    return {'followup_scheduled': True, 'delay': followup_delay}


# Billing and Payment Actions
@register_action('send_payment_reminder')
def send_payment_reminder(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Send payment reminder email"""
    user_id = context.get('user_id')
    if not user_id:
        return {'reminder_sent': False}
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        send_mail(
            subject='Payment Reminder - RetirementAdvisorPro',
            message=f'''Hi {user.first_name},

We noticed there was an issue with your recent payment. Please update your payment method to continue using RetirementAdvisorPro.

You can update your payment information in your account settings.

If you have any questions, please contact our support team.

Best regards,
The RetirementAdvisorPro Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return {'reminder_sent': True, 'recipient': user.email}
        
    except User.DoesNotExist:
        return {'reminder_sent': False, 'reason': 'User not found'}


@register_action('attempt_payment_retry')
def attempt_payment_retry(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Attempt to retry failed payment"""
    user_id = context.get('user_id')
    if not user_id:
        return {'retry_attempted': False}
    
    try:
        # Integrate with Stripe to retry payment
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        if user.stripe_customer_id:
            # Get the most recent failed payment intent
            payment_intents = stripe.PaymentIntent.list(
                customer=user.stripe_customer_id,
                limit=1
            )
            
            if payment_intents.data:
                payment_intent = payment_intents.data[0]
                if payment_intent.status == 'requires_payment_method':
                    # Attempt to confirm payment with existing payment method
                    stripe.PaymentIntent.confirm(payment_intent.id)
                    return {'retry_attempted': True, 'status': 'confirmed'}
        
        return {'retry_attempted': True, 'status': 'no_retry_needed'}
        
    except Exception as e:
        logger.error(f"Payment retry failed for user {user_id}: {str(e)}")
        return {'retry_attempted': False, 'error': str(e)}


@register_action('suspend_account_warning')
def suspend_account_warning(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Send account suspension warning"""
    user_id = context.get('user_id')
    if not user_id:
        return {'warning_sent': False}
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        send_mail(
            subject='Account Suspension Warning - RetirementAdvisorPro',
            message=f'''Hi {user.first_name},

Your RetirementAdvisorPro account will be suspended soon due to an outstanding payment issue.

Please update your payment method immediately to avoid service interruption.

If you believe this is an error, please contact our support team right away.

Best regards,
The RetirementAdvisorPro Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return {'warning_sent': True, 'recipient': user.email}
        
    except User.DoesNotExist:
        return {'warning_sent': False, 'reason': 'User not found'}


@register_action('suspend_account')
def suspend_account(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Suspend user account for non-payment"""
    user_id = context.get('user_id')
    if not user_id:
        return {'account_suspended': False}
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        # Suspend account (set as inactive)
        user.is_active = False
        user.suspension_reason = 'payment_failure'
        user.suspended_at = timezone.now()
        user.save()
        
        # Send suspension notification
        send_mail(
            subject='Account Suspended - RetirementAdvisorPro',
            message=f'''Hi {user.first_name},

Your RetirementAdvisorPro account has been suspended due to payment issues.

To reactivate your account, please contact our support team or update your payment method.

Best regards,
The RetirementAdvisorPro Team''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        return {'account_suspended': True, 'user_id': user_id}
        
    except User.DoesNotExist:
        return {'account_suspended': False, 'reason': 'User not found'}


# System Health and Monitoring Actions
@register_action('check_system_resources')
def check_system_resources(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Check system resource usage"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get thresholds from conditions
        cpu_threshold = conditions.get('cpu_threshold', 80)
        memory_threshold = conditions.get('memory_threshold', 85)
        disk_threshold = conditions.get('disk_threshold', 90)
        
        # Check for alerts
        alerts = []
        if cpu_percent > cpu_threshold:
            alerts.append({
                'type': 'cpu',
                'message': f'High CPU usage: {cpu_percent}%',
                'value': cpu_percent,
                'threshold': cpu_threshold
            })
        
        if memory.percent > memory_threshold:
            alerts.append({
                'type': 'memory',
                'message': f'High memory usage: {memory.percent}%',
                'value': memory.percent,
                'threshold': memory_threshold
            })
        
        if disk.percent > disk_threshold:
            alerts.append({
                'type': 'disk',
                'message': f'High disk usage: {disk.percent}%',
                'value': disk.percent,
                'threshold': disk_threshold
            })
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'alerts': alerts,
            'alert_count': len(alerts)
        }
        
    except ImportError:
        return {'error': 'psutil not available'}


@register_action('check_database_performance')
def check_database_performance(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Check database performance metrics"""
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            # Check for slow queries
            cursor.execute("""
                SELECT query, calls, total_time, mean_time
                FROM pg_stat_statements
                WHERE mean_time > %s
                ORDER BY mean_time DESC
                LIMIT 10;
            """, [conditions.get('slow_query_threshold', 1000)])
            
            slow_queries = cursor.fetchall()
            
            # Check database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()));
            """)
            db_size = cursor.fetchone()[0]
            
            # Check connection count
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity;
            """)
            connection_count = cursor.fetchone()[0]
            
        alerts = []
        if len(slow_queries) > 5:
            alerts.append(f'Found {len(slow_queries)} slow queries')
        
        if connection_count > conditions.get('max_connections', 100):
            alerts.append(f'High connection count: {connection_count}')
        
        return {
            'slow_queries': len(slow_queries),
            'database_size': db_size,
            'connection_count': connection_count,
            'alerts': alerts
        }
        
    except Exception as e:
        logger.error(f"Database performance check failed: {str(e)}")
        return {'error': str(e)}


@register_action('check_api_response_times')
def check_api_response_times(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Check API endpoint response times"""
    from ..models import SystemPerformanceMetric
    from django.db.models import Avg
    
    try:
        # Get average response times for last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        avg_response_times = SystemPerformanceMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=one_hour_ago
        ).values('endpoint').annotate(
            avg_time=Avg('value')
        ).order_by('-avg_time')[:10]
        
        threshold = conditions.get('response_time_threshold', 2000)
        slow_endpoints = [
            endpoint for endpoint in avg_response_times
            if endpoint['avg_time'] > threshold
        ]
        
        alerts = []
        if slow_endpoints:
            alerts.append(f'Found {len(slow_endpoints)} slow endpoints')
        
        return {
            'avg_response_times': list(avg_response_times),
            'slow_endpoints': slow_endpoints,
            'alerts': alerts
        }
        
    except Exception as e:
        logger.error(f"API response time check failed: {str(e)}")
        return {'error': str(e)}


# Support Ticket Actions
@register_action('analyze_ticket_content')
def analyze_ticket_content(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Analyze support ticket content for auto-routing"""
    ticket_id = context.get('ticket_id')
    if not ticket_id:
        return {'analysis_completed': False}
    
    from ..models import SupportTicket
    
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
        
        # Simple keyword-based analysis
        content = f"{ticket.subject} {ticket.description}".lower()
        
        routing_rules = conditions.get('auto_assignment_rules', {})
        suggested_team = 'general'
        confidence = 0.0
        
        for team, keywords in routing_rules.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > confidence:
                confidence = score
                suggested_team = team
        
        # Determine priority based on keywords
        priority_keywords = {
            'urgent': ['urgent', 'critical', 'down', 'broken', 'emergency'],
            'high': ['important', 'asap', 'problem', 'issue'],
            'medium': ['help', 'question', 'support'],
            'low': ['feature', 'suggestion', 'enhancement']
        }
        
        suggested_priority = 'medium'
        for priority, keywords in priority_keywords.items():
            if any(keyword in content for keyword in keywords):
                suggested_priority = priority
                break
        
        return {
            'analysis_completed': True,
            'suggested_team': suggested_team,
            'suggested_priority': suggested_priority,
            'confidence': confidence,
            'keywords_found': [kw for kw in routing_rules.get(suggested_team, []) if kw in content]
        }
        
    except SupportTicket.DoesNotExist:
        return {'analysis_completed': False, 'reason': 'Ticket not found'}


@register_action('assign_to_team')
def assign_to_team(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Assign support ticket to appropriate team"""
    ticket_id = context.get('ticket_id')
    suggested_team = context.get('suggested_team', 'general')
    
    if not ticket_id:
        return {'assignment_completed': False}
    
    from ..models import SupportTicket
    from django.contrib.auth import get_user_model
    
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
        User = get_user_model()
        
        # Find available team members
        team_members = User.objects.filter(
            is_staff=True,
            is_active=True,
            role=suggested_team
        ).order_by('?')[:5]  # Random selection for load balancing
        
        if team_members:
            # Assign to least loaded team member
            assigned_user = min(team_members, key=lambda u: u.assigned_tickets.filter(
                status__in=['open', 'in_progress']
            ).count())
            
            ticket.assigned_to = assigned_user
            ticket.category = suggested_team
            ticket.save()
            
            return {
                'assignment_completed': True,
                'assigned_to': assigned_user.id,
                'team': suggested_team
            }
        
        return {'assignment_completed': False, 'reason': 'No team members available'}
        
    except SupportTicket.DoesNotExist:
        return {'assignment_completed': False, 'reason': 'Ticket not found'}


# Data Cleanup Actions
@register_action('cleanup_old_logs')
def cleanup_old_logs(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Clean up old log entries"""
    retention_days = conditions.get('log_retention_days', 90)
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    from ..models import ActivityLog, AdminAudit, SystemPerformanceMetric
    
    try:
        with transaction.atomic():
            # Clean up activity logs
            activity_deleted = ActivityLog.objects.filter(
                created_at__lt=cutoff_date
            ).delete()[0]
            
            # Clean up admin audit logs (keep longer)
            audit_cutoff = timezone.now() - timedelta(days=retention_days * 2)
            audit_deleted = AdminAudit.objects.filter(
                created_at__lt=audit_cutoff
            ).delete()[0]
            
            # Clean up performance metrics
            perf_deleted = SystemPerformanceMetric.objects.filter(
                timestamp__lt=cutoff_date
            ).delete()[0]
        
        return {
            'cleanup_completed': True,
            'activity_logs_deleted': activity_deleted,
            'audit_logs_deleted': audit_deleted,
            'performance_metrics_deleted': perf_deleted,
            'retention_days': retention_days
        }
        
    except Exception as e:
        logger.error(f"Log cleanup failed: {str(e)}")
        return {'cleanup_completed': False, 'error': str(e)}


@register_action('cleanup_expired_sessions')
def cleanup_expired_sessions(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Clean up expired user sessions"""
    from django.contrib.sessions.models import Session
    
    try:
        expired_count = Session.objects.filter(
            expire_date__lt=timezone.now()
        ).delete()[0]
        
        return {
            'cleanup_completed': True,
            'expired_sessions_deleted': expired_count
        }
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")
        return {'cleanup_completed': False, 'error': str(e)}


@register_action('generate_health_report')
def generate_health_report(context: Dict, step: Dict, conditions: Dict) -> Dict:
    """Generate system health report"""
    from .notification_service import NotificationService
    
    try:
        # Aggregate health data from previous steps
        cpu_data = context.get('cpu_percent', 0)
        memory_data = context.get('memory_percent', 0)
        disk_data = context.get('disk_percent', 0)
        db_metrics = context.get('database_metrics', {})
        api_metrics = context.get('api_metrics', {})
        
        # Generate report
        report = f"""
System Health Report - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

Resource Usage:
- CPU: {cpu_data}%
- Memory: {memory_data}%
- Disk: {disk_data}%

Database Performance:
- Slow Queries: {db_metrics.get('slow_queries', 0)}
- Connections: {db_metrics.get('connection_count', 0)}

API Performance:
- Slow Endpoints: {len(api_metrics.get('slow_endpoints', []))}

Status: {'HEALTHY' if cpu_data < 80 and memory_data < 85 else 'WARNING'}
        """
        
        # Send to admins if there are issues
        if cpu_data > 80 or memory_data > 85:
            notification_service = NotificationService()
            notification_service.send_admin_notification(
                type='system_health',
                title='System Health Alert',
                message=report,
                priority='high'
            )
        
        return {
            'report_generated': True,
            'report_content': report,
            'status': 'healthy' if cpu_data < 80 and memory_data < 85 else 'warning'
        }
        
    except Exception as e:
        logger.error(f"Health report generation failed: {str(e)}")
        return {'report_generated': False, 'error': str(e)}