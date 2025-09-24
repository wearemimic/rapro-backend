"""
Activity Service for logging and managing activity events
"""
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from ..models import ActivityLog, Client


class ActivityService:
    """Service for managing activity logging across the application"""
    
    @staticmethod
    def log_activity(
        user,
        activity_type,
        description,
        client=None,
        lead=None,
        metadata=None
    ):
        """
        Log an activity to the unified activity log
        
        Args:
            user: The user performing the activity
            activity_type: Type of activity (from ActivityLog.ACTIVITY_TYPES)
            description: Human-readable description of the activity
            client: Related client (optional)
            lead: Related lead (optional)
            metadata: Additional data specific to the activity type
            
        Returns:
            ActivityLog instance
        """
        return ActivityLog.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            client=client,
            lead=lead,
            metadata=metadata or {}
        )
    
    @staticmethod
    def log_document_upload(user, document, client=None):
        """Log a document upload activity"""
        description = f"Uploaded document: {document.original_filename}"
        metadata = {
            'document_id': str(document.id),
            'file_name': document.original_filename,
            'file_size': document.file_size,
            'mime_type': document.mime_type,
            'category': document.category.name if document.category else None,
            's3_key': document.s3_key
        }
        
        return ActivityService.log_activity(
            user=user,
            activity_type='document_uploaded',
            description=description,
            client=client or document.client,
            metadata=metadata
        )
    
    @staticmethod
    def log_scenario_created(user, scenario, client):
        """Log scenario creation activity"""
        description = f"Created scenario: {scenario.name}"
        metadata = {
            'scenario_id': scenario.id,
            'scenario_name': scenario.name,
            'scenario_type': scenario.scenario_type if hasattr(scenario, 'scenario_type') else None
        }
        
        return ActivityService.log_activity(
            user=user,
            activity_type='scenario_created',
            description=description,
            client=client,
            metadata=metadata
        )
    
    @staticmethod
    def log_report_generated(user, report_type, client, metadata=None):
        """Log report generation activity"""
        description = f"Generated {report_type} report"
        report_metadata = {
            'report_type': report_type,
            'generated_at': timezone.now().isoformat()
        }
        if metadata:
            report_metadata.update(metadata)
        
        return ActivityService.log_activity(
            user=user,
            activity_type='report_generated',
            description=description,
            client=client,
            metadata=report_metadata
        )
    
    @staticmethod
    def log_task_completed(user, task, client=None):
        """Log task completion activity"""
        description = f"Completed task: {task.title}"
        metadata = {
            'task_id': task.id,
            'task_title': task.title,
            'task_type': task.task_type if hasattr(task, 'task_type') else None,
            'completed_at': timezone.now().isoformat()
        }
        
        return ActivityService.log_activity(
            user=user,
            activity_type='task_completed',
            description=description,
            client=client or task.client,
            metadata=metadata
        )
    
    @staticmethod
    def log_email_activity(user, email_type, subject, client=None, metadata=None):
        """Log email activities (sent/received)"""
        activity_type = 'email_sent' if email_type == 'sent' else 'email_received'
        description = f"{'Sent' if email_type == 'sent' else 'Received'} email: {subject}"
        
        email_metadata = {
            'subject': subject,
            'timestamp': timezone.now().isoformat()
        }
        if metadata:
            email_metadata.update(metadata)
        
        return ActivityService.log_activity(
            user=user,
            activity_type=activity_type,
            description=description,
            client=client,
            metadata=email_metadata
        )
    
    @staticmethod
    def get_recent_activities(user, client=None, days=30, limit=100):
        """
        Get recent activities for a user or client
        
        Args:
            user: The user to get activities for
            client: Optional client to filter by
            days: Number of days to look back
            limit: Maximum number of activities to return
            
        Returns:
            QuerySet of ActivityLog instances
        """
        from datetime import timedelta
        
        queryset = ActivityLog.objects.filter(user=user)
        
        if client:
            queryset = queryset.filter(client=client)
        
        # Filter by date range
        if days:
            cutoff = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=cutoff)
        
        return queryset[:limit]
    
    @staticmethod
    def get_activity_stats(user, client=None):
        """Get activity statistics for dashboard display"""
        from datetime import timedelta
        from django.db.models import Count, Q
        
        queryset = ActivityLog.objects.filter(user=user)
        if client:
            queryset = queryset.filter(client=client)
        
        # Get counts by type for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_activities = queryset.filter(created_at__gte=thirty_days_ago)
        
        stats = {
            'total_30_days': recent_activities.count(),
            'by_type': dict(
                recent_activities.values('activity_type')
                .annotate(count=Count('id'))
                .values_list('activity_type', 'count')
            ),
            'today': queryset.filter(
                created_at__date=timezone.now().date()
            ).count(),
            'this_week': queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
        
        return stats