import multiprocessing
from .scenario_processor import ScenarioProcessor
import copy
import numpy as np
import math
import random
import statistics

class RothConversionOptimizer:
    def __init__(self, scenario, client, spouse, assets, optimizer_params):
        self.scenario = scenario
        self.client = client
        self.spouse = spouse
        self.assets = assets
        self.optimizer_params = optimizer_params

    def progress_wrapper(self, args):
        idx, candidate = args
        res = self._run_candidate(candidate)
        total = self._progress_total
        if idx % max(1, total // 10) == 0:
            print(f"[RothOptimizer] Progress: {int(100*idx/total)}% ({idx}/{total})")
        return res

    def _extract_asset_balances(self, baseline_results, conversion_results):
        """
        Extract asset balances for charting.
        """
        if not baseline_results or not conversion_results:
            return {'years': [], 'assets': {}}
            
        years = [row.get('year', 0) for row in baseline_results]
        
        # Find all asset balance fields
        balance_fields = set()
        for row in baseline_results + conversion_results:
            for key in row:
                if key.endswith('_balance'):
                    balance_fields.add(key)
        
        # Create datasets for each asset type
        asset_datasets = {}
        for field in balance_fields:
            asset_type = field.replace('_balance', '')
            asset_datasets[asset_type] = {
                'baseline': [row.get(field, 0) for row in baseline_results],
                'conversion': [row.get(field, 0) for row in conversion_results]
            }
        
        return {
            'years': years,
            'assets': asset_datasets
        }
        
    def run(self):
        # 1. Run baseline scenario (no conversions)
        baseline_scenario = copy.deepcopy(self.scenario)
        baseline_scenario['roth_conversion_start_year'] = None
        baseline_scenario['roth_conversion_duration'] = None
        baseline_scenario['roth_conversion_annual_amount'] = None
        baseline_results = self._run_single_scenario(baseline_scenario)
        baseline_metrics = self._extract_metrics(baseline_results)

        # 2. Generate candidate schedules
        candidates = self._generate_candidates()
        print(f"[RothOptimizer] Number of candidate schedules: {len(candidates)}")

        # 3. Run scenario for each candidate (parallel, with progress reporting)
        results = []
        total = len(candidates)
        self._progress_total = total  # store for use in progress_wrapper
        if total == 0:
            raise Exception("No valid Roth conversion candidates generated.")
        from multiprocessing import Pool
        with Pool() as pool:
            results = pool.map(self.progress_wrapper, list(enumerate(candidates)))

        # 4. Select candidate that uses the full eligible balance if possible
        eligible_balance = sum(
            min(
                float(asset.get('current_asset_balance', 0)),
                float(asset.get('max_to_convert', asset.get('current_asset_balance', 0)))
            )
            for asset in self.assets
            if asset.get('income_type', '').lower() in ['traditional_401k', 'ira', 'traditional_ira']
        )
        duration_param = self.optimizer_params.get('years_to_convert') or self.optimizer_params.get('conversion_duration')
        if duration_param:
            try:
                duration = int(duration_param)
                full_conversion = eligible_balance
                # Find all candidates that use the full eligible balance
                full_candidates = [r for r in results if r['schedule']['annual_amount'] * duration >= full_conversion - 1 and r['schedule']['annual_amount'] * duration <= full_conversion + 1]
                if full_candidates:
                    best_result = min(full_candidates, key=lambda x: x['score'])
                else:
                    best_result = min(results, key=lambda x: x['score'])
            except Exception:
                best_result = min(results, key=lambda x: x['score'])
        else:
            best_result = min(results, key=lambda x: x['score'])

        # 5. Filter results to start at the earlier of retirement year or conversion start year
        retirement_year = None
        if isinstance(self.client, dict) and 'birthdate' in self.client and isinstance(self.scenario, dict) and 'retirement_age' in self.scenario:
            try:
                from datetime import datetime
                if isinstance(self.client['birthdate'], str):
                    birth_year = datetime.strptime(self.client['birthdate'], '%Y-%m-%d').year
                else:
                    birth_year = self.client['birthdate'].year
                retirement_year = birth_year + int(self.scenario['retirement_age'])
            except Exception:
                pass
        
        # conversion_start_year = best_result['schedule']['start_year']
        # filter_year = conversion_start_year
        # if retirement_year:
        #     filter_year = min(retirement_year, conversion_start_year)
        
        # Filter baseline and conversion results to start from the filter year
        # filtered_baseline = [row for row in baseline_results if row.get('year', 0) >= filter_year]
        # filtered_conversion = [row for row in best_result['year_by_year'] if row.get('year', 0) >= filter_year]

        # Instead, return all years (no filtering)
        filtered_baseline = baseline_results
        filtered_conversion = best_result['year_by_year']
        
        # 6. Prepare enhanced API contract output
        return {
            "optimal_schedule": best_result['schedule'],
            "baseline": {
                "metrics": baseline_metrics,
                "year_by_year": filtered_baseline
            },
            "conversion": {
                "metrics": best_result['metrics'],
                "year_by_year": filtered_conversion
            },
            "comparison": self._compare_metrics(baseline_metrics, best_result['metrics']),
            "asset_balances": self._extract_asset_balances(filtered_baseline, filtered_conversion)
        }

    def _run_single_scenario(self, scenario):
        processor = ScenarioProcessor.from_dicts(
            scenario=scenario,
            client=self.client,
            spouse=self.spouse,
            assets=copy.deepcopy(self.assets),
            debug=False
        )
        return processor.calculate()

    def _generate_candidates(self):
        # Grid search: start year, duration, annual amount
        candidates = []
        # Determine eligible balance (sum of per-asset max_to_convert or current balance)
        eligible_balance = sum(
            min(
                float(asset.get('current_asset_balance', 0)),
                float(asset.get('max_to_convert', asset.get('current_asset_balance', 0)))
            )
            for asset in self.assets
            if asset.get('income_type', '').lower() in ['traditional_401k', 'ira', 'traditional_ira']
        )
        # Reasonable bounds
        current_year = self.scenario.get('current_year') if isinstance(self.scenario, dict) and 'current_year' in self.scenario else None
        if not current_year:
            from datetime import datetime
            current_year = datetime.now().year
        retirement_year = current_year + 1
        if 'retirement_age' in self.scenario and 'client' in self.scenario and 'birthdate' in self.client:
            retirement_year = self.client['birthdate'].year + int(self.scenario['retirement_age'])
        start_years = list(range(current_year, retirement_year + 3))
        # Use UI-constrained duration if provided
        duration_param = self.optimizer_params.get('years_to_convert') or self.optimizer_params.get('conversion_duration')
        if duration_param:
            try:
                duration = int(duration_param)
                durations = [duration]
            except Exception:
                durations = list(range(1, 11))
        else:
            durations = list(range(1, 11))
        min_amount = 20000
        max_amount = int(math.floor(eligible_balance / 10000) * 10000)
        if max_amount < min_amount:
            max_amount = min_amount
        # Apply max_annual_amount and max_total_amount from optimizer_params
        max_annual = float(self.optimizer_params.get('max_annual_amount') or max_amount)
        max_total = float(self.optimizer_params.get('max_total_amount') or eligible_balance)
        # Clamp max_amount to max_annual
        max_amount = min(max_amount, max_annual)
        annual_amounts = list(range(min_amount, int(max_amount) + 1, 10000))
        # Always include the exact max possible annual amount for the selected duration
        if eligible_balance > 0 and duration_param:
            try:
                exact_annual = int(eligible_balance // int(duration_param))
                if exact_annual not in annual_amounts and exact_annual >= min_amount and exact_annual <= max_amount:
                    annual_amounts.append(exact_annual)
                annual_amounts = sorted(set(annual_amounts))
            except Exception:
                pass
        for start in start_years:
            for duration in durations:
                for amount in annual_amounts:
                    total_conversion = amount * duration
                    if total_conversion > eligible_balance:
                        continue  # Pre-filter: can't convert more than available
                    if amount > max_annual:
                        continue  # Exceeds advisor-set max annual
                    if total_conversion > max_total:
                        continue  # Exceeds advisor-set max total
                    candidates.append({
                        'roth_conversion_start_year': start,
                        'roth_conversion_duration': duration,
                        'roth_conversion_annual_amount': amount
                    })
        MAX_CANDIDATES = 300
        if len(candidates) > MAX_CANDIDATES:
            candidates = random.sample(candidates, MAX_CANDIDATES)
        return candidates

    def _run_candidate(self, schedule):
        scenario = copy.deepcopy(self.scenario)
        scenario.update(schedule)
        results = self._run_single_scenario(scenario)
        metrics = self._extract_metrics(results)
        score = self._score_candidate(metrics)
        return {
            'schedule': {
                'start_year': schedule['roth_conversion_start_year'],
                'duration': schedule['roth_conversion_duration'],
                'annual_amount': schedule['roth_conversion_annual_amount'],
                'score_breakdown': metrics
            },
            'metrics': metrics,
            'score': score,
            'year_by_year': results
        }

    def _extract_metrics(self, results):
        # Extract real metrics from year-by-year results
        if not results:
            return {
                'lifetime_tax': 0,
                'lifetime_medicare': 0,
                'total_irmaa': 0,
                'final_roth': 0,
                'cumulative_net_income': 0,
                'income_stability': 0,
                'total_rmds': 0,           # Add RMD tracking
                'inheritance_tax': 0       # Add inheritance tax estimation
            }
        
        # Helper function to safely convert values to float
        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        
        lifetime_tax = sum(safe_float(row.get('federal_tax', 0)) for row in results)
        lifetime_medicare = sum(safe_float(row.get('total_medicare', 0)) for row in results)
        total_irmaa = sum(safe_float(row.get('irmaa_surcharge', 0)) for row in results)
        cumulative_net_income = sum(safe_float(row.get('net_income', 0)) for row in results)
        
        # Track RMDs across all assets
        total_rmds = 0
        for row in results:
            # Look for any field that might contain RMD information
            rmd_amount = row.get('rmd_amount', 0)
            if isinstance(rmd_amount, (int, float, str)):
                try:
                    total_rmds += float(rmd_amount)
                except (ValueError, TypeError):
                    pass
                    
            # Also check for asset-specific RMD fields
            for key, value in row.items():
                if '_rmd' in key.lower() and isinstance(value, (int, float, str)):
                    try:
                        total_rmds += float(value)
                    except (ValueError, TypeError):
                        pass
        
        # Calculate inheritance tax based on final balances
        inheritance_tax = 0
        if results:
            final_year_data = results[-1]
            # Calculate inheritance tax directly here instead of relying on external methods
            tax_status = self.client.get('tax_status', 'Single').lower() if self.client else 'single'
            
            # Extract traditional (taxable) and Roth (non-taxable) balances
            traditional_balances = 0
            roth_balances = 0
            
            # Look for any asset balance in the final year data
            for key, value in final_year_data.items():
                if key.endswith('_balance'):
                    try:
                        balance = float(value)
                        if 'roth' in key.lower():
                            roth_balances += balance
                        else:
                            traditional_balances += balance
                    except (ValueError, TypeError):
                        pass
            
            # Apply simplified inheritance tax model
            # Traditional assets are subject to income tax for beneficiaries
            # Roth assets pass tax-free
            if tax_status in ['married filing jointly', 'qualifying widow(er)']:
                # Higher exemption for married couples
                tax_rate = 0.24  # Simplified average tax rate for beneficiaries
            else:
                tax_rate = 0.22  # Simplified average tax rate for beneficiaries
            
            inheritance_tax = traditional_balances * tax_rate
        
        # Calculate income stability
        net_incomes = [safe_float(row.get('net_income', 0)) for row in results]
        income_stability = statistics.stdev(net_incomes) if len(net_incomes) > 1 else 0
        
        # Get final Roth IRA balance
        final_roth = 0
        for key in ['Roth_IRA_balance', 'Roth_401k_balance', 'Roth_balance']:
            if results and key in results[-1]:
                final_roth = safe_float(results[-1][key])
                break
        
        return {
            'lifetime_tax': lifetime_tax,
            'lifetime_medicare': lifetime_medicare,
            'total_irmaa': total_irmaa,
            'final_roth': final_roth,
            'cumulative_net_income': cumulative_net_income,
            'income_stability': income_stability,
            'total_rmds': total_rmds,
            'inheritance_tax': inheritance_tax
        }
    
    def _calculate_inheritance_tax(self, final_year_data):
        """
        Calculate estimated inheritance tax based on remaining balances.
        This is a simplified model that can be enhanced with more specific tax rules.
        """
        # Get tax status for inheritance tax calculation
        tax_status = self.client.get('tax_status', 'Single').lower()
        
        # Extract traditional (taxable) and Roth (non-taxable) balances
        traditional_balances = 0
        roth_balances = 0
        
        # Look for any asset balance in the final year data
        for key, value in final_year_data.items():
            if key.endswith('_balance'):
                try:
                    balance = float(value)
                    if 'roth' in key.lower():
                        roth_balances += balance
                    else:
                        traditional_balances += balance
                except (ValueError, TypeError):
                    pass
        
        # Apply simplified inheritance tax model
        # Traditional assets are subject to income tax for beneficiaries
        # Roth assets pass tax-free
        if tax_status in ['married filing jointly', 'qualifying widow(er)']:
            # Higher exemption for married couples
            tax_rate = 0.24  # Simplified average tax rate for beneficiaries
        else:
            tax_rate = 0.22  # Simplified average tax rate for beneficiaries
        
        inheritance_tax = traditional_balances * tax_rate
        
        return inheritance_tax

    def _calculate_inheritance_tax_fallback(self, final_year_data):
        """
        Fallback method for calculating inheritance tax if the ScenarioProcessor method is unavailable.
        This is a simplified model that can be enhanced with more specific tax rules.
        """
        # Get tax status for inheritance tax calculation
        tax_status = self.client.get('tax_status', 'Single').lower()
        
        # Extract traditional (taxable) and Roth (non-taxable) balances
        traditional_balances = 0
        roth_balances = 0
        
        # Look for any asset balance in the final year data
        for key, value in final_year_data.items():
            if key.endswith('_balance'):
                try:
                    balance = float(value)
                    if 'roth' in key.lower():
                        roth_balances += balance
                    else:
                        traditional_balances += balance
                except (ValueError, TypeError):
                    pass
        
        # Apply simplified inheritance tax model
        # Traditional assets are subject to income tax for beneficiaries
        # Roth assets pass tax-free
        if tax_status in ['married filing jointly', 'qualifying widow(er)']:
            # Higher exemption for married couples
            tax_rate = 0.24  # Simplified average tax rate for beneficiaries
        else:
            tax_rate = 0.22  # Simplified average tax rate for beneficiaries
        
        inheritance_tax = traditional_balances * tax_rate
        
        return inheritance_tax

    def _score_candidate(self, metrics):
        # Use advisor goals to set weights
        goals = self.optimizer_params.get('goals', {})
        # Default weights
        base_weights = {
            'taxes': 0.5,
            'medicare': 0.2,
            'roth': 0.2,
            'volatility': 0.1
        }
        # Adjust weights based on advisor goals
        weights = base_weights.copy()
        if goals.get('taxes'):
            weights['taxes'] += 0.2
        if goals.get('irmaa'):
            weights['medicare'] += 0.2
        if goals.get('roth'):
            weights['roth'] += 0.2
        if goals.get('volatility'):
            weights['volatility'] += 0.2
        # Normalize weights to sum to 1
        total = sum(weights.values())
        for k in weights:
            weights[k] /= total
        # Use real metrics and dynamic weights
        lifetime_tax = float(metrics['lifetime_tax'])
        lifetime_medicare = float(metrics['lifetime_medicare'])
        final_roth = float(metrics['final_roth'])
        income_stability = float(metrics['income_stability'])
        return (
            weights['taxes'] * lifetime_tax +
            weights['medicare'] * lifetime_medicare +
            weights['roth'] * (1e6 - final_roth) +
            weights['volatility'] * income_stability
        )

    def _compare_metrics(self, baseline, candidate):
        """
        Calculate comprehensive comparison metrics between baseline and conversion scenarios.
        """
        # Ensure all values are converted to float to avoid Decimal + float errors
        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        
        # Get baseline values as floats
        baseline_tax = safe_float(baseline['lifetime_tax'])
        baseline_medicare = safe_float(baseline['lifetime_medicare'])
        baseline_irmaa = safe_float(baseline['total_irmaa'])
        baseline_rmds = safe_float(baseline['total_rmds'])
        baseline_inheritance = safe_float(baseline['inheritance_tax'])
        baseline_roth = safe_float(baseline['final_roth'])
        baseline_net_income = safe_float(baseline['cumulative_net_income'])
        baseline_stability = safe_float(baseline['income_stability'])
        
        # Get candidate values as floats
        candidate_tax = safe_float(candidate['lifetime_tax'])
        candidate_medicare = safe_float(candidate['lifetime_medicare'])
        candidate_irmaa = safe_float(candidate['total_irmaa'])
        candidate_rmds = safe_float(candidate['total_rmds'])
        candidate_inheritance = safe_float(candidate['inheritance_tax'])
        candidate_roth = safe_float(candidate['final_roth'])
        candidate_net_income = safe_float(candidate['cumulative_net_income'])
        candidate_stability = safe_float(candidate['income_stability'])
        
        # Calculate absolute differences
        tax_savings = baseline_tax - candidate_tax
        medicare_savings = baseline_medicare - candidate_medicare
        irmaa_savings = baseline_irmaa - candidate_irmaa
        rmd_reduction = baseline_rmds - candidate_rmds
        inheritance_tax_savings = baseline_inheritance - candidate_inheritance
        roth_increase = candidate_roth - baseline_roth
        net_income_increase = candidate_net_income - baseline_net_income
        
        # Calculate percentage improvements
        tax_savings_pct = (tax_savings / baseline_tax) * 100 if baseline_tax > 0 else 0
        medicare_savings_pct = (medicare_savings / baseline_medicare) * 100 if baseline_medicare > 0 else 0
        irmaa_savings_pct = (irmaa_savings / baseline_irmaa) * 100 if baseline_irmaa > 0 else 0
        rmd_reduction_pct = (rmd_reduction / baseline_rmds) * 100 if baseline_rmds > 0 else 0
        inheritance_tax_savings_pct = (inheritance_tax_savings / baseline_inheritance) * 100 if baseline_inheritance > 0 else 0
        
        # Calculate total lifetime savings
        total_savings = tax_savings + medicare_savings + irmaa_savings + inheritance_tax_savings
        
        return {
            'tax_savings': tax_savings,
            'tax_savings_pct': tax_savings_pct,
            'medicare_savings': medicare_savings,
            'medicare_savings_pct': medicare_savings_pct,
            'irmaa_savings': irmaa_savings,
            'irmaa_savings_pct': irmaa_savings_pct,
            'rmd_reduction': rmd_reduction,
            'rmd_reduction_pct': rmd_reduction_pct,
            'inheritance_tax_savings': inheritance_tax_savings,
            'inheritance_tax_savings_pct': inheritance_tax_savings_pct,
            'roth_increase': roth_increase,
            'net_income_increase': net_income_increase,
            'total_savings': total_savings,
            'income_stability_improvement': baseline_stability - candidate_stability
        } 