"""
API views for bulk export functionality
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import logging

from ..services.bulk_export_service import BulkExportService
from ..models import BulkExportJob
from core.models import Client, Scenario

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_bulk_export(request):
    """
    Initiate a bulk export job
    
    POST /api/report-center/bulk-export/initiate/
    {
        "export_config": {
            "format": "pdf",  // pdf, excel, powerpoint
            "include_charts": true,
            "pdf_options": {
                "page_size": "letter",
                "orientation": "portrait"
            }
        },
        "selection_type": "clients",  // clients, scenarios, mixed
        "client_ids": [1, 2, 3],      // optional
        "scenario_ids": [4, 5, 6],    // optional
        "template_ids": [1],          // required - templates to use
        "filters": {                  // optional additional filters
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            }
        }
    }
    """
    try:
        data = request.data
        user = request.user
        
        # Validate required fields
        if not data.get('export_config'):
            return Response(
                {'error': 'export_config is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('template_ids'):
            return Response(
                {'error': 'template_ids is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        selection_type = data.get('selection_type', 'clients')
        client_ids = data.get('client_ids', [])
        scenario_ids = data.get('scenario_ids', [])
        template_ids = data.get('template_ids', [])
        
        # Validate selection
        if selection_type == 'clients' and not client_ids:
            return Response(
                {'error': 'client_ids is required when selection_type is clients'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if selection_type == 'scenarios' and not scenario_ids:
            return Response(
                {'error': 'scenario_ids is required when selection_type is scenarios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate that user has access to specified clients/scenarios
        if client_ids:
            accessible_clients = Client.objects.filter(
                id__in=client_ids,
                advisor=user
            ).values_list('id', flat=True)
            
            if len(accessible_clients) != len(client_ids):
                return Response(
                    {'error': 'Some specified clients are not accessible'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if scenario_ids:
            accessible_scenarios = Scenario.objects.filter(
                id__in=scenario_ids,
                client__advisor=user
            ).values_list('id', flat=True)
            
            if len(accessible_scenarios) != len(scenario_ids):
                return Response(
                    {'error': 'Some specified scenarios are not accessible'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Initialize bulk export service
        bulk_service = BulkExportService()
        
        # Start bulk export job
        bulk_job = bulk_service.initiate_bulk_export(
            user_id=user.id,
            export_config=data['export_config'],
            client_ids=client_ids if client_ids else None,
            scenario_ids=scenario_ids if scenario_ids else None,
            template_ids=template_ids
        )
        
        return Response({
            'job_id': bulk_job.id,
            'status': bulk_job.status,
            'total_items': bulk_job.total_items,
            'message': 'Bulk export job initiated successfully'
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error initiating bulk export: {str(e)}")
        return Response(
            {'error': 'Failed to initiate bulk export'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bulk_export_status(request, job_id):
    """
    Get the status of a bulk export job
    
    GET /api/report-center/bulk-export/{job_id}/status/
    """
    try:
        # Verify user owns this job
        bulk_job = get_object_or_404(
            BulkExportJob, 
            id=job_id, 
            user=request.user
        )
        
        bulk_service = BulkExportService()
        job_status = bulk_service.get_job_status(job_id)
        
        return Response(job_status, status=status.HTTP_200_OK)
        
    except BulkExportJob.DoesNotExist:
        return Response(
            {'error': 'Bulk export job not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error getting bulk export status: {str(e)}")
        return Response(
            {'error': 'Failed to get job status'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_bulk_export(request, job_id):
    """
    Cancel a running bulk export job
    
    POST /api/report-center/bulk-export/{job_id}/cancel/
    """
    try:
        # Verify user owns this job
        bulk_job = get_object_or_404(
            BulkExportJob, 
            id=job_id, 
            user=request.user
        )
        
        bulk_service = BulkExportService()
        cancelled = bulk_service.cancel_job(job_id)
        
        if cancelled:
            return Response({
                'message': 'Bulk export job cancelled successfully',
                'job_id': job_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Job cannot be cancelled (may already be completed or failed)',
                'job_id': job_id
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except BulkExportJob.DoesNotExist:
        return Response(
            {'error': 'Bulk export job not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error cancelling bulk export: {str(e)}")
        return Response(
            {'error': 'Failed to cancel job'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_bulk_export(request, job_id):
    """
    Download the result file from a completed bulk export job
    
    GET /api/report-center/bulk-export/{job_id}/download/
    """
    try:
        # Verify user owns this job
        bulk_job = get_object_or_404(
            BulkExportJob, 
            id=job_id, 
            user=request.user
        )
        
        if bulk_job.status not in ['completed', 'completed_with_errors']:
            return Response(
                {'error': 'Export job is not completed yet'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not bulk_job.file_path:
            return Response(
                {'error': 'No export file available'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return download URL or redirect to file
        # In a real implementation, this would handle S3 signed URLs or direct file serving
        return Response({
            'download_url': f"/media/{bulk_job.file_path}",
            'file_path': bulk_job.file_path,
            'job_id': job_id,
            'status': bulk_job.status,
            'successful_exports': bulk_job.successful_exports,
            'failed_exports': bulk_job.failed_exports
        }, status=status.HTTP_200_OK)
        
    except BulkExportJob.DoesNotExist:
        return Response(
            {'error': 'Bulk export job not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error downloading bulk export: {str(e)}")
        return Response(
            {'error': 'Failed to prepare download'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_bulk_export_jobs(request):
    """
    List bulk export jobs for the current user
    
    GET /api/report-center/bulk-export/jobs/
    """
    try:
        user = request.user
        
        # Get query parameters for filtering/pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status_filter = request.GET.get('status')
        
        # Build queryset
        queryset = BulkExportJob.objects.filter(user=user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        jobs = queryset[start_idx:end_idx]
        
        # Serialize job data
        job_data = []
        for job in jobs:
            job_data.append({
                'id': job.id,
                'status': job.status,
                'export_config': job.export_config,
                'total_items': job.total_items,
                'progress': job.progress,
                'successful_exports': job.successful_exports,
                'failed_exports': job.failed_exports,
                'file_path': job.file_path,
                'error_message': job.error_message,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'duration': job.duration,
                'is_completed': job.is_completed
            })
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        return Response({
            'jobs': job_data,
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
        logger.error(f"Error listing bulk export jobs: {str(e)}")
        return Response(
            {'error': 'Failed to list bulk export jobs'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_bulk_export_job(request, job_id):
    """
    Delete a bulk export job and its associated files
    
    DELETE /api/report-center/bulk-export/{job_id}/
    """
    try:
        # Verify user owns this job
        bulk_job = get_object_or_404(
            BulkExportJob, 
            id=job_id, 
            user=request.user
        )
        
        # Only allow deletion of completed jobs
        if not bulk_job.is_completed:
            return Response(
                {'error': 'Cannot delete job that is still running'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Delete associated files from storage
        # if bulk_job.file_path:
        #     storage_service = ReportFileStorageService()
        #     storage_service.delete_file(bulk_job.file_path)
        
        # Delete the job record
        bulk_job.delete()
        
        return Response({
            'message': 'Bulk export job deleted successfully',
            'job_id': job_id
        }, status=status.HTTP_200_OK)
        
    except BulkExportJob.DoesNotExist:
        return Response(
            {'error': 'Bulk export job not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting bulk export job: {str(e)}")
        return Response(
            {'error': 'Failed to delete job'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )