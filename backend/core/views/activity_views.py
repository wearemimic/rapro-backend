"""
Activity Views for the unified activity log
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from ..models import ActivityLog
from ..serializers.activity_serializers import ActivityLogSerializer
from ..services.activity_service import ActivityService


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing activity logs
    Provides read-only access to activity history
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter activities to current user's data"""
        queryset = ActivityLog.objects.filter(user=self.request.user)
        
        # Filter by client if specified
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by activity type if specified
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            try:
                days = int(days)
                cutoff = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=cutoff)
            except (ValueError, TypeError):
                pass  # Ignore invalid days parameter
        
        # Search in description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(description__icontains=search)
        
        return queryset.select_related('user', 'client', 'lead')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get activity statistics for the current user"""
        client_id = request.query_params.get('client_id')
        client = None
        if client_id:
            from ..models import Client
            try:
                client = Client.objects.get(id=client_id, advisor=request.user)
            except Client.DoesNotExist:
                return Response(
                    {"error": "Client not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        stats = ActivityService.get_activity_stats(
            user=request.user,
            client=client
        )
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities with smart grouping"""
        client_id = request.query_params.get('client_id')
        days = int(request.query_params.get('days', 7))
        limit = int(request.query_params.get('limit', 50))
        
        activities = ActivityService.get_recent_activities(
            user=request.user,
            client_id=client_id,
            days=days,
            limit=limit
        )
        
        serializer = self.get_serializer(activities, many=True)
        
        # Group activities by date for better display
        from itertools import groupby
        from operator import attrgetter
        
        grouped_data = []
        for date, items in groupby(serializer.data, key=lambda x: x['created_at'][:10]):
            grouped_data.append({
                'date': date,
                'activities': list(items)
            })
        
        return Response({
            'grouped': grouped_data,
            'total': activities.count()
        })
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available activity types"""
        return Response({
            'types': [
                {'value': choice[0], 'label': choice[1]}
                for choice in ActivityLog.ACTIVITY_TYPES
            ]
        })