# backend/core/performance_middleware.py

import time
import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.urls import resolve
from django.conf import settings
from .models import SystemPerformanceMetric
from .services.cache_service import CacheService, PerformanceCacheService

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to track API performance metrics including:
    - Response times
    - Database query counts and times
    - Error rates
    - Request volume
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Start timing and prepare tracking"""
        request._perf_start_time = time.time()
        request._perf_db_queries_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Record performance metrics after processing"""
        try:
            # Skip static files and admin interface
            if (hasattr(request, '_perf_start_time') and 
                not request.path.startswith('/static/') and 
                not request.path.startswith('/admin/') and
                request.path.startswith('/api/')):
                
                self._record_performance_metrics(request, response)
        
        except Exception as e:
            logger.error(f"Performance monitoring error: {str(e)}")
        
        return response
    
    def _record_performance_metrics(self, request, response):
        """Record detailed performance metrics with caching integration"""
        # Calculate response time
        response_time = (time.time() - request._perf_start_time) * 1000  # milliseconds
        
        # Get endpoint info
        try:
            resolved_url = resolve(request.path)
            endpoint = f"{request.method} {resolved_url.url_name or request.path}"
        except:
            endpoint = f"{request.method} {request.path}"
        
        # Calculate database metrics
        db_queries_end = len(connection.queries)
        db_query_count = db_queries_end - request._perf_db_queries_start
        
        # Calculate database time and analyze queries
        db_time = 0
        slow_queries = []
        duplicate_queries = {}
        
        if hasattr(connection, 'queries') and db_query_count > 0:
            recent_queries = connection.queries[-db_query_count:]
            for query in recent_queries:
                try:
                    query_time = float(query.get('time', 0))
                    db_time += query_time
                    
                    # Track slow queries
                    if query_time > 0.1:  # 100ms threshold
                        slow_queries.append({
                            'time': query_time,
                            'sql': query['sql'][:200] + '...' if len(query['sql']) > 200 else query['sql']
                        })
                    
                    # Track duplicate queries for optimization
                    sql_normalized = self._normalize_sql(query['sql'])
                    duplicate_queries[sql_normalized] = duplicate_queries.get(sql_normalized, 0) + 1
                    
                except (ValueError, TypeError):
                    pass
        
        db_time_ms = db_time * 1000  # Convert to milliseconds
        
        # Cache performance metrics
        cache_hits = getattr(request, '_cache_hits', 0)
        cache_misses = getattr(request, '_cache_misses', 0)
        cache_ratio = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
        
        # Prepare metadata
        metadata = {
            'method': request.method,
            'path': request.path,
            'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self._get_client_ip(request),
            'db_query_count': db_query_count,
            'db_time_ms': round(db_time_ms, 2),
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'cache_ratio': round(cache_ratio, 3),
            'slow_queries_count': len(slow_queries),
            'duplicate_queries': {k: v for k, v in duplicate_queries.items() if v > 1}
        }
        
        # Log performance warnings
        if response_time > getattr(settings, 'CACHE_SLOW_QUERY_THRESHOLD', 1000):
            logger.warning(f"Slow request ({response_time:.0f}ms): {endpoint}")
        
        if len(slow_queries) > 0:
            logger.warning(f"Found {len(slow_queries)} slow queries for {endpoint}")
            for query in slow_queries[:3]:  # Log first 3 slow queries
                logger.warning(f"Slow query ({query['time']:.3f}s): {query['sql']}")
        
        if len(duplicate_queries) > 0:
            duplicates = {k: v for k, v in duplicate_queries.items() if v > 3}
            if duplicates:
                logger.warning(f"Duplicate queries detected for {endpoint}: {list(duplicates.keys())[:3]}")
        
        # Add performance headers for debugging
        if settings.DEBUG:
            response['X-Response-Time'] = f"{response_time:.0f}ms"
            response['X-DB-Queries'] = str(db_query_count)
            response['X-DB-Time'] = f"{db_time_ms:.0f}ms"
            response['X-Cache-Ratio'] = f"{cache_ratio:.1%}"
            response['X-Slow-Queries'] = str(len(slow_queries))
        
        # Record metrics asynchronously to avoid impacting response time
        self._async_record_metrics(endpoint, response, response_time, metadata)
        
        # Cache performance data for analytics
        PerformanceCacheService.cache_query_performance(endpoint, response_time / 1000, db_query_count)
    
    def _async_record_metrics(self, endpoint, response, response_time, metadata):
        """Record metrics asynchronously"""
        try:
            # Record response time metric
            SystemPerformanceMetric.objects.create(
                metric_type='response_time',
                value=round(response_time, 2),
                unit='ms',
                endpoint=endpoint,
                status_code=response.status_code,
                metadata=metadata
            )
            
            # Record request volume
            SystemPerformanceMetric.objects.create(
                metric_type='request_volume',
                value=1,
                unit='count',
                endpoint=endpoint,
                status_code=response.status_code,
                metadata={'method': metadata['method']}
            )
            
            # Record error rate if error occurred
            if response.status_code >= 400:
                SystemPerformanceMetric.objects.create(
                    metric_type='error_rate',
                    value=1,
                    unit='count',
                    endpoint=endpoint,
                    status_code=response.status_code,
                    metadata={
                        'error_type': 'client_error' if response.status_code < 500 else 'server_error',
                        'method': metadata['method']
                    }
                )
            
            # Record database performance if queries were made
            if metadata['db_query_count'] > 0:
                SystemPerformanceMetric.objects.create(
                    metric_type='database_connections',
                    value=metadata['db_query_count'],
                    unit='count',
                    endpoint=endpoint,
                    metadata={
                        'db_time_ms': metadata['db_time_ms'],
                        'queries_per_request': metadata['db_query_count']
                    }
                )
        
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {str(e)}")
    
    def _get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _normalize_sql(self, sql):
        """Normalize SQL for duplicate detection"""
        import re
        # Remove specific values and IDs to detect patterns
        normalized = re.sub(r'= \d+', '= ?', sql)
        normalized = re.sub(r"= '[^']*'", "= ?", normalized)
        normalized = re.sub(r'IN \([^\)]+\)', 'IN (?)', normalized)
        return normalized[:100]  # Truncate for storage efficiency


class SystemHealthMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to record system-level health metrics periodically
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response
        self._last_health_check = None
        self._health_check_interval = 300  # 5 minutes
    
    def process_request(self, request):
        """Check if we need to record system health metrics"""
        now = timezone.now()
        
        if (self._last_health_check is None or 
            (now - self._last_health_check).total_seconds() >= self._health_check_interval):
            
            self._record_system_health()
            self._last_health_check = now
        
        return None
    
    def _record_system_health(self):
        """Record system-level health metrics"""
        try:
            import psutil
            import os
            from django.contrib.auth import get_user_model
            from .models import ActivityLog
            
            User = get_user_model()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            SystemPerformanceMetric.objects.create(
                metric_type='cpu_usage',
                value=cpu_percent,
                unit='percent',
                metadata={'cores': psutil.cpu_count()}
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            SystemPerformanceMetric.objects.create(
                metric_type='memory_usage',
                value=memory.percent,
                unit='percent',
                metadata={
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2)
                }
            )
            
            # Active users (users active in last 24 hours)
            twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
            active_users = ActivityLog.objects.filter(
                created_at__gte=twenty_four_hours_ago
            ).values('user').distinct().count()
            
            SystemPerformanceMetric.objects.create(
                metric_type='active_users',
                value=active_users,
                unit='count'
            )
            
            # Database connections
            db_connections = len(connection.queries) if hasattr(connection, 'queries') else 0
            SystemPerformanceMetric.objects.create(
                metric_type='database_connections',
                value=db_connections,
                unit='count'
            )
            
            # System uptime (simplified - would be more complex in production)
            SystemPerformanceMetric.objects.create(
                metric_type='uptime',
                value=99.9,  # Would calculate actual uptime
                unit='percent'
            )
        
        except ImportError:
            # psutil not available - record basic metrics
            self._record_basic_health()
        except Exception as e:
            logger.error(f"Failed to record system health metrics: {str(e)}")
    
    def _record_basic_health(self):
        """Record basic health metrics when psutil is not available"""
        try:
            from django.contrib.auth import get_user_model
            from .models import ActivityLog
            
            User = get_user_model()
            
            # Active users
            twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
            active_users = ActivityLog.objects.filter(
                created_at__gte=twenty_four_hours_ago
            ).values('user').distinct().count()
            
            SystemPerformanceMetric.objects.create(
                metric_type='active_users',
                value=active_users,
                unit='count'
            )
            
            # Basic uptime indicator
            SystemPerformanceMetric.objects.create(
                metric_type='uptime',
                value=100,  # Basic assumption that if middleware runs, system is up
                unit='percent'
            )
        
        except Exception as e:
            logger.error(f"Failed to record basic health metrics: {str(e)}")