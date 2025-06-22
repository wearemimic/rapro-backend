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

        # 5. Prepare API contract output
        return {
            "optimal_schedule": best_result['schedule'],
            "baseline": baseline_metrics,
            "comparison": self._compare_metrics(baseline_metrics, best_result['metrics']),
            "year_by_year": best_result['year_by_year']
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
                'income_stability': 0
            }
        lifetime_tax = sum(row.get('federal_tax', 0) for row in results)
        lifetime_medicare = sum(row.get('total_medicare', 0) for row in results)
        total_irmaa = sum(row.get('irmaa_surcharge', 0) for row in results)
        cumulative_net_income = sum(row.get('net_income', 0) for row in results)
        net_incomes = [row.get('net_income', 0) for row in results]
        income_stability = statistics.stdev(net_incomes) if len(net_incomes) > 1 else 0
        # Try to get final Roth IRA balance (last year, prefer Roth_IRA_balance, fallback to 0)
        final_roth = 0
        for key in ['Roth_IRA_balance', 'Roth_401k_balance', 'Roth_balance']:
            if key in results[-1]:
                final_roth = results[-1][key]
                break
        return {
            'lifetime_tax': lifetime_tax,
            'lifetime_medicare': lifetime_medicare,
            'total_irmaa': total_irmaa,
            'final_roth': final_roth,
            'cumulative_net_income': cumulative_net_income,
            'income_stability': income_stability
        }

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
        # TODO: Implement full comparison logic
        return {
            'tax_savings': baseline['lifetime_tax'] - candidate['lifetime_tax'],
            'medicare_savings': baseline['lifetime_medicare'] - candidate['lifetime_medicare'],
            'irmaa_savings': baseline['total_irmaa'] - candidate['total_irmaa'],
            'roth_increase': candidate['final_roth'] - baseline['final_roth'],
            'net_income_increase': candidate['cumulative_net_income'] - baseline['cumulative_net_income'],
            'income_stability_improvement': baseline['income_stability'] - candidate['income_stability']
        } 