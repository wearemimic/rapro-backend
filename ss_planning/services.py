"""
Social Security Planning Services

This module provides business logic for Social Security planning,
wrapping the existing scenario_processor calculations without modifying it.
"""

from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from core.scenario_processor import ScenarioProcessor
from .models import SSCalculationCache, SSStrategy
from .utils import (
    calculate_fra,
    get_life_expectancy,
    calculate_monthly_benefit,
    get_current_age
)


class SSPreviewService:
    """
    Service for generating Social Security claiming strategy previews.

    This wraps the existing scenario_processor to run "what-if" scenarios
    without modifying the original scenario data.
    """

    @staticmethod
    def generate_preview(scenario, primary_claiming_age, spouse_claiming_age=None,
                        life_expectancy_primary=None, life_expectancy_spouse=None,
                        survivor_takes_higher_benefit=None):
        """
        Generate preview of SS strategy by temporarily modifying scenario and running calculations.

        Args:
            scenario: Scenario object
            primary_claiming_age (float): Primary's claiming age (62-70)
            spouse_claiming_age (float, optional): Spouse's claiming age
            life_expectancy_primary (int, optional): Override life expectancy
            life_expectancy_spouse (int, optional): Override life expectancy
            survivor_takes_higher_benefit (bool, optional): Override survivor benefit setting

        Returns:
            dict: Preview results with years, summary, and comparison
        """
        # TEMPORARILY DISABLED: Check cache first
        # TODO: Re-enable cache after adding survivor_takes_higher_benefit to cache key
        # cached = SSPreviewService._get_cached_preview(
        #     scenario, primary_claiming_age, spouse_claiming_age,
        #     life_expectancy_primary, life_expectancy_spouse
        # )
        # if cached:
        #     return cached

        # Create temporary scenario data dicts
        scenario_dict, client_dict, spouse_dict, assets_list = SSPreviewService._create_temp_scenario_dicts(
            scenario, primary_claiming_age, spouse_claiming_age,
            life_expectancy_primary, life_expectancy_spouse,
            survivor_takes_higher_benefit
        )

        print(f"\n{'='*80}")
        print(f"DEBUG: Running ScenarioProcessor.from_dicts")
        print(f"  Scenario ID: {scenario.id}")
        print(f"  Primary claiming age: {primary_claiming_age}")
        print(f"  Mortality age: {scenario_dict.get('mortality_age')}")
        print(f"  Survivor takes higher benefit: {scenario_dict.get('survivor_takes_higher_benefit')}")
        print(f"  Number of assets: {len(assets_list)}")

        # Find SS assets and print their claiming ages
        ss_assets = [a for a in assets_list if a['income_type'] == 'social_security']
        for ss in ss_assets:
            print(f"  SS Asset ({ss['owned_by']}): claiming age = {ss['age_to_begin_withdrawal']}")
        print(f"{'='*80}\n")

        # Run scenario_processor calculations using from_dicts
        processor = ScenarioProcessor.from_dicts(scenario_dict, client_dict, spouse_dict, assets_list)
        results = processor.calculate()

        # ScenarioProcessor.calculate() returns a list directly, not a dict with 'years' key
        if isinstance(results, list):
            results = {'years': results}

        print(f"\nDEBUG: ScenarioProcessor returned {len(results.get('years', []))} years of data\n")

        # Extract and format results
        preview_data = SSPreviewService._format_preview_results(
            results, scenario, primary_claiming_age, spouse_claiming_age
        )

        # Cache the results
        SSPreviewService._cache_preview(
            scenario, primary_claiming_age, spouse_claiming_age,
            life_expectancy_primary, life_expectancy_spouse,
            preview_data
        )

        return preview_data

    @staticmethod
    def _get_cached_preview(scenario, primary_age, spouse_age, life_exp_primary, life_exp_spouse):
        """Check if preview is already cached and still valid."""
        try:
            cache_entry = SSCalculationCache.objects.get(
                scenario=scenario,
                primary_claiming_age=primary_age,
                spouse_claiming_age=spouse_age or 0,
                life_expectancy_primary=life_exp_primary or scenario.mortality_age,
                life_expectancy_spouse=life_exp_spouse or scenario.spouse_mortality_age
            )

            if not cache_entry.is_expired():
                return {
                    'years': cache_entry.calculation_results,
                    'summary': cache_entry.summary_results,
                    'cached': True,
                    'cached_at': cache_entry.created_at.isoformat()
                }
        except SSCalculationCache.DoesNotExist:
            pass

        return None

    @staticmethod
    def _create_temp_scenario_dicts(scenario, primary_age, spouse_age, life_exp_primary, life_exp_spouse, survivor_override=None):
        """Create dictionary representations of scenario data with modified claiming ages."""
        from django.forms.models import model_to_dict

        # Use override if provided, otherwise use scenario setting
        survivor_setting = survivor_override if survivor_override is not None else getattr(scenario, 'survivor_takes_higher_benefit', False)

        # Convert scenario to dict
        scenario_dict = {
            'retirement_age': scenario.retirement_age,
            'spouse_retirement_age': getattr(scenario, 'spouse_retirement_age', None),
            'mortality_age': life_exp_primary or scenario.mortality_age,
            'spouse_mortality_age': life_exp_spouse or getattr(scenario, 'spouse_mortality_age', None),
            'reduction_2030_ss': getattr(scenario, 'reduction_2030_ss', False),
            'ss_adjustment_year': getattr(scenario, 'ss_adjustment_year', 2030),
            'ss_adjustment_percentage': getattr(scenario, 'ss_adjustment_percentage', 0),
            'primary_ss_claiming_age': primary_age,
            'spouse_ss_claiming_age': spouse_age,
            'apply_standard_deduction': getattr(scenario, 'apply_standard_deduction', True),
            'primary_state': getattr(scenario, 'primary_state', None),
            'survivor_takes_higher_benefit': survivor_setting,
            # Medicare/IRMAA fields
            'medicare_age': getattr(scenario, 'medicare_age', 65),
            'spouse_medicare_age': getattr(scenario, 'spouse_medicare_age', 65),
            'part_b_inflation_rate': getattr(scenario, 'part_b_inflation_rate', 5.0),
            'part_d_inflation_rate': getattr(scenario, 'part_d_inflation_rate', 6.0),
            'medicare_irmaa_percent': getattr(scenario, 'medicare_irmaa_percent', None),
            'ss_include_irmaa': getattr(scenario, 'ss_include_irmaa', False),
        }

        # Convert client to dict
        client = scenario.client
        client_dict = {
            'tax_status': client.tax_status,
            'gender': getattr(client, 'gender', 'M'),
            'birthdate': client.birthdate,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'state': getattr(client, 'state', 'CA'),
        }

        # Convert spouse to dict (if exists)
        spouse_dict = None
        if hasattr(client, 'spouse') and client.spouse:
            spouse = client.spouse
            spouse_dict = {
                'gender': getattr(spouse, 'gender', 'F'),
                'birthdate': spouse.birthdate if hasattr(spouse, 'birthdate') else None,
                'first_name': getattr(spouse, 'first_name', ''),
                'last_name': getattr(spouse, 'last_name', ''),
            }

        # Convert income sources to list of dicts
        assets_list = []
        for asset in scenario.income_sources.all():
            asset_dict = {
                'id': asset.id,
                'income_type': asset.income_type,
                'income_name': getattr(asset, 'income_name', ''),
                'investment_name': getattr(asset, 'investment_name', asset.income_name),
                'owned_by': asset.owned_by,
                'current_asset_balance': getattr(asset, 'current_asset_balance', 0),
                'monthly_amount': getattr(asset, 'monthly_amount', 0),
                'monthly_contribution': getattr(asset, 'monthly_contribution', 0),
                'rate_of_return': getattr(asset, 'rate_of_return', 0),
                'age_to_begin_withdrawal': getattr(asset, 'age_to_begin_withdrawal', 65),
                'age_to_end_withdrawal': getattr(asset, 'age_to_end_withdrawal', 90),
                'inflation_rate': getattr(asset, 'inflation_rate', 0),
                'withdrawal_amount': getattr(asset, 'withdrawal_amount', 0),
                'cola': getattr(asset, 'cola', 0),
                'survivor_benefit': getattr(asset, 'survivor_benefit', 0),
                'pension_start_age': getattr(asset, 'pension_start_age', None),
            }

            # Update Social Security claiming ages
            if asset.income_type == 'social_security':
                if asset.owned_by == 'primary':
                    asset_dict['age_to_begin_withdrawal'] = int(primary_age)
                elif asset.owned_by == 'spouse' and spouse_age:
                    asset_dict['age_to_begin_withdrawal'] = int(spouse_age)

            assets_list.append(asset_dict)

        return scenario_dict, client_dict, spouse_dict, assets_list

    @staticmethod
    def _format_preview_results(results, original_scenario, primary_age, spouse_age):
        """Format scenario_processor results for preview response."""
        years_data = results.get('years', [])

        # Calculate summary metrics
        summary = SSPreviewService._calculate_summary_metrics(
            years_data, primary_age, spouse_age
        )

        # Calculate comparison to current strategy
        comparison = SSPreviewService._calculate_comparison(
            original_scenario, summary
        )

        return {
            'years': years_data,
            'summary': summary,
            'comparison_to_current': comparison,
            'cached': False
        }

    @staticmethod
    def _calculate_summary_metrics(years_data, primary_age, spouse_age):
        """Calculate summary metrics from year-by-year data."""
        print(f"\n{'='*80}")
        print(f"DEBUG: _calculate_summary_metrics called")
        print(f"  Primary claiming age: {primary_age}")
        print(f"  Spouse claiming age: {spouse_age}")
        print(f"  Number of years in data: {len(years_data)}")
        print(f"{'='*80}\n")

        total_ss_primary = sum(
            Decimal(str(y.get('ss_income_primary_gross', 0)))
            for y in years_data
        )
        total_ss_spouse = sum(
            Decimal(str(y.get('ss_income_spouse_gross', 0)))
            for y in years_data
        )
        # Total of ALL taxes (federal + state) during retirement
        total_all_taxes = sum(
            Decimal(str(y.get('total_taxes', 0)))
            for y in years_data
        )
        # Total IRMAA costs (should match Medicare tab)
        total_irmaa = sum(
            Decimal(str(y.get('irmaa_surcharge', 0)))
            for y in years_data
        )
        # Total Medicare costs (for reference)
        total_medicare = sum(
            Decimal(str(y.get('total_medicare', 0)))
            for y in years_data
        )

        # DEBUG: Print detailed breakdown
        print(f"DEBUG: Summary calculation breakdown:")
        print(f"  Total SS Primary: ${total_ss_primary:,.2f}")
        print(f"  Total SS Spouse: ${total_ss_spouse:,.2f}")
        print(f"  Total ALL Taxes (federal + state): ${total_all_taxes:,.2f}")
        print(f"  Total IRMAA (irmaa_surcharge): ${total_irmaa:,.2f}")
        print(f"  Total Medicare (total_medicare): ${total_medicare:,.2f}")

        # DEBUG: Sample first year and check for survivor benefit years
        print(f"\nDEBUG: First year data:")
        if years_data:
            year = years_data[0]
            print(f"  Age: {year.get('primary_age')}")
            print(f"  Primary SS: ${year.get('ss_income_primary_gross', 0):,.2f}")
            print(f"  Spouse SS: ${year.get('ss_income_spouse_gross', 0):,.2f}")
            print(f"  Total SS: ${year.get('ss_income_primary_gross', 0) + year.get('ss_income_spouse_gross', 0):,.2f}")

        # DEBUG: Check a year after expected death (assuming ~85 mortality)
        if len(years_data) > 20:
            late_year = years_data[20]
            print(f"\nDEBUG: Year 20+ data (checking for survivor benefits):")
            print(f"  Primary age: {late_year.get('primary_age')}")
            print(f"  Primary SS: ${late_year.get('ss_income_primary_gross', 0):,.2f}")
            print(f"  Spouse SS: ${late_year.get('ss_income_spouse_gross', 0):,.2f}")
            print(f"  Total SS: ${late_year.get('ss_income_primary_gross', 0) + late_year.get('ss_income_spouse_gross', 0):,.2f}")

        # Find asset depletion age (first year assets go to zero)
        asset_depletion_age = None
        for year_data in years_data:
            if year_data.get('total_assets', 0) <= 0:
                asset_depletion_age = year_data.get('primary_age')
                break

        return {
            'lifetime_primary_benefits': float(total_ss_primary),
            'lifetime_spouse_benefits': float(total_ss_spouse),
            'total_lifetime_benefits': float(total_ss_primary + total_ss_spouse),
            'total_taxes_on_ss': float(total_all_taxes),  # Changed to total_all_taxes (federal + state)
            'total_irmaa_costs': float(total_irmaa),
            'net_lifetime_benefits': float(total_ss_primary + total_ss_spouse - total_all_taxes - total_irmaa),
            'years_of_asset_support': len([y for y in years_data if y.get('total_assets', 0) > 0]),
            'asset_depletion_age': asset_depletion_age,
            'claiming_ages': {
                'primary': primary_age,
                'spouse': spouse_age
            }
        }

    @staticmethod
    def _calculate_comparison(original_scenario, new_summary):
        """Calculate delta between new strategy and current/saved strategy."""
        # Get current active strategy or use scenario defaults
        current_strategy = original_scenario.ss_strategies.filter(is_active=True).first()

        if not current_strategy:
            # No saved strategy, compare to scenario defaults
            current_lifetime = 0  # Would need to calculate from scenario defaults
            current_net = 0
            current_depletion_age = None
        else:
            current_lifetime = float(current_strategy.lifetime_benefits_total or 0)
            current_net = float(current_strategy.net_lifetime_benefits or 0)
            current_depletion_age = None  # Not stored in strategy

        new_lifetime = new_summary['total_lifetime_benefits']
        new_net = new_summary['net_lifetime_benefits']
        new_depletion_age = new_summary.get('asset_depletion_age')

        return {
            'lifetime_benefits_delta': new_lifetime - current_lifetime,
            'net_benefits_delta': new_net - current_net,
            'asset_depletion_delta_years': (
                (new_depletion_age - current_depletion_age)
                if new_depletion_age and current_depletion_age
                else None
            )
        }

    @staticmethod
    def _cache_preview(scenario, primary_age, spouse_age, life_exp_primary, life_exp_spouse, preview_data):
        """Cache preview results for 24 hours."""
        try:
            SSCalculationCache.objects.update_or_create(
                scenario=scenario,
                primary_claiming_age=primary_age,
                spouse_claiming_age=spouse_age or 0,
                life_expectancy_primary=life_exp_primary or scenario.mortality_age,
                life_expectancy_spouse=life_exp_spouse or getattr(scenario, 'spouse_mortality_age', None),
                defaults={
                    'calculation_results': preview_data['years'],
                    'summary_results': preview_data['summary'],
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to cache SS preview: {e}")


class SSStrategyService:
    """
    Service for managing and comparing Social Security strategies.
    """

    @staticmethod
    def save_strategy(scenario, strategy_data):
        """
        Save a Social Security claiming strategy.

        Args:
            scenario: Scenario object
            strategy_data (dict): Strategy parameters

        Returns:
            SSStrategy: Saved strategy object
        """
        # Run calculations for this strategy
        preview = SSPreviewService.generate_preview(
            scenario,
            strategy_data['primary_claiming_age'],
            strategy_data.get('spouse_claiming_age'),
            strategy_data.get('life_expectancy_primary'),
            strategy_data.get('life_expectancy_spouse')
        )

        # Create or update strategy
        strategy, created = SSStrategy.objects.update_or_create(
            scenario=scenario,
            name=strategy_data['name'],
            defaults={
                'primary_claiming_age': strategy_data['primary_claiming_age'],
                'spouse_claiming_age': strategy_data.get('spouse_claiming_age'),
                'optimization_goal': strategy_data.get('optimization_goal', 'maximize_lifetime'),
                'health_status_primary': strategy_data.get('health_status_primary', 'good'),
                'health_status_spouse': strategy_data.get('health_status_spouse', 'good'),
                'life_expectancy_primary': strategy_data.get('life_expectancy_primary', scenario.mortality_age),
                'life_expectancy_spouse': strategy_data.get('life_expectancy_spouse'),
                'earned_income_primary': strategy_data.get('earned_income_primary', 0),
                'earned_income_spouse': strategy_data.get('earned_income_spouse', 0),
                'wep_applies': strategy_data.get('wep_applies', False),
                'gpo_applies': strategy_data.get('gpo_applies', False),
                'pension_amount': strategy_data.get('pension_amount', 0),
                'lifetime_benefits_total': preview['summary']['total_lifetime_benefits'],
                'lifetime_benefits_primary': preview['summary']['lifetime_primary_benefits'],
                'lifetime_benefits_spouse': preview['summary']['lifetime_spouse_benefits'],
                'total_taxes': preview['summary']['total_taxes_on_ss'],
                'total_irmaa': preview['summary']['total_irmaa_costs'],
                'net_lifetime_benefits': preview['summary']['net_lifetime_benefits'],
                'notes': strategy_data.get('notes', ''),
                'is_active': strategy_data.get('is_active', False),
                'calculated_at': timezone.now()
            }
        )

        return strategy

    @staticmethod
    def compare_strategies(scenario, strategy_ids):
        """
        Compare multiple saved strategies side-by-side.

        Args:
            scenario: Scenario object
            strategy_ids (list): List of strategy IDs to compare

        Returns:
            dict: Comparison data
        """
        strategies = SSStrategy.objects.filter(
            scenario=scenario,
            id__in=strategy_ids
        )

        return {
            'strategies': [
                SSStrategyService._format_strategy_for_comparison(s)
                for s in strategies
            ]
        }

    @staticmethod
    def _format_strategy_for_comparison(strategy):
        """Format strategy for comparison view."""
        return {
            'id': strategy.id,
            'name': strategy.name,
            'is_active': strategy.is_active,
            'claiming_ages': {
                'primary': strategy.primary_claiming_age,
                'spouse': strategy.spouse_claiming_age
            },
            'metrics': {
                'monthly_at_start': None,  # Would need to calculate
                'lifetime_benefits': float(strategy.lifetime_benefits_total or 0),
                'total_taxes': float(strategy.total_taxes or 0),
                'total_irmaa': float(strategy.total_irmaa or 0),
                'net_benefits': float(strategy.net_lifetime_benefits or 0)
            },
            'notes': strategy.notes,
            'calculated_at': strategy.calculated_at.isoformat() if strategy.calculated_at else None
        }
