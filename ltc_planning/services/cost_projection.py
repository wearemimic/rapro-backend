from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from .data_loader import CostDataLoader


class CostProjectionService:
    """
    Service for calculating long-term care cost projections
    """

    def __init__(self):
        self.data_loader = CostDataLoader()

    def generate_projection(
        self,
        care_level: str,
        state_code: str,
        years_projected: int = 20,
        start_age: int = 65,
        care_progression: Optional[List[Dict]] = None,
        scenario_type: str = 'likely'
    ) -> Dict:
        """
        Generate a comprehensive cost projection

        Args:
            care_level: Initial care level (e.g., 'assisted_living', 'in_home_care')
            state_code: Two-letter state code for regional adjustment
            years_projected: Number of years to project (default 20)
            start_age: Client's starting age (default 65)
            care_progression: Optional list of care level changes over time
            scenario_type: 'optimistic', 'likely', or 'pessimistic'

        Returns:
            Dict with complete projection data
        """
        if care_progression is None:
            care_progression = self._generate_default_progression(
                care_level, years_projected, scenario_type
            )

        annual_projections = []
        cumulative_cost = 0
        current_age = start_age

        for year in range(years_projected):
            year_care_level = self._get_care_level_for_year(year, care_progression)

            care_type_map = {
                'independent_with_monitoring': 'independent_living',
                'in_home_care': 'in_home_care',
                'adult_day_care': 'adult_day_care',
                'assisted_living': 'assisted_living',
                'memory_care': 'memory_care',
                'skilled_nursing': 'skilled_nursing'
            }

            care_type = care_type_map.get(year_care_level, 'assisted_living')
            service_type = self._get_default_service_type(care_type)

            base_cost = self.data_loader.get_regional_cost(
                care_type,
                state_code,
                service_type
            )

            inflation_rate = self.data_loader.get_inflation_rate(care_type)

            inflated_annual_cost = base_cost['annual'] * ((1 + inflation_rate) ** year)
            inflated_monthly_cost = inflated_annual_cost / 12

            cumulative_cost += inflated_annual_cost

            annual_projections.append({
                'year': year + 1,
                'client_age': current_age + year,
                'care_level': year_care_level,
                'care_type': care_type,
                'service_type': service_type,
                'annual_cost': round(inflated_annual_cost, 2),
                'monthly_cost': round(inflated_monthly_cost, 2),
                'cumulative_cost': round(cumulative_cost, 2),
                'inflation_rate': inflation_rate
            })

        regional_info = self.data_loader.load_regional_multipliers()[state_code]

        return {
            'scenario_name': f"{scenario_type.title()} Scenario - {care_level.replace('_', ' ').title()}",
            'scenario_type': scenario_type,
            'initial_care_level': care_level,
            'state_code': state_code,
            'state_name': regional_info['state'],
            'regional_multiplier': regional_info['multiplier'],
            'years_projected': years_projected,
            'start_age': start_age,
            'end_age': start_age + years_projected - 1,
            'annual_projections': annual_projections,
            'total_lifetime_cost': round(cumulative_cost, 2),
            'average_annual_cost': round(cumulative_cost / years_projected, 2),
            'care_progression': care_progression,
            'generated_at': datetime.now().isoformat()
        }

    def _generate_default_progression(
        self,
        initial_care_level: str,
        years_projected: int,
        scenario_type: str
    ) -> List[Dict]:
        """
        Generate default care level progression based on scenario type

        Args:
            initial_care_level: Starting care level
            years_projected: Total years to project
            scenario_type: 'optimistic', 'likely', or 'pessimistic'

        Returns:
            List of care level changes with timing
        """
        progression = [
            {'year': 0, 'care_level': initial_care_level, 'reason': 'Initial assessment'}
        ]

        care_escalation_path = {
            'independent_with_monitoring': ['in_home_care', 'assisted_living', 'skilled_nursing'],
            'in_home_care': ['adult_day_care', 'assisted_living', 'skilled_nursing'],
            'adult_day_care': ['assisted_living', 'memory_care', 'skilled_nursing'],
            'assisted_living': ['memory_care', 'skilled_nursing'],
            'memory_care': ['skilled_nursing'],
            'skilled_nursing': []
        }

        escalation_timing = {
            'optimistic': [8, 15, None],
            'likely': [5, 10, 15],
            'pessimistic': [3, 6, 10]
        }

        next_levels = care_escalation_path.get(initial_care_level, [])
        timing = escalation_timing.get(scenario_type, escalation_timing['likely'])

        for i, next_level in enumerate(next_levels):
            if i < len(timing) and timing[i] and timing[i] < years_projected:
                progression.append({
                    'year': timing[i],
                    'care_level': next_level,
                    'reason': f'Anticipated care escalation ({scenario_type} scenario)'
                })

        return progression

    def _get_care_level_for_year(self, year: int, care_progression: List[Dict]) -> str:
        """
        Determine the care level for a specific year based on progression

        Args:
            year: Year number (0-indexed)
            care_progression: List of care level changes

        Returns:
            Care level string for that year
        """
        current_level = care_progression[0]['care_level']

        for change in care_progression:
            if change['year'] <= year:
                current_level = change['care_level']
            else:
                break

        return current_level

    def _get_default_service_type(self, care_type: str) -> Optional[str]:
        """
        Get the default service type for a care type

        Args:
            care_type: The care type (e.g., 'assisted_living')

        Returns:
            Default service type string or None
        """
        default_services = {
            'in_home_care': 'home_health_aide',
            'adult_day_care': 'adult_day_health_care',
            'assisted_living': 'one_bedroom',
            'memory_care': 'monthly_private',
            'skilled_nursing': 'semi_private_room',
            'independent_living': 'one_bedroom'
        }

        return default_services.get(care_type)

    def generate_multiple_scenarios(
        self,
        care_level: str,
        state_code: str,
        years_projected: int = 20,
        start_age: int = 65
    ) -> Dict[str, Dict]:
        """
        Generate optimistic, likely, and pessimistic scenarios

        Returns:
            Dict with three scenarios: optimistic, likely, pessimistic
        """
        scenarios = {}

        for scenario_type in ['optimistic', 'likely', 'pessimistic']:
            scenarios[scenario_type] = self.generate_projection(
                care_level=care_level,
                state_code=state_code,
                years_projected=years_projected,
                start_age=start_age,
                scenario_type=scenario_type
            )

        return {
            'scenarios': scenarios,
            'comparison': self._compare_scenarios(scenarios)
        }

    def _compare_scenarios(self, scenarios: Dict[str, Dict]) -> Dict:
        """
        Compare the three scenarios and provide summary statistics

        Args:
            scenarios: Dict with optimistic, likely, pessimistic scenarios

        Returns:
            Comparison summary
        """
        return {
            'cost_range': {
                'lowest': scenarios['optimistic']['total_lifetime_cost'],
                'likely': scenarios['likely']['total_lifetime_cost'],
                'highest': scenarios['pessimistic']['total_lifetime_cost'],
                'range_dollars': scenarios['pessimistic']['total_lifetime_cost'] -
                               scenarios['optimistic']['total_lifetime_cost']
            },
            'average_annual_cost_range': {
                'lowest': scenarios['optimistic']['average_annual_cost'],
                'likely': scenarios['likely']['average_annual_cost'],
                'highest': scenarios['pessimistic']['average_annual_cost']
            }
        }

    def calculate_cost_with_inflation(
        self,
        base_annual_cost: float,
        care_type: str,
        years: int
    ) -> List[Dict]:
        """
        Calculate year-by-year costs with inflation

        Args:
            base_annual_cost: Base annual cost (current dollars)
            care_type: Type of care for inflation rate lookup
            years: Number of years to project

        Returns:
            List of yearly costs with inflation applied
        """
        inflation_rate = self.data_loader.get_inflation_rate(care_type)

        yearly_costs = []
        for year in range(years):
            inflated_cost = base_annual_cost * ((1 + inflation_rate) ** year)
            yearly_costs.append({
                'year': year + 1,
                'annual_cost': round(inflated_cost, 2),
                'monthly_cost': round(inflated_cost / 12, 2),
                'inflation_rate': inflation_rate
            })

        return yearly_costs

    def estimate_asset_depletion(
        self,
        projection: Dict,
        starting_assets: float,
        annual_income: float = 0,
        other_annual_expenses: float = 50000
    ) -> Dict:
        """
        Estimate when assets will be depleted given care costs

        Args:
            projection: Cost projection from generate_projection()
            starting_assets: Initial liquid assets available for care
            annual_income: Annual income (Social Security, pensions, etc.)
            other_annual_expenses: Other living expenses beyond care costs

        Returns:
            Asset depletion analysis
        """
        remaining_assets = starting_assets
        years_until_depletion = None

        asset_timeline = []

        for year_data in projection['annual_projections']:
            year = year_data['year']
            care_cost = year_data['annual_cost']

            net_annual_cost = care_cost + other_annual_expenses - annual_income

            remaining_assets -= net_annual_cost

            asset_timeline.append({
                'year': year,
                'client_age': year_data['client_age'],
                'care_cost': care_cost,
                'total_expenses': care_cost + other_annual_expenses,
                'income': annual_income,
                'net_annual_cost': net_annual_cost,
                'remaining_assets': max(0, round(remaining_assets, 2))
            })

            if remaining_assets <= 0 and years_until_depletion is None:
                years_until_depletion = year

        return {
            'starting_assets': starting_assets,
            'annual_income': annual_income,
            'other_annual_expenses': other_annual_expenses,
            'years_until_depletion': years_until_depletion,
            'asset_depleted': years_until_depletion is not None,
            'depletion_age': projection['start_age'] + years_until_depletion if years_until_depletion else None,
            'final_assets': asset_timeline[-1]['remaining_assets'] if asset_timeline else starting_assets,
            'asset_timeline': asset_timeline
        }