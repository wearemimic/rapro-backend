"""
Views Package for RetirementAdvisorPro Core

This package contains all API views including document management,
client management, and other core functionality.
"""

# Views package - no circular imports

from .document_views import (
    DocumentViewSet, DocumentCategoryViewSet, DocumentVersionViewSet,
    DocumentAuditLogViewSet, DocumentTemplateViewSet, DocumentRetentionPolicyViewSet,
    bulk_document_action
)

__all__ = [
    'DocumentViewSet', 'DocumentCategoryViewSet', 'DocumentVersionViewSet',
    'DocumentAuditLogViewSet', 'DocumentTemplateViewSet', 'DocumentRetentionPolicyViewSet',
    'bulk_document_action'
]