from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views_main import login_view, logout_view, register_view, profile_view, AdvisorClientListView, ClientCreateView, ClientDetailView, ClientEditView, RothConversionAPIView, register_advisor, complete_registration
from .views_main import ScenarioCreateView, create_scenario, run_scenario_calculation, proxy_to_wealthbox, get_scenario_assets, duplicate_scenario, get_scenario_detail, get_scenario_for_editing, get_scenario_comparison_data, comparison_preferences, get_federal_standard_deduction, get_irmaa_thresholds_for_years
from .views_main import ListCreateRealEstateView, RealEstateDetailView, ReportTemplateViewSet
from .views_main import EmailAccountViewSet, CommunicationViewSet, LeadViewSet, LeadSourceViewSet, ActivityLogViewSet, TaskViewSet, TaskTemplateViewSet, CalendarAccountViewSet, CalendarEventViewSet, MeetingTemplateViewSet
from .views.document_views import DocumentViewSet, DocumentCategoryViewSet, DocumentVersionViewSet, DocumentAuditLogViewSet, DocumentTemplateViewSet, DocumentRetentionPolicyViewSet, bulk_document_action
from .views_main import gmail_auth_url, gmail_oauth_callback, outlook_auth_url, outlook_oauth_callback, send_email, sync_all_emails, oauth_settings_status, google_calendar_auth_url, google_calendar_oauth_callback, outlook_calendar_auth_url, outlook_calendar_oauth_callback, calendar_settings_status, create_video_meeting, update_video_meeting, delete_video_meeting, get_meeting_join_info, send_meeting_reminder, video_settings_status, get_jump_ai_meeting_insights
from .views_main import analyze_communication, bulk_analyze_communications, ai_analysis_stats, high_priority_communications, trigger_auto_analysis
from .views_main import celery_health_check, task_status, queue_monitoring
from . import views_main as views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .webhooks import stripe_webhook
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from .auth0_views import auth0_login, auth0_signup, list_users, user_detail, reset_user_password, auth0_debug, auth0_exchange_code, auth0_complete_registration, validate_coupon

# Create routers for ViewSets
reporttemplate_router = DefaultRouter()
reporttemplate_router.register(r'reporttemplates', ReportTemplateViewSet, basename='reporttemplate')

# CRM routers
crm_router = DefaultRouter()
crm_router.register(r'email-accounts', EmailAccountViewSet, basename='emailaccount')
crm_router.register(r'communications', CommunicationViewSet, basename='communication')
crm_router.register(r'leads', LeadViewSet, basename='lead')
crm_router.register(r'lead-sources', LeadSourceViewSet, basename='leadsource')
crm_router.register(r'activities', ActivityLogViewSet, basename='activity')
crm_router.register(r'tasks', TaskViewSet, basename='task')
crm_router.register(r'task-templates', TaskTemplateViewSet, basename='tasktemplate')
crm_router.register(r'calendar-accounts', CalendarAccountViewSet, basename='calendaraccount')
crm_router.register(r'calendar-events', CalendarEventViewSet, basename='calendarevent')
crm_router.register(r'meeting-templates', MeetingTemplateViewSet, basename='meetingtemplate')

# Document Management router
document_router = DefaultRouter()
document_router.register(r'documents', DocumentViewSet, basename='document')
document_router.register(r'document-categories', DocumentCategoryViewSet, basename='documentcategory')
document_router.register(r'document-templates', DocumentTemplateViewSet, basename='documenttemplate')
document_router.register(r'document-retention-policies', DocumentRetentionPolicyViewSet, basename='documentretentionpolicy')

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_view),  # 👈 expose JWT login at root if needed
    path('auth0/login/', auth0_login, name='auth0_login'),  # Auth0 login endpoint
    path('auth0/signup/', auth0_signup, name='auth0_signup'),  # Auth0 signup endpoint
    path('auth0/debug/', auth0_debug, name='auth0_debug'),  # Auth0 debug endpoint
    path('auth0/exchange-code/', auth0_exchange_code, name='auth0_exchange_code'),  # Auth0 code exchange
    path('auth0/complete-registration/', auth0_complete_registration, name='auth0_complete_registration'),  # Auth0 registration completion
    path('validate-coupon/', validate_coupon, name='validate_coupon'),  # Validate coupon code
    path('users/', list_users, name='list_users'),  # List all users
    path('users/<int:user_id>/', user_detail, name='user_detail'),  # Get/Update/Delete user
    path('users/<int:user_id>/reset-password/', reset_user_password, name='reset_user_password'),  # Reset user password
    path('clients/', AdvisorClientListView.as_view(), name='advisor-client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit/', ClientEditView.as_view(), name='client-edit'),
    path('clients/<int:client_id>/comparison-preferences/', comparison_preferences, name='comparison-preferences'),
    path('clients/<int:client_id>/scenarios/create/', create_scenario, name='scenario-create'),
    path('scenarios/<int:scenario_id>/calculate/', run_scenario_calculation, name='scenario-calculate'),
    path('scenarios/<int:scenario_id>/assets/', get_scenario_assets, name='scenario-assets'),
    path('scenarios/<int:scenario_id>/detail/', get_scenario_detail, name='scenario-detail'),
    path('scenarios/<int:scenario_id>/edit/', get_scenario_for_editing, name='scenario-for-editing'),
    path('scenarios/<int:scenario_id>/duplicate/', duplicate_scenario, name='scenario-duplicate'),
    path('scenarios/<int:scenario_id>/comparison-data/', get_scenario_comparison_data, name='scenario-comparison-data'),
    path('scenarios/<int:scenario_id>/toggle-sharing/', views.toggle_scenario_sharing, name='scenario-toggle-sharing'),
    path('scenarios/<int:scenario_id>/update/', views.update_scenario, name='scenario-update'),
    path('scenarios/<int:scenario_id>/update-assets/', views.update_scenario_assets, name='scenario-update-assets'),
    path('scenarios/<int:scenario_id>/update-percentages/', views.update_scenario_percentages, name='scenario-update-percentages'),
    path('clients/<int:client_id>/scenarios/<int:scenario_id>/', views.delete_scenario, name='scenario-delete'),
    path('integrations/', lambda request: HttpResponse('Integrations endpoint placeholder'), name='integrations'),
   #  path('proxy/<path:path>', proxy_to_wealthbox, name='proxy_to_wealthbox'),
    path('proxy/v1/me/', proxy_to_wealthbox, name='proxy_to_wealthbox'),
    path('roth-optimize/', RothConversionAPIView.as_view(), name='roth-optimize'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register-advisor/', register_advisor, name='register_advisor'),
    path('complete-registration/', complete_registration, name='complete_registration'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('clients/<int:client_id>/realestate/', ListCreateRealEstateView.as_view(), name='realestate-list-create'),
    path('realestate/<int:pk>/', RealEstateDetailView.as_view(), name='realestate-detail'),
    
    # Include the reporttemplate router
    path('', include(reporttemplate_router.urls)),
    
    # Include CRM router
    path('', include(crm_router.urls)),
    
    # Include Document Management router
    path('', include(document_router.urls)),
    
    # CRM-specific endpoints
    path('email/gmail/auth-url/', gmail_auth_url, name='gmail-auth-url'),
    path('email/gmail/callback/', gmail_oauth_callback, name='gmail_oauth_callback'),
    path('email/outlook/auth-url/', outlook_auth_url, name='outlook-auth-url'), 
    path('email/outlook/callback/', outlook_oauth_callback, name='outlook_oauth_callback'),
    path('email/send/', send_email, name='send-email'),
    path('email/sync-all/', sync_all_emails, name='sync-all-emails'),
    path('oauth/status/', oauth_settings_status, name='oauth-settings-status'),
    
    # AI Analysis endpoints
    path('ai/analyze/<int:communication_id>/', analyze_communication, name='analyze-communication'),
    path('ai/bulk-analyze/', bulk_analyze_communications, name='bulk-analyze-communications'),
    path('ai/stats/', ai_analysis_stats, name='ai-analysis-stats'),
    path('ai/high-priority/', high_priority_communications, name='high-priority-communications'),
    path('ai/auto-analyze/', trigger_auto_analysis, name='trigger-auto-analysis'),
    
    # Calendar Integration endpoints
    path('calendar/google/auth-url/', google_calendar_auth_url, name='google-calendar-auth-url'),
    path('calendar/google/callback/', google_calendar_oauth_callback, name='google_calendar_oauth_callback'),
    path('calendar/outlook/auth-url/', outlook_calendar_auth_url, name='outlook-calendar-auth-url'),
    path('calendar/outlook/callback/', outlook_calendar_oauth_callback, name='outlook_calendar_oauth_callback'),
    path('calendar/settings/status/', calendar_settings_status, name='calendar-settings-status'),
    
    # Video Conferencing endpoints
    path('calendar/events/<int:event_id>/video-meeting/', create_video_meeting, name='create-video-meeting'),
    path('calendar/events/<int:event_id>/video-meeting/update/', update_video_meeting, name='update-video-meeting'),
    path('calendar/events/<int:event_id>/video-meeting/delete/', delete_video_meeting, name='delete-video-meeting'),
    path('calendar/events/<int:event_id>/video-meeting/join/', get_meeting_join_info, name='get-meeting-join-info'),
    path('calendar/events/<int:event_id>/jump-ai-insights/', get_jump_ai_meeting_insights, name='get-jump-ai-insights'),
    path('calendar/events/<int:event_id>/reminder/', send_meeting_reminder, name='send-meeting-reminder'),
    path('video/settings/status/', video_settings_status, name='video-settings-status'),
    
    # Celery monitoring endpoints
    path('celery/health/', celery_health_check, name='celery-health-check'),
    path('celery/task/<str:task_id>/', task_status, name='task-status'),
    path('celery/queues/', queue_monitoring, name='queue-monitoring'),
    
    # Add simplified endpoints for report templates
    path('clients/<int:client_id>/reporttemplates/', views.client_report_templates, name='client-reporttemplates'),
    path('reporttemplates/<uuid:template_id>/', views.report_template_detail, name='report-template-detail'),
    path('reporttemplates/<uuid:template_id>/slides/', views.template_slides, name='template-slides'),
    path('reporttemplates/<uuid:template_id>/update_slides/', views.update_template_slides, name='update-template-slides'),
    path('tax/federal-standard-deduction/', get_federal_standard_deduction, name='federal-standard-deduction'),
    path('tax/irmaa-thresholds/', get_irmaa_thresholds_for_years, name='irmaa-thresholds'),
    
    # Document Management endpoints
    path('documents/bulk-action/', bulk_document_action, name='bulk-document-action'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)