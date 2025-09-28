from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    LTCAssessment,
    LTCCostProjection,
    InsuranceProduct,
    InsuranceIllustration,
    LTCCostCoverageComparison,
    LTCAIConversation,
    LTCClientPresentation,
    LTCFacilityRecommendation,
)
from .serializers import (
    LTCAssessmentSerializer,
    LTCAssessmentListSerializer,
    LTCCostProjectionSerializer,
    LTCCostProjectionListSerializer,
    InsuranceProductSerializer,
    InsuranceIllustrationSerializer,
    LTCCostCoverageComparisonSerializer,
    LTCAIConversationSerializer,
    LTCClientPresentationSerializer,
    LTCFacilityRecommendationSerializer,
)


class LTCAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LTC Assessments
    Provides CRUD operations and custom actions for assessments
    """
    queryset = LTCAssessment.objects.all()
    serializer_class = LTCAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use lightweight serializer for list action"""
        if self.action == 'list':
            return LTCAssessmentListSerializer
        return LTCAssessmentSerializer

    def get_queryset(self):
        """Filter by client_id if provided"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

    @action(detail=True, methods=['get'])
    def calculate_scores(self, request, pk=None):
        """
        Calculate ADL and IADL scores for an assessment
        GET /api/ltc/assessments/<id>/calculate_scores/
        """
        assessment = self.get_object()
        return Response({
            'adl_score': assessment.calculate_adl_score(),
            'iadl_score': assessment.calculate_iadl_score(),
            'total_score': assessment.calculate_adl_score() + assessment.calculate_iadl_score()
        })


class LTCCostProjectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LTC Cost Projections
    """
    queryset = LTCCostProjection.objects.all()
    serializer_class = LTCCostProjectionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use lightweight serializer for list action"""
        if self.action == 'list':
            return LTCCostProjectionListSerializer
        return LTCCostProjectionSerializer

    def get_queryset(self):
        """Filter by client_id if provided"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

    @action(detail=False, methods=['post'])
    def generate_projection(self, request):
        """
        Generate a new cost projection
        POST /api/ltc/cost-projections/generate_projection/

        Body:
        {
            "client_id": "uuid",
            "assessment_id": "uuid" (optional),
            "years_to_project": 20,
            "state_code": "CA",
            "start_age": 65,
            "scenario_type": "likely",
            "starting_assets": 500000 (optional),
            "annual_income": 50000 (optional),
            "generate_all_scenarios": false
        }
        """
        from ltc_planning.services.cost_projection import CostProjectionService
        from clients.models import Client

        client_id = request.data.get('client_id')
        assessment_id = request.data.get('assessment_id')
        years_to_project = request.data.get('years_to_project', 20)
        state_code = request.data.get('state_code')
        start_age = request.data.get('start_age', 65)
        scenario_type = request.data.get('scenario_type', 'likely')
        generate_all_scenarios = request.data.get('generate_all_scenarios', False)
        starting_assets = request.data.get('starting_assets')
        annual_income = request.data.get('annual_income', 0)

        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not state_code:
            return Response(
                {'error': 'state_code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        assessment = None
        care_level = 'assisted_living'

        if assessment_id:
            try:
                assessment = LTCAssessment.objects.get(id=assessment_id)
                care_level = assessment.care_level_recommendation
            except LTCAssessment.DoesNotExist:
                return Response(
                    {'error': 'Assessment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        projection_service = CostProjectionService()

        try:
            if generate_all_scenarios:
                result = projection_service.generate_multiple_scenarios(
                    care_level=care_level,
                    state_code=state_code,
                    years_projected=years_to_project,
                    start_age=start_age
                )

                for scenario_name, scenario_data in result['scenarios'].items():
                    projection = LTCCostProjection.objects.create(
                        client=client,
                        assessment=assessment,
                        scenario_name=scenario_data['scenario_name'],
                        years_projected=years_to_project,
                        state=state_code,
                        start_age=start_age,
                        care_level=care_level,
                        scenario_type=scenario_name,
                        annual_cost_projections=scenario_data['annual_projections'],
                        total_lifetime_cost=scenario_data['total_lifetime_cost'],
                        regional_multiplier=scenario_data['regional_multiplier'],
                        care_progression=scenario_data['care_progression']
                    )

                return Response({
                    'message': 'Multiple scenarios generated successfully',
                    'scenarios': result['scenarios'],
                    'comparison': result['comparison']
                }, status=status.HTTP_201_CREATED)
            else:
                projection_data = projection_service.generate_projection(
                    care_level=care_level,
                    state_code=state_code,
                    years_projected=years_to_project,
                    start_age=start_age,
                    scenario_type=scenario_type
                )

                projection = LTCCostProjection.objects.create(
                    client=client,
                    assessment=assessment,
                    scenario_name=projection_data['scenario_name'],
                    years_projected=years_to_project,
                    state=state_code,
                    start_age=start_age,
                    care_level=care_level,
                    scenario_type=scenario_type,
                    annual_cost_projections=projection_data['annual_projections'],
                    total_lifetime_cost=projection_data['total_lifetime_cost'],
                    regional_multiplier=projection_data['regional_multiplier'],
                    care_progression=projection_data['care_progression']
                )

                response_data = {
                    'projection_id': str(projection.id),
                    **projection_data
                }

                if starting_assets:
                    asset_analysis = projection_service.estimate_asset_depletion(
                        projection_data,
                        starting_assets,
                        annual_income
                    )
                    response_data['asset_depletion_analysis'] = asset_analysis

                serializer = self.get_serializer(projection)
                return Response(response_data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate projection: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InsuranceProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Insurance Products
    """
    queryset = InsuranceProduct.objects.all()
    serializer_class = InsuranceProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by carrier or state if provided"""
        queryset = super().get_queryset()
        carrier = self.request.query_params.get('carrier')
        state = self.request.query_params.get('state')
        is_active = self.request.query_params.get('is_active')

        if carrier:
            queryset = queryset.filter(carrier__icontains=carrier)
        if state:
            queryset = queryset.filter(available_states__contains=[state])
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))

        return queryset


class InsuranceIllustrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Insurance Illustrations
    """
    queryset = InsuranceIllustration.objects.all()
    serializer_class = InsuranceIllustrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by client_id if provided"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

    @action(detail=False, methods=['post'])
    def upload_illustration(self, request):
        """
        Upload and parse an insurance illustration PDF
        POST /api/ltc/illustrations/upload_illustration/

        Form data:
        - file: PDF file
        - client_id: UUID
        """
        # TODO: Implement PDF upload and parsing logic
        # This will be implemented in Phase 4
        return Response(
            {'message': 'Illustration upload not yet implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class LTCCostCoverageComparisonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cost vs Coverage Comparisons
    """
    queryset = LTCCostCoverageComparison.objects.all()
    serializer_class = LTCCostCoverageComparisonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by client through cost projection"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(cost_projection__client_id=client_id)
        return queryset

    @action(detail=False, methods=['post'])
    def generate_comparison(self, request):
        """
        Generate cost vs coverage comparison
        POST /api/ltc/comparisons/generate_comparison/

        Body:
        {
            "cost_projection_id": "uuid",
            "insurance_product": {insurance product object} OR "illustration_id": "uuid",
            "client_assets": 500000,
            "annual_income": 50000
        }
        """
        from ltc_planning.services.comparison_service import ComparisonService

        cost_projection_id = request.data.get('cost_projection_id')
        insurance_product_data = request.data.get('insurance_product')
        illustration_id = request.data.get('illustration_id')
        client_assets = request.data.get('client_assets', 0)
        annual_income = request.data.get('annual_income', 0)

        if not cost_projection_id:
            return Response(
                {'error': 'cost_projection_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cost_projection = LTCCostProjection.objects.get(id=cost_projection_id)
        except LTCCostProjection.DoesNotExist:
            return Response(
                {'error': 'Cost projection not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if illustration_id:
            try:
                illustration = InsuranceIllustration.objects.get(id=illustration_id)
                insurance_product_data = illustration.parsed_data
            except InsuranceIllustration.DoesNotExist:
                return Response(
                    {'error': 'Illustration not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        if not insurance_product_data:
            return Response(
                {'error': 'Either insurance_product or illustration_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cost_projection_data = {
            'annual_projections': cost_projection.annual_cost_projections,
            'years_projected': cost_projection.years_projected,
            'total_lifetime_cost': float(cost_projection.total_lifetime_cost)
        }

        comparison_service = ComparisonService()

        try:
            comparison_result = comparison_service.generate_comparison(
                cost_projection_data,
                insurance_product_data,
                client_assets,
                annual_income
            )

            comparison = LTCCostCoverageComparison.objects.create(
                cost_projection=cost_projection,
                insurance_illustration_id=illustration_id if illustration_id else None,
                comparison_data=comparison_result,
                out_of_pocket_gap=comparison_result['summary']['coverage_gap'],
                coverage_ratio_percent=comparison_result['summary']['coverage_ratio_percent']
            )

            serializer = self.get_serializer(comparison)
            return Response({
                'comparison_id': str(comparison.id),
                **comparison_result
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Failed to generate comparison: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LTCAIConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AI Conversations
    """
    queryset = LTCAIConversation.objects.all()
    serializer_class = LTCAIConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by client_id if provided"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        """
        Start a new AI-assisted assessment conversation
        POST /api/ltc/ai-conversations/start_conversation/

        Body:
        {
            "client_id": "uuid",
            "initial_message": "I have a 70-year-old father who needs long-term care" (optional)
        }
        """
        from ltc_planning.services.ai_assistant import LTCAIAssistant
        from clients.models import Client

        client_id = request.data.get('client_id')
        initial_message = request.data.get('initial_message', '')

        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        ai_assistant = LTCAIAssistant()

        client_info = {
            'name': f"{client.first_name} {client.last_name}",
            'age': getattr(client, 'age', None)
        }

        result = ai_assistant.start_new_conversation(client_info)

        if result['success']:
            conversation = LTCAIConversation.objects.create(
                client=client,
                advisor=request.user,
                conversation_history=[
                    {
                        'role': 'assistant',
                        'content': result['assistant_message'],
                        'timestamp': str(timezone.now())
                    }
                ],
                extracted_data={},
                current_intent='greeting'
            )

            if initial_message:
                continue_result = ai_assistant.continue_conversation(
                    initial_message,
                    conversation.conversation_history,
                    conversation.extracted_data
                )

                if continue_result['success']:
                    conversation.conversation_history.extend([
                        {
                            'role': 'user',
                            'content': initial_message,
                            'timestamp': str(timezone.now())
                        },
                        {
                            'role': 'assistant',
                            'content': continue_result['assistant_message'],
                            'timestamp': str(timezone.now())
                        }
                    ])
                    conversation.extracted_data = continue_result['extracted_data']
                    conversation.current_intent = continue_result['intent']
                    conversation.save()

                    serializer = self.get_serializer(conversation)
                    return Response({
                        **serializer.data,
                        'next_question': continue_result.get('next_question', '')
                    }, status=status.HTTP_201_CREATED)

            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result.get('error', 'Failed to start conversation')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def continue_conversation(self, request, pk=None):
        """
        Continue an existing AI conversation
        POST /api/ltc/ai-conversations/<id>/continue_conversation/

        Body:
        {
            "message": "He lives alone and has difficulty bathing"
        }
        """
        from ltc_planning.services.ai_assistant import LTCAIAssistant

        conversation = self.get_object()
        user_message = request.data.get('message', '')

        if not user_message:
            return Response(
                {'error': 'message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ai_assistant = LTCAIAssistant()

        result = ai_assistant.continue_conversation(
            user_message,
            conversation.conversation_history,
            conversation.extracted_data
        )

        if result['success']:
            conversation.conversation_history.extend([
                {
                    'role': 'user',
                    'content': user_message,
                    'timestamp': str(timezone.now())
                },
                {
                    'role': 'assistant',
                    'content': result['assistant_message'],
                    'timestamp': str(timezone.now())
                }
            ])

            conversation.extracted_data = result['extracted_data']
            conversation.current_intent = result['intent']

            if result['intent'] == 'end_conversation':
                conversation.status = 'completed'

                adl_score = ai_assistant._calculate_adl_impairment(
                    result['extracted_data'].get('adl_scores', {})
                )
                iadl_score = ai_assistant._calculate_iadl_impairment(
                    result['extracted_data'].get('iadl_scores', {})
                )
                cognitive_status = result['extracted_data'].get('cognitive_status', 'unknown')
                care_level = ai_assistant._determine_care_level(adl_score, iadl_score, cognitive_status)

                assessment_data = {
                    'assessment_score_adl': result['extracted_data'].get('adl_scores', {}),
                    'assessment_score_iadl': result['extracted_data'].get('iadl_scores', {}),
                    'health_conditions': result['extracted_data'].get('health_conditions', []),
                    'cognitive_status': cognitive_status,
                    'care_level_recommendation': care_level,
                    'living_situation': result['extracted_data'].get('living_situation', ''),
                }

                try:
                    assessment = LTCAssessment.objects.create(
                        client=conversation.client,
                        advisor=conversation.advisor,
                        assessment_type='ai_assisted',
                        **assessment_data
                    )
                    conversation.assessment = assessment
                except Exception as e:
                    print(f"Error creating assessment: {str(e)}")

            conversation.save()

            serializer = self.get_serializer(conversation)
            return Response({
                **serializer.data,
                'next_question': result.get('next_question', ''),
                'tokens_used': result.get('tokens_used', 0)
            })
        else:
            return Response(
                {'error': result.get('error', 'Failed to continue conversation')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LTCClientPresentationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Client Presentations
    """
    queryset = LTCClientPresentation.objects.all()
    serializer_class = LTCClientPresentationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by client_id if provided"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        return queryset

    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """
        Generate PDF report for presentation
        POST /api/ltc/presentations/<id>/generate_pdf/
        """
        # TODO: Implement PDF generation
        # Note: Phase 5 (Presentation) was removed from build plan
        return Response(
            {'message': 'PDF generation not yet implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class LTCFacilityRecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Facility Recommendations
    """
    queryset = LTCFacilityRecommendation.objects.all()
    serializer_class = LTCFacilityRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter by client_id, state, or facility_type"""
        queryset = super().get_queryset()
        client_id = self.request.query_params.get('client_id')
        state = self.request.query_params.get('state')
        facility_type = self.request.query_params.get('facility_type')

        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if state:
            queryset = queryset.filter(state=state)
        if facility_type:
            queryset = queryset.filter(facility_type=facility_type)

        return queryset

    @action(detail=False, methods=['post'])
    def search_facilities(self, request):
        """
        Search for facilities based on criteria
        POST /api/ltc/facilities/search_facilities/

        Body:
        {
            "client_id": "uuid",
            "facility_type": "assisted_living",
            "zip_code": "90210",
            "radius_miles": 25,
            "max_monthly_cost": 5000
        }
        """
        # TODO: Implement facility search logic
        return Response(
            {'message': 'Facility search not yet implemented'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )