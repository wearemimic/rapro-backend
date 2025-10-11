"""
Social Security Planning API Views

This module provides REST API endpoints for Social Security planning features.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from core.models import Scenario
from .models import SSStrategy
from .services import SSPreviewService, SSStrategyService
from .utils import calculate_fra, get_life_expectancy, get_current_age


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ss_preview(request, scenario_id):
    """
    Generate Social Security claiming strategy preview.

    GET /api/ss-planning/scenarios/:id/preview/
    Query params:
        - primary_claiming_age (float, required): Primary's claiming age (62-70)
        - spouse_claiming_age (float, optional): Spouse's claiming age (62-70)
        - life_expectancy_primary (int, optional): Override primary's life expectancy
        - life_expectancy_spouse (int, optional): Override spouse's life expectancy

    Returns:
        {
            "years": [...],  // Year-by-year calculations
            "summary": {
                "lifetime_primary_benefits": 806400.00,
                "lifetime_spouse_benefits": 499200.00,
                "total_lifetime_benefits": 1305600.00,
                "total_taxes_on_ss": 287500.00,
                "total_irmaa_costs": 45000.00,
                "net_lifetime_benefits": 973100.00,
                "years_of_asset_support": 25,
                "asset_depletion_age": 88,
                "claiming_ages": {"primary": 70, "spouse": 67}
            },
            "comparison_to_current": {
                "lifetime_benefits_delta": 127000.00,
                "net_benefits_delta": 95000.00,
                "asset_depletion_delta_years": -2
            },
            "cached": false
        }
    """
    # Get scenario (ensure user owns this scenario through client->advisor relationship)
    scenario = get_object_or_404(Scenario, id=scenario_id, client__advisor=request.user)

    # Validate parameters
    primary_claiming_age = request.GET.get('primary_claiming_age')
    if not primary_claiming_age:
        return Response(
            {'error': 'primary_claiming_age is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        primary_claiming_age = float(primary_claiming_age)
        if not (62 <= primary_claiming_age <= 70):
            raise ValueError("Claiming age must be between 62 and 70")
    except ValueError as e:
        return Response(
            {'error': f'Invalid primary_claiming_age: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Optional parameters
    spouse_claiming_age = request.GET.get('spouse_claiming_age')
    if spouse_claiming_age:
        try:
            spouse_claiming_age = float(spouse_claiming_age)
            if not (62 <= spouse_claiming_age <= 70):
                raise ValueError("Spouse claiming age must be between 62 and 70")
        except ValueError as e:
            return Response(
                {'error': f'Invalid spouse_claiming_age: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    life_expectancy_primary = request.GET.get('life_expectancy_primary')
    if life_expectancy_primary:
        life_expectancy_primary = int(life_expectancy_primary)

    life_expectancy_spouse = request.GET.get('life_expectancy_spouse')
    if life_expectancy_spouse:
        life_expectancy_spouse = int(life_expectancy_spouse)

    # Optional: survivor_takes_higher_benefit override
    survivor_takes_higher_benefit = request.GET.get('survivor_takes_higher_benefit')
    if survivor_takes_higher_benefit is not None:
        survivor_takes_higher_benefit = survivor_takes_higher_benefit.lower() == 'true'
    else:
        survivor_takes_higher_benefit = None  # Use scenario default

    # DEBUG: Log all parameters
    print(f"\n{'='*80}")
    print(f"DEBUG: ss_preview API called with parameters:")
    print(f"  scenario_id: {scenario_id}")
    print(f"  primary_claiming_age: {primary_claiming_age}")
    print(f"  spouse_claiming_age: {spouse_claiming_age}")
    print(f"  life_expectancy_primary: {life_expectancy_primary}")
    print(f"  life_expectancy_spouse: {life_expectancy_spouse}")
    print(f"  survivor_takes_higher_benefit: {survivor_takes_higher_benefit}")
    print(f"  scenario.mortality_age (original): {scenario.mortality_age}")
    print(f"{'='*80}\n")

    # Generate preview
    try:
        preview_data = SSPreviewService.generate_preview(
            scenario,
            primary_claiming_age,
            spouse_claiming_age,
            life_expectancy_primary,
            life_expectancy_spouse,
            survivor_takes_higher_benefit
        )
        return Response(preview_data)
    except Exception as e:
        import traceback
        print(f"\n{'='*80}")
        print(f"ERROR in ss_preview:")
        print(f"Exception: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        print(f"{'='*80}\n")
        return Response(
            {'error': f'Failed to generate preview: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_strategy(request, scenario_id):
    """
    Save a Social Security claiming strategy.

    POST /api/ss-planning/scenarios/:id/strategies/
    Body:
        {
            "name": "Max Survivor",
            "primary_claiming_age": 70,
            "spouse_claiming_age": 67,
            "optimization_goal": "maximize_survivor",
            "health_status_primary": "excellent",
            "health_status_spouse": "good",
            "life_expectancy_primary": 88,
            "life_expectancy_spouse": 92,
            "notes": "Client wants to maximize survivor benefits for younger spouse",
            "is_active": true
        }

    Returns:
        {
            "id": 1,
            "name": "Max Survivor",
            "created_at": "2025-01-09T12:00:00Z",
            ...
        }
    """
    scenario = get_object_or_404(Scenario, id=scenario_id, client__advisor=request.user)

    # Validate required fields
    required_fields = ['name', 'primary_claiming_age']
    for field in required_fields:
        if field not in request.data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

    try:
        strategy = SSStrategyService.save_strategy(scenario, request.data)
        return Response({
            'id': strategy.id,
            'name': strategy.name,
            'is_active': strategy.is_active,
            'primary_claiming_age': strategy.primary_claiming_age,
            'spouse_claiming_age': strategy.spouse_claiming_age,
            'lifetime_benefits_total': float(strategy.lifetime_benefits_total or 0),
            'net_lifetime_benefits': float(strategy.net_lifetime_benefits or 0),
            'created_at': strategy.created_at.isoformat(),
            'calculated_at': strategy.calculated_at.isoformat() if strategy.calculated_at else None
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': f'Failed to save strategy: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_strategies(request, scenario_id):
    """
    List all saved strategies for a scenario.

    GET /api/ss-planning/scenarios/:id/strategies/

    Returns:
        {
            "strategies": [
                {
                    "id": 1,
                    "name": "Baseline",
                    "is_active": true,
                    ...
                },
                ...
            ]
        }
    """
    scenario = get_object_or_404(Scenario, id=scenario_id, client__advisor=request.user)
    strategies = SSStrategy.objects.filter(scenario=scenario)

    return Response({
        'strategies': [
            {
                'id': s.id,
                'name': s.name,
                'is_active': s.is_active,
                'primary_claiming_age': s.primary_claiming_age,
                'spouse_claiming_age': s.spouse_claiming_age,
                'optimization_goal': s.optimization_goal,
                'lifetime_benefits_total': float(s.lifetime_benefits_total or 0),
                'net_lifetime_benefits': float(s.net_lifetime_benefits or 0),
                'total_taxes': float(s.total_taxes or 0),
                'total_irmaa': float(s.total_irmaa or 0),
                'notes': s.notes,
                'created_at': s.created_at.isoformat(),
                'calculated_at': s.calculated_at.isoformat() if s.calculated_at else None
            }
            for s in strategies
        ]
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_strategies(request, scenario_id):
    """
    Compare multiple saved strategies.

    POST /api/ss-planning/scenarios/:id/strategies/compare/
    Body:
        {
            "strategy_ids": [1, 2, 3]
        }

    Returns:
        {
            "strategies": [...]
        }
    """
    scenario = get_object_or_404(Scenario, id=scenario_id, client__advisor=request.user)
    strategy_ids = request.data.get('strategy_ids', [])

    if not strategy_ids:
        return Response(
            {'error': 'strategy_ids is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        comparison = SSStrategyService.compare_strategies(scenario, strategy_ids)
        return Response(comparison)
    except Exception as e:
        return Response(
            {'error': f'Failed to compare strategies: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_info(request, scenario_id):
    """
    Get client info for SS planning (FRA, life expectancy, etc.).

    GET /api/ss-planning/scenarios/:id/client-info/

    Returns:
        {
            "primary": {
                "birthdate": "1958-03-15",
                "current_age": 66,
                "fra": 66.67,
                "fra_display": "66 and 8 months",
                "life_expectancy": 85,
                "gender": "male",
                "amount_at_fra": 4500.00,
                "claiming_age": 65
            },
            "spouse": {
                "birthdate": "1961-07-22",
                "current_age": 63,
                "fra": 67.0,
                "fra_display": "67",
                "life_expectancy": 88,
                "gender": "female",
                "amount_at_fra": 3200.00,
                "claiming_age": 67
            }
        }
    """
    scenario = get_object_or_404(Scenario, id=scenario_id, client__advisor=request.user)
    client = scenario.client

    # Extract Social Security income sources
    primary_ss_income = None
    spouse_ss_income = None

    for income_source in scenario.income_sources.all():
        if income_source.income_type.lower() in ['social security', 'social_security']:
            if income_source.owned_by == 'primary':
                primary_ss_income = income_source
            elif income_source.owned_by == 'spouse':
                spouse_ss_income = income_source

    response = {
        'primary': {
            'birthdate': client.birthdate.isoformat() if client.birthdate else None,
            'current_age': get_current_age(client.birthdate) if client.birthdate else None,
            'fra': calculate_fra(client.birthdate) if client.birthdate else 67.0,
            'fra_display': None,  # Calculated below
            'life_expectancy': scenario.mortality_age or 85,
            'gender': getattr(client, 'gender', 'male'),
            'amount_at_fra': float(primary_ss_income.monthly_amount) if primary_ss_income and primary_ss_income.monthly_amount else 0,
            'claiming_age': primary_ss_income.age_to_begin_withdrawal if primary_ss_income else None
        }
    }

    # Add FRA display
    from .utils import format_fra_display
    response['primary']['fra_display'] = format_fra_display(response['primary']['fra'])

    # Add spouse info if exists
    if hasattr(client, 'spouse') and client.spouse:
        spouse = client.spouse
        response['spouse'] = {
            'birthdate': spouse.birthdate.isoformat() if hasattr(spouse, 'birthdate') and spouse.birthdate else None,
            'current_age': get_current_age(spouse.birthdate) if hasattr(spouse, 'birthdate') and spouse.birthdate else None,
            'fra': calculate_fra(spouse.birthdate) if hasattr(spouse, 'birthdate') and spouse.birthdate else 67.0,
            'fra_display': format_fra_display(
                calculate_fra(spouse.birthdate)
            ) if hasattr(spouse, 'birthdate') and spouse.birthdate else "67",
            'life_expectancy': scenario.spouse_mortality_age or 87,
            'gender': getattr(spouse, 'gender', 'female'),
            'amount_at_fra': float(spouse_ss_income.monthly_amount) if spouse_ss_income and spouse_ss_income.monthly_amount else 0,
            'claiming_age': spouse_ss_income.age_to_begin_withdrawal if spouse_ss_income else None
        }

    return Response(response)
