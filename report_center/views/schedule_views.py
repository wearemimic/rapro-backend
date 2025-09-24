"""
API views for report scheduling functionality
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import logging

from ..services.report_scheduler_service import ReportSchedulerService
from ..models import ReportSchedule, ReportScheduleExecution

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_schedule(request):
    """
    Create a new report schedule
    
    POST /api/report-center/schedules/
    {
        "name": "Weekly Client Reports",
        "description": "Weekly reports for all active clients",
        "template_id": 1,
        "client_id": null,  // null for bulk, specific ID for single client
        "scenario_id": null,  // optional specific scenario
        "client_filter": {  // for bulk scheduling
            "tags": ["active"],
            "has_scenarios": true
        },
        "frequency": "weekly",  // daily, weekly, monthly, quarterly, yearly, custom
        "frequency_config": {
            "day_of_week": 1  // 0=Monday, 1=Tuesday, etc.
        },
        "scheduled_time": "09:00:00",
        "timezone": "America/New_York",
        "format": "pdf",  // pdf, excel, powerpoint, both
        "generation_options": {
            "page_size": "letter",
            "orientation": "portrait"
        },
        "auto_email": true,
        "email_recipients": ["client@example.com", "advisor@example.com"],
        "email_subject_template": "Weekly Report for {{ client.first_name }}",
        "email_body_template": "Please find your weekly report attached.",
        "end_date": null,  // optional end date
        "max_runs": null   // optional max number of runs
    }
    """
    try:
        user = request.user
        schedule_data = request.data
        
        # Validate required fields
        required_fields = ['name', 'template_id', 'frequency', 'scheduled_time']
        for field in required_fields:
            if field not in schedule_data:
                return Response(
                    {'error': f'{field} is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate frequency configuration
        if schedule_data['frequency'] == 'custom' and not schedule_data.get('frequency_config'):
            return Response(
                {'error': 'frequency_config is required for custom frequency'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate target configuration
        if not any([
            schedule_data.get('client_id'),
            schedule_data.get('scenario_id'),
            schedule_data.get('client_filter')
        ]):
            return Response(
                {'error': 'Must specify client_id, scenario_id, or client_filter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create schedule
        scheduler_service = ReportSchedulerService()
        schedule = scheduler_service.create_schedule(user.id, schedule_data)
        
        return Response({
            'id': schedule.id,
            'name': schedule.name,
            'status': schedule.status,
            'frequency': schedule.frequency,
            'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
            'message': 'Report schedule created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating report schedule: {str(e)}")
        return Response(
            {'error': 'Failed to create report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_schedules(request):
    """
    List report schedules for the current user
    
    GET /api/report-center/schedules/
    """
    try:
        user = request.user
        
        # Get query parameters
        status_filter = request.GET.get('status')
        frequency_filter = request.GET.get('frequency')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Build queryset
        queryset = ReportSchedule.objects.filter(user=user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if frequency_filter:
            queryset = queryset.filter(frequency=frequency_filter)
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        schedules = queryset[start_idx:end_idx]
        
        # Serialize schedule data
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'id': schedule.id,
                'name': schedule.name,
                'description': schedule.description,
                'status': schedule.status,
                'template': {
                    'id': schedule.template.id,
                    'name': schedule.template.name
                },
                'client': {
                    'id': schedule.client.id,
                    'name': f"{schedule.client.first_name} {schedule.client.last_name}"
                } if schedule.client else None,
                'scenario': {
                    'id': schedule.scenario.id,
                    'name': schedule.scenario.name
                } if schedule.scenario else None,
                'frequency': schedule.frequency,
                'frequency_config': schedule.frequency_config,
                'scheduled_time': schedule.scheduled_time.strftime('%H:%M:%S'),
                'timezone': schedule.timezone,
                'format': schedule.format,
                'auto_email': schedule.auto_email,
                'email_recipients': schedule.email_recipients,
                'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
                'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
                'run_count': schedule.run_count,
                'success_count': schedule.success_count,
                'failure_count': schedule.failure_count,
                'success_rate': schedule.success_rate,
                'is_active': schedule.is_active,
                'created_at': schedule.created_at.isoformat(),
                'updated_at': schedule.updated_at.isoformat()
            })
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        return Response({
            'schedules': schedule_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_previous': has_previous
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing report schedules: {str(e)}")
        return Response(
            {'error': 'Failed to list report schedules'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule(request, schedule_id):
    """
    Get detailed information about a specific schedule
    
    GET /api/report-center/schedules/{schedule_id}/
    """
    try:
        schedule = get_object_or_404(
            ReportSchedule, 
            id=schedule_id, 
            user=request.user
        )
        
        # Get recent executions
        recent_executions = schedule.executions.order_by('-scheduled_for')[:10]
        execution_data = []
        for execution in recent_executions:
            execution_data.append({
                'id': execution.id,
                'status': execution.status,
                'scheduled_for': execution.scheduled_for.isoformat(),
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'reports_generated': execution.reports_generated,
                'emails_sent': execution.emails_sent,
                'execution_time_seconds': execution.execution_time_seconds,
                'error_message': execution.error_message,
                'duration': execution.duration
            })
        
        schedule_data = {
            'id': schedule.id,
            'name': schedule.name,
            'description': schedule.description,
            'status': schedule.status,
            'template': {
                'id': schedule.template.id,
                'name': schedule.template.name,
                'description': schedule.template.description
            },
            'client': {
                'id': schedule.client.id,
                'name': f"{schedule.client.first_name} {schedule.client.last_name}",
                'email': schedule.client.email
            } if schedule.client else None,
            'scenario': {
                'id': schedule.scenario.id,
                'name': schedule.scenario.name
            } if schedule.scenario else None,
            'client_filter': schedule.client_filter,
            'frequency': schedule.frequency,
            'frequency_config': schedule.frequency_config,
            'scheduled_time': schedule.scheduled_time.strftime('%H:%M:%S'),
            'timezone': schedule.timezone,
            'format': schedule.format,
            'generation_options': schedule.generation_options,
            'auto_email': schedule.auto_email,
            'email_recipients': schedule.email_recipients,
            'email_subject_template': schedule.email_subject_template,
            'email_body_template': schedule.email_body_template,
            'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
            'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
            'run_count': schedule.run_count,
            'success_count': schedule.success_count,
            'failure_count': schedule.failure_count,
            'success_rate': schedule.success_rate,
            'end_date': schedule.end_date.isoformat() if schedule.end_date else None,
            'max_runs': schedule.max_runs,
            'is_active': schedule.is_active,
            'created_at': schedule.created_at.isoformat(),
            'updated_at': schedule.updated_at.isoformat(),
            'recent_executions': execution_data
        }
        
        return Response(schedule_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting report schedule: {str(e)}")
        return Response(
            {'error': 'Failed to get report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_schedule(request, schedule_id):
    """
    Update a report schedule
    
    PUT /api/report-center/schedules/{schedule_id}/
    """
    try:
        scheduler_service = ReportSchedulerService()
        schedule = scheduler_service.update_schedule(
            schedule_id,
            request.user.id,
            request.data
        )
        
        return Response({
            'id': schedule.id,
            'name': schedule.name,
            'status': schedule.status,
            'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
            'message': 'Report schedule updated successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error updating report schedule: {str(e)}")
        return Response(
            {'error': 'Failed to update report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_schedule(request, schedule_id):
    """
    Delete a report schedule
    
    DELETE /api/report-center/schedules/{schedule_id}/
    """
    try:
        scheduler_service = ReportSchedulerService()
        scheduler_service.delete_schedule(schedule_id, request.user.id)
        
        return Response({
            'message': 'Report schedule deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting report schedule: {str(e)}")
        return Response(
            {'error': 'Failed to delete report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_schedule(request, schedule_id):
    """
    Pause a report schedule
    
    POST /api/report-center/schedules/{schedule_id}/pause/
    """
    try:
        scheduler_service = ReportSchedulerService()
        schedule = scheduler_service.pause_schedule(schedule_id, request.user.id)
        
        return Response({
            'id': schedule.id,
            'status': schedule.status,
            'message': 'Report schedule paused successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error pausing report schedule: {str(e)}")
        return Response(
            {'error': 'Failed to pause report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_schedule(request, schedule_id):
    """
    Resume a paused report schedule
    
    POST /api/report-center/schedules/{schedule_id}/resume/
    """
    try:
        scheduler_service = ReportSchedulerService()
        schedule = scheduler_service.resume_schedule(schedule_id, request.user.id)
        
        return Response({
            'id': schedule.id,
            'status': schedule.status,
            'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
            'message': 'Report schedule resumed successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resuming report schedule: {str(e)}")
        return Response(
            {'error': 'Failed to resume report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_schedule_now(request, schedule_id):
    """
    Execute a schedule immediately (manual trigger)
    
    POST /api/report-center/schedules/{schedule_id}/run/
    """
    try:
        # Verify user owns this schedule
        schedule = get_object_or_404(
            ReportSchedule, 
            id=schedule_id, 
            user=request.user
        )
        
        # Execute the schedule
        scheduler_service = ReportSchedulerService()
        result = scheduler_service.execute_schedule(schedule_id)
        
        return Response({
            'message': 'Schedule executed successfully',
            'execution_result': result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error executing report schedule manually: {str(e)}")
        return Response(
            {'error': 'Failed to execute report schedule'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule_executions(request, schedule_id):
    """
    Get execution history for a schedule
    
    GET /api/report-center/schedules/{schedule_id}/executions/
    """
    try:
        # Verify user owns this schedule
        schedule = get_object_or_404(
            ReportSchedule, 
            id=schedule_id, 
            user=request.user
        )
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status_filter = request.GET.get('status')
        
        # Build queryset
        queryset = schedule.executions.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        executions = queryset[start_idx:end_idx]
        
        # Serialize execution data
        execution_data = []
        for execution in executions:
            execution_data.append({
                'id': execution.id,
                'status': execution.status,
                'scheduled_for': execution.scheduled_for.isoformat(),
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'reports_generated': execution.reports_generated,
                'emails_sent': execution.emails_sent,
                'execution_time_seconds': execution.execution_time_seconds,
                'error_message': execution.error_message,
                'error_details': execution.error_details,
                'generated_reports': execution.generated_reports,
                'duration': execution.duration
            })
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        return Response({
            'executions': execution_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_previous': has_previous
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting schedule executions: {str(e)}")
        return Response(
            {'error': 'Failed to get schedule executions'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """
    Get scheduling dashboard statistics
    
    GET /api/report-center/schedules/stats/
    """
    try:
        user = request.user
        
        # Get basic stats
        total_schedules = ReportSchedule.objects.filter(user=user).count()
        active_schedules = ReportSchedule.objects.filter(user=user, status='active').count()
        paused_schedules = ReportSchedule.objects.filter(user=user, status='paused').count()
        
        # Get recent executions
        recent_executions = ReportScheduleExecution.objects.filter(
            schedule__user=user
        ).order_by('-completed_at')[:5]
        
        # Calculate success rate
        total_executions = ReportScheduleExecution.objects.filter(schedule__user=user).count()
        successful_executions = ReportScheduleExecution.objects.filter(
            schedule__user=user,
            status='completed'
        ).count()
        
        success_rate = 0
        if total_executions > 0:
            success_rate = round((successful_executions / total_executions) * 100, 1)
        
        # Get upcoming schedules
        upcoming_schedules = ReportSchedule.objects.filter(
            user=user,
            status='active',
            next_run__isnull=False
        ).order_by('next_run')[:5]
        
        upcoming_data = []
        for schedule in upcoming_schedules:
            upcoming_data.append({
                'id': schedule.id,
                'name': schedule.name,
                'next_run': schedule.next_run.isoformat(),
                'frequency': schedule.frequency
            })
        
        recent_execution_data = []
        for execution in recent_executions:
            recent_execution_data.append({
                'id': execution.id,
                'schedule_name': execution.schedule.name,
                'status': execution.status,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'reports_generated': execution.reports_generated,
                'duration': execution.duration
            })
        
        return Response({
            'total_schedules': total_schedules,
            'active_schedules': active_schedules,
            'paused_schedules': paused_schedules,
            'total_executions': total_executions,
            'success_rate': success_rate,
            'upcoming_schedules': upcoming_data,
            'recent_executions': recent_execution_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return Response(
            {'error': 'Failed to get dashboard statistics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )