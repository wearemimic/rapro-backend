# core/views/workflow_views.py
"""
API views for workflow management in admin interface
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import logging

from ..decorators import admin_required
from ..services.workflow_service import workflow_engine, workflow_scheduler
from ..services.search_service import search_service, filter_service
from ..services.cache_service import CacheService

logger = logging.getLogger(__name__)


class WorkflowViewSet(viewsets.ViewSet):
    """
    ViewSet for managing automated workflows
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all available workflows"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        workflows = []
        for workflow_id, definition in workflow_engine.workflows.items():
            workflows.append({
                'id': workflow_id,
                'name': definition['name'],
                'description': definition['description'],
                'triggers': definition['triggers'],
                'step_count': len(definition['steps']),
                'is_scheduled': 'schedule' in definition,
                'schedule': definition.get('schedule'),
                'conditions': definition.get('conditions', {})
            })
        
        return Response(workflows)
    
    def retrieve(self, request, pk=None):
        """Get workflow details"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if pk not in workflow_engine.workflows:
            return Response(
                {'error': 'Workflow not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        definition = workflow_engine.workflows[pk]
        
        # Get execution statistics
        cache_key = f"workflow_stats:{pk}"
        stats = CacheService.get(cache_key, {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_duration': 0,
            'last_execution': None
        })
        
        return Response({
            'id': pk,
            'definition': definition,
            'statistics': stats
        })
    
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Manually trigger a workflow"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if pk not in workflow_engine.workflows:
            return Response(
                {'error': 'Workflow not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        context = request.data.get('context', {})
        context['triggered_by'] = request.user.id
        context['trigger_type'] = 'manual'
        
        try:
            instance_id = workflow_engine.trigger_workflow(
                pk,
                context,
                request.user.id
            )
            
            return Response({
                'instance_id': instance_id,
                'message': 'Workflow triggered successfully'
            })
            
        except Exception as e:
            logger.error(f"Failed to trigger workflow {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to trigger workflow', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """List active workflow instances"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_workflows = workflow_engine.list_active_workflows()
        return Response(active_workflows)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get workflow instance status"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance_id = request.query_params.get('instance_id')
        if not instance_id:
            return Response(
                {'error': 'instance_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        workflow_status = workflow_engine.get_workflow_status(instance_id)
        return Response(workflow_status)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get workflow analytics and performance metrics"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get workflow execution statistics
            analytics = self._generate_workflow_analytics()
            return Response(analytics)
            
        except Exception as e:
            logger.error(f"Failed to generate workflow analytics: {str(e)}")
            return Response(
                {'error': 'Failed to generate analytics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_workflow_analytics(self):
        """Generate workflow analytics data"""
        now = timezone.now()
        analytics = {
            'summary': {
                'total_workflows': len(workflow_engine.workflows),
                'active_instances': len(workflow_engine.active_workflows),
                'scheduled_workflows': sum(1 for w in workflow_engine.workflows.values() if 'schedule' in w)
            },
            'execution_stats': {},
            'performance_metrics': {}
        }
        
        # Get execution stats for each workflow
        for workflow_id in workflow_engine.workflows.keys():
            cache_key = f"workflow_stats:{workflow_id}"
            stats = CacheService.get(cache_key, {})
            analytics['execution_stats'][workflow_id] = stats
        
        return analytics


class SearchViewSet(viewsets.ViewSet):
    """
    ViewSet for global search functionality
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Perform global search"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        query = request.query_params.get('q', '')
        page = int(request.query_params.get('page', 1))
        per_page = min(int(request.query_params.get('per_page', 20)), 100)
        
        # Extract filters
        filters = {}
        for key, value in request.query_params.items():
            if key not in ['q', 'page', 'per_page'] and value:
                if key == 'types':
                    filters[key] = value.split(',')
                else:
                    filters[key] = value
        
        try:
            results = search_service.search(query, filters, page, per_page)
            return Response(results)
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        query = request.query_params.get('q', '')
        limit = min(int(request.query_params.get('limit', 10)), 20)
        
        try:
            suggestions = search_service.get_suggestions(query, limit)
            return Response(suggestions)
            
        except Exception as e:
            logger.error(f"Suggestions failed: {str(e)}")
            return Response([], status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """Get available filter options"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        model_name = request.query_params.get('model', 'users')
        
        try:
            options = filter_service.get_filter_options(model_name)
            
            # Add user list for user filter
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(is_staff=True).values('id', 'first_name', 'last_name')
            options['users'] = [
                {'id': user['id'], 'name': f"{user['first_name']} {user['last_name']}"}
                for user in users
            ]
            
            return Response(options)
            
        except Exception as e:
            logger.error(f"Failed to load filter options: {str(e)}")
            return Response({}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export search results"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        query = request.query_params.get('q', '')
        format_type = request.query_params.get('format', 'csv')
        
        # Extract filters
        filters = {}
        for key, value in request.query_params.items():
            if key not in ['q', 'format'] and value:
                if key == 'types':
                    filters[key] = value.split(',')
                else:
                    filters[key] = value
        
        try:
            # Get all results (no pagination for export)
            results = search_service.search(query, filters, page=1, per_page=1000)
            
            if format_type == 'csv':
                return self._export_csv(results)
            elif format_type == 'json':
                return self._export_json(results)
            else:
                return Response(
                    {'error': 'Unsupported format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return Response(
                {'error': 'Export failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _export_csv(self, results):
        """Export results as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="search-results-{timezone.now().strftime("%Y%m%d")}.csv"'
        
        if results['results']:
            writer = csv.writer(response)
            
            # Header
            writer.writerow(['Type', 'Title', 'Description', 'URL', 'Score', 'Created At'])
            
            # Data rows
            for result in results['results']:
                writer.writerow([
                    result['type'],
                    result['title'],
                    result['description'],
                    result['url'],
                    result['score'],
                    result['metadata'].get('created_at', '')
                ])
        
        return response
    
    def _export_json(self, results):
        """Export results as JSON"""
        from django.http import JsonResponse
        
        response = JsonResponse(results)
        response['Content-Disposition'] = f'attachment; filename="search-results-{timezone.now().strftime("%Y%m%d")}.json"'
        return response


class FilterPresetViewSet(viewsets.ViewSet):
    """
    ViewSet for managing search filter presets
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List saved filter presets for user"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        model_name = request.query_params.get('model', 'users')
        
        try:
            presets = filter_service.get_saved_filters(request.user.id, model_name)
            return Response(presets)
            
        except Exception as e:
            logger.error(f"Failed to load filter presets: {str(e)}")
            return Response([], status=status.HTTP_200_OK)
    
    def create(self, request):
        """Save a new filter preset"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        name = request.data.get('name')
        filters = request.data.get('filters', {})
        model_name = request.data.get('model', 'users')
        
        if not name:
            return Response(
                {'error': 'Preset name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            success = filter_service.save_filter_preset(
                request.user.id,
                model_name,
                name,
                filters
            )
            
            if success:
                return Response({'message': 'Filter preset saved successfully'})
            else:
                return Response(
                    {'error': 'Failed to save filter preset'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Failed to save filter preset: {str(e)}")
            return Response(
                {'error': 'Failed to save filter preset'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, pk=None):
        """Delete a filter preset"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        model_name = request.query_params.get('model', 'users')
        
        try:
            # Get current presets
            presets = filter_service.get_saved_filters(request.user.id, model_name)
            
            # Remove the specified preset
            updated_presets = [p for p in presets if p['name'] != pk]
            
            # Save updated presets
            cache_key = f"saved_filters:{request.user.id}:{model_name}"
            CacheService.set(cache_key, updated_presets, 'search_results')
            
            return Response({'message': 'Filter preset deleted successfully'})
            
        except Exception as e:
            logger.error(f"Failed to delete filter preset: {str(e)}")
            return Response(
                {'error': 'Failed to delete filter preset'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@admin_required
def workflow_dashboard(request):
    """Get workflow dashboard data"""
    try:
        now = timezone.now()
        
        # Active workflows summary
        active_count = len(workflow_engine.active_workflows)
        
        # Recent execution statistics
        recent_executions = []
        for instance_id, instance in workflow_engine.active_workflows.items():
            recent_executions.append({
                'instance_id': instance_id,
                'workflow_id': instance.workflow_id,
                'status': instance.status,
                'progress': (instance.current_step / len(instance.definition['steps'])) * 100,
                'started_at': instance.started_at,
                'error_count': instance.error_count
            })
        
        # Workflow performance metrics
        performance_metrics = {}
        for workflow_id in workflow_engine.workflows.keys():
            cache_key = f"workflow_stats:{workflow_id}"
            stats = CacheService.get(cache_key, {
                'total_executions': 0,
                'success_rate': 100.0,
                'avg_duration': 0,
                'last_execution': None
            })
            performance_metrics[workflow_id] = stats
        
        # System health indicators
        health_indicators = {
            'active_workflows': active_count,
            'total_workflows': len(workflow_engine.workflows),
            'scheduled_workflows': sum(1 for w in workflow_engine.workflows.values() if 'schedule' in w),
            'system_status': 'healthy' if active_count < 50 else 'busy'
        }
        
        data = {
            'active_workflows': active_count,
            'recent_executions': recent_executions[:10],  # Last 10 executions
            'performance_metrics': performance_metrics,
            'health_indicators': health_indicators,
            'last_updated': now.isoformat()
        }
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Failed to generate workflow dashboard: {str(e)}")
        return Response(
            {'error': 'Failed to generate dashboard data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )