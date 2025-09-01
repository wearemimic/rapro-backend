# backend/core/services/analytics_service.py

import stripe
from django.conf import settings
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from ..models import (
    CustomUser, Client, Scenario, RevenueMetric, UserEngagementMetric,
    ClientPortfolioAnalytics, ActivityLog
)

logger = logging.getLogger(__name__)


class RevenueAnalyticsService:
    """Service for calculating and storing revenue analytics"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def calculate_mrr(self, date=None):
        """Calculate Monthly Recurring Revenue for a specific date"""
        if not date:
            date = timezone.now().date()
        
        try:
            # Get all active subscriptions from Stripe
            subscriptions = stripe.Subscription.list(
                status='active',
                limit=100,
                expand=['data.items.data.price']
            )
            
            monthly_revenue = Decimal('0.00')
            annual_revenue = Decimal('0.00')
            
            for subscription in subscriptions.auto_paging_iter():
                for item in subscription.items.data:
                    price = item.price
                    amount = Decimal(str(price.unit_amount / 100))  # Convert cents to dollars
                    
                    if price.recurring.interval == 'month':
                        monthly_revenue += amount * item.quantity
                    elif price.recurring.interval == 'year':
                        annual_revenue += amount * item.quantity
            
            # Convert annual to monthly
            total_mrr = monthly_revenue + (annual_revenue / 12)
            
            # Store the metric
            RevenueMetric.objects.update_or_create(
                date=date,
                metric_type='mrr',
                plan_type='all',
                defaults={
                    'value': total_mrr,
                    'currency': 'USD',
                    'calculation_method': 'stripe_subscription_sum',
                    'stripe_data': {
                        'monthly_revenue': float(monthly_revenue),
                        'annual_revenue': float(annual_revenue),
                        'total_active_subscriptions': subscriptions.data.__len__()
                    }
                }
            )
            
            # Store segmented metrics
            RevenueMetric.objects.update_or_create(
                date=date,
                metric_type='mrr',
                plan_type='monthly',
                defaults={'value': monthly_revenue, 'currency': 'USD'}
            )
            
            RevenueMetric.objects.update_or_create(
                date=date,
                metric_type='mrr', 
                plan_type='annual',
                defaults={'value': annual_revenue / 12, 'currency': 'USD'}
            )
            
            return {
                'total_mrr': float(total_mrr),
                'monthly_mrr': float(monthly_revenue),
                'annual_mrr': float(annual_revenue / 12),
                'date': date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating MRR: {str(e)}")
            return None
    
    def calculate_arr(self, date=None):
        """Calculate Annual Recurring Revenue"""
        if not date:
            date = timezone.now().date()
        
        mrr_data = self.calculate_mrr(date)
        if mrr_data:
            arr = mrr_data['total_mrr'] * 12
            
            # Store ARR metric
            RevenueMetric.objects.update_or_create(
                date=date,
                metric_type='arr',
                plan_type='all',
                defaults={
                    'value': Decimal(str(arr)),
                    'currency': 'USD',
                    'calculation_method': 'mrr_times_12',
                    'stripe_data': mrr_data
                }
            )
            
            return arr
        return None
    
    def calculate_churn_rate(self, date=None, period_days=30):
        """Calculate churn rate over specified period"""
        if not date:
            date = timezone.now().date()
        
        period_start = date - timedelta(days=period_days)
        
        # Count users who had active subscriptions at start of period
        users_at_start = CustomUser.objects.filter(
            subscription_status='active',
            date_joined__lte=period_start
        ).count()
        
        if users_at_start == 0:
            return 0
        
        # Count users who churned during the period
        churned_users = CustomUser.objects.filter(
            subscription_status__in=['canceled', 'past_due'],
            subscription_end_date__gte=period_start,
            subscription_end_date__lte=date
        ).count()
        
        churn_rate = (churned_users / users_at_start) * 100
        
        # Store churn rate metric
        RevenueMetric.objects.update_or_create(
            date=date,
            metric_type='churn_rate',
            plan_type='all',
            defaults={
                'value': Decimal(str(churn_rate)),
                'currency': 'USD',
                'calculation_method': f'churned_users_over_{period_days}_days',
                'stripe_data': {
                    'users_at_start': users_at_start,
                    'churned_users': churned_users,
                    'period_days': period_days
                }
            }
        )
        
        return churn_rate
    
    def calculate_arpu(self, date=None):
        """Calculate Average Revenue Per User"""
        if not date:
            date = timezone.now().date()
        
        mrr_data = self.calculate_mrr(date)
        if not mrr_data:
            return None
        
        active_users = CustomUser.objects.filter(
            subscription_status='active'
        ).count()
        
        if active_users == 0:
            return 0
        
        arpu = mrr_data['total_mrr'] / active_users
        
        # Store ARPU metric
        RevenueMetric.objects.update_or_create(
            date=date,
            metric_type='arpu',
            plan_type='all',
            defaults={
                'value': Decimal(str(arpu)),
                'currency': 'USD',
                'calculation_method': 'mrr_divided_by_active_users',
                'stripe_data': {
                    'total_mrr': mrr_data['total_mrr'],
                    'active_users': active_users
                }
            }
        )
        
        return arpu
    
    def get_revenue_trends(self, days=30):
        """Get revenue trends over specified period"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = RevenueMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            plan_type='all'
        ).order_by('date', 'metric_type')
        
        trends = {}
        for metric in metrics:
            if metric.metric_type not in trends:
                trends[metric.metric_type] = []
            
            trends[metric.metric_type].append({
                'date': metric.date.isoformat(),
                'value': float(metric.value),
                'currency': metric.currency
            })
        
        return trends


class UserEngagementAnalyticsService:
    """Service for calculating user engagement metrics"""
    
    def calculate_daily_engagement(self, user, date=None):
        """Calculate engagement metrics for a user on specific date"""
        if not date:
            date = timezone.now().date()
        
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        
        # Get user activity for the day
        activity_logs = ActivityLog.objects.filter(
            user=user,
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        )
        
        # Calculate metrics
        login_count = activity_logs.filter(activity_type='login').count()
        
        # Calculate session duration (simplified)
        session_duration = 0
        login_times = list(activity_logs.filter(
            activity_type='login'
        ).values_list('created_at', flat=True))
        
        if login_times:
            # Estimate session duration based on last activity
            last_activity = activity_logs.order_by('-created_at').first()
            if last_activity:
                session_start = login_times[0]
                session_end = last_activity.created_at
                session_duration = int((session_end - session_start).total_seconds() / 60)
        
        # Count various activities
        scenarios_created = Scenario.objects.filter(
            client__advisor=user,
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).count()
        
        clients_added = Client.objects.filter(
            advisor=user,
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).count()
        
        reports_generated = activity_logs.filter(
            activity_type='report_generated'
        ).count()
        
        # Create or update engagement metric
        engagement_metric, created = UserEngagementMetric.objects.update_or_create(
            user=user,
            date=date,
            defaults={
                'login_count': login_count,
                'session_duration_minutes': session_duration,
                'pages_viewed': activity_logs.count(),
                'actions_performed': activity_logs.count(),
                'scenarios_created': scenarios_created,
                'clients_added': clients_added,
                'reports_generated': reports_generated,
            }
        )
        
        # Calculate engagement score
        engagement_metric.calculate_engagement_score()
        engagement_metric.assess_churn_risk()
        engagement_metric.save()
        
        return engagement_metric
    
    def calculate_engagement_trends(self, days=30):
        """Calculate engagement trends across all users"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = UserEngagementMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values('date').annotate(
            avg_engagement_score=Avg('engagement_score'),
            total_users_at_risk=Count('id', filter=Q(is_at_risk=True)),
            total_active_users=Count('id', filter=Q(engagement_score__gt=0))
        ).order_by('date')
        
        return list(metrics)
    
    def identify_at_risk_users(self, threshold_score=20, days=7):
        """Identify users at risk of churning"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        at_risk_users = UserEngagementMetric.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_at_risk=True
        ).select_related('user').values(
            'user__id',
            'user__email',
            'user__first_name',
            'user__last_name',
            'engagement_score',
            'risk_factors',
            'date'
        ).order_by('engagement_score')
        
        return list(at_risk_users)


class ClientPortfolioAnalyticsService:
    """Service for analyzing client portfolios across all advisors"""
    
    def calculate_portfolio_analytics(self, date=None):
        """Calculate comprehensive portfolio analytics"""
        if not date:
            date = timezone.now().date()
        
        # Basic counts
        total_clients = Client.objects.filter(is_deleted=False).count()
        total_scenarios = Scenario.objects.count()
        
        # Calculate total assets (simplified - would need actual asset values)
        total_assets_tracked = Decimal('0.00')  # Would sum actual asset values
        
        # Distribution metrics
        client_distribution = Client.objects.values('advisor').annotate(
            client_count=Count('id')
        )
        
        if client_distribution:
            avg_clients_per_advisor = sum(
                item['client_count'] for item in client_distribution
            ) / len(client_distribution)
        else:
            avg_clients_per_advisor = 0
        
        scenario_distribution = Scenario.objects.values('client').annotate(
            scenario_count=Count('id')
        )
        
        if scenario_distribution and total_clients > 0:
            avg_scenarios_per_client = total_scenarios / total_clients
        else:
            avg_scenarios_per_client = 0
        
        # Age demographics
        now = timezone.now().date()
        clients_under_50 = Client.objects.filter(
            is_deleted=False,
            birthdate__gt=now - timedelta(days=365*50)
        ).count()
        
        clients_50_to_65 = Client.objects.filter(
            is_deleted=False,
            birthdate__lte=now - timedelta(days=365*50),
            birthdate__gt=now - timedelta(days=365*65)
        ).count()
        
        clients_over_65 = Client.objects.filter(
            is_deleted=False,
            birthdate__lte=now - timedelta(days=365*65)
        ).count()
        
        # Geographic distribution
        geographic_data = {}
        geo_distribution = Client.objects.filter(
            is_deleted=False
        ).exclude(
            state__isnull=True
        ).exclude(
            state__exact=''
        ).values('state').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for item in geo_distribution:
            geographic_data[item['state']] = item['count']
        
        # Feature adoption (simplified)
        roth_conversion_usage = Scenario.objects.filter(
            roth_conversion_annual_amount__gt=0
        ).count()
        
        social_security_planning_usage = Scenario.objects.exclude(
            primary_ss_claiming_age__isnull=True
        ).count()
        
        # Store analytics
        portfolio_analytics, created = ClientPortfolioAnalytics.objects.update_or_create(
            date=date,
            defaults={
                'total_clients': total_clients,
                'total_scenarios': total_scenarios,
                'total_assets_tracked': total_assets_tracked,
                'avg_clients_per_advisor': Decimal(str(avg_clients_per_advisor)),
                'avg_scenarios_per_client': Decimal(str(avg_scenarios_per_client)),
                'avg_assets_per_client': Decimal('0.00'),  # Would calculate from assets
                'clients_under_50': clients_under_50,
                'clients_50_to_65': clients_50_to_65,
                'clients_over_65': clients_over_65,
                'geographic_data': geographic_data,
                'roth_conversion_usage': roth_conversion_usage,
                'social_security_planning_usage': social_security_planning_usage,
                'monte_carlo_usage': 0  # Would count Monte Carlo runs
            }
        )
        
        return portfolio_analytics


class AnalyticsOrchestrator:
    """Main service to coordinate all analytics calculations"""
    
    def __init__(self):
        self.revenue_service = RevenueAnalyticsService()
        self.engagement_service = UserEngagementAnalyticsService()
        self.portfolio_service = ClientPortfolioAnalyticsService()
    
    def run_daily_analytics(self, date=None):
        """Run all daily analytics calculations"""
        if not date:
            date = timezone.now().date()
        
        logger.info(f"Starting daily analytics calculation for {date}")
        
        results = {}
        
        try:
            # Revenue analytics
            logger.info("Calculating revenue metrics...")
            results['mrr'] = self.revenue_service.calculate_mrr(date)
            results['arr'] = self.revenue_service.calculate_arr(date)
            results['churn_rate'] = self.revenue_service.calculate_churn_rate(date)
            results['arpu'] = self.revenue_service.calculate_arpu(date)
            
            # User engagement analytics for all active users
            logger.info("Calculating user engagement metrics...")
            active_users = CustomUser.objects.filter(is_active=True)
            engagement_results = []
            
            for user in active_users:
                try:
                    engagement_metric = self.engagement_service.calculate_daily_engagement(user, date)
                    engagement_results.append({
                        'user_id': user.id,
                        'engagement_score': engagement_metric.engagement_score,
                        'is_at_risk': engagement_metric.is_at_risk
                    })
                except Exception as e:
                    logger.error(f"Error calculating engagement for user {user.id}: {str(e)}")
            
            results['user_engagement'] = engagement_results
            
            # Portfolio analytics
            logger.info("Calculating portfolio analytics...")
            results['portfolio_analytics'] = self.portfolio_service.calculate_portfolio_analytics(date)
            
            logger.info(f"Completed daily analytics calculation for {date}")
            
        except Exception as e:
            logger.error(f"Error in daily analytics calculation: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def get_analytics_dashboard_data(self, days=30):
        """Get comprehensive analytics data for dashboard"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Revenue trends
        revenue_trends = self.revenue_service.get_revenue_trends(days)
        
        # Engagement trends
        engagement_trends = self.engagement_service.calculate_engagement_trends(days)
        
        # At-risk users
        at_risk_users = self.engagement_service.identify_at_risk_users()
        
        # Latest portfolio analytics
        latest_portfolio = ClientPortfolioAnalytics.objects.filter(
            date__lte=end_date
        ).order_by('-date').first()
        
        return {
            'revenue_trends': revenue_trends,
            'engagement_trends': engagement_trends,
            'at_risk_users': at_risk_users,
            'portfolio_analytics': latest_portfolio,
            'generated_at': timezone.now().isoformat()
        }