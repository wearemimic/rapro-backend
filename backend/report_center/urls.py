from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ai_views

router = DefaultRouter()
router.register(r'templates', views.ReportTemplateViewSet, basename='reporttemplate')
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'sections', views.ReportSectionViewSet, basename='reportsection')
router.register(r'shares', views.ReportShareViewSet, basename='reportshare')
router.register(r'comments', views.ReportCommentViewSet, basename='reportcomment')
router.register(r'analytics', views.TemplateAnalyticsViewSet, basename='templateanalytics')
router.register(r'generations', views.ReportGenerationViewSet, basename='reportgeneration')

urlpatterns = [
    path('report-center/', include(router.urls)),
    
    # AI-powered content generation endpoints
    path('report-center/ai/executive-summary/', ai_views.generate_executive_summary, name='ai-executive-summary'),
    path('report-center/ai/slide-recommendations/', ai_views.generate_slide_recommendations, name='ai-slide-recommendations'),
    path('report-center/ai/content-suggestions/', ai_views.generate_content_for_section, name='ai-content-suggestions'),
    path('report-center/ai/client-insights/', ai_views.generate_client_insights, name='ai-client-insights'),
    path('report-center/ai/usage-analytics/', ai_views.get_ai_usage_analytics, name='ai-usage-analytics'),
]