# core/views/communication_views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from datetime import timedelta
import logging

from ..models import (
    BroadcastMessage, BroadcastDelivery, EmailCampaign, EmailCampaignDelivery,
    InAppNotification, MaintenanceMode, UserFeedback, FeedbackResponse, CustomUser
)

from ..serializers_main import (
    BroadcastMessageSerializer, BroadcastDeliverySerializer, EmailCampaignSerializer,
    EmailCampaignListSerializer, EmailCampaignDeliverySerializer,
    InAppNotificationSerializer, MaintenanceModeSerializer, UserFeedbackSerializer,
    UserFeedbackListSerializer, FeedbackResponseSerializer, CommunicationSummarySerializer
)

from ..decorators import admin_required

logger = logging.getLogger(__name__)
User = get_user_model()


class BroadcastMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing broadcast messages
    """
    serializer_class = BroadcastMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'message_type', 'delivery_method']
    search_fields = ['title', 'message']
    ordering = ['-created_at']

    def get_queryset(self):
        """Only staff can manage broadcasts"""
        if not self.request.user.is_staff:
            return BroadcastMessage.objects.none()
        return BroadcastMessage.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Send broadcast immediately"""
        broadcast = self.get_object()
        
        if broadcast.status != 'draft':
            return Response(
                {'error': 'Only draft broadcasts can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update broadcast status
            broadcast.status = 'sending'
            broadcast.sent_at = timezone.now()
            broadcast.save()
            
            # Get target users
            target_users = self._get_target_users(broadcast)
            broadcast.total_recipients = len(target_users)
            broadcast.save()
            
            # Create delivery records
            deliveries = []
            for user in target_users:
                delivery = BroadcastDelivery(
                    broadcast=broadcast,
                    user=user,
                    delivery_method=broadcast.delivery_method,
                    status='pending'
                )
                deliveries.append(delivery)
            
            BroadcastDelivery.objects.bulk_create(deliveries)
            
            # Process deliveries (this would typically be done async with Celery)
            self._process_broadcast_deliveries(broadcast)
            
            # Update status
            broadcast.status = 'sent'
            broadcast.save()
            
            serializer = self.get_serializer(broadcast)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error sending broadcast {pk}: {str(e)}")
            broadcast.status = 'draft'
            broadcast.save()
            return Response(
                {'error': 'Failed to send broadcast', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule broadcast for later sending"""
        broadcast = self.get_object()
        scheduled_time = request.data.get('scheduled_send_time')
        
        if not scheduled_time:
            return Response(
                {'error': 'scheduled_send_time is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        broadcast.scheduled_send_time = scheduled_time
        broadcast.status = 'scheduled'
        broadcast.send_immediately = False
        broadcast.save()
        
        serializer = self.get_serializer(broadcast)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def preview_recipients(self, request, pk=None):
        """Preview who will receive this broadcast"""
        broadcast = self.get_object()
        target_users = self._get_target_users(broadcast)
        
        return Response({
            'total_recipients': len(target_users),
            'recipients': [
                {
                    'id': user.id,
                    'name': user.get_full_name() or user.email,
                    'email': user.email
                }
                for user in target_users[:50]  # Limit preview to 50 users
            ],
            'showing_first_50': len(target_users) > 50
        })

    def _get_target_users(self, broadcast):
        """Get list of users who should receive this broadcast"""
        if broadcast.target_all_users:
            return list(User.objects.filter(is_active=True))
        
        users = set()
        
        # Add specific users
        users.update(broadcast.specific_users.all())
        
        # Add users by role
        if broadcast.target_roles:
            role_users = User.objects.filter(
                is_active=True,
                # Add role filtering logic here based on your user model
            )
            users.update(role_users)
        
        # Add users by segments (implement segmentation logic)
        if broadcast.target_user_segments:
            segment_users = self._get_users_by_segments(broadcast.target_user_segments)
            users.update(segment_users)
        
        return list(users)

    def _get_users_by_segments(self, segments):
        """Get users based on segmentation rules"""
        # Implement complex segmentation logic here
        # This is a simplified example
        queryset = User.objects.filter(is_active=True)
        
        # Example segmentation rules
        if 'new_users' in segments:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(date_joined__gte=thirty_days_ago)
        
        if 'active_users' in segments:
            seven_days_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(last_login__gte=seven_days_ago)
        
        return queryset

    def _process_broadcast_deliveries(self, broadcast):
        """Process broadcast deliveries (simplified implementation)"""
        deliveries = BroadcastDelivery.objects.filter(broadcast=broadcast, status='pending')
        
        delivered_count = 0
        for delivery in deliveries:
            try:
                if broadcast.delivery_method in ['email', 'both']:
                    # Send email (implement actual email sending)
                    pass
                
                if broadcast.delivery_method in ['in_app', 'both']:
                    # Create in-app notification
                    InAppNotification.objects.create(
                        user=delivery.user,
                        title=broadcast.title,
                        message=broadcast.message,
                        notification_type='system',
                        has_action=broadcast.has_action_button,
                        action_text=broadcast.action_button_text,
                        action_url=broadcast.action_button_url,
                        source_broadcast=broadcast,
                        created_by=broadcast.created_by
                    )
                
                delivery.status = 'delivered'
                delivery.sent_at = timezone.now()
                delivery.delivered_at = timezone.now()
                delivery.save()
                delivered_count += 1
                
            except Exception as e:
                logger.error(f"Error delivering broadcast to user {delivery.user.id}: {str(e)}")
                delivery.status = 'failed'
                delivery.error_message = str(e)
                delivery.save()
        
        # Update broadcast statistics
        broadcast.delivered_count = delivered_count
        broadcast.save()


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email campaigns
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'campaign_type']
    search_fields = ['campaign_name', 'subject_line']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailCampaignListSerializer
        return EmailCampaignSerializer

    def get_queryset(self):
        """Only staff can manage email campaigns"""
        if not self.request.user.is_staff:
            return EmailCampaign.objects.none()
        return EmailCampaign.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send email campaign"""
        campaign = self.get_object()
        
        if campaign.status != 'draft':
            return Response(
                {'error': 'Only draft campaigns can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update campaign status
            campaign.status = 'sending'
            campaign.sent_at = timezone.now()
            campaign.save()
            
            # Get target users (implement segmentation logic)
            target_users = self._get_campaign_targets(campaign)
            campaign.total_sent = len(target_users)
            campaign.save()
            
            # Create delivery records and send emails
            self._process_campaign_deliveries(campaign, target_users)
            
            # Update status and calculate metrics
            campaign.status = 'sent'
            campaign.calculate_metrics()
            
            serializer = self.get_serializer(campaign)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error sending campaign {pk}: {str(e)}")
            campaign.status = 'draft'
            campaign.save()
            return Response(
                {'error': 'Failed to send campaign', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get detailed campaign analytics"""
        campaign = self.get_object()
        
        # Get delivery analytics
        deliveries = EmailCampaignDelivery.objects.filter(campaign=campaign)
        
        analytics_data = {
            'overview': {
                'total_sent': campaign.total_sent,
                'delivered': campaign.delivered_count,
                'opened': campaign.opened_count,
                'clicked': campaign.clicked_count,
                'bounced': campaign.bounced_count,
                'unsubscribed': campaign.unsubscribed_count
            },
            'rates': {
                'delivery_rate': (campaign.delivered_count / max(campaign.total_sent, 1)) * 100,
                'open_rate': campaign.open_rate or 0,
                'click_rate': campaign.click_rate or 0,
                'bounce_rate': (campaign.bounced_count / max(campaign.total_sent, 1)) * 100,
                'unsubscribe_rate': campaign.unsubscribe_rate or 0
            },
            'engagement_over_time': self._get_engagement_timeline(campaign),
            'device_breakdown': self._get_device_breakdown(deliveries),
            'link_clicks': self._get_link_clicks(deliveries)
        }
        
        return Response(analytics_data)

    def _get_campaign_targets(self, campaign):
        """Get target users for campaign based on segments"""
        # Implement segmentation logic similar to broadcasts
        return User.objects.filter(is_active=True)[:100]  # Simplified

    def _process_campaign_deliveries(self, campaign, target_users):
        """Process campaign deliveries"""
        for user in target_users:
            EmailCampaignDelivery.objects.create(
                campaign=campaign,
                user=user,
                email_address=user.email,
                subject_line=campaign.subject_line,
                status='sent',
                sent_at=timezone.now()
            )
        
        # Update delivered count
        campaign.delivered_count = len(target_users)
        campaign.save()

    def _get_engagement_timeline(self, campaign):
        """Get engagement timeline data"""
        # Mock data - implement actual timeline logic
        return [
            {'hour': 1, 'opens': 45, 'clicks': 12},
            {'hour': 2, 'opens': 67, 'clicks': 18},
            # ... more data points
        ]

    def _get_device_breakdown(self, deliveries):
        """Get device breakdown data"""
        # Mock data - implement actual device detection
        return {
            'desktop': 65,
            'mobile': 30,
            'tablet': 5
        }

    def _get_link_clicks(self, deliveries):
        """Get link click data"""
        # Mock data - implement actual link tracking
        return [
            {'url': 'https://example.com/link1', 'clicks': 25},
            {'url': 'https://example.com/link2', 'clicks': 18},
        ]


class InAppNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing in-app notifications
    """
    serializer_class = InAppNotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['notification_type', 'priority', 'is_read', 'is_dismissed']
    ordering = ['-created_at']

    def get_queryset(self):
        """Users see their own notifications, staff can see all"""
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all_users'):
            return InAppNotification.objects.all()
        return InAppNotification.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss notification"""
        notification = self.get_object()
        notification.dismiss()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for current user"""
        updated = InAppNotification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({'marked_read': updated})


class MaintenanceModeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing maintenance mode
    """
    serializer_class = MaintenanceModeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'maintenance_type', 'is_active']
    ordering = ['-scheduled_start']

    def get_queryset(self):
        """Only staff can manage maintenance mode"""
        if not self.request.user.is_staff:
            # Regular users can only see active maintenance
            return MaintenanceMode.objects.filter(is_active=True)
        return MaintenanceMode.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate maintenance mode"""
        maintenance = self.get_object()
        
        # Deactivate any other active maintenance
        MaintenanceMode.objects.filter(is_active=True).update(is_active=False)
        
        # Activate this maintenance
        maintenance.activate()
        
        # Send notifications to users if not already sent
        if not maintenance.notification_sent:
            self._notify_users_maintenance_active(maintenance)
            maintenance.notification_sent = True
            maintenance.save()
        
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate maintenance mode"""
        maintenance = self.get_object()
        maintenance.deactivate()
        
        # Notify users that maintenance is complete
        self._notify_users_maintenance_complete(maintenance)
        
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update maintenance progress"""
        maintenance = self.get_object()
        
        progress_percentage = request.data.get('progress_percentage')
        progress_message = request.data.get('progress_message')
        estimated_completion = request.data.get('estimated_completion')
        
        if progress_percentage is not None:
            maintenance.progress_percentage = progress_percentage
        if progress_message:
            maintenance.progress_message = progress_message
        if estimated_completion:
            maintenance.estimated_completion = estimated_completion
        
        maintenance.save()
        
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

    def _notify_users_maintenance_active(self, maintenance):
        """Send notifications about active maintenance"""
        # Create broadcast message for maintenance
        BroadcastMessage.objects.create(
            title=f"Maintenance: {maintenance.title}",
            message=maintenance.public_message,
            message_type='maintenance',
            delivery_method='both',
            target_all_users=True,
            send_immediately=True,
            created_by=maintenance.created_by
        )

    def _notify_users_maintenance_complete(self, maintenance):
        """Send notifications about maintenance completion"""
        BroadcastMessage.objects.create(
            title="Maintenance Complete",
            message=f"Scheduled maintenance '{maintenance.title}' has been completed. All services are now fully operational.",
            message_type='announcement',
            delivery_method='both',
            target_all_users=True,
            send_immediately=True,
            created_by=maintenance.created_by
        )


class UserFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user feedback
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['feedback_type', 'priority', 'status', 'assigned_to']
    search_fields = ['title', 'description', 'email']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserFeedbackListSerializer
        return UserFeedbackSerializer

    def get_queryset(self):
        """Users see their own feedback, staff see all"""
        user = self.request.user
        if user.is_staff:
            return UserFeedback.objects.all()
        return UserFeedback.objects.filter(user=user)

    def perform_create(self, serializer):
        # Auto-assign user if authenticated
        serializer.save(
            user=self.request.user if self.request.user.is_authenticated else None,
            email=self.request.user.email if self.request.user.is_authenticated else serializer.validated_data.get('email')
        )

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign feedback to staff member"""
        feedback = self.get_object()
        staff_user_id = request.data.get('staff_user_id')
        
        if not staff_user_id:
            return Response(
                {'error': 'staff_user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            staff_user = User.objects.get(id=staff_user_id, is_staff=True)
            feedback.assign_to_staff(staff_user)
            
            serializer = self.get_serializer(feedback)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Staff user not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark feedback as resolved"""
        feedback = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        feedback.mark_resolved(resolution_notes)
        
        # Create response if message provided
        response_message = request.data.get('response_message')
        if response_message:
            FeedbackResponse.objects.create(
                feedback=feedback,
                staff_user=request.user,
                message=response_message,
                is_internal_note=False,
                visible_to_user=True
            )
        
        serializer = self.get_serializer(feedback)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """Get all responses for this feedback"""
        feedback = self.get_object()
        
        # Users can only see visible responses, staff can see all
        if request.user.is_staff:
            responses = feedback.responses.all()
        else:
            responses = feedback.responses.filter(visible_to_user=True)
        
        serializer = FeedbackResponseSerializer(responses, many=True)
        return Response(serializer.data)


class FeedbackResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing feedback responses
    """
    serializer_class = FeedbackResponseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['feedback', 'is_internal_note', 'visible_to_user']
    ordering = ['created_at']

    def get_queryset(self):
        """Filter responses based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return FeedbackResponse.objects.all()
        else:
            # Users can only see responses to their own feedback that are visible
            return FeedbackResponse.objects.filter(
                feedback__user=user,
                visible_to_user=True
            )

    def perform_create(self, serializer):
        serializer.save(staff_user=self.request.user)


# Communication summary view for dashboard
@admin_required
def communication_summary(request):
    """Get communication summary for dashboard"""
    try:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Broadcast metrics
        broadcasts_sent = BroadcastMessage.objects.filter(
            status='sent',
            sent_at__gte=thirty_days_ago
        ).count()
        
        broadcasts_pending = BroadcastMessage.objects.filter(
            status__in=['scheduled', 'draft']
        ).count()
        
        # Email campaign metrics
        campaigns_sent = EmailCampaign.objects.filter(
            status='sent',
            sent_at__gte=thirty_days_ago
        ).count()
        
        campaigns_pending = EmailCampaign.objects.filter(
            status__in=['scheduled', 'draft']
        ).count()
        
        # Notification metrics
        notifications_unread = InAppNotification.objects.filter(
            is_read=False,
            created_at__gte=thirty_days_ago
        ).count()
        
        # Feedback metrics
        feedback_open = UserFeedback.objects.filter(
            status__in=['open', 'in_review', 'in_progress']
        ).count()
        
        feedback_pending_response = UserFeedback.objects.filter(
            status='in_review',
            responses__isnull=True
        ).count()
        
        # Maintenance metrics
        maintenance_scheduled = MaintenanceMode.objects.filter(
            status='planned',
            scheduled_start__gte=now
        ).count()
        
        maintenance_active = MaintenanceMode.objects.filter(
            is_active=True
        ).count()
        
        data = {
            'broadcasts_sent': broadcasts_sent,
            'broadcasts_pending': broadcasts_pending,
            'broadcast_avg_open_rate': 65.2,  # Mock data
            'campaigns_sent': campaigns_sent,
            'campaigns_pending': campaigns_pending,
            'campaign_avg_open_rate': 23.5,  # Mock data
            'campaign_avg_click_rate': 3.2,  # Mock data
            'notifications_unread': notifications_unread,
            'feedback_open': feedback_open,
            'feedback_pending_response': feedback_pending_response,
            'avg_response_time_hours': 4.5,  # Mock data
            'maintenance_scheduled': maintenance_scheduled,
            'maintenance_active': maintenance_active
        }
        
        serializer = CommunicationSummarySerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating communication summary: {str(e)}")
        return Response(
            {'error': 'Failed to generate communication summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )