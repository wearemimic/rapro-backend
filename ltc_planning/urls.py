from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LTCAssessmentViewSet,
    LTCCostProjectionViewSet,
    InsuranceProductViewSet,
    InsuranceIllustrationViewSet,
    LTCCostCoverageComparisonViewSet,
    LTCAIConversationViewSet,
    LTCClientPresentationViewSet,
    LTCFacilityRecommendationViewSet,
)

app_name = 'ltc_planning'

router = DefaultRouter()
router.register(r'assessments', LTCAssessmentViewSet, basename='ltc-assessment')
router.register(r'cost-projections', LTCCostProjectionViewSet, basename='ltc-cost-projection')
router.register(r'insurance-products', InsuranceProductViewSet, basename='insurance-product')
router.register(r'illustrations', InsuranceIllustrationViewSet, basename='insurance-illustration')
router.register(r'comparisons', LTCCostCoverageComparisonViewSet, basename='ltc-comparison')
router.register(r'ai-conversations', LTCAIConversationViewSet, basename='ai-conversation')
router.register(r'presentations', LTCClientPresentationViewSet, basename='client-presentation')
router.register(r'facilities', LTCFacilityRecommendationViewSet, basename='facility-recommendation')

urlpatterns = [
    path('', include(router.urls)),
]