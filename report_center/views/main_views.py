from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes as action_permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import (
    ReportTemplate, Report, ReportSection, ReportShare, 
    ReportComment, TemplateAnalytics, ReportGeneration
)
from ..serializers import (
    ReportTemplateSerializer, ReportSerializer, ReportSectionSerializer,
    ReportShareSerializer, ReportCommentSerializer, TemplateAnalyticsSerializer,
    ReportGenerationSerializer
)
from ..permissions import (
    CanAccessReportCenter, CanManageReportTemplates, CanGenerateReports,
    CanShareReports, IsReportOwnerOrReadOnly, IsTemplateOwnerOrPublic
)

User = get_user_model()


class ReportTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReportTemplateSerializer
    permission_classes = [CanManageReportTemplates, IsTemplateOwnerOrPublic]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'is_public', 'is_active', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        # Users can see their own templates + public templates
        return ReportTemplate.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        ).select_related('created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        template = self.get_object()
        new_template = ReportTemplate.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            template_type=template.template_type,
            template_config=template.template_config,
            is_public=False,
            created_by=request.user
        )
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [CanAccessReportCenter, IsReportOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'scenario', 'template', 'status', 'created_by']
    search_fields = ['title', 'client__full_name', 'scenario__name']
    ordering_fields = ['title', 'created_at', 'updated_at', 'generation_completed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see reports they created or have access to
        return Report.objects.filter(
            created_by=self.request.user
        ).select_related('client', 'scenario', 'template', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    @action_permission_classes([CanGenerateReports])
    def generate(self, request, pk=None):
        report = self.get_object()
        if report.status in ['generating', 'completed']:
            return Response(
                {'error': 'Report is already being generated or has been completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get format from request (default to PDF)
        format_type = request.data.get('format', 'pdf').lower()
        if format_type not in ['pdf', 'pptx']:
            return Response(
                {'error': 'Invalid format. Must be "pdf" or "pptx"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update report status and create generation record
        report.status = 'generating'
        report.generation_started_at = timezone.now()
        report.save()
        
        generation_record = ReportGeneration.objects.create(
            report=report,
            generation_status='started',
            started_at=timezone.now()
        )
        
        # Trigger background task for report generation
        try:
            from .tasks import generate_report_pdf, generate_report_pptx
            
            if format_type == 'pdf':
                task = generate_report_pdf.apply_async(
                    args=[str(report.id)],
                    queue='analytics'
                )
            else:  # pptx
                task = generate_report_pptx.apply_async(
                    args=[str(report.id)],
                    queue='analytics'
                )
            
            return Response({
                'message': f'Report generation started ({format_type.upper()})',
                'task_id': task.id,
                'format': format_type,
                'report_id': str(report.id),
                'generation_id': str(generation_record.id)
            })
            
        except ImportError:
            # Fallback if Celery tasks not available
            report.status = 'failed'
            report.save()
            
            generation_record.generation_status = 'failed'
            generation_record.error_message = 'Background task system not available'
            generation_record.completed_at = timezone.now()
            generation_record.save()
            
            return Response(
                {'error': 'Report generation service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        report = self.get_object()
        new_report = Report.objects.create(
            title=f"{report.title} (Copy)",
            client=report.client,
            scenario=report.scenario,
            template=report.template,
            report_config=report.report_config,
            created_by=request.user
        )
        
        # Duplicate sections
        for section in report.sections.all():
            ReportSection.objects.create(
                report=new_report,
                section_type=section.section_type,
                title=section.title,
                content_config=section.content_config,
                order=section.order,
                is_enabled=section.is_enabled
            )
        
        serializer = self.get_serializer(new_report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get detailed generation status for a report"""
        report = self.get_object()
        
        # Get latest generation record
        generation_record = ReportGeneration.objects.filter(
            report=report
        ).order_by('-started_at').first()
        
        status_data = {
            'report_id': str(report.id),
            'status': report.status,
            'generation_started_at': report.generation_started_at,
            'generation_completed_at': report.generation_completed_at,
            'file_path': report.file_path,
        }
        
        if generation_record:
            status_data.update({
                'generation_status': generation_record.generation_status,
                'error_message': generation_record.error_message,
                'file_size': generation_record.file_size,
                'processing_time': generation_record.processing_time,
            })
        
        return Response(status_data)
    
    @action(detail=False, methods=['post'])
    @action_permission_classes([CanGenerateReports])
    def batch_generate(self, request):
        """Generate multiple reports in batch"""
        report_ids = request.data.get('report_ids', [])
        format_type = request.data.get('format', 'pdf').lower()
        
        if not report_ids:
            return Response(
                {'error': 'report_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if format_type not in ['pdf', 'pptx']:
            return Response(
                {'error': 'Invalid format. Must be "pdf" or "pptx"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user owns all reports
        user_reports = self.get_queryset().filter(id__in=report_ids)
        if user_reports.count() != len(report_ids):
            return Response(
                {'error': 'One or more reports not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if any reports are already generating or completed
        busy_reports = user_reports.filter(status__in=['generating', 'completed'])
        if busy_reports.exists():
            busy_ids = list(busy_reports.values_list('id', flat=True))
            return Response(
                {
                    'error': 'Some reports are already generating or completed',
                    'busy_reports': [str(rid) for rid in busy_ids]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .tasks import batch_generate_reports
            
            # Queue batch generation task
            task = batch_generate_reports.apply_async(
                args=[[str(rid) for rid in report_ids], format_type],
                queue='analytics'
            )
            
            return Response({
                'message': f'Batch generation started for {len(report_ids)} reports ({format_type.upper()})',
                'task_id': task.id,
                'format': format_type,
                'report_count': len(report_ids),
                'report_ids': [str(rid) for rid in report_ids]
            })
            
        except ImportError:
            return Response(
                {'error': 'Report generation service not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class ReportSectionViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSectionSerializer
    permission_classes = [CanAccessReportCenter]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['report', 'section_type', 'is_enabled']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_queryset(self):
        # Users can only see sections for reports they own
        return ReportSection.objects.filter(
            report__created_by=self.request.user
        ).select_related('report')
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Reorder sections for a report"""
        report_id = request.data.get('report_id')
        section_orders = request.data.get('section_orders', [])
        
        if not report_id or not section_orders:
            return Response(
                {'error': 'report_id and section_orders are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user owns the report
        try:
            report = Report.objects.get(id=report_id, created_by=request.user)
        except Report.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update section orders
        for item in section_orders:
            ReportSection.objects.filter(
                id=item['section_id'],
                report=report
            ).update(order=item['order'])
        
        return Response({'message': 'Sections reordered successfully'})


class ReportShareViewSet(viewsets.ModelViewSet):
    serializer_class = ReportShareSerializer
    permission_classes = [CanShareReports]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['report', 'share_type', 'access_level', 'is_active']
    ordering_fields = ['created_at', 'expires_at', 'last_accessed']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see shares for reports they own
        return ReportShare.objects.filter(
            report__created_by=self.request.user
        ).select_related('report', 'shared_by')
    
    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        share = self.get_object()
        share.is_active = False
        share.save()
        return Response({'message': 'Share access revoked'})


class ReportCommentViewSet(viewsets.ModelViewSet):
    serializer_class = ReportCommentSerializer
    permission_classes = [CanAccessReportCenter]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['report', 'author']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see comments on reports they own or have access to
        return ReportComment.objects.filter(
            Q(report__created_by=self.request.user) |
            Q(report__reportshare__recipient_email=self.request.user.email,
              report__reportshare__is_active=True)
        ).select_related('report', 'author').distinct()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TemplateAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TemplateAnalyticsSerializer
    permission_classes = [CanAccessReportCenter]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['template']
    ordering_fields = ['usage_count', 'average_generation_time', 'last_used']
    ordering = ['-usage_count']
    
    def get_queryset(self):
        # Users can see analytics for templates they created or public templates
        return TemplateAnalytics.objects.filter(
            Q(template__created_by=self.request.user) | Q(template__is_public=True)
        ).select_related('template')


class ReportGenerationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportGenerationSerializer
    permission_classes = [CanAccessReportCenter]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['report', 'generation_status']
    ordering_fields = ['started_at', 'completed_at', 'processing_time']
    ordering = ['-started_at']
    
    def get_queryset(self):
        # Users can see generation logs for their reports
        return ReportGeneration.objects.filter(
            report__created_by=self.request.user
        ).select_related('report')
