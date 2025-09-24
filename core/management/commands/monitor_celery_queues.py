"""
Management command to monitor Celery queue status and health
"""

import json
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from celery import current_app

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor Celery queue status and health'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            type=str,
            help='Specific queue to monitor (default: all queues)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'json'],
            default='table',
            help='Output format (table or json)'
        )
        parser.add_argument(
            '--show-tasks',
            action='store_true',
            help='Show active tasks details'
        )
        parser.add_argument(
            '--show-workers',
            action='store_true', 
            help='Show worker details'
        )
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Perform health check and exit'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        try:
            if options['health_check']:
                self._health_check()
                return
            
            # Get Celery inspector
            inspect = current_app.control.inspect()
            
            if not inspect:
                raise CommandError("Cannot connect to Celery. Make sure workers are running.")
            
            # Gather information
            queue_stats = self._get_queue_stats(inspect, options.get('queue'))
            worker_stats = self._get_worker_stats(inspect) if options.get('show_workers') else {}
            active_tasks = self._get_active_tasks(inspect) if options.get('show_tasks') else {}
            
            # Output results
            if options['format'] == 'json':
                self._output_json(queue_stats, worker_stats, active_tasks)
            else:
                self._output_table(queue_stats, worker_stats, active_tasks, options)
                
        except Exception as e:
            logger.error(f"Queue monitoring failed: {str(e)}")
            raise CommandError(f"Queue monitoring failed: {str(e)}")
    
    def _health_check(self):
        """Perform basic health check"""
        try:
            from retirementadvisorpro.celery import celery_health_check
            
            if celery_health_check():
                self.stdout.write(
                    self.style.SUCCESS("✓ Celery workers are healthy and responsive")
                )
                return True
            else:
                self.stdout.write(
                    self.style.ERROR("✗ Celery workers are not responsive")
                )
                return False
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Health check failed: {str(e)}")
            )
            return False
    
    def _get_queue_stats(self, inspect, target_queue=None):
        """Get queue statistics"""
        stats = {}
        
        try:
            # Get active tasks by queue
            active = inspect.active()
            if active:
                for worker, tasks in active.items():
                    for task in tasks:
                        routing_key = task.get('delivery_info', {}).get('routing_key', 'default')
                        
                        if target_queue and routing_key != target_queue:
                            continue
                        
                        if routing_key not in stats:
                            stats[routing_key] = {
                                'active': 0,
                                'scheduled': 0,
                                'reserved': 0,
                                'workers': set()
                            }
                        
                        stats[routing_key]['active'] += 1
                        stats[routing_key]['workers'].add(worker)
            
            # Get scheduled tasks
            scheduled = inspect.scheduled()
            if scheduled:
                for worker, tasks in scheduled.items():
                    for task in tasks:
                        routing_key = task.get('delivery_info', {}).get('routing_key', 'default')
                        
                        if target_queue and routing_key != target_queue:
                            continue
                        
                        if routing_key not in stats:
                            stats[routing_key] = {
                                'active': 0,
                                'scheduled': 0,
                                'reserved': 0,
                                'workers': set()
                            }
                        
                        stats[routing_key]['scheduled'] += 1
                        stats[routing_key]['workers'].add(worker)
            
            # Get reserved tasks
            reserved = inspect.reserved()
            if reserved:
                for worker, tasks in reserved.items():
                    for task in tasks:
                        routing_key = task.get('delivery_info', {}).get('routing_key', 'default')
                        
                        if target_queue and routing_key != target_queue:
                            continue
                        
                        if routing_key not in stats:
                            stats[routing_key] = {
                                'active': 0,
                                'scheduled': 0,
                                'reserved': 0,
                                'workers': set()
                            }
                        
                        stats[routing_key]['reserved'] += 1
                        stats[routing_key]['workers'].add(worker)
            
            # Convert sets to lists for JSON serialization
            for queue in stats:
                stats[queue]['workers'] = list(stats[queue]['workers'])
                stats[queue]['worker_count'] = len(stats[queue]['workers'])
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {str(e)}")
        
        return stats
    
    def _get_worker_stats(self, inspect):
        """Get worker statistics"""
        try:
            stats = inspect.stats()
            registered = inspect.registered()
            
            worker_info = {}
            if stats:
                for worker, worker_stats in stats.items():
                    worker_info[worker] = {
                        'status': 'online',
                        'pool': worker_stats.get('pool', {}),
                        'rusage': worker_stats.get('rusage', {}),
                        'total_processed': worker_stats.get('total', {}).get('total', 0),
                        'load_avg': worker_stats.get('rusage', {}).get('stime', 0),
                    }
            
            if registered:
                for worker, tasks in registered.items():
                    if worker in worker_info:
                        worker_info[worker]['registered_tasks'] = len(tasks)
            
            return worker_info
            
        except Exception as e:
            logger.error(f"Failed to get worker stats: {str(e)}")
            return {}
    
    def _get_active_tasks(self, inspect):
        """Get detailed active task information"""
        try:
            active = inspect.active()
            task_details = {}
            
            if active:
                for worker, tasks in active.items():
                    task_details[worker] = []
                    for task in tasks:
                        task_info = {
                            'id': task.get('id'),
                            'name': task.get('name'),
                            'queue': task.get('delivery_info', {}).get('routing_key', 'default'),
                            'args': task.get('args', []),
                            'kwargs': task.get('kwargs', {}),
                            'time_start': task.get('time_start'),
                            'worker_pid': task.get('worker_pid')
                        }
                        task_details[worker].append(task_info)
            
            return task_details
            
        except Exception as e:
            logger.error(f"Failed to get active tasks: {str(e)}")
            return {}
    
    def _output_json(self, queue_stats, worker_stats, active_tasks):
        """Output results in JSON format"""
        output = {
            'timestamp': timezone.now().isoformat(),
            'queues': queue_stats,
            'workers': worker_stats,
            'active_tasks': active_tasks
        }
        
        self.stdout.write(json.dumps(output, indent=2, default=str))
    
    def _output_table(self, queue_stats, worker_stats, active_tasks, options):
        """Output results in table format"""
        self.stdout.write(
            self.style.SUCCESS(f"\nCelery Queue Status - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        )
        self.stdout.write("=" * 80)
        
        # Queue Statistics Table
        if queue_stats:
            self.stdout.write("\nQueue Statistics:")
            self.stdout.write("-" * 60)
            self.stdout.write(f"{'Queue':<20} {'Active':<8} {'Scheduled':<10} {'Reserved':<8} {'Workers':<8}")
            self.stdout.write("-" * 60)
            
            for queue, stats in queue_stats.items():
                self.stdout.write(
                    f"{queue:<20} {stats['active']:<8} {stats['scheduled']:<10} "
                    f"{stats['reserved']:<8} {stats['worker_count']:<8}"
                )
        else:
            self.stdout.write("\nNo queue statistics available")
        
        # Worker Statistics Table
        if options.get('show_workers') and worker_stats:
            self.stdout.write("\nWorker Statistics:")
            self.stdout.write("-" * 80)
            self.stdout.write(f"{'Worker':<30} {'Status':<10} {'Processed':<10} {'Load':<10}")
            self.stdout.write("-" * 80)
            
            for worker, stats in worker_stats.items():
                load_avg = f"{stats.get('load_avg', 0):.2f}"
                self.stdout.write(
                    f"{worker:<30} {stats['status']:<10} {stats['total_processed']:<10} {load_avg:<10}"
                )
        
        # Active Tasks Details
        if options.get('show_tasks') and active_tasks:
            self.stdout.write("\nActive Tasks:")
            self.stdout.write("-" * 80)
            
            for worker, tasks in active_tasks.items():
                if tasks:
                    self.stdout.write(f"\nWorker: {worker}")
                    for task in tasks:
                        self.stdout.write(f"  - {task['name']} ({task['id'][:8]}...) in {task['queue']}")
        
        self.stdout.write("=" * 80)
        
        # Summary
        total_active = sum(stats.get('active', 0) for stats in queue_stats.values())
        total_scheduled = sum(stats.get('scheduled', 0) for stats in queue_stats.values())
        total_workers = len(worker_stats) if worker_stats else 0
        
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"  Total Queues: {len(queue_stats)}")
        self.stdout.write(f"  Total Workers: {total_workers}")
        self.stdout.write(f"  Active Tasks: {total_active}")
        self.stdout.write(f"  Scheduled Tasks: {total_scheduled}")
        
        # Health indicators
        if total_workers == 0:
            self.stdout.write(self.style.ERROR("  ⚠️  No workers detected"))
        elif total_active > 100:
            self.stdout.write(self.style.WARNING(f"  ⚠️  High task load: {total_active} active tasks"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ System appears healthy"))
    
    def _get_queue_lengths_from_redis(self):
        """Get queue lengths directly from Redis (alternative method)"""
        try:
            import redis
            from django.conf import settings
            
            # Connect to Redis
            redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
            
            queues = ['default', 'ai_processing', 'email_sync', 'sms_processing', 'analytics']
            queue_lengths = {}
            
            for queue_name in queues:
                length = redis_client.llen(queue_name)
                queue_lengths[queue_name] = length
            
            return queue_lengths
            
        except Exception as e:
            logger.error(f"Failed to get queue lengths from Redis: {str(e)}")
            return {}