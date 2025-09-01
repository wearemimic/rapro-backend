# backend/core/services/notification_service.py

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from typing import List, Dict, Optional, Any
from ..models import SupportTicket, AlertRule, AlertNotification

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for handling all types of notifications including:
    - Support ticket notifications
    - Alert notifications
    - System notifications
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@retirementadvisorpro.com')
    
    def send_support_ticket_notification(self, ticket: SupportTicket, notification_type: str, 
                                       recipient_email: str = None, additional_context: Dict = None) -> bool:
        """
        Send support ticket related notifications
        
        Args:
            ticket: SupportTicket instance
            notification_type: Type of notification ('created', 'updated', 'resolved', 'comment_added')
            recipient_email: Optional specific recipient, otherwise uses ticket user email
            additional_context: Additional context for email template
            
        Returns:
            bool: Success status
        """
        try:
            # Determine recipient
            if recipient_email:
                to_email = recipient_email
            else:
                to_email = ticket.user.email
            
            # Prepare context
            context = {
                'ticket': ticket,
                'user': ticket.user,
                'assigned_admin': ticket.assigned_admin,
                'notification_type': notification_type,
                'site_url': getattr(settings, 'SITE_URL', 'https://app.retirementadvisorpro.com')
            }
            
            if additional_context:
                context.update(additional_context)
            
            # Generate subject based on notification type
            subject_map = {
                'created': f'Support Ticket Created - {ticket.ticket_id}',
                'updated': f'Support Ticket Updated - {ticket.ticket_id}',
                'resolved': f'Support Ticket Resolved - {ticket.ticket_id}',
                'closed': f'Support Ticket Closed - {ticket.ticket_id}',
                'comment_added': f'New Response to Support Ticket - {ticket.ticket_id}',
                'assigned': f'Support Ticket Assigned - {ticket.ticket_id}',
                'escalated': f'Support Ticket Escalated - {ticket.ticket_id}'
            }
            
            subject = subject_map.get(notification_type, f'Support Ticket Update - {ticket.ticket_id}')
            
            # Load email template
            html_content = render_to_string(
                'emails/support_ticket_notification.html', 
                context
            )
            text_content = strip_tags(html_content)
            
            # Send email
            success = send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False
            )
            
            logger.info(f"Support ticket notification sent successfully: {ticket.ticket_id} to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send support ticket notification: {str(e)}")
            return False
    
    def send_alert_notification(self, alert_rule: AlertRule, alert_data: Dict, 
                              severity: str = 'medium') -> List[AlertNotification]:
        """
        Send alert notifications based on alert rule configuration
        
        Args:
            alert_rule: AlertRule instance
            alert_data: Data that triggered the alert
            severity: Alert severity level
            
        Returns:
            List[AlertNotification]: Created notification records
        """
        notifications_sent = []
        
        try:
            # Generate alert message
            alert_message = self._generate_alert_message(alert_rule, alert_data, severity)
            
            # Send notifications via configured channels
            for channel in alert_rule.notification_channels:
                for recipient in alert_rule.recipients:
                    notification = AlertNotification.objects.create(
                        alert_rule=alert_rule,
                        alert_message=alert_message,
                        alert_data=alert_data,
                        severity=severity,
                        notification_channel=channel,
                        recipient=recipient,
                        status='pending'
                    )
                    
                    # Send via appropriate channel
                    if channel == 'email':
                        success = self._send_alert_email(notification, alert_rule, alert_data)
                    elif channel == 'slack':
                        success = self._send_alert_slack(notification, alert_rule, alert_data)
                    elif channel == 'webhook':
                        success = self._send_alert_webhook(notification, alert_rule, alert_data)
                    elif channel == 'sms':
                        success = self._send_alert_sms(notification, alert_rule, alert_data)
                    else:
                        success = False
                        notification.error_message = f"Unsupported notification channel: {channel}"
                    
                    # Update notification status
                    if success:
                        notification.status = 'sent'
                        notification.sent_at = timezone.now()
                    else:
                        notification.status = 'failed'
                        if not notification.error_message:
                            notification.error_message = "Failed to send notification"
                    
                    notification.save()
                    notifications_sent.append(notification)
            
            # Update alert rule trigger count
            alert_rule.trigger_count += 1
            alert_rule.last_triggered = timezone.now()
            alert_rule.save()
            
        except Exception as e:
            logger.error(f"Failed to send alert notifications: {str(e)}")
        
        return notifications_sent
    
    def _generate_alert_message(self, alert_rule: AlertRule, alert_data: Dict, severity: str) -> str:
        """Generate human-readable alert message"""
        alert_type_messages = {
            'metric_threshold': f"Metric threshold exceeded: {alert_data.get('metric_name', 'Unknown')} is {alert_data.get('current_value', 'N/A')} (threshold: {alert_rule.threshold_value})",
            'error_rate': f"Error rate alert: {alert_data.get('error_rate', 'N/A')}% errors in the last {alert_data.get('time_period', 'N/A')}",
            'user_activity': f"User activity alert: {alert_data.get('description', 'Unusual user activity detected')}",
            'revenue_change': f"Revenue alert: {alert_data.get('change_description', 'Significant revenue change detected')}",
            'system_health': f"System health alert: {alert_data.get('health_issue', 'System health issue detected')}",
            'sla_breach': f"SLA breach alert: {alert_data.get('sla_description', 'SLA target not met')}"
        }
        
        base_message = alert_type_messages.get(
            alert_rule.alert_type, 
            f"Alert triggered for rule: {alert_rule.name}"
        )
        
        return f"[{severity.upper()}] {alert_rule.name}: {base_message}"
    
    def _send_alert_email(self, notification: AlertNotification, alert_rule: AlertRule, alert_data: Dict) -> bool:
        """Send alert via email"""
        try:
            context = {
                'alert_rule': alert_rule,
                'alert_data': alert_data,
                'notification': notification,
                'severity': notification.severity,
                'timestamp': timezone.now(),
                'site_url': getattr(settings, 'SITE_URL', 'https://app.retirementadvisorpro.com')
            }
            
            subject = f"[ALERT - {notification.severity.upper()}] {alert_rule.name}"
            
            html_content = render_to_string('emails/alert_notification.html', context)
            text_content = strip_tags(html_content)
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=[notification.recipient],
                html_message=html_content,
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {str(e)}")
            notification.error_message = str(e)
            return False
    
    def _send_alert_slack(self, notification: AlertNotification, alert_rule: AlertRule, alert_data: Dict) -> bool:
        """Send alert via Slack (placeholder for future implementation)"""
        try:
            # TODO: Implement Slack webhook integration
            logger.info(f"Slack alert would be sent: {notification.alert_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            notification.error_message = str(e)
            return False
    
    def _send_alert_webhook(self, notification: AlertNotification, alert_rule: AlertRule, alert_data: Dict) -> bool:
        """Send alert via webhook (placeholder for future implementation)"""
        try:
            # TODO: Implement webhook integration
            logger.info(f"Webhook alert would be sent: {notification.alert_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            notification.error_message = str(e)
            return False
    
    def _send_alert_sms(self, notification: AlertNotification, alert_rule: AlertRule, alert_data: Dict) -> bool:
        """Send alert via SMS (placeholder for future implementation)"""
        try:
            # TODO: Implement SMS integration (Twilio, etc.)
            logger.info(f"SMS alert would be sent: {notification.alert_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {str(e)}")
            notification.error_message = str(e)
            return False
    
    def send_system_notification(self, recipient_email: str, subject: str, 
                               message: str, template_name: str = None, 
                               context: Dict = None) -> bool:
        """
        Send general system notifications
        
        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            message: Plain text message
            template_name: Optional template name for HTML email
            context: Optional context for template rendering
            
        Returns:
            bool: Success status
        """
        try:
            if template_name and context:
                html_content = render_to_string(f'emails/{template_name}', context)
                text_content = strip_tags(html_content)
            else:
                html_content = None
                text_content = message
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=[recipient_email],
                html_message=html_content,
                fail_silently=False
            )
            
            logger.info(f"System notification sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send system notification: {str(e)}")
            return False


# Convenience function for easy access
def get_notification_service() -> NotificationService:
    """Get notification service instance"""
    return NotificationService()