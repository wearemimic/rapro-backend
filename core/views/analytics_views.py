# core/views/analytics_views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import timedelta, datetime
import json
import csv
import io
import logging
import time

from ..models import (
    CustomReport, ReportSchedule, ReportExecution, PredictiveAnalyticsModel,
    UserChurnPrediction, CustomerLifetimeValue, ExecutiveDashboard, CustomUser
)

from ..serializers_main import (
    CustomReportSerializer, CustomReportListSerializer, ReportScheduleSerializer,
    ReportExecutionSerializer, PredictiveAnalyticsModelSerializer,
    UserChurnPredictionSerializer, CustomerLifetimeValueSerializer,
    ExecutiveDashboardSerializer, AnalyticsSummarySerializer
)

from ..decorators import admin_required
from ..services.cache_service import CacheService, cached, PerformanceCacheService

logger = logging.getLogger(__name__)


class CustomReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom reports
    """
    serializer_class = CustomReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['report_type', 'is_public', 'created_by']
    search_fields = ['report_name', 'description']
    ordering_fields = ['created_at', 'view_count', 'last_viewed']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomReportListSerializer
        return CustomReportSerializer

    def get_queryset(self):
        """Filter reports based on user permissions"""
        user = self.request.user
        queryset = CustomReport.objects.all()
        
        if not user.is_staff:
            # Non-staff can only see public reports or reports they're allowed to view
            queryset = queryset.filter(
                Q(is_public=True) |
                Q(created_by=user) |
                Q(allowed_users=user)
            ).distinct()
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a report and return results"""
        report = self.get_object()
        
        try:
            # Create execution record
            execution = ReportExecution.objects.create(
                report=report,
                executed_by=request.user,
                status='running',
                execution_params=request.data.get('params', {})
            )
            
            # Update view count
            report.view_count = F('view_count') + 1
            report.last_viewed = timezone.now()
            report.save(update_fields=['view_count', 'last_viewed'])
            
            # Execute the report (this would be implemented with actual query logic)
            results = self._execute_report_query(report, request.data.get('params', {}))
            
            # Update execution record
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
            execution.result_count = len(results.get('data', []))
            execution.save()
            
            return Response({
                'execution_id': execution.id,
                'results': results,
                'metadata': {
                    'execution_time': execution.execution_time,
                    'result_count': execution.result_count
                }
            })
            
        except Exception as e:
            logger.error(f"Report execution failed: {str(e)}")
            if 'execution' in locals():
                execution.status = 'failed'
                execution.error_message = str(e)
                execution.completed_at = timezone.now()
                execution.save()
            
            return Response(
                {'error': 'Report execution failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export report results in various formats"""
        report = self.get_object()
        export_format = request.data.get('format', 'csv')
        
        try:
            # Execute report to get data
            results = self._execute_report_query(report, request.data.get('params', {}))
            data = results.get('data', [])
            
            if export_format == 'csv':
                return self._export_csv(data, report.report_name)
            elif export_format == 'json':
                return self._export_json(results, report.report_name)
            else:
                return Response(
                    {'error': 'Unsupported export format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Report export failed: {str(e)}")
            return Response(
                {'error': 'Export failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a copy of the report"""
        original_report = self.get_object()
        
        # Create a copy
        new_report = CustomReport.objects.create(
            report_name=f"{original_report.report_name} (Copy)",
            description=original_report.description,
            report_type=original_report.report_type,
            data_sources=original_report.data_sources,
            filters=original_report.filters,
            grouping=original_report.grouping,
            aggregations=original_report.aggregations,
            sorting=original_report.sorting,
            chart_type=original_report.chart_type,
            chart_config=original_report.chart_config,
            created_by=request.user
        )
        
        serializer = self.get_serializer(new_report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _execute_report_query(self, report, params):
        """
        Execute the actual report query based on configuration
        This is a simplified implementation - in production you'd have
        a proper query engine
        """
        # Mock data for demonstration
        return {
            'data': [
                {'name': 'Sample Data', 'value': 100, 'date': '2024-01-01'},
                {'name': 'More Data', 'value': 200, 'date': '2024-01-02'},
            ],
            'metadata': {
                'total_rows': 2,
                'columns': ['name', 'value', 'date']
            }
        }

    def _export_csv(self, data, filename):
        """Export data as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return response

    def _export_json(self, results, filename):
        """Export data as JSON"""
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        response.write(json.dumps(results, indent=2))
        return response


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing report schedules
    """
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'frequency', 'report']
    search_fields = ['schedule_name', 'report__report_name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter schedules based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return ReportSchedule.objects.all()
        else:
            # Users can only see schedules for reports they have access to
            return ReportSchedule.objects.filter(
                Q(created_by=user) |
                Q(report__created_by=user) |
                Q(report__allowed_users=user) |
                Q(report__is_public=True)
            ).distinct()

    def perform_create(self, serializer):
        # Calculate next run time based on frequency
        schedule = serializer.save(created_by=self.request.user)
        schedule.next_run = self._calculate_next_run(schedule)
        schedule.save()

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause a schedule"""
        schedule = self.get_object()
        schedule.status = 'paused'
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused schedule"""
        schedule = self.get_object()
        schedule.status = 'active'
        schedule.next_run = self._calculate_next_run(schedule)
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)

    def _calculate_next_run(self, schedule):
        """Calculate the next run time for a schedule"""
        now = timezone.now()
        
        if schedule.frequency == 'daily':
            next_run = now.replace(
                hour=schedule.time_of_day.hour,
                minute=schedule.time_of_day.minute,
                second=0,
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
                
        elif schedule.frequency == 'weekly':
            days_ahead = schedule.day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=schedule.time_of_day.hour,
                minute=schedule.time_of_day.minute,
                second=0,
                microsecond=0
            )
            
        elif schedule.frequency == 'monthly':
            next_run = now.replace(
                day=schedule.day_of_month,
                hour=schedule.time_of_day.hour,
                minute=schedule.time_of_day.minute,
                second=0,
                microsecond=0
            )
            if next_run <= now:
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
                    
        else:
            next_run = now + timedelta(days=1)
        
        return next_run


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for report execution history
    """
    serializer_class = ReportExecutionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'report', 'executed_by']
    ordering = ['-started_at']

    def get_queryset(self):
        """Filter executions based on user permissions"""
        user = self.request.user
        if user.is_staff:
            return ReportExecution.objects.all()
        else:
            return ReportExecution.objects.filter(
                Q(executed_by=user) |
                Q(report__created_by=user) |
                Q(report__allowed_users=user) |
                Q(report__is_public=True)
            ).distinct()


class ExecutiveDashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing executive dashboards
    """
    serializer_class = ExecutiveDashboardSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_default', 'created_by']
    search_fields = ['dashboard_name', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter dashboards based on user permissions"""
        user = self.request.user
        if not user.is_staff:
            return ExecutiveDashboard.objects.filter(
                Q(created_by=user) |
                Q(visible_to_roles__overlap=[user.role]) if hasattr(user, 'role') else Q(id__isnull=True)
            ).distinct()
        return ExecutiveDashboard.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this dashboard as the default for the user"""
        dashboard = self.get_object()
        
        # Remove default from other dashboards
        ExecutiveDashboard.objects.filter(
            created_by=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set this as default
        dashboard.is_default = True
        dashboard.save()
        
        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get dashboard data for widgets"""
        dashboard = self.get_object()
        
        # Update view count
        dashboard.view_count = F('view_count') + 1
        dashboard.last_viewed = timezone.now()
        dashboard.save(update_fields=['view_count', 'last_viewed'])
        
        # Generate widget data based on configuration
        widget_data = {}
        
        for widget in dashboard.widgets:
            widget_id = widget.get('id')
            widget_type = widget.get('type')
            
            try:
                if widget_type == 'user_metrics':
                    widget_data[widget_id] = self._get_user_metrics()
                elif widget_type == 'revenue_metrics':
                    widget_data[widget_id] = self._get_revenue_metrics()
                elif widget_type == 'engagement_metrics':
                    widget_data[widget_id] = self._get_engagement_metrics()
                elif widget_type == 'churn_metrics':
                    widget_data[widget_id] = self._get_churn_metrics()
                else:
                    widget_data[widget_id] = {'error': 'Unknown widget type'}
                    
            except Exception as e:
                logger.error(f"Error generating widget data for {widget_id}: {str(e)}")
                widget_data[widget_id] = {'error': str(e)}
        
        return Response({
            'dashboard_id': dashboard.id,
            'widget_data': widget_data,
            'last_updated': timezone.now()
        })

    @cached('user_metrics')
    def _get_user_metrics(self):
        """Get user-related metrics with caching"""
        start_time = time.time()
        
        try:
            now = timezone.now()
            thirty_days_ago = now - timedelta(days=30)
            
            total_users = CustomUser.objects.count()
            new_users_30d = CustomUser.objects.filter(date_joined__gte=thirty_days_ago).count()
            active_users_30d = CustomUser.objects.filter(last_login__gte=thirty_days_ago).count()
            
            result = {
                'total_users': total_users,
                'new_users_30d': new_users_30d,
                'active_users_30d': active_users_30d,
                'growth_rate': (new_users_30d / max(total_users - new_users_30d, 1)) * 100,
                'last_updated': timezone.now().isoformat()
            }
            
            # Track performance
            execution_time = time.time() - start_time
            PerformanceCacheService.cache_query_performance('user_metrics', execution_time, total_users)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating user metrics: {str(e)}")
            raise

    @cached('revenue_metrics')
    def _get_revenue_metrics(self):
        """Get revenue-related metrics with caching"""
        start_time = time.time()
        
        try:
            # Mock data - replace with actual revenue calculations from Stripe
            result = {
                'total_revenue': 50000.00,
                'revenue_30d': 15000.00,
                'avg_revenue_per_user': 125.00,
                'revenue_growth': 12.5,
                'last_updated': timezone.now().isoformat()
            }
            
            # Track performance
            execution_time = time.time() - start_time
            PerformanceCacheService.cache_query_performance('revenue_metrics', execution_time, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating revenue metrics: {str(e)}")
            raise

    @cached('engagement_metrics')
    def _get_engagement_metrics(self):
        """Get engagement-related metrics with caching"""
        start_time = time.time()
        
        try:
            # Mock data - replace with actual engagement calculations
            result = {
                'avg_session_duration': '00:23:45',
                'page_views_30d': 125000,
                'bounce_rate': 35.2,
                'return_visitor_rate': 68.4,
                'last_updated': timezone.now().isoformat()
            }
            
            # Track performance
            execution_time = time.time() - start_time
            PerformanceCacheService.cache_query_performance('engagement_metrics', execution_time, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating engagement metrics: {str(e)}")
            raise

    @cached('churn_metrics')
    def _get_churn_metrics(self):
        """Get churn-related metrics with caching"""
        start_time = time.time()
        
        try:
            high_risk_users = UserChurnPrediction.objects.filter(
                risk_level__in=['high', 'critical'],
                predicted_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            result = {
                'churn_rate_30d': 5.2,
                'high_risk_users': high_risk_users,
                'retention_rate': 94.8,
                'avg_customer_lifetime': '18 months',
                'last_updated': timezone.now().isoformat()
            }
            
            # Track performance
            execution_time = time.time() - start_time
            PerformanceCacheService.cache_query_performance('churn_metrics', execution_time, high_risk_users)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating churn metrics: {str(e)}")
            raise


# Analytics summary views for dashboards
@admin_required
@cached('analytics_summary')
def analytics_summary(request):
    """Get analytics summary for dashboard with caching"""
    start_time = time.time()
    
    try:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # User metrics
        total_users = CustomUser.objects.count()
        active_users_30d = CustomUser.objects.filter(last_login__gte=thirty_days_ago).count()
        new_users_30d = CustomUser.objects.filter(date_joined__gte=thirty_days_ago).count()
        
        # Churn metrics
        high_risk_users = UserChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical']
        ).count()
        
        high_value_users = CustomerLifetimeValue.objects.filter(
            value_segment='high_value'
        ).count()
        
        # Report metrics
        reports_executed = ReportExecution.objects.filter(
            started_at__gte=thirty_days_ago,
            status='completed'
        ).count()
        
        scheduled_reports_active = ReportSchedule.objects.filter(
            status='active'
        ).count()
        
        data = {
            'total_users': total_users,
            'active_users_30d': active_users_30d,
            'new_users_30d': new_users_30d,
            'churn_rate_30d': 5.2,  # Mock data
            'total_revenue': 50000.00,  # Mock data
            'revenue_30d': 15000.00,  # Mock data
            'avg_revenue_per_user': 125.00,  # Mock data
            'reports_executed': reports_executed,
            'scheduled_reports_active': scheduled_reports_active,
            'high_risk_users': high_risk_users,
            'high_value_users': high_value_users,
            'last_updated': timezone.now().isoformat()
        }
        
        # Track performance
        execution_time = time.time() - start_time
        PerformanceCacheService.cache_query_performance('analytics_summary', execution_time, total_users)
        
        serializer = AnalyticsSummarySerializer(data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error generating analytics summary: {str(e)}")
        return Response(
            {'error': 'Failed to generate analytics summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )