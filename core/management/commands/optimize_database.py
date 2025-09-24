# core/management/commands/optimize_database.py
"""
Django management command to optimize database performance through indices and analysis
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize database performance by adding indices and analyzing queries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze-only',
            action='store_true',
            help='Only analyze existing queries without making changes',
        )
        parser.add_argument(
            '--drop-unused',
            action='store_true',
            help='Drop unused indices (use with caution)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force execution without confirmation prompts',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('Starting database optimization...')
        )

        if options['analyze_only']:
            self._analyze_performance()
        else:
            self._optimize_database(options)

        self.stdout.write(
            self.style.SUCCESS('Database optimization completed.')
        )

    def _analyze_performance(self):
        """Analyze current database performance"""
        self.stdout.write('Analyzing database performance...')
        
        with connection.cursor() as cursor:
            # Get table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY tablename, attname;
            """)
            
            stats = cursor.fetchall()
            
            self.stdout.write('\nTable Statistics:')
            current_table = None
            for row in stats:
                schema, table, column, n_distinct, correlation = row
                if table != current_table:
                    self.stdout.write(f'\n{table}:')
                    current_table = table
                
                self.stdout.write(f'  {column}: distinct={n_distinct}, correlation={correlation}')

            # Get slow queries from logs (if available)
            self._analyze_slow_queries()

    def _analyze_slow_queries(self):
        """Analyze slow queries from performance logs"""
        try:
            from core.models import SystemPerformanceMetric
            from django.db.models import Avg, Count
            
            # Get slowest endpoints
            slow_endpoints = SystemPerformanceMetric.objects.filter(
                metric_type='response_time'
            ).values('endpoint').annotate(
                avg_time=Avg('value'),
                request_count=Count('id')
            ).filter(avg_time__gt=1000).order_by('-avg_time')[:10]
            
            self.stdout.write('\nSlowest Endpoints (>1000ms average):')
            for endpoint in slow_endpoints:
                self.stdout.write(
                    f"  {endpoint['endpoint']}: {endpoint['avg_time']:.0f}ms "
                    f"({endpoint['request_count']} requests)"
                )
                
        except ImportError:
            self.stdout.write('Performance metrics not available for analysis.')

    def _optimize_database(self, options):
        """Apply database optimizations"""
        optimizations = [
            ('User indices', self._create_user_indices),
            ('Client indices', self._create_client_indices),
            ('Scenario indices', self._create_scenario_indices),
            ('Analytics indices', self._create_analytics_indices),
            ('Admin indices', self._create_admin_indices),
            ('Performance indices', self._create_performance_indices),
        ]

        for name, func in optimizations:
            if not options['force']:
                confirm = input(f"Apply {name}? (y/n): ")
                if confirm.lower() != 'y':
                    continue
            
            self.stdout.write(f'Applying {name}...')
            try:
                func()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {name} applied successfully')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error applying {name}: {str(e)}')
                )

    def _create_user_indices(self):
        """Create indices for user-related queries"""
        indices = [
            # User lookup and authentication
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_email_active ON core_customuser(email) WHERE is_active = true;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_last_login ON core_customuser(last_login) WHERE last_login IS NOT NULL;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_date_joined ON core_customuser(date_joined);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_role_active ON core_customuser(role, is_active) WHERE is_active = true;",
            
            # Subscription and billing
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_stripe_customer ON core_customuser(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_subscription_status ON core_customuser(subscription_status);",
        ]
        
        self._execute_indices(indices)

    def _create_client_indices(self):
        """Create indices for client-related queries"""
        indices = [
            # Client lookup by advisor
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_client_advisor ON core_client(advisor_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_client_created_at ON core_client(created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_client_advisor_created ON core_client(advisor_id, created_at);",
            
            # Client search
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_client_name_search ON core_client USING gin(to_tsvector('english', first_name || ' ' || last_name));",
        ]
        
        self._execute_indices(indices)

    def _create_scenario_indices(self):
        """Create indices for scenario-related queries"""
        indices = [
            # Scenario lookup
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_client ON core_scenario(client_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_created_at ON core_scenario(created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_client_created ON core_scenario(client_id, created_at);",
            
            # Income sources
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_income_scenario ON core_incomesource(scenario_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_income_type ON core_incomesource(income_type);",
            
            # Real estate
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_realestate_scenario ON core_realestate(scenario_id);",
        ]
        
        self._execute_indices(indices)

    def _create_analytics_indices(self):
        """Create indices for analytics queries"""
        indices = [
            # Report executions
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_report_execution_report ON core_reportexecution(report_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_report_execution_user ON core_reportexecution(executed_by_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_report_execution_date ON core_reportexecution(started_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_report_execution_status ON core_reportexecution(status);",
            
            # Churn predictions
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_churn_prediction_user ON core_userchurnprediction(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_churn_prediction_risk ON core_userchurnprediction(risk_level);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_churn_prediction_date ON core_userchurnprediction(predicted_at);",
            
            # Customer lifetime value
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clv_user ON core_customerlifetimevalue(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clv_segment ON core_customerlifetimevalue(value_segment);",
        ]
        
        self._execute_indices(indices)

    def _create_admin_indices(self):
        """Create indices for admin operations"""
        indices = [
            # Activity logs
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activity_log_user ON core_activitylog(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activity_log_date ON core_activitylog(created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activity_log_action ON core_activitylog(action);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activity_log_user_date ON core_activitylog(user_id, created_at);",
            
            # Admin audit logs
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admin_audit_user ON core_adminaudit(admin_user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admin_audit_date ON core_adminaudit(created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_admin_audit_action ON core_adminaudit(action);",
            
            # Support tickets
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_support_ticket_user ON core_supportticket(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_support_ticket_status ON core_supportticket(status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_support_ticket_priority ON core_supportticket(priority);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_support_ticket_created ON core_supportticket(created_at);",
        ]
        
        self._execute_indices(indices)

    def _create_performance_indices(self):
        """Create indices for performance monitoring"""
        indices = [
            # System performance metrics
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_perf_metric_type ON core_systemperformancemetric(metric_type);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_perf_metric_endpoint ON core_systemperformancemetric(endpoint);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_perf_metric_date ON core_systemperformancemetric(timestamp);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_perf_metric_type_date ON core_systemperformancemetric(metric_type, timestamp);",
            
            # Communication logs
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communication_user ON core_communication(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communication_date ON core_communication(created_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communication_type ON core_communication(communication_type);",
        ]
        
        self._execute_indices(indices)

    def _execute_indices(self, indices):
        """Execute a list of index creation statements"""
        with connection.cursor() as cursor:
            for index_sql in indices:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(f'  ✓ Created index')
                except Exception as e:
                    if 'already exists' in str(e):
                        self.stdout.write(f'  - Index already exists')
                    else:
                        self.stdout.write(f'  ✗ Error: {str(e)}')

    def _drop_unused_indices(self):
        """Drop unused indices (use with caution)"""
        # This would analyze index usage statistics and drop unused ones
        # Implementation would depend on PostgreSQL pg_stat_user_indexes
        self.stdout.write('Unused index dropping not implemented yet.')

    def _analyze_index_usage(self):
        """Analyze index usage statistics"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC;
            """)
            
            results = cursor.fetchall()
            
            self.stdout.write('\nIndex Usage Statistics:')
            for row in results:
                schema, table, index, scans, reads, fetches = row
                self.stdout.write(
                    f'  {table}.{index}: {scans} scans, {reads} reads, {fetches} fetches'
                )