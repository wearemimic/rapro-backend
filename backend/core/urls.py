from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, logout_view, register_view, profile_view, AdvisorClientListView, ClientCreateView, ClientDetailView, ClientEditView, RothConversionAPIView, register_advisor, complete_registration
from .views import ScenarioCreateView, create_scenario, run_scenario_calculation, proxy_to_wealthbox, get_scenario_assets
from .views import ListCreateRealEstateView, RealEstateDetailView, ReportTemplateViewSet
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .webhooks import stripe_webhook
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

# Create a router for ReportTemplateViewSet
reporttemplate_router = DefaultRouter()
reporttemplate_router.register(r'reporttemplates', ReportTemplateViewSet, basename='reporttemplate')

urlpatterns = [
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('login/', login_view),  # 👈 expose JWT login at root if needed
    path('clients/', AdvisorClientListView.as_view(), name='advisor-client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit/', ClientEditView.as_view(), name='client-edit'),
    path('clients/<int:client_id>/scenarios/create/', create_scenario, name='scenario-create'),
    path('scenarios/<int:scenario_id>/calculate/', run_scenario_calculation, name='scenario-calculate'),
    path('scenarios/<int:scenario_id>/assets/', get_scenario_assets, name='scenario-assets'),
    path('scenarios/<int:scenario_id>/update/', views.update_scenario, name='scenario-update'),
    path('scenarios/<int:scenario_id>/update-assets/', views.update_scenario_assets, name='scenario-update-assets'),
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
    path('api/', include(reporttemplate_router.urls)),
    
    # Add simplified endpoints for report templates
    path('clients/<int:client_id>/reporttemplates/', views.client_report_templates, name='client-reporttemplates'),
    path('reporttemplates/<uuid:template_id>/', views.report_template_detail, name='report-template-detail'),
    path('reporttemplates/<uuid:template_id>/slides/', views.template_slides, name='template-slides'),
    path('reporttemplates/<uuid:template_id>/update_slides/', views.update_template_slides, name='update-template-slides'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)