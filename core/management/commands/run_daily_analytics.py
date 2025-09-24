# backend/core/management/commands/run_daily_analytics.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta

from core.services.analytics_service import AnalyticsOrchestrator


class Command(BaseCommand):
    help = 'Run daily analytics calculations for revenue, engagement, and portfolio metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to run analytics for (YYYY-MM-DD format). Defaults to today.',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=0,
            help='Number of days back from today to run analytics for. Overrides --date.',
        )
        parser.add_argument(
            '--backfill',
            type=int,
            help='Backfill analytics for the specified number of days.',
        )

    def handle(self, *args, **options):
        orchestrator = AnalyticsOrchestrator()
        
        if options['backfill']:
            # Backfill analytics for multiple days
            self.stdout.write(
                self.style.SUCCESS(f"Starting backfill for {options['backfill']} days...")
            )
            
            end_date = timezone.now().date()
            for i in range(options['backfill']):
                date = end_date - timedelta(days=i)
                self.stdout.write(f"Running analytics for {date}...")
                
                try:
                    results = orchestrator.run_daily_analytics(date)
                    self.stdout.write(
                        self.style.SUCCESS(f"Completed analytics for {date}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error running analytics for {date}: {str(e)}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS("Backfill completed!")
            )
            return
        
        # Determine target date
        if options['days_back']:
            target_date = timezone.now().date() - timedelta(days=options['days_back'])
        elif options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Date must be in YYYY-MM-DD format')
                )
                return
        else:
            target_date = timezone.now().date()
        
        self.stdout.write(f"Running daily analytics for {target_date}...")
        
        try:
            results = orchestrator.run_daily_analytics(target_date)
            
            # Display results
            if 'error' in results:
                self.stdout.write(
                    self.style.ERROR(f"Analytics calculation failed: {results['error']}")
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS("Daily analytics completed successfully!")
            )
            
            # Revenue metrics
            if results.get('mrr'):
                self.stdout.write(f"MRR: ${results['mrr']['total_mrr']:,.2f}")
            if results.get('arr'):
                self.stdout.write(f"ARR: ${results['arr']:,.2f}")
            if results.get('churn_rate') is not None:
                self.stdout.write(f"Churn Rate: {results['churn_rate']:.2f}%")
            if results.get('arpu') is not None:
                self.stdout.write(f"ARPU: ${results['arpu']:,.2f}")
            
            # User engagement
            engagement_results = results.get('user_engagement', [])
            if engagement_results:
                avg_engagement = sum(u['engagement_score'] for u in engagement_results) / len(engagement_results)
                at_risk_count = sum(1 for u in engagement_results if u['is_at_risk'])
                
                self.stdout.write(f"Users processed: {len(engagement_results)}")
                self.stdout.write(f"Average engagement score: {avg_engagement:.1f}")
                self.stdout.write(f"Users at risk: {at_risk_count}")
            
            # Portfolio analytics
            portfolio = results.get('portfolio_analytics')
            if portfolio:
                self.stdout.write(f"Total clients: {portfolio.total_clients}")
                self.stdout.write(f"Total scenarios: {portfolio.total_scenarios}")
                self.stdout.write(f"Avg clients per advisor: {portfolio.avg_clients_per_advisor}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error running daily analytics: {str(e)}")
            )