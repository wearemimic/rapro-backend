"""
Client Portal URL Configuration

URL patterns for client portal API endpoints, separate from main advisor API
"""

from django.urls import path
from . import client_portal_views

urlpatterns = [
    # Client portal authentication
    path('auth/login/', client_portal_views.ClientPortalAuthView.as_view(), name='client-portal-auth'),
    path('auth/setup-password/', client_portal_views.ClientPortalPasswordSetupView.as_view(), name='client-portal-password-setup'),
    path('auth/logout/', client_portal_views.client_portal_logout, name='client-portal-logout'),
    path('auth/validate/', client_portal_views.client_portal_session_validate, name='client-portal-session-validate'),
    
    # Client portal data access
    path('dashboard/', client_portal_views.ClientPortalDashboardView.as_view(), name='client-portal-dashboard'),
    
    # Client portal scenarios
    path('scenarios/', client_portal_views.ClientPortalScenariosView.as_view(), name='client-portal-scenarios'),
    path('scenarios/<int:scenario_id>/', client_portal_views.ClientPortalScenariosView.as_view(), name='client-portal-scenario-detail'),
    
    # Client portal documents
    path('documents/', client_portal_views.ClientPortalDocumentsView.as_view(), name='client-portal-documents'),
    path('documents/<int:document_id>/', client_portal_views.ClientPortalDocumentsView.as_view(), name='client-portal-document-detail'),
    
    # Advisor-side client portal management
    path('manage/<int:client_id>/enable/', client_portal_views.enable_client_portal_access, name='enable-client-portal-access'),
    path('manage/<int:client_id>/revoke/', client_portal_views.revoke_client_portal_access, name='revoke-client-portal-access'),
    path('manage/<int:client_id>/send-invitation/', client_portal_views.send_client_portal_invitation, name='send-client-portal-invitation'),
]