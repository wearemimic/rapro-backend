"""
AI Views for Report Center
Provides API endpoints for AI-powered content generation and analysis
"""

import logging
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta

from django.utils import timezone
from django.db.models import Sum, Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Client, Scenario
from ..services.ai_report_service import get_ai_report_service
from ..models import Report, AIUsageTracking

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_executive_summary(request):
    """
    Generate AI-powered executive summary for a scenario
    
    POST /api/report-center/ai/executive-summary/
    Body: {
        "client_id": int,
        "scenario_id": int,
        "report_id": str (optional)
    }
    """
    try:
        client_id = request.data.get('client_id')
        scenario_id = request.data.get('scenario_id')
        report_id = request.data.get('report_id')
        
        if not client_id or not scenario_id:
            return Response(
                {'error': 'client_id and scenario_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get client and scenario data
        try:
            client = Client.objects.get(id=client_id, advisor=request.user)
            scenario = Scenario.objects.get(id=scenario_id, client=client)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Scenario.DoesNotExist:
            return Response(
                {'error': 'Scenario not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare data for AI service
        client_data = _serialize_client_for_ai(client)
        scenario_data = _serialize_scenario_for_ai(scenario)
        
        # Generate summary using AI service
        ai_service = get_ai_report_service()
        result = ai_service.generate_executive_summary(scenario_data, client_data)
        
        # Track usage
        _track_ai_usage(
            user=request.user,
            feature='executive_summary',
            cost=result.get('cost', 0),
            tokens=result.get('tokens_used', 0),
            report_id=report_id
        )
        
        return Response({
            'summary': result['summary'],
            'confidence': result.get('confidence', 0.9),
            'generated_at': timezone.now().isoformat(),
            'cached': result.get('cached', False)
        })
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {str(e)}")
        return Response(
            {'error': 'Failed to generate executive summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_slide_recommendations(request):
    """
    Generate AI-powered slide order recommendations
    
    POST /api/report-center/ai/slide-recommendations/
    Body: {
        "client_id": int,
        "scenario_id": int,
        "report_id": str (optional)
    }
    """
    try:
        client_id = request.data.get('client_id')
        scenario_id = request.data.get('scenario_id')
        report_id = request.data.get('report_id')
        
        if not client_id or not scenario_id:
            return Response(
                {'error': 'client_id and scenario_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get client and scenario data
        try:
            client = Client.objects.get(id=client_id, advisor=request.user)
            scenario = Scenario.objects.get(id=scenario_id, client=client)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Scenario.DoesNotExist:
            return Response(
                {'error': 'Scenario not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare data for AI service
        client_profile = _serialize_client_profile_for_ai(client, scenario)
        scenario_results = _serialize_scenario_results_for_ai(scenario)
        
        # Generate recommendations using AI service
        ai_service = get_ai_report_service()
        recommendations = ai_service.recommend_slide_order(client_profile, scenario_results)
        
        # Track usage (estimated cost since we don't have actual usage from the service)
        _track_ai_usage(
            user=request.user,
            feature='slide_recommendations',
            cost=0.05,  # Estimated cost
            tokens=400,  # Estimated tokens
            report_id=report_id
        )
        
        return Response({
            'recommendations': recommendations,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating slide recommendations: {str(e)}")
        return Response(
            {'error': 'Failed to generate slide recommendations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_content_for_section(request):
    """
    Generate AI content for specific report sections
    
    POST /api/report-center/ai/content-suggestions/
    Body: {
        "section_type": str,  # e.g., "risk_explanation", "irmaa_impact"
        "data": dict,         # Relevant data for the section
        "tone": str,          # Optional: "professional", "friendly", "technical"
        "report_id": str      # Optional
    }
    """
    try:
        section_type = request.data.get('section_type')
        data = request.data.get('data', {})
        tone = request.data.get('tone', 'professional')
        report_id = request.data.get('report_id')
        
        if not section_type:
            return Response(
                {'error': 'section_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate content using AI service
        ai_service = get_ai_report_service()
        content = ai_service.generate_content_for_section(section_type, data, tone)
        
        if not content:
            return Response(
                {'error': f'Content generation not available for section type: {section_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Track usage
        _track_ai_usage(
            user=request.user,
            feature=f'content_{section_type}',
            cost=0.03,  # Estimated cost
            tokens=300,  # Estimated tokens
            report_id=report_id
        )
        
        return Response({
            'content': content,
            'section_type': section_type,
            'tone': tone,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating content for {section_type}: {str(e)}")
        return Response(
            {'error': 'Failed to generate section content'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_client_insights(request):
    """
    Generate AI-powered client insights and analysis
    
    POST /api/report-center/ai/client-insights/
    Body: {
        "client_id": int,
        "scenario_id": int,
        "report_id": str (optional)
    }
    """
    try:
        client_id = request.data.get('client_id')
        scenario_id = request.data.get('scenario_id')
        report_id = request.data.get('report_id')
        
        if not client_id or not scenario_id:
            return Response(
                {'error': 'client_id and scenario_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get client and scenario data
        try:
            client = Client.objects.get(id=client_id, advisor=request.user)
            scenario = Scenario.objects.get(id=scenario_id, client=client)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Scenario.DoesNotExist:
            return Response(
                {'error': 'Scenario not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare data for AI service
        client_data = _serialize_client_for_ai(client)
        scenario_data = _serialize_scenario_for_ai(scenario)
        
        # Generate insights using AI service
        ai_service = get_ai_report_service()
        insights = ai_service.analyze_client_insights(client_data, scenario_data)
        
        # Track usage
        _track_ai_usage(
            user=request.user,
            feature='client_insights',
            cost=insights.get('cost', 0.04),
            tokens=350,  # Estimated tokens
            report_id=report_id
        )
        
        return Response(insights)
        
    except Exception as e:
        logger.error(f"Error generating client insights: {str(e)}")
        return Response(
            {'error': 'Failed to generate client insights'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_usage_analytics(request):
    """
    Get AI usage analytics for the current user
    
    GET /api/report-center/ai/usage-analytics/
    Query params:
        - days: int (default: 30) - number of days to look back
        - feature: str (optional) - filter by specific feature
    """
    try:
        days = int(request.GET.get('days', 30))
        feature_filter = request.GET.get('feature')
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        queryset = AIUsageTracking.objects.filter(
            user=request.user,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        # Apply feature filter if provided
        if feature_filter:
            queryset = queryset.filter(feature=feature_filter)
        
        # Calculate aggregations
        totals = queryset.aggregate(
            total_cost=Sum('cost'),
            total_tokens=Sum('tokens_used'),
            total_requests=Count('id')
        )
        
        # Get usage by feature
        by_feature = list(queryset.values('feature').annotate(
            cost=Sum('cost'),
            tokens=Sum('tokens_used'),
            requests=Count('id')
        ).order_by('-cost'))
        
        # Get daily usage for trend analysis
        daily_usage = {}
        for usage in queryset.values('timestamp__date').annotate(
            cost=Sum('cost'),
            tokens=Sum('tokens_used'),
            requests=Count('id')
        ).order_by('timestamp__date'):
            date_str = usage['timestamp__date'].isoformat()
            daily_usage[date_str] = {
                'cost': float(usage['cost']),
                'tokens': usage['tokens'],
                'requests': usage['requests']
            }
        
        return Response({
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            },
            'totals': {
                'cost': float(totals['total_cost'] or 0),
                'tokens': totals['total_tokens'] or 0,
                'requests': totals['total_requests'] or 0
            },
            'by_feature': by_feature,
            'daily_usage': daily_usage,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting AI usage analytics: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve usage analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _serialize_client_for_ai(client: Client) -> Dict[str, Any]:
    """Serialize client data for AI processing"""
    return {
        'id': client.id,
        'first_name': client.first_name,
        'last_name': client.last_name,
        'age': client.age,
        'tax_status': client.tax_status,
        'email': client.email,
        'phone': client.phone,
        'birthdate': client.birthdate.isoformat() if client.birthdate else None,
        'created_at': client.created_at.isoformat()
    }


def _serialize_scenario_for_ai(scenario: Scenario) -> Dict[str, Any]:
    """Serialize scenario data for AI processing"""
    # Get the latest scenario results (you'd need to implement this based on your models)
    # For now, returning basic scenario info
    return {
        'id': scenario.id,
        'name': scenario.name,
        'retirement_age': scenario.retirement_age,
        'life_expectancy': scenario.life_expectancy,
        'annual_income_needed': float(scenario.annual_income_needed) if scenario.annual_income_needed else 0,
        'created_at': scenario.created_at.isoformat(),
        # Add more fields as needed based on your Scenario model
    }


def _serialize_client_profile_for_ai(client: Client, scenario: Scenario) -> Dict[str, Any]:
    """Serialize client profile for AI analysis"""
    current_age = client.age
    retirement_age = scenario.retirement_age
    years_to_retirement = retirement_age - current_age if current_age and retirement_age else 0
    
    return {
        'age': current_age,
        'retirement_age': retirement_age,
        'years_to_retirement': years_to_retirement,
        'tax_status': client.tax_status,
        # Add more profile data as needed
    }


def _serialize_scenario_results_for_ai(scenario: Scenario) -> Dict[str, Any]:
    """Serialize scenario results for AI analysis"""
    # This would typically pull from your scenario calculation results
    # For now, returning basic structure
    return {
        'success_rate': 85,  # Example - replace with actual calculation
        'irmaa_impact': False,  # Example - replace with actual analysis
        'needs_tax_optimization': True,  # Example - replace with actual analysis
        # Add more results data as needed
    }


def _track_ai_usage(
    user,
    feature: str,
    cost: float,
    tokens: int,
    report_id: str = None
):
    """Track AI usage for analytics and billing"""
    try:
        report_instance = None
        if report_id:
            try:
                report_instance = Report.objects.get(id=report_id)
            except Report.DoesNotExist:
                pass
        
        AIUsageTracking.objects.create(
            user=user,
            feature=feature,
            tokens_used=tokens,
            cost=Decimal(str(cost)),
            report=report_instance,
            request_metadata={
                'timestamp': timezone.now().isoformat(),
                'user_id': user.id
            }
        )
    except Exception as e:
        logger.error(f"Error tracking AI usage: {str(e)}")
        # Don't fail the main request if usage tracking fails