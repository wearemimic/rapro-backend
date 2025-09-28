from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime


class ComparisonService:
    """
    Service for comparing cost projections with insurance coverage
    """

    def generate_comparison(
        self,
        cost_projection_data: Dict,
        insurance_product: Dict,
        client_assets: float = 0,
        annual_income: float = 0
    ) -> Dict:
        """
        Generate comprehensive comparison between costs and insurance coverage

        Args:
            cost_projection_data: Cost projection with annual_projections
            insurance_product: Insurance product details
            client_assets: Client's liquid assets
            annual_income: Client's annual income

        Returns:
            Dict with complete comparison analysis
        """
        daily_benefit = insurance_product.get('daily_benefit_amount', 0)
        benefit_period_years = insurance_product.get('benefit_period_years', 3)
        elimination_period_days = insurance_product.get('elimination_period_days', 90)
        inflation_protection = insurance_product.get('inflation_protection_percent', 0) / 100

        annual_projections = cost_projection_data.get('annual_projections', [])

        comparison_timeline = []
        total_cost = 0
        total_insurance_paid = 0
        total_out_of_pocket = 0
        remaining_assets = client_assets

        for year_data in annual_projections:
            year = year_data['year']
            annual_care_cost = year_data['annual_cost']

            daily_care_cost = annual_care_cost / 365

            insurance_daily_benefit_adjusted = daily_benefit * ((1 + inflation_protection) ** (year - 1))

            if year <= benefit_period_years:
                elimination_cost = 0
                if year == 1:
                    elimination_cost = daily_care_cost * elimination_period_days

                days_after_elimination = 365 - (elimination_period_days if year == 1 else 0)

                insurance_coverage = min(
                    insurance_daily_benefit_adjusted * days_after_elimination,
                    annual_care_cost - elimination_cost
                )
            else:
                insurance_coverage = 0

            out_of_pocket = annual_care_cost - insurance_coverage

            net_cost_after_income = out_of_pocket - annual_income
            remaining_assets -= max(0, net_cost_after_income)

            comparison_timeline.append({
                'year': year,
                'client_age': year_data['client_age'],
                'care_level': year_data['care_level'],
                'annual_care_cost': round(annual_care_cost, 2),
                'insurance_coverage': round(insurance_coverage, 2),
                'out_of_pocket': round(out_of_pocket, 2),
                'coverage_percentage': round((insurance_coverage / annual_care_cost * 100) if annual_care_cost > 0 else 0, 1),
                'net_after_income': round(max(0, net_cost_after_income), 2),
                'remaining_assets': round(max(0, remaining_assets), 2)
            })

            total_cost += annual_care_cost
            total_insurance_paid += insurance_coverage
            total_out_of_pocket += out_of_pocket

        coverage_gap = total_cost - total_insurance_paid
        coverage_ratio = (total_insurance_paid / total_cost * 100) if total_cost > 0 else 0

        asset_depletion_year = None
        for timeline_year in comparison_timeline:
            if timeline_year['remaining_assets'] <= 0 and asset_depletion_year is None:
                asset_depletion_year = timeline_year['year']
                break

        roi_analysis = self._calculate_roi(
            insurance_product,
            total_insurance_paid,
            cost_projection_data.get('years_projected', 20)
        )

        return {
            'comparison_timeline': comparison_timeline,
            'summary': {
                'total_projected_cost': round(total_cost, 2),
                'total_insurance_coverage': round(total_insurance_paid, 2),
                'total_out_of_pocket': round(total_out_of_pocket, 2),
                'coverage_gap': round(coverage_gap, 2),
                'coverage_ratio_percent': round(coverage_ratio, 1),
                'average_annual_coverage': round(total_insurance_paid / len(annual_projections), 2) if annual_projections else 0
            },
            'insurance_details': {
                'daily_benefit': daily_benefit,
                'benefit_period_years': benefit_period_years,
                'elimination_period_days': elimination_period_days,
                'inflation_protection_percent': insurance_product.get('inflation_protection_percent', 0),
                'total_benefit_pool': round(daily_benefit * 365 * benefit_period_years, 2)
            },
            'asset_analysis': {
                'starting_assets': client_assets,
                'annual_income': annual_income,
                'asset_depletion_year': asset_depletion_year,
                'final_remaining_assets': comparison_timeline[-1]['remaining_assets'] if comparison_timeline else 0,
                'assets_depleted': asset_depletion_year is not None
            },
            'roi_analysis': roi_analysis,
            'recommendations': self._generate_recommendations(
                coverage_ratio,
                coverage_gap,
                asset_depletion_year,
                cost_projection_data.get('years_projected', 20)
            ),
            'generated_at': datetime.now().isoformat()
        }

    def _calculate_roi(
        self,
        insurance_product: Dict,
        total_benefit_received: float,
        years: int
    ) -> Dict:
        """
        Calculate ROI for insurance product

        Args:
            insurance_product: Product details with premium
            total_benefit_received: Total benefits paid out
            years: Number of years in projection

        Returns:
            ROI analysis dict
        """
        monthly_premium = insurance_product.get('monthly_premium', 0)

        if monthly_premium == 0:
            return {
                'total_premiums_paid': 0,
                'total_benefits_received': round(total_benefit_received, 2),
                'roi_percent': 0,
                'break_even_year': None,
                'net_benefit': round(total_benefit_received, 2)
            }

        total_premiums = monthly_premium * 12 * years

        roi_percent = ((total_benefit_received - total_premiums) / total_premiums * 100) if total_premiums > 0 else 0

        break_even_year = None
        if total_benefit_received > total_premiums:
            annual_premium = monthly_premium * 12
            break_even_year = int(total_premiums / annual_premium) + 1

        return {
            'total_premiums_paid': round(total_premiums, 2),
            'total_benefits_received': round(total_benefit_received, 2),
            'roi_percent': round(roi_percent, 1),
            'break_even_year': break_even_year,
            'net_benefit': round(total_benefit_received - total_premiums, 2),
            'benefit_to_premium_ratio': round(total_benefit_received / total_premiums, 2) if total_premiums > 0 else 0
        }

    def _generate_recommendations(
        self,
        coverage_ratio: float,
        coverage_gap: float,
        asset_depletion_year: Optional[int],
        total_years: int
    ) -> List[Dict]:
        """
        Generate recommendations based on comparison analysis

        Args:
            coverage_ratio: Percentage of costs covered by insurance
            coverage_gap: Dollar amount not covered
            asset_depletion_year: Year when assets run out (if applicable)
            total_years: Total projection years

        Returns:
            List of recommendation dicts
        """
        recommendations = []

        if coverage_ratio < 50:
            recommendations.append({
                'type': 'coverage_gap',
                'severity': 'high',
                'title': 'Significant Coverage Gap',
                'description': f'Insurance covers only {coverage_ratio:.1f}% of projected costs. Consider increasing daily benefit or benefit period.',
                'action_items': [
                    f'Consider increasing daily benefit amount',
                    f'Evaluate longer benefit period options',
                    f'Review inflation protection riders'
                ]
            })
        elif coverage_ratio < 70:
            recommendations.append({
                'type': 'coverage_gap',
                'severity': 'medium',
                'title': 'Moderate Coverage Gap',
                'description': f'Insurance covers {coverage_ratio:.1f}% of projected costs. May need additional planning.',
                'action_items': [
                    'Consider supplemental coverage',
                    'Review current benefit amounts',
                    'Plan for out-of-pocket expenses'
                ]
            })

        if asset_depletion_year and asset_depletion_year <= total_years:
            recommendations.append({
                'type': 'asset_depletion',
                'severity': 'high',
                'title': 'Asset Depletion Risk',
                'description': f'Assets projected to be depleted by year {asset_depletion_year}. Immediate action needed.',
                'action_items': [
                    'Increase insurance coverage',
                    'Review Medicaid planning strategies',
                    'Consider asset protection trusts',
                    'Explore hybrid insurance products'
                ]
            })

        if coverage_ratio >= 80:
            recommendations.append({
                'type': 'adequate_coverage',
                'severity': 'low',
                'title': 'Strong Coverage Position',
                'description': f'Insurance covers {coverage_ratio:.1f}% of projected costs. Coverage appears adequate.',
                'action_items': [
                    'Monitor coverage annually',
                    'Review inflation protection',
                    'Consider additional riders if needed'
                ]
            })

        if coverage_gap > 500000:
            recommendations.append({
                'type': 'high_gap',
                'severity': 'high',
                'title': 'Large Coverage Gap',
                'description': f'${coverage_gap:,.0f} gap between costs and coverage over projection period.',
                'action_items': [
                    'Develop comprehensive funding strategy',
                    'Review all available insurance options',
                    'Consider combination of insurance and self-funding',
                    'Explore state partnership programs'
                ]
            })

        if not recommendations:
            recommendations.append({
                'type': 'review',
                'severity': 'low',
                'title': 'Regular Review Recommended',
                'description': 'Continue monitoring and adjusting coverage as needed.',
                'action_items': [
                    'Annual policy review',
                    'Update cost projections every 2-3 years',
                    'Monitor health status changes'
                ]
            })

        return recommendations

    def compare_multiple_products(
        self,
        cost_projection_data: Dict,
        insurance_products: List[Dict],
        client_assets: float = 0,
        annual_income: float = 0
    ) -> Dict:
        """
        Compare multiple insurance products side-by-side

        Args:
            cost_projection_data: Cost projection data
            insurance_products: List of insurance products to compare
            client_assets: Client's liquid assets
            annual_income: Client's annual income

        Returns:
            Dict with side-by-side comparison
        """
        comparisons = []

        for product in insurance_products:
            comparison = self.generate_comparison(
                cost_projection_data,
                product,
                client_assets,
                annual_income
            )

            comparisons.append({
                'product_name': product.get('product_name', 'Unknown'),
                'carrier': product.get('carrier', 'Unknown'),
                'comparison': comparison
            })

        best_coverage = max(comparisons, key=lambda x: x['comparison']['summary']['coverage_ratio_percent'])
        best_roi = max(
            [c for c in comparisons if c['comparison']['roi_analysis']['total_premiums_paid'] > 0],
            key=lambda x: x['comparison']['roi_analysis']['roi_percent'],
            default=None
        )

        return {
            'comparisons': comparisons,
            'best_coverage': best_coverage['product_name'] if best_coverage else None,
            'best_roi': best_roi['product_name'] if best_roi else None,
            'total_products_compared': len(comparisons)
        }