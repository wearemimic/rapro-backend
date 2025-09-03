from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views_main import login_view, logout_view, register_view, profile_view, AdvisorClientListView, ClientCreateView, ClientDetailView, ClientEditView, RothConversionAPIView, register_advisor, complete_registration, mock_report_templates, mock_reports, mock_generate_report, mock_report_status
from . import report_views
from .views_main import ScenarioCreateView, create_scenario, run_scenario_calculation, start_scenario_calculation_async, get_task_status, cancel_task, proxy_to_wealthbox, get_scenario_assets, duplicate_scenario, get_scenario_detail, get_scenario_for_editing, get_scenario_comparison_data, comparison_preferences, get_federal_standard_deduction, get_irmaa_thresholds_for_years, medicare_inflation_rates
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
from .auth0_views import auth0_login_redirect, auth0_login_google, auth0_callback, auth0_logout, auth0_exchange_code, complete_professional_info, auth0_complete_registration, validate_coupon, embedded_signup, create_account
from .admin_views import (
    admin_dashboard_stats, admin_user_list, update_user_admin_role, admin_analytics_overview, 
    admin_system_monitoring, admin_support_overview, start_user_impersonation, 
    end_user_impersonation, get_active_impersonation_sessions, delete_user_complete,
    admin_revenue_analytics, admin_recalculate_revenue_metrics, admin_user_engagement_analytics,
    admin_client_portfolio_analytics, admin_run_analytics_calculation, admin_billing_data,
    # Phase 2.3: System Performance Monitoring
    admin_performance_metrics, admin_record_performance_metric, admin_system_health_dashboard,
    # Phase 2.4: Support Ticket System
    admin_support_tickets_list, admin_support_ticket_detail, admin_create_support_ticket,
    admin_update_support_ticket, admin_add_ticket_comment, admin_support_sla_report,
    # Phase 2.5: Alert & Notification System  
    admin_alert_rules_list, admin_create_alert_rule, admin_update_alert_rule, 
    admin_delete_alert_rule, admin_alert_notifications_list, admin_test_alert_rule,
    # Phase 3.1: Tax Data Management
    admin_tax_data_files_list, admin_tax_data_file_content, admin_upload_tax_data_file,
    admin_update_tax_data_file, admin_validate_tax_data_file, admin_tax_data_backups_list,
    admin_restore_tax_data_backup, admin_tax_data_validation_rules,
    # Phase 3.2: Configuration Management
    FeatureFlagViewSet, SystemConfigurationViewSet, IntegrationSettingsViewSet,
    EmailTemplateViewSet, ConfigurationAuditLogViewSet, configuration_summary
)

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

# Configuration Management router
config_router = DefaultRouter()
config_router.register(r'admin/feature-flags', FeatureFlagViewSet, basename='featureflag')
config_router.register(r'admin/system-configs', SystemConfigurationViewSet, basename='systemconfiguration')
config_router.register(r'admin/integrations', IntegrationSettingsViewSet, basename='integrationsettings')
config_router.register(r'admin/email-templates', EmailTemplateViewSet, basename='emailtemplate')
config_router.register(r'admin/config-audit', ConfigurationAuditLogViewSet, basename='configurationauditlog')

# Analytics & Reporting router
from .views.analytics_views import (
    CustomReportViewSet, ReportScheduleViewSet, ReportExecutionViewSet,
    ExecutiveDashboardViewSet, analytics_summary
)

analytics_router = DefaultRouter()
analytics_router.register(r'admin/reports', CustomReportViewSet, basename='customreport')
analytics_router.register(r'admin/report-schedules', ReportScheduleViewSet, basename='reportschedule')
analytics_router.register(r'admin/report-executions', ReportExecutionViewSet, basename='reportexecution')
analytics_router.register(r'admin/dashboards', ExecutiveDashboardViewSet, basename='executivedashboard')

# Communication Tools router
from .views.communication_views import (
    BroadcastMessageViewSet, EmailCampaignViewSet, InAppNotificationViewSet,
    MaintenanceModeViewSet, UserFeedbackViewSet, FeedbackResponseViewSet,
    communication_summary
)

communication_router = DefaultRouter()
communication_router.register(r'admin/broadcasts', BroadcastMessageViewSet, basename='broadcastmessage')
communication_router.register(r'admin/campaigns', EmailCampaignViewSet, basename='emailcampaign')
communication_router.register(r'notifications', InAppNotificationViewSet, basename='inappnotification')
communication_router.register(r'admin/maintenance', MaintenanceModeViewSet, basename='maintenancemode')
communication_router.register(r'feedback', UserFeedbackViewSet, basename='userfeedback')
communication_router.register(r'admin/feedback-responses', FeedbackResponseViewSet, basename='feedbackresponse')

# Phase 4: Optimization & Enhancement router
from .views.workflow_views import (
    WorkflowViewSet, SearchViewSet, FilterPresetViewSet, workflow_dashboard
)

workflow_router = DefaultRouter()
workflow_router.register(r'admin/workflows', WorkflowViewSet, basename='workflow')
workflow_router.register(r'admin/search', SearchViewSet, basename='search')
workflow_router.register(r'admin/search/filter-presets', FilterPresetViewSet, basename='filterpreset')

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_view),  # 👈 expose JWT login at root if needed
    # Clean Django Regular Web Application Auth0 endpoints
    path('auth0/login-redirect/', auth0_login_redirect, name='auth0_login_redirect'),  # Auth0 login redirect
    path('auth0/login-google/', auth0_login_google, name='auth0_login_google'),  # Auth0 Google login redirect
    path('auth0/callback/', auth0_callback, name='auth0_callback'),  # Auth0 callback handler
    path('auth0/logout/', auth0_logout, name='auth0_logout'),  # Auth0 logout redirect
    path('auth0/exchange-code/', auth0_exchange_code, name='auth0_exchange_code'),  # Frontend calls this to exchange code
    path('auth0/embedded-signup/', embedded_signup, name='embedded_signup'),  # Embedded signup without redirects
    path('auth0/create-account/', create_account, name='create_account'),  # Create Auth0 account only (no auth)
    path('auth0/complete-professional-info/', complete_professional_info, name='complete_professional_info'),  # Professional info step
    path('auth0/complete-registration/', auth0_complete_registration, name='auth0_complete_registration'),  # Registration completion with Stripe
    path('validate-coupon/', validate_coupon, name='validate_coupon'),  # Coupon validation
    path('clients/', AdvisorClientListView.as_view(), name='advisor-client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit/', ClientEditView.as_view(), name='client-edit'),
    path('clients/<int:client_id>/comparison-preferences/', comparison_preferences, name='comparison-preferences'),
    path('clients/<int:client_id>/scenarios/create/', create_scenario, name='scenario-create'),
    path('scenarios/<int:scenario_id>/calculate/', run_scenario_calculation, name='scenario-calculate'),
    path('scenarios/<int:scenario_id>/calculate-async/', start_scenario_calculation_async, name='scenario-calculate-async'),
    path('tasks/<str:task_id>/status/', get_task_status, name='task-status'),
    path('tasks/<str:task_id>/cancel/', cancel_task, name='task-cancel'),
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
    
    # Include Configuration Management router
    path('', include(config_router.urls)),
    
    # Include Analytics & Reporting router
    path('', include(analytics_router.urls)),
    
    # Include Communication Tools router
    path('', include(communication_router.urls)),
    
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
    path('medicare/inflation-rates/', medicare_inflation_rates, name='medicare-inflation-rates'),
    
    # Document Management endpoints
    path('documents/bulk-action/', bulk_document_action, name='bulk-document-action'),
    
    # Admin API endpoints
    path('admin/stats/', admin_dashboard_stats, name='admin-dashboard-stats'),
    path('admin/users/', admin_user_list, name='admin-user-list'),
    path('admin/users/<int:user_id>/admin-role/', update_user_admin_role, name='update-user-admin-role'),
    path('admin/users/<int:user_id>/impersonate/', start_user_impersonation, name='start-user-impersonation'),
    path('admin/users/<int:user_id>/delete/', delete_user_complete, name='delete-user-complete'),
    path('admin/impersonation/<int:session_id>/end/', end_user_impersonation, name='end-user-impersonation'),
    path('admin/impersonation/active/', get_active_impersonation_sessions, name='get-active-impersonation-sessions'),
    path('admin/analytics/', admin_analytics_overview, name='admin-analytics-overview'),
    path('admin/monitoring/', admin_system_monitoring, name='admin-system-monitoring'),
    path('admin/support/', admin_support_overview, name='admin-support-overview'),
    
    # Phase 2: Enhanced Analytics API endpoints
    path('admin/analytics/revenue/', admin_revenue_analytics, name='admin-revenue-analytics'),
    path('admin/analytics/revenue/recalculate/', admin_recalculate_revenue_metrics, name='admin-recalculate-revenue-metrics'),
    path('admin/analytics/engagement/', admin_user_engagement_analytics, name='admin-user-engagement-analytics'),
    path('admin/analytics/portfolio/', admin_client_portfolio_analytics, name='admin-client-portfolio-analytics'),
    path('admin/analytics/calculate/', admin_run_analytics_calculation, name='admin-run-analytics-calculation'),
    
    # Billing Management API endpoints
    path('admin/billing/', admin_billing_data, name='admin-billing-data'),
    
    # Phase 2.3: System Performance Monitoring
    path('admin/performance/metrics/', admin_performance_metrics, name='admin-performance-metrics'),
    path('admin/performance/record/', admin_record_performance_metric, name='admin-record-performance-metric'),
    path('admin/performance/health/', admin_system_health_dashboard, name='admin-system-health-dashboard'),
    
    # Phase 2.4: Support Ticket System
    path('admin/support/tickets/', admin_support_tickets_list, name='admin-support-tickets-list'),
    path('admin/support/tickets/<int:ticket_id>/', admin_support_ticket_detail, name='admin-support-ticket-detail'),
    path('admin/support/tickets/create/', admin_create_support_ticket, name='admin-create-support-ticket'),
    path('admin/support/tickets/<int:ticket_id>/update/', admin_update_support_ticket, name='admin-update-support-ticket'),
    path('admin/support/tickets/<int:ticket_id>/comment/', admin_add_ticket_comment, name='admin-add-ticket-comment'),
    path('admin/support/sla-report/', admin_support_sla_report, name='admin-support-sla-report'),
    
    # Phase 2.5: Alert & Notification System
    path('admin/alerts/rules/', admin_alert_rules_list, name='admin-alert-rules-list'),
    path('admin/alerts/rules/create/', admin_create_alert_rule, name='admin-create-alert-rule'),
    path('admin/alerts/rules/<int:rule_id>/', admin_update_alert_rule, name='admin-update-alert-rule'),
    path('admin/alerts/rules/<int:rule_id>/delete/', admin_delete_alert_rule, name='admin-delete-alert-rule'),
    path('admin/alerts/rules/<int:rule_id>/test/', admin_test_alert_rule, name='admin-test-alert-rule'),
    path('admin/alerts/notifications/', admin_alert_notifications_list, name='admin-alert-notifications-list'),
    
    # Phase 3.1: Tax Data Management
    path('admin/tax-data/files/', admin_tax_data_files_list, name='admin-tax-data-files-list'),
    path('admin/tax-data/files/<str:filename>/', admin_tax_data_file_content, name='admin-tax-data-file-content'),
    path('admin/tax-data/upload/', admin_upload_tax_data_file, name='admin-upload-tax-data-file'),
    path('admin/tax-data/files/<str:filename>/update/', admin_update_tax_data_file, name='admin-update-tax-data-file'),
    path('admin/tax-data/validate/', admin_validate_tax_data_file, name='admin-validate-tax-data-file'),
    path('admin/tax-data/backups/', admin_tax_data_backups_list, name='admin-tax-data-backups-list'),
    path('admin/tax-data/backups/<str:backup_filename>/restore/', admin_restore_tax_data_backup, name='admin-restore-tax-data-backup'),
    path('admin/tax-data/validation-rules/', admin_tax_data_validation_rules, name='admin-tax-data-validation-rules'),
    
    # Phase 3.2: Configuration Management
    path('admin/config-summary/', configuration_summary, name='admin-configuration-summary'),
    
    # Phase 3.3: Analytics & Reporting
    path('admin/analytics-summary/', analytics_summary, name='admin-analytics-summary'),
    
    # Phase 3.4: Communication Tools
    path('admin/communication-summary/', communication_summary, name='admin-communication-summary'),
    
    # Phase 4: Optimization & Enhancement
    path('admin/workflows/dashboard/', workflow_dashboard, name='admin-workflows-dashboard'),
    
    # Report Center endpoints - PRODUCTION READY
    path('report-center/reports/<uuid:report_id>/download/', report_views.download_report, name='download-report'),
    path('report-center/templates/', report_views.ReportTemplateListView.as_view(), name='report-templates'),
    path('report-center/reports/', report_views.ReportListView.as_view(), name='report-list'),
    path('report-center/reports/<uuid:report_id>/generate/', report_views.generate_report, name='generate-report'),
    path('report-center/reports/<uuid:report_id>/status/', report_views.report_status, name='report-status'),
    path('report-center/data/<int:client_id>/', report_views.report_data, name='report-data'),
]

# Add router URLs
urlpatterns += reporttemplate_router.urls
urlpatterns += crm_router.urls
urlpatterns += document_router.urls
urlpatterns += config_router.urls
urlpatterns += analytics_router.urls
urlpatterns += communication_router.urls
urlpatterns += workflow_router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)