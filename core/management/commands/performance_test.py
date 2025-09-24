# core/management/commands/performance_test.py
"""
Automated performance testing command for regression detection
"""

from django.core.management.base import BaseCommand, CommandError
from django.test import Client, override_settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone
import time
import json
import statistics
import logging
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = 'Run automated performance tests and detect regressions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--endpoints',
            nargs='+',
            default=['dashboard', 'analytics', 'reports', 'users'],
            help='Endpoints to test (default: all)',
        )
        parser.add_argument(
            '--concurrent-users',
            type=int,
            default=5,
            help='Number of concurrent users to simulate',
        )
        parser.add_argument(
            '--requests-per-user',
            type=int,
            default=10,
            help='Number of requests per user',
        )
        parser.add_argument(
            '--threshold-ms',
            type=int,
            default=2000,
            help='Response time threshold in milliseconds',
        )
        parser.add_argument(
            '--save-baseline',
            action='store_true',
            help='Save results as performance baseline',
        )
        parser.add_argument(
            '--compare-baseline',
            action='store_true',
            help='Compare results with saved baseline',
        )
        parser.add_argument(
            '--output-format',
            choices=['json', 'csv', 'text'],
            default='text',
            help='Output format for results',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('Starting performance test suite...')
        )
        
        # Setup test environment
        test_user = self._setup_test_environment()
        
        # Run performance tests
        results = self._run_performance_tests(test_user, options)
        
        # Analyze results
        analysis = self._analyze_results(results, options)
        
        # Output results
        self._output_results(analysis, options)
        
        # Save or compare baseline
        if options['save_baseline']:
            self._save_baseline(analysis)
        
        if options['compare_baseline']:
            regression_detected = self._compare_baseline(analysis)
            if regression_detected:
                self.stdout.write(
                    self.style.ERROR('Performance regression detected!')
                )
                exit(1)
        
        self.stdout.write(
            self.style.SUCCESS('Performance testing completed.')
        )

    def _setup_test_environment(self):
        """Setup test user and data"""
        try:
            # Create or get test user
            test_user, created = User.objects.get_or_create(
                email='performance_test@example.com',
                defaults={
                    'first_name': 'Performance',
                    'last_name': 'Test',
                    'is_active': True,
                    'is_staff': True,
                    'is_admin': True
                }
            )
            
            if created:
                test_user.set_password('test123')
                test_user.save()
            
            return test_user
            
        except Exception as e:
            raise CommandError(f"Failed to setup test environment: {str(e)}")

    def _run_performance_tests(self, test_user, options):
        """Run concurrent performance tests"""
        endpoints = self._get_test_endpoints(options['endpoints'])
        results = []
        
        self.stdout.write(f"Testing {len(endpoints)} endpoints with {options['concurrent_users']} concurrent users")
        
        with ThreadPoolExecutor(max_workers=options['concurrent_users']) as executor:
            # Submit tasks for each user
            futures = []
            for user_id in range(options['concurrent_users']):
                future = executor.submit(
                    self._run_user_tests,
                    test_user,
                    endpoints,
                    options['requests_per_user'],
                    user_id
                )
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    results.extend(user_results)
                except Exception as e:
                    logger.error(f"User test failed: {str(e)}")
        
        return results

    def _run_user_tests(self, test_user, endpoints, requests_per_user, user_id):
        """Run tests for a single user"""
        client = Client()
        
        # Login
        login_success = client.login(email=test_user.email, password='test123')
        if not login_success:
            # Force login for testing
            client.force_login(test_user)
        
        results = []
        
        for request_num in range(requests_per_user):
            for endpoint_name, endpoint_config in endpoints.items():
                result = self._test_endpoint(
                    client, 
                    endpoint_name, 
                    endpoint_config,
                    user_id,
                    request_num
                )
                results.append(result)
        
        return results

    def _test_endpoint(self, client, endpoint_name, endpoint_config, user_id, request_num):
        """Test a single endpoint"""
        start_time = time.time()
        start_queries = len(connection.queries)
        
        try:
            # Make request
            response = client.get(
                endpoint_config['url'],
                data=endpoint_config.get('params', {}),
                **endpoint_config.get('headers', {})
            )
            
            end_time = time.time()
            end_queries = len(connection.queries)
            
            # Calculate metrics
            response_time = (end_time - start_time) * 1000  # milliseconds
            query_count = end_queries - start_queries
            
            return {
                'endpoint': endpoint_name,
                'user_id': user_id,
                'request_num': request_num,
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'query_count': query_count,
                'content_length': len(response.content) if hasattr(response, 'content') else 0,
                'timestamp': timezone.now().isoformat(),
                'success': 200 <= response.status_code < 300
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                'endpoint': endpoint_name,
                'user_id': user_id,
                'request_num': request_num,
                'response_time_ms': response_time,
                'status_code': 500,
                'query_count': 0,
                'content_length': 0,
                'timestamp': timezone.now().isoformat(),
                'success': False,
                'error': str(e)
            }

    def _get_test_endpoints(self, endpoint_names):
        """Get endpoint configurations for testing"""
        all_endpoints = {
            'dashboard': {
                'url': '/api/admin/dashboard/',
                'params': {},
                'expected_queries': 5
            },
            'analytics': {
                'url': '/api/admin/analytics/summary/',
                'params': {},
                'expected_queries': 10
            },
            'users': {
                'url': '/api/admin/users/',
                'params': {'limit': 20},
                'expected_queries': 3
            },
            'reports': {
                'url': '/api/reports/',
                'params': {'limit': 10},
                'expected_queries': 5
            },
            'monitoring': {
                'url': '/api/admin/monitoring/',
                'params': {},
                'expected_queries': 8
            },
            'performance': {
                'url': '/api/admin/performance/',
                'params': {},
                'expected_queries': 6
            },
            'support': {
                'url': '/api/admin/support/tickets/',
                'params': {'status': 'open'},
                'expected_queries': 4
            }
        }
        
        # Return only requested endpoints
        return {name: config for name, config in all_endpoints.items() 
                if name in endpoint_names}

    def _analyze_results(self, results, options):
        """Analyze performance test results"""
        if not results:
            return {}
        
        analysis = {
            'total_requests': len(results),
            'successful_requests': sum(1 for r in results if r['success']),
            'failed_requests': sum(1 for r in results if not r['success']),
            'success_rate': sum(1 for r in results if r['success']) / len(results) * 100,
            'total_duration': max(r['timestamp'] for r in results),
            'endpoints': {}
        }
        
        # Analyze by endpoint
        endpoints = {}
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result)
        
        for endpoint, endpoint_results in endpoints.items():
            successful_results = [r for r in endpoint_results if r['success']]
            
            if successful_results:
                response_times = [r['response_time_ms'] for r in successful_results]
                query_counts = [r['query_count'] for r in successful_results]
                
                endpoint_analysis = {
                    'total_requests': len(endpoint_results),
                    'successful_requests': len(successful_results),
                    'success_rate': len(successful_results) / len(endpoint_results) * 100,
                    'response_time': {
                        'min': min(response_times),
                        'max': max(response_times),
                        'mean': statistics.mean(response_times),
                        'median': statistics.median(response_times),
                        'p95': self._percentile(response_times, 95),
                        'p99': self._percentile(response_times, 99)
                    },
                    'query_count': {
                        'min': min(query_counts),
                        'max': max(query_counts),
                        'mean': statistics.mean(query_counts),
                        'median': statistics.median(query_counts)
                    },
                    'threshold_violations': sum(1 for rt in response_times if rt > options['threshold_ms']),
                    'errors': [r.get('error') for r in endpoint_results if not r['success']]
                }
            else:
                endpoint_analysis = {
                    'total_requests': len(endpoint_results),
                    'successful_requests': 0,
                    'success_rate': 0,
                    'errors': [r.get('error') for r in endpoint_results]
                }
            
            analysis['endpoints'][endpoint] = endpoint_analysis
        
        return analysis

    def _percentile(self, data, percentile):
        """Calculate percentile of data"""
        return statistics.quantiles(data, n=100)[percentile - 1]

    def _output_results(self, analysis, options):
        """Output test results in specified format"""
        if options['output_format'] == 'json':
            self.stdout.write(json.dumps(analysis, indent=2, default=str))
        elif options['output_format'] == 'csv':
            self._output_csv(analysis)
        else:
            self._output_text(analysis, options)

    def _output_text(self, analysis, options):
        """Output results in human-readable text format"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('PERFORMANCE TEST RESULTS')
        self.stdout.write('=' * 60)
        
        # Overall stats
        self.stdout.write(f"\nOverall Results:")
        self.stdout.write(f"  Total Requests: {analysis['total_requests']}")
        self.stdout.write(f"  Successful: {analysis['successful_requests']}")
        self.stdout.write(f"  Failed: {analysis['failed_requests']}")
        self.stdout.write(f"  Success Rate: {analysis['success_rate']:.1f}%")
        
        # Endpoint details
        for endpoint, stats in analysis['endpoints'].items():
            self.stdout.write(f"\n{endpoint.upper()} Endpoint:")
            self.stdout.write(f"  Requests: {stats['total_requests']}")
            self.stdout.write(f"  Success Rate: {stats['success_rate']:.1f}%")
            
            if 'response_time' in stats:
                rt = stats['response_time']
                self.stdout.write(f"  Response Time (ms):")
                self.stdout.write(f"    Min: {rt['min']:.0f}")
                self.stdout.write(f"    Max: {rt['max']:.0f}")
                self.stdout.write(f"    Mean: {rt['mean']:.0f}")
                self.stdout.write(f"    Median: {rt['median']:.0f}")
                self.stdout.write(f"    95th percentile: {rt['p95']:.0f}")
                self.stdout.write(f"    99th percentile: {rt['p99']:.0f}")
                
                qc = stats['query_count']
                self.stdout.write(f"  Database Queries:")
                self.stdout.write(f"    Min: {qc['min']:.0f}")
                self.stdout.write(f"    Max: {qc['max']:.0f}")
                self.stdout.write(f"    Mean: {qc['mean']:.1f}")
                
                threshold_violations = stats['threshold_violations']
                if threshold_violations > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Threshold Violations: {threshold_violations} "
                            f"requests exceeded {options['threshold_ms']}ms"
                        )
                    )
                
            if stats.get('errors'):
                self.stdout.write(
                    self.style.ERROR(f"  Errors: {len(stats['errors'])}")
                )

    def _output_csv(self, analysis):
        """Output results in CSV format"""
        import csv
        import sys
        
        writer = csv.writer(sys.stdout)
        
        # Header
        writer.writerow([
            'endpoint', 'total_requests', 'success_rate', 'mean_response_time',
            'p95_response_time', 'mean_query_count', 'threshold_violations'
        ])
        
        # Data rows
        for endpoint, stats in analysis['endpoints'].items():
            if 'response_time' in stats:
                writer.writerow([
                    endpoint,
                    stats['total_requests'],
                    f"{stats['success_rate']:.1f}",
                    f"{stats['response_time']['mean']:.0f}",
                    f"{stats['response_time']['p95']:.0f}",
                    f"{stats['query_count']['mean']:.1f}",
                    stats['threshold_violations']
                ])

    def _save_baseline(self, analysis):
        """Save performance baseline for future comparisons"""
        from core.models import SystemPerformanceMetric
        
        try:
            # Save baseline metrics
            for endpoint, stats in analysis['endpoints'].items():
                if 'response_time' in stats:
                    SystemPerformanceMetric.objects.create(
                        metric_type='performance_baseline',
                        endpoint=endpoint,
                        value=stats['response_time']['mean'],
                        unit='ms',
                        metadata={
                            'p95': stats['response_time']['p95'],
                            'p99': stats['response_time']['p99'],
                            'query_count': stats['query_count']['mean'],
                            'success_rate': stats['success_rate'],
                            'test_date': timezone.now().isoformat()
                        }
                    )
            
            self.stdout.write(
                self.style.SUCCESS('Performance baseline saved successfully.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to save baseline: {str(e)}')
            )

    def _compare_baseline(self, analysis):
        """Compare results with saved baseline"""
        from core.models import SystemPerformanceMetric
        
        try:
            regression_detected = False
            
            for endpoint, stats in analysis['endpoints'].items():
                if 'response_time' not in stats:
                    continue
                
                # Get baseline
                baseline = SystemPerformanceMetric.objects.filter(
                    metric_type='performance_baseline',
                    endpoint=endpoint
                ).order_by('-timestamp').first()
                
                if not baseline:
                    self.stdout.write(
                        self.style.WARNING(f'No baseline found for {endpoint}')
                    )
                    continue
                
                # Compare metrics
                current_mean = stats['response_time']['mean']
                baseline_mean = baseline.value
                
                # 20% regression threshold
                regression_threshold = baseline_mean * 1.2
                
                if current_mean > regression_threshold:
                    self.stdout.write(
                        self.style.ERROR(
                            f'REGRESSION DETECTED in {endpoint}: '
                            f'{current_mean:.0f}ms vs baseline {baseline_mean:.0f}ms '
                            f'({((current_mean / baseline_mean - 1) * 100):.1f}% slower)'
                        )
                    )
                    regression_detected = True
                else:
                    improvement = (1 - current_mean / baseline_mean) * 100
                    if improvement > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'{endpoint}: {improvement:.1f}% faster than baseline'
                            )
                        )
            
            return regression_detected
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to compare baseline: {str(e)}')
            )
            return False