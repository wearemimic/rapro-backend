"""
Serializers Package for RetirementAdvisorPro Core

This package contains all API serializers including document management,
client management, and other core functionality.
"""

# Import all serializers from main serializers.py file
from ..serializers_main import *

# Import document-specific serializers
from .document_serializers import (
    DocumentSerializer, DocumentListSerializer, DocumentCreateSerializer,
    DocumentCategorySerializer, DocumentVersionSerializer, DocumentPermissionSerializer,
    DocumentAuditLogSerializer, DocumentTemplateSerializer, DocumentRetentionPolicySerializer,
    DocumentUploadSerializer, DocumentStatsSerializer, DocumentShareSerializer
)

# Extend the __all__ list
__all__ = [
    'DocumentSerializer', 'DocumentListSerializer', 'DocumentCreateSerializer',
    'DocumentCategorySerializer', 'DocumentVersionSerializer', 'DocumentPermissionSerializer',
    'DocumentAuditLogSerializer', 'DocumentTemplateSerializer', 'DocumentRetentionPolicySerializer',
    'DocumentUploadSerializer', 'DocumentStatsSerializer', 'DocumentShareSerializer'
]