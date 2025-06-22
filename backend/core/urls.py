from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, logout_view, register_view, profile_view, AdvisorClientListView, ClientCreateView, ClientDetailView, ClientEditView, RothOptimizeAPIView
from .views import ScenarioCreateView, create_scenario, run_scenario_calculation, proxy_to_wealthbox, get_scenario_assets


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
    path('integrations/', lambda request: HttpResponse('Integrations endpoint placeholder'), name='integrations'),
   #  path('proxy/<path:path>', proxy_to_wealthbox, name='proxy_to_wealthbox'),
    path('proxy/v1/me/', proxy_to_wealthbox, name='proxy_to_wealthbox'),
    path('roth-optimize/', RothOptimizeAPIView.as_view(), name='roth-optimize'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)