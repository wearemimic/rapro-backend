"""
Document Management API Views

This module provides REST API endpoints for secure document management
with FINRA compliance, AWS S3 integration, and comprehensive audit logging.
"""

import logging
import mimetypes
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError as DRFValidationError

# from django_filters.rest_framework import DjangoFilterBackend

from ..models import (
    Document, DocumentCategory, DocumentVersion, DocumentPermission, 
    DocumentAuditLog, DocumentTemplate, DocumentRetentionPolicy, Client, CustomUser
)
from ..serializers.document_serializers import (
    DocumentSerializer, DocumentListSerializer, DocumentCreateSerializer,
    DocumentCategorySerializer, DocumentVersionSerializer, DocumentPermissionSerializer,
    DocumentAuditLogSerializer, DocumentTemplateSerializer, DocumentRetentionPolicySerializer,
    DocumentUploadSerializer, DocumentStatsSerializer
)
from ..services.s3_service import get_s3_service

logger = logging.getLogger(__name__)


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document categories
    """
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        """Get global categories and advisor-specific categories"""
        from django.db.models import Q
        return DocumentCategory.objects.filter(
            Q(advisor=None) | Q(advisor=self.request.user),  # Global OR user-specific
            is_active=True
        ).select_related('advisor').order_by('name')

    def perform_create(self, serializer):
        """Set advisor when creating category"""
        serializer.save(advisor=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents with S3 integration
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'category', 'status', 'retention_status', 'compliance_type', 
        'contains_pii', 'contains_phi', 'client'
    ]
    search_fields = ['original_filename', 'title', 'description', 'tags']
    ordering_fields = ['original_filename', 'uploaded_at', 'last_accessed', 'file_size']
    ordering = ['-uploaded_at']
    
    def get_audit_context(self, request):
        """
        Extract audit context information from request for compliance logging
        """
        # Get IP address (handle X-Forwarded-For for proxy/load balancer)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get or create session ID
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        return {
            'user_ip': ip_address,
            'user_agent': user_agent,
            'session_id': session_id
        }

    def get_queryset(self):
        """Filter documents to current advisor's data"""
        base_queryset = Document.objects.filter(
            advisor=self.request.user
        ).select_related(
            'advisor', 'category', 'client', 'uploaded_by'
        ).prefetch_related('versions', 'audit_logs')

        # Add client filter if specified
        client_id = self.request.query_params.get('client_id')
        if client_id:
            base_queryset = base_queryset.filter(client_id=client_id)

        return base_queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DocumentCreateSerializer
        elif self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'upload':
            return DocumentUploadSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        """Set advisor and handle file upload when creating document"""
        with transaction.atomic():
            # Set advisor
            document = serializer.save(
                advisor=self.request.user,
                uploaded_by=self.request.user,
                status='active'
            )

            # Create audit log with compliance tracking
            audit_context = self.get_audit_context(self.request)
            DocumentAuditLog.objects.create(
                document=document,
                user=self.request.user,
                action='created',
                details={'filename': document.original_filename, 'method': 'api_create'},
                user_ip=audit_context['user_ip'],
                user_agent=audit_context['user_agent'],
                session_id=audit_context['session_id'],
                client_involved=document.client,
                compliance_relevant=True,
                success=True
            )

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload(self, request):
        """
        Handle file upload with S3 integration
        """
        try:
            serializer = DocumentUploadSerializer(data=request.data)
            if not serializer.is_valid():
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Upload validation failed: {serializer.errors}")
                logger.error(f"Request data: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            file_obj = serializer.validated_data['file']
            category_id = serializer.validated_data.get('category_id')
            client_id = serializer.validated_data.get('client_id')
            title = serializer.validated_data.get('title', file_obj.name)
            description = serializer.validated_data.get('description', '')
            tags = serializer.validated_data.get('tags', '')
            compliance_type = serializer.validated_data.get('compliance_type', 'standard')

            # Validate file size
            if file_obj.size > settings.MAX_UPLOAD_SIZE:
                return Response(
                    {'error': f'File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file type
            content_type = file_obj.content_type
            if content_type not in settings.ALLOWED_DOCUMENT_TYPES:
                return Response(
                    {'error': f'File type {content_type} is not allowed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Read file content
            file_content = file_obj.read()

            # Get category and client objects
            category = None
            if category_id:
                try:
                    from django.db.models import Q
                    category = DocumentCategory.objects.get(
                        Q(advisor=None) | Q(advisor=request.user),  # Global OR user-specific
                        id=category_id, 
                        is_active=True
                    )
                except DocumentCategory.DoesNotExist:
                    return Response(
                        {'error': 'Invalid category ID'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            client = None
            if client_id:
                try:
                    client = Client.objects.get(
                        id=client_id, 
                        advisor=request.user
                    )
                except Client.DoesNotExist:
                    return Response(
                        {'error': 'Invalid client ID'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Upload to S3
            document_type = category.category_type if category else 'general'
            upload_result = get_s3_service().upload_document(
                file_content=file_content,
                filename=file_obj.name,
                advisor_id=str(request.user.id),
                document_type=document_type,
                metadata={
                    'title': title,
                    'description': description,
                    'compliance_type': compliance_type
                }
            )

            # Check if document with same hash already exists
            existing_document = Document.objects.filter(
                file_hash=upload_result['file_hash'],
                advisor=request.user
            ).first()
            
            if existing_document:
                # Update existing document with new metadata instead of creating duplicate
                existing_document.title = title or existing_document.title
                existing_document.description = description or existing_document.description
                existing_document.category = category or existing_document.category
                existing_document.client = client or existing_document.client
                existing_document.tags = tags or existing_document.tags
                existing_document.compliance_type = compliance_type
                existing_document.last_accessed = timezone.now()
                existing_document.save()
                
                # Create a new version for the re-upload
                version_count = existing_document.versions.count()
                DocumentVersion.objects.create(
                    document=existing_document,
                    version_number=version_count + 1,
                    s3_key=upload_result['s3_key'],
                    s3_version_id=upload_result.get('version_id', ''),
                    file_hash=upload_result['file_hash'],
                    file_size=upload_result['file_size'],
                    changed_by=request.user,
                    change_description=f'Re-uploaded file (duplicate of version 1)'
                )
                
                document = existing_document
                logger.info(f"Document with same hash already exists, updated metadata for document {document.id}")
            else:
                # Create new document record
                with transaction.atomic():
                    document = Document.objects.create(
                        advisor=request.user,
                        uploaded_by=request.user,
                        category=category,
                        client=client,
                        original_filename=file_obj.name,
                        title=title,
                        description=description,
                        s3_key=upload_result['s3_key'],
                        file_hash=upload_result['file_hash'],
                        file_size=upload_result['file_size'],
                        file_type=file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else 'unknown',
                        mime_type=upload_result.get('content_type', content_type),
                        s3_bucket=settings.AWS_STORAGE_BUCKET_NAME,  # Use configured bucket
                        tags=tags,
                        compliance_type=compliance_type,
                        status='active'
                    )

                    # Create initial version
                    DocumentVersion.objects.create(
                        document=document,
                        version_number=1,
                        s3_key=upload_result['s3_key'],
                        s3_version_id=upload_result.get('version_id', ''),
                        file_hash=upload_result['file_hash'],
                        file_size=upload_result['file_size'],
                        changed_by=request.user,
                        change_description='Initial upload'
                    )

                # Create audit log with full compliance tracking
                audit_context = self.get_audit_context(request)
                DocumentAuditLog.objects.create(
                    document=document,
                    user=request.user,
                    action='uploaded',
                    details={
                        'filename': file_obj.name,
                        'file_size': upload_result['file_size'],
                        's3_key': upload_result['s3_key'],
                        'file_hash': upload_result['file_hash'],
                        'title': title,
                        'category_id': category_id,
                        'client_id': client_id
                    },
                    user_ip=audit_context['user_ip'],
                    user_agent=audit_context['user_agent'],
                    session_id=audit_context['session_id'],
                    client_involved=client,
                    compliance_relevant=True,
                    success=True
                )
                
                # Log to unified activity log
                from ..services.activity_service import ActivityService
                ActivityService.log_document_upload(
                    user=request.user,
                    document=document,
                    client=client
                )

            # Return document details
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.error(f"Document upload validation error: {str(e)}")
            # Log failed upload attempt for compliance
            if request.user.is_authenticated:
                audit_context = self.get_audit_context(request)
                DocumentAuditLog.objects.create(
                    document=None,  # No document created
                    user=request.user,
                    action='uploaded',
                    details={
                        'error': 'validation_error',
                        'error_message': str(e),
                        'filename': request.data.get('file', {}).name if 'file' in request.data else 'unknown'
                    },
                    user_ip=audit_context['user_ip'],
                    user_agent=audit_context['user_agent'],
                    session_id=audit_context['session_id'],
                    client_involved=Client.objects.filter(id=client_id).first() if client_id else None,
                    compliance_relevant=True,
                    success=False,
                    error_message=str(e)
                )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Document upload error: {str(e)}")
            # Log failed upload attempt for compliance
            if request.user.is_authenticated:
                audit_context = self.get_audit_context(request)
                DocumentAuditLog.objects.create(
                    document=None,  # No document created
                    user=request.user,
                    action='uploaded',
                    details={
                        'error': 'system_error',
                        'error_type': type(e).__name__,
                        'filename': request.data.get('file', {}).name if 'file' in request.data else 'unknown'
                    },
                    user_ip=audit_context['user_ip'],
                    user_agent=audit_context['user_agent'],
                    session_id=audit_context['session_id'],
                    client_involved=Client.objects.filter(id=client_id).first() if client_id else None,
                    compliance_relevant=True,
                    success=False,
                    error_message=str(e)[:500]  # Limit error message length
                )
            return Response(
                {'error': 'Failed to upload document. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download document file from S3
        """
        try:
            document = self.get_object()
            
            # Check permissions
            if not self._check_document_access(document, request.user, 'download'):
                raise PermissionDenied("You don't have permission to download this document")

            # Get file from S3
            file_content, metadata = get_s3_service().download_document(
                s3_key=document.s3_key,
                advisor_id=str(request.user.id)
            )

            # Update access tracking
            document.last_accessed = timezone.now()
            document.access_count += 1
            document.save(update_fields=['last_accessed', 'access_count'])

            # Create audit log with full compliance tracking
            audit_context = self.get_audit_context(request)
            DocumentAuditLog.objects.create(
                document=document,
                user=request.user,
                action='downloaded',
                details={
                    'filename': document.original_filename,
                    'file_size': document.file_size,
                    's3_key': document.s3_key,
                    'download_method': 'direct'
                },
                user_ip=audit_context['user_ip'],
                user_agent=audit_context['user_agent'],
                session_id=audit_context['session_id'],
                client_involved=document.client,
                compliance_relevant=True,
                success=True
            )

            # Return file response
            response = HttpResponse(file_content, content_type=document.content_type)
            response['Content-Disposition'] = f'attachment; filename="{document.original_filename}"'
            response['Content-Length'] = str(len(file_content))
            
            return response

        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Document download error: {str(e)}")
            return Response(
                {'error': 'Failed to download document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def toggle_sharing(self, request, pk=None):
        """
        Toggle document visibility in client portal
        """
        try:
            document = self.get_object()
            
            # Check permissions - only advisor can toggle sharing
            if document.advisor != request.user:
                raise PermissionDenied("You don't have permission to modify this document")
            
            # Get the new visibility state
            is_client_visible = request.data.get('is_client_visible', not document.is_client_visible)
            
            # Update document
            document.is_client_visible = is_client_visible
            document.save(update_fields=['is_client_visible'])
            
            # Create audit log
            action = 'shared_with_client' if is_client_visible else 'made_private'
            audit_context = self.get_audit_context(request)
            DocumentAuditLog.objects.create(
                document=document,
                user=request.user,
                action=action,
                details={
                    'filename': document.original_filename,
                    'visibility_changed_to': 'client_visible' if is_client_visible else 'private',
                    'previous_visibility': 'private' if is_client_visible else 'client_visible'
                },
                user_ip=audit_context['user_ip'],
                user_agent=audit_context['user_agent'],
                session_id=audit_context['session_id'],
                client_involved=document.client,
                compliance_relevant=True,
                success=True
            )
            
            return Response({
                'id': document.id,
                'is_client_visible': document.is_client_visible,
                'message': f'Document {"shared with client" if is_client_visible else "made private"} successfully'
            }, status=status.HTTP_200_OK)
            
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Document toggle sharing error: {str(e)}")
            return Response(
                {'error': 'Failed to update document sharing'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """
        Create shareable link for document
        """
        try:
            document = self.get_object()
            
            # Check permissions
            if not self._check_document_access(document, request.user, 'share'):
                raise PermissionDenied("You don't have permission to share this document")

            expiration_hours = request.data.get('expiration_hours', 24)
            permission_type = request.data.get('permission_type', 'view')

            # Generate presigned URL
            expiration_seconds = expiration_hours * 3600
            presigned_url = get_s3_service().generate_presigned_url(
                s3_key=document.s3_key,
                advisor_id=str(request.user.id),
                expiration=expiration_seconds,
                download=True
            )

            # Create permission record
            permission = DocumentPermission.objects.create(
                document=document,
                user=request.user,
                permission_type=permission_type,
                share_token=presigned_url.split('?')[0].split('/')[-1],  # Extract token
                expires_at=timezone.now() + timedelta(hours=expiration_hours)
            )

            # Create audit log with compliance tracking
            audit_context = self.get_audit_context(request)
            DocumentAuditLog.objects.create(
                document=document,
                user=request.user,
                action='shared',
                details={
                    'filename': document.original_filename,
                    'expiration_hours': expiration_hours,
                    'share_method': 'presigned_url'
                },
                user_ip=audit_context['user_ip'],
                user_agent=audit_context['user_agent'],
                session_id=audit_context['session_id'],
                client_involved=document.client,
                compliance_relevant=True,
                success=True
            )

            return Response({
                'share_url': presigned_url,
                'expires_at': permission.expires_at,
                'permission_type': permission_type
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Document sharing error: {str(e)}")
            return Response(
                {'error': 'Failed to create shareable link'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['delete'])
    def archive(self, request, pk=None):
        """
        Archive document (soft delete)
        """
        try:
            document = self.get_object()
            
            # Check permissions
            if document.advisor != request.user:
                raise PermissionDenied("You don't have permission to archive this document")

            # Update status
            document.status = 'archived'
            document.archived_at = timezone.now()
            document.save(update_fields=['status', 'archived_at'])

            # Create audit log with compliance tracking
            audit_context = self.get_audit_context(request)
            DocumentAuditLog.objects.create(
                document=document,
                user=request.user,
                action='archived',
                details={
                    'filename': document.original_filename,
                    'previous_status': document.status,
                    'archive_reason': request.data.get('reason', 'manual_archive')
                },
                user_ip=audit_context['user_ip'],
                user_agent=audit_context['user_agent'],
                session_id=audit_context['session_id'],
                client_involved=document.client,
                compliance_relevant=True,
                success=True
            )

            return Response({'message': 'Document archived successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Document archiving error: {str(e)}")
            return Response(
                {'error': 'Failed to archive document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get document statistics for advisor
        """
        try:
            queryset = self.get_queryset()
            
            # Basic stats
            total_documents = queryset.count()
            total_size = queryset.aggregate(total=models.Sum('file_size'))['total'] or 0
            
            # Status breakdown
            status_stats = queryset.values('status').annotate(count=models.Count('id'))
            
            # Category breakdown
            category_stats = queryset.values('category__name').annotate(count=models.Count('id'))
            
            # Client breakdown
            client_stats = queryset.filter(client__isnull=False).values('client__first_name', 'client__last_name').annotate(count=models.Count('id'))
            
            # Recent uploads (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_uploads = queryset.filter(uploaded_at__gte=thirty_days_ago).count()

            # Get S3 storage stats
            s3_stats = get_s3_service().get_storage_stats(str(request.user.id))

            stats_data = {
                'total_documents': total_documents,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0,
                'recent_uploads_30d': recent_uploads,
                'status_breakdown': list(status_stats),
                'category_breakdown': list(category_stats),
                'client_breakdown': list(client_stats),
                's3_storage': s3_stats,
                'last_updated': timezone.now()
            }

            return Response(stats_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Document stats error: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve document statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _check_document_access(self, document: Document, user: CustomUser, action: str) -> bool:
        """
        Check if user has permission to perform action on document
        """
        # Advisor always has access to their own documents
        if document.advisor == user:
            return True

        # Check explicit permissions
        permissions = DocumentPermission.objects.filter(
            document=document,
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        )

        for permission in permissions:
            if action == 'view' and permission.permission_type in ['view', 'edit', 'admin']:
                return True
            elif action == 'edit' and permission.permission_type in ['edit', 'admin']:
                return True
            elif action == 'download' and permission.permission_type in ['view', 'edit', 'admin']:
                return True
            elif action == 'share' and permission.permission_type in ['edit', 'admin']:
                return True

        return False


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing document versions
    """
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-version_number']

    def get_queryset(self):
        """Filter versions to current advisor's documents"""
        document_id = self.kwargs.get('document_pk')
        if document_id:
            # Nested route - get versions for specific document
            return DocumentVersion.objects.filter(
                document_id=document_id,
                document__advisor=self.request.user
            ).select_related('document', 'uploaded_by')
        else:
            # List all versions for advisor's documents
            return DocumentVersion.objects.filter(
                document__advisor=self.request.user
            ).select_related('document', 'uploaded_by')


class DocumentAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing document audit logs
    """
    serializer_class = DocumentAuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['action', 'document']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter audit logs to current advisor's documents"""
        document_id = self.kwargs.get('document_pk')
        if document_id:
            # Nested route - get logs for specific document
            return DocumentAuditLog.objects.filter(
                document_id=document_id,
                document__advisor=self.request.user
            ).select_related('document', 'user')
        else:
            # List all logs for advisor's documents
            return DocumentAuditLog.objects.filter(
                document__advisor=self.request.user
            ).select_related('document', 'user')


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document templates
    """
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'times_used', 'created_at']
    ordering = ['-times_used', 'name']

    def get_queryset(self):
        """Filter templates to current advisor's data"""
        return DocumentTemplate.objects.filter(
            advisor=self.request.user,
            is_active=True
        ).select_related('advisor')

    def perform_create(self, serializer):
        """Set advisor when creating template"""
        serializer.save(advisor=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()


class DocumentRetentionPolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document retention policies
    """
    serializer_class = DocumentRetentionPolicySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ['category', 'auto_disposal_enabled']
    ordering = ['retention_years']

    def get_queryset(self):
        """Filter policies to current advisor's data"""
        return DocumentRetentionPolicy.objects.filter(
            advisor=self.request.user,
            is_active=True
        ).select_related('advisor', 'category')

    def perform_create(self, serializer):
        """Set advisor when creating policy"""
        serializer.save(advisor=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_active = False
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_document_action(request):
    """
    Perform bulk actions on multiple documents
    """
    try:
        action = request.data.get('action')
        document_ids = request.data.get('document_ids', [])

        if not action or not document_ids:
            return Response(
                {'error': 'Action and document_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get documents
        documents = Document.objects.filter(
            id__in=document_ids,
            advisor=request.user
        )

        if documents.count() != len(document_ids):
            return Response(
                {'error': 'Some documents not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        with transaction.atomic():
            for document in documents:
                try:
                    if action == 'archive':
                        document.status = 'archived'
                        document.archived_at = timezone.now()
                        document.save(update_fields=['status', 'archived_at'])
                        
                        # Create audit log with compliance tracking
                        audit_context = self.get_audit_context(request)
                        DocumentAuditLog.objects.create(
                            document=document,
                            user=request.user,
                            action='archived',
                            details={
                                'filename': document.original_filename,
                                'operation': 'bulk_archive',
                                'batch_size': len(document_ids)
                            },
                            user_ip=audit_context['user_ip'],
                            user_agent=audit_context['user_agent'],
                            session_id=audit_context['session_id'],
                            client_involved=document.client,
                            compliance_relevant=True,
                            success=True
                        )
                        
                        results.append({'id': document.id, 'status': 'archived'})
                        
                    elif action == 'delete':
                        # Hard delete - remove from S3 and database
                        get_s3_service().delete_document(
                            s3_key=document.s3_key,
                            advisor_id=str(request.user.id)
                        )
                        document.delete()
                        results.append({'id': document.id, 'status': 'deleted'})
                        
                    else:
                        results.append({'id': document.id, 'status': 'unsupported_action'})

                except Exception as e:
                    logger.error(f"Bulk action error for document {document.id}: {str(e)}")
                    results.append({'id': document.id, 'status': 'error', 'message': str(e)})

        return Response({'results': results}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Bulk document action error: {str(e)}")
        return Response(
            {'error': 'Failed to perform bulk action'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )