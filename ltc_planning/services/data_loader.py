import csv
import os
from decimal import Decimal
from typing import Dict, List, Optional
from django.conf import settings


class CostDataLoader:
    """
    Utility class for loading LTC cost data from CSV files
    """

    def __init__(self):
        self.data_dir = os.path.join(
            settings.BASE_DIR,
            'ltc_planning',
            'data'
        )

        self._national_costs_cache = None
        self._regional_multipliers_cache = None
        self._inflation_rates_cache = None

    def load_national_costs(self) -> Dict[str, Dict[str, float]]:
        """
        Load national median costs from CSV file

        Returns:
            Dict structure:
            {
                'in_home_care': {
                    'homemaker_services': {'annual': 61776, 'monthly': 5148, 'hourly': 28.00},
                    'home_health_aide': {'annual': 61776, 'monthly': 5148, 'hourly': 28.00}
                },
                'adult_day_care': {...},
                ...
            }
        """
        if self._national_costs_cache:
            return self._national_costs_cache

        costs = {}
        csv_path = os.path.join(self.data_dir, 'genworth_national_costs_2024.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"National costs CSV not found at {csv_path}. "
                f"Please ensure genworth_national_costs_2024.csv exists in ltc_planning/data/"
            )

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                care_type = row['care_type']
                service_type = row['service_type']

                if care_type not in costs:
                    costs[care_type] = {}

                cost_data = {
                    'annual': float(row['annual_cost']),
                    'monthly': float(row['monthly_cost'])
                }

                if row.get('hourly_cost'):
                    cost_data['hourly'] = float(row['hourly_cost'])

                costs[care_type][service_type] = cost_data

        self._national_costs_cache = costs
        return costs

    def load_regional_multipliers(self) -> Dict[str, Dict[str, any]]:
        """
        Load regional cost multipliers from CSV file

        Returns:
            Dict structure:
            {
                'CA': {'multiplier': 1.52, 'region': 'West', 'state': 'California'},
                'CT': {'multiplier': 1.45, 'region': 'Northeast', 'state': 'Connecticut'},
                ...
            }
        """
        if self._regional_multipliers_cache:
            return self._regional_multipliers_cache

        multipliers = {}
        csv_path = os.path.join(self.data_dir, 'genworth_regional_multipliers_2024.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Regional multipliers CSV not found at {csv_path}. "
                f"Please ensure genworth_regional_multipliers_2024.csv exists in ltc_planning/data/"
            )

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state_code = row['state_code']
                multipliers[state_code] = {
                    'multiplier': float(row['multiplier']),
                    'region': row['region'],
                    'state': row['state'],
                    'notes': row.get('notes', '')
                }

        self._regional_multipliers_cache = multipliers
        return multipliers

    def load_inflation_rates(self) -> Dict[str, float]:
        """
        Load inflation rates from CSV file

        Returns:
            Dict structure:
            {
                'in_home_care': 0.0475,
                'adult_day_care': 0.0425,
                'assisted_living': 0.0450,
                ...
            }
        """
        if self._inflation_rates_cache:
            return self._inflation_rates_cache

        rates = {}
        csv_path = os.path.join(self.data_dir, 'inflation_rates.csv')

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Inflation rates CSV not found at {csv_path}. "
                f"Please ensure inflation_rates.csv exists in ltc_planning/data/"
            )

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                care_type = row['care_type']
                rates[care_type] = float(row['annual_inflation_rate'])

        self._inflation_rates_cache = rates
        return rates

    def get_care_type_cost(self, care_type: str, service_type: Optional[str] = None) -> Dict[str, float]:
        """
        Get cost for a specific care type and service type

        Args:
            care_type: e.g., 'in_home_care', 'assisted_living', 'skilled_nursing'
            service_type: e.g., 'homemaker_services', 'one_bedroom', 'private_room'

        Returns:
            Dict with annual, monthly, and optionally hourly costs
        """
        national_costs = self.load_national_costs()

        if care_type not in national_costs:
            raise ValueError(f"Invalid care_type: {care_type}")

        care_type_costs = national_costs[care_type]

        if service_type:
            if service_type not in care_type_costs:
                raise ValueError(f"Invalid service_type '{service_type}' for care_type '{care_type}'")
            return care_type_costs[service_type]

        if len(care_type_costs) == 1:
            return list(care_type_costs.values())[0]

        return list(care_type_costs.values())[0]

    def get_regional_cost(self, care_type: str, state_code: str, service_type: Optional[str] = None) -> Dict[str, float]:
        """
        Get regionally-adjusted cost

        Args:
            care_type: e.g., 'assisted_living'
            state_code: Two-letter state code, e.g., 'CA', 'NY'
            service_type: Optional specific service type

        Returns:
            Dict with regionally-adjusted annual, monthly costs
        """
        base_cost = self.get_care_type_cost(care_type, service_type)
        regional_multipliers = self.load_regional_multipliers()

        if state_code not in regional_multipliers:
            raise ValueError(f"Invalid state_code: {state_code}")

        multiplier = regional_multipliers[state_code]['multiplier']

        adjusted_cost = {}
        for key, value in base_cost.items():
            adjusted_cost[key] = round(value * multiplier, 2)

        return adjusted_cost

    def get_inflation_rate(self, care_type: str) -> float:
        """
        Get inflation rate for a specific care type

        Args:
            care_type: e.g., 'in_home_care', 'skilled_nursing'

        Returns:
            Annual inflation rate as decimal (e.g., 0.0475 for 4.75%)
        """
        inflation_rates = self.load_inflation_rates()

        if care_type in inflation_rates:
            return inflation_rates[care_type]

        return inflation_rates.get('general', 0.045)

    def validate_data_files(self) -> Dict[str, any]:
        """
        Validate that all required CSV files exist and are properly formatted

        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }

        try:
            national_costs = self.load_national_costs()
            results['stats']['care_types'] = len(national_costs)
            results['stats']['total_cost_entries'] = sum(len(services) for services in national_costs.values())
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"National costs error: {str(e)}")

        try:
            regional_multipliers = self.load_regional_multipliers()
            results['stats']['states'] = len(regional_multipliers)

            if len(regional_multipliers) != 50:
                results['warnings'].append(
                    f"Expected 50 states, found {len(regional_multipliers)}"
                )
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Regional multipliers error: {str(e)}")

        try:
            inflation_rates = self.load_inflation_rates()
            results['stats']['inflation_rate_entries'] = len(inflation_rates)
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Inflation rates error: {str(e)}")

        return results

    def get_available_care_types(self) -> List[str]:
        """Get list of all available care types"""
        national_costs = self.load_national_costs()
        return list(national_costs.keys())

    def get_available_states(self) -> List[Dict[str, str]]:
        """Get list of all available states with their info"""
        regional_multipliers = self.load_regional_multipliers()
        return [
            {
                'state_code': code,
                'state': info['state'],
                'region': info['region'],
                'multiplier': info['multiplier']
            }
            for code, info in regional_multipliers.items()
        ]