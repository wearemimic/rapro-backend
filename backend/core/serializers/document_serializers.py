"""
Document Management Serializers

This module provides serializers for document management with FINRA compliance
and secure data handling.
"""

from rest_framework import serializers
from django.utils import timezone
from ..models import (
    Document, DocumentCategory, DocumentVersion, DocumentPermission,
    DocumentAuditLog, DocumentTemplate, DocumentRetentionPolicy, Client, CustomUser
)


class DocumentCategorySerializer(serializers.ModelSerializer):
    """Serializer for DocumentCategory model"""
    
    document_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DocumentCategory
        fields = [
            'id', 'name', 'description', 'category_type', 'color_code',
            'icon', 'is_active', 'document_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'document_count']

    def validate_category_type(self, value):
        """Validate category type is allowed"""
        allowed_types = [choice[0] for choice in DocumentCategory.CATEGORY_TYPES]
        if value not in allowed_types:
            raise serializers.ValidationError(f"Invalid category type. Must be one of: {allowed_types}")
        return value


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentVersion model"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'version_number', 's3_key', 'file_hash', 'file_size', 'file_size_mb',
            'uploaded_by', 'uploaded_by_name', 'change_notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'uploaded_by_name', 'file_size_mb']

    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0


class DocumentPermissionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentPermission model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentPermission
        fields = [
            'id', 'user', 'user_name', 'permission_type', 'share_token',
            'expires_at', 'is_expired', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user_name', 'is_expired']

    def get_is_expired(self, obj):
        """Check if permission has expired"""
        if obj.expires_at:
            return timezone.now() > obj.expires_at
        return False


class DocumentAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for DocumentAuditLog model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    document_filename = serializers.CharField(source='document.original_filename', read_only=True)
    
    class Meta:
        model = DocumentAuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'details', 'document_filename',
            'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp', 'user_name', 'document_filename']


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document list views"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    client_name = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    version_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'original_filename', 'title', 'category', 'category_name',
            'client', 'client_name', 'file_size', 'file_size_mb', 'content_type',
            'status', 'compliance_type', 'uploaded_by_name', 'uploaded_at',
            'last_accessed', 'access_count', 'version_count', 'tags'
        ]
        read_only_fields = [
            'id', 'uploaded_at', 'last_accessed', 'access_count', 'category_name',
            'client_name', 'uploaded_by_name', 'file_size_mb', 'version_count'
        ]

    def get_client_name(self, obj):
        """Get client full name"""
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        return None

    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0


class DocumentSerializer(serializers.ModelSerializer):
    """Full serializer for Document model"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    client_name = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    advisor_name = serializers.CharField(source='advisor.get_full_name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    # Related objects
    versions = DocumentVersionSerializer(many=True, read_only=True)
    permissions = DocumentPermissionSerializer(many=True, read_only=True)
    recent_audit_logs = serializers.SerializerMethodField()
    
    # Computed fields
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    retention_end_date = serializers.DateField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'original_filename', 'title', 'description', 'category', 'category_name',
            'client', 'client_name', 's3_key', 'file_hash', 'file_size', 'file_size_mb',
            'content_type', 'tags', 'status', 'compliance_type', 'retention_status',
            'retention_end_date', 'contains_pii', 'contains_phi', 'encryption_status',
            'advisor', 'advisor_name', 'uploaded_by', 'uploaded_by_name',
            'uploaded_at', 'last_accessed', 'access_count', 'archived_at',
            'versions', 'permissions', 'recent_audit_logs',
            'can_edit', 'can_delete'
        ]
        read_only_fields = [
            'id', 's3_key', 'file_hash', 'file_size', 'file_size_mb', 'content_type',
            'uploaded_at', 'last_accessed', 'access_count', 'archived_at',
            'category_name', 'client_name', 'uploaded_by_name', 'advisor_name',
            'versions', 'permissions', 'recent_audit_logs', 'can_edit', 'can_delete',
            'retention_end_date'
        ]

    def get_client_name(self, obj):
        """Get client full name"""
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        return None

    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0

    def get_recent_audit_logs(self, obj):
        """Get last 5 audit log entries"""
        recent_logs = obj.audit_logs.order_by('-timestamp')[:5]
        return DocumentAuditLogSerializer(recent_logs, many=True).data

    def get_can_edit(self, obj):
        """Check if current user can edit document"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Advisor can always edit their documents
        if obj.advisor == request.user:
            return True
            
        # Check explicit permissions
        return obj.permissions.filter(
            user=request.user,
            permission_type__in=['edit', 'admin'],
            is_active=True,
            expires_at__gt=timezone.now()
        ).exists()

    def get_can_delete(self, obj):
        """Check if current user can delete document"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Only advisor can delete their documents
        return obj.advisor == request.user


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating documents without file upload"""
    
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'category', 'client', 'tags',
            'compliance_type', 'contains_pii', 'contains_phi'
        ]

    def validate_category(self, value):
        """Validate category belongs to advisor"""
        request = self.context.get('request')
        if request and value and value.advisor != request.user:
            raise serializers.ValidationError("Invalid category for this advisor")
        return value

    def validate_client(self, value):
        """Validate client belongs to advisor"""
        request = self.context.get('request')
        if request and value and value.advisor != request.user:
            raise serializers.ValidationError("Invalid client for this advisor")
        return value


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document file upload"""
    
    file = serializers.FileField(required=True)
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    client_id = serializers.IntegerField(required=False)
    tags = serializers.CharField(required=False, allow_blank=True)
    compliance_type = serializers.ChoiceField(
        choices=Document.COMPLIANCE_TYPES,
        default='standard'
    )
    contains_pii = serializers.BooleanField(default=False)
    contains_phi = serializers.BooleanField(default=False)

    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size
        from django.conf import settings
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size {value.size} exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Check content type
        if value.content_type not in settings.ALLOWED_DOCUMENT_TYPES:
            raise serializers.ValidationError(
                f"File type '{value.content_type}' is not allowed"
            )
        
        return value


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for DocumentTemplate model"""
    
    advisor_name = serializers.CharField(source='advisor.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 's3_template_key',
            'required_fields', 'instructions', 'times_used', 'is_active',
            'advisor', 'advisor_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_used', 'created_at', 'updated_at', 'advisor_name']

    def validate_template_type(self, value):
        """Validate template type is allowed"""
        allowed_types = [choice[0] for choice in DocumentTemplate.TEMPLATE_TYPES]
        if value not in allowed_types:
            raise serializers.ValidationError(f"Invalid template type. Must be one of: {allowed_types}")
        return value


class DocumentRetentionPolicySerializer(serializers.ModelSerializer):
    """Serializer for DocumentRetentionPolicy model"""
    
    advisor_name = serializers.CharField(source='advisor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    affected_documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentRetentionPolicy
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'retention_years', 'auto_disposal_enabled', 'disposal_method',
            'notification_days_before', 'is_active', 'affected_documents_count',
            'advisor', 'advisor_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'advisor_name', 'category_name',
            'affected_documents_count'
        ]

    def get_affected_documents_count(self, obj):
        """Get count of documents affected by this policy"""
        if obj.category:
            return Document.objects.filter(
                advisor=obj.advisor,
                category=obj.category,
                status='active'
            ).count()
        return 0

    def validate_category(self, value):
        """Validate category belongs to advisor"""
        request = self.context.get('request')
        if request and value and value.advisor != request.user:
            raise serializers.ValidationError("Invalid category for this advisor")
        return value


class DocumentStatsSerializer(serializers.Serializer):
    """Serializer for document statistics"""
    
    total_documents = serializers.IntegerField()
    total_size_bytes = serializers.IntegerField()
    total_size_mb = serializers.FloatField()
    recent_uploads_30d = serializers.IntegerField()
    status_breakdown = serializers.ListField()
    category_breakdown = serializers.ListField()
    client_breakdown = serializers.ListField()
    s3_storage = serializers.DictField()
    last_updated = serializers.DateTimeField()


class DocumentShareSerializer(serializers.Serializer):
    """Serializer for document sharing requests"""
    
    expiration_hours = serializers.IntegerField(default=24, min_value=1, max_value=168)  # Max 7 days
    permission_type = serializers.ChoiceField(
        choices=DocumentPermission.PERMISSION_TYPES,
        default='view'
    )
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)