"""
URL Configuration for Social Security Planning API
"""

from django.urls import path
from . import views

app_name = 'ss_planning'

urlpatterns = [
    # Preview endpoint
    path('scenarios/<int:scenario_id>/preview/', views.ss_preview, name='ss_preview'),

    # Client info endpoint
    path('scenarios/<int:scenario_id>/client-info/', views.client_info, name='client_info'),

    # Strategy management endpoints
    path('scenarios/<int:scenario_id>/strategies/', views.list_strategies, name='list_strategies'),
    path('scenarios/<int:scenario_id>/strategies/save/', views.save_strategy, name='save_strategy'),
    path('scenarios/<int:scenario_id>/strategies/compare/', views.compare_strategies, name='compare_strategies'),
]
