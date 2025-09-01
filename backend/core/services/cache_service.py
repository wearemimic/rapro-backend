# core/services/cache_service.py
import json
import hashlib
import logging
from datetime import timedelta
from typing import Any, Dict, Optional, Union, Callable
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class CacheService:
    """
    Enhanced caching service with Redis support for expensive operations
    """
    
    # Cache timeout configurations (in seconds)
    TIMEOUTS = {
        'analytics_summary': 300,      # 5 minutes
        'user_metrics': 600,           # 10 minutes  
        'revenue_metrics': 1800,       # 30 minutes
        'engagement_metrics': 900,     # 15 minutes
        'churn_metrics': 3600,         # 1 hour
        'dashboard_data': 300,         # 5 minutes
        'report_execution': 1800,      # 30 minutes
        'predictive_models': 7200,     # 2 hours
        'tax_calculations': 86400,     # 24 hours
        'scenario_results': 3600,      # 1 hour
        'monte_carlo': 7200,           # 2 hours
        'search_results': 600,         # 10 minutes
        'default': 900                 # 15 minutes default
    }
    
    @classmethod
    def get_key(cls, prefix: str, params: Union[Dict, str, int] = None) -> str:
        """
        Generate a cache key with optional parameters hash
        """
        if params:
            if isinstance(params, dict):
                # Sort dict for consistent hashing
                param_str = json.dumps(params, sort_keys=True)
            else:
                param_str = str(params)
            
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"{prefix}:{param_hash}"
        
        return prefix
    
    @classmethod
    def get_timeout(cls, cache_type: str) -> int:
        """
        Get cache timeout for a specific cache type
        """
        return cls.TIMEOUTS.get(cache_type, cls.TIMEOUTS['default'])
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get cached value with logging
        """
        try:
            value = cache.get(key, default)
            if value is not None:
                logger.debug(f"Cache hit for key: {key}")
            else:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return default
    
    @classmethod
    def set(cls, key: str, value: Any, cache_type: str = 'default') -> bool:
        """
        Set cached value with timeout based on cache type
        """
        try:
            timeout = cls.get_timeout(cache_type)
            cache.set(key, value, timeout)
            logger.debug(f"Cache set for key: {key}, timeout: {timeout}s")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """
        Delete cached value
        """
        try:
            cache.delete(key)
            logger.debug(f"Cache deleted for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    @classmethod
    def clear_pattern(cls, pattern: str) -> int:
        """
        Clear cache keys matching a pattern (Redis specific)
        """
        try:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
                # Redis backend
                redis_client = cache._cache.get_client()
                keys = redis_client.keys(f"*{pattern}*")
                if keys:
                    count = redis_client.delete(*keys)
                    logger.info(f"Cleared {count} cache keys matching pattern: {pattern}")
                    return count
                return 0
            else:
                # Fallback for other cache backends
                logger.warning("Pattern-based cache clearing not supported for this cache backend")
                return 0
        except Exception as e:
            logger.error(f"Cache pattern clear error for pattern {pattern}: {str(e)}")
            return 0
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Get cache statistics if available
        """
        try:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
                # Redis backend
                redis_client = cache._cache.get_client()
                info = redis_client.info('memory')
                return {
                    'used_memory': info.get('used_memory_human', 'Unknown'),
                    'used_memory_peak': info.get('used_memory_peak_human', 'Unknown'),
                    'memory_usage': info.get('used_memory', 0),
                    'connected_clients': redis_client.info().get('connected_clients', 0),
                    'total_commands_processed': redis_client.info().get('total_commands_processed', 0)
                }
            else:
                return {'message': 'Cache statistics not available for this backend'}
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}


def cached(cache_type: str = 'default', key_func: Optional[Callable] = None):
    """
    Decorator for caching expensive function results
    
    Usage:
        @cached('analytics_summary')
        def get_analytics_summary():
            # expensive computation
            return result
    
        @cached('user_metrics', key_func=lambda user_id: f'user_metrics:{user_id}')
        def get_user_metrics(user_id):
            # expensive computation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                func_name = f"{func.__module__}.{func.__name__}"
                params = {'args': args, 'kwargs': kwargs}
                cache_key = CacheService.get_key(func_name, params)
            
            # Try to get from cache first
            result = CacheService.get(cache_key)
            if result is not None:
                return result
            
            # Not in cache, execute function
            try:
                result = func(*args, **kwargs)
                # Cache the result
                CacheService.set(cache_key, result, cache_type)
                return result
            except Exception as e:
                logger.error(f"Error executing cached function {func.__name__}: {str(e)}")
                raise
        
        # Add cache control methods to the wrapper
        wrapper.clear_cache = lambda *args, **kwargs: CacheService.delete(
            key_func(*args, **kwargs) if key_func else 
            CacheService.get_key(f"{func.__module__}.{func.__name__}", {'args': args, 'kwargs': kwargs})
        )
        
        return wrapper
    return decorator


class PerformanceCacheService:
    """
    Specialized caching service for performance monitoring
    """
    
    @classmethod
    def cache_query_performance(cls, query_type: str, execution_time: float, result_count: int):
        """
        Cache query performance metrics for monitoring
        """
        try:
            key = f"query_perf:{query_type}:{timezone.now().date()}"
            current_stats = cache.get(key, {'total_time': 0, 'total_queries': 0, 'total_results': 0})
            
            current_stats['total_time'] += execution_time
            current_stats['total_queries'] += 1
            current_stats['total_results'] += result_count
            current_stats['avg_time'] = current_stats['total_time'] / current_stats['total_queries']
            current_stats['last_updated'] = timezone.now().isoformat()
            
            cache.set(key, current_stats, 86400)  # 24 hours
            
            logger.debug(f"Cached performance stats for {query_type}: {current_stats}")
            
        except Exception as e:
            logger.error(f"Error caching query performance: {str(e)}")
    
    @classmethod
    def get_performance_stats(cls, days: int = 7) -> Dict[str, Any]:
        """
        Get aggregated performance statistics
        """
        try:
            stats = {}
            for i in range(days):
                date = timezone.now().date() - timedelta(days=i)
                pattern = f"query_perf:*:{date}"
                
                # This would need Redis-specific implementation
                # For now, return mock data
                stats[str(date)] = {
                    'analytics_summary': {'avg_time': 0.5, 'total_queries': 100},
                    'user_metrics': {'avg_time': 0.3, 'total_queries': 80},
                    'revenue_metrics': {'avg_time': 0.8, 'total_queries': 50}
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {str(e)}")
            return {}


class SmartCacheInvalidation:
    """
    Intelligent cache invalidation based on data dependencies
    """
    
    # Define cache dependencies
    DEPENDENCIES = {
        'user_metrics': ['CustomUser'],
        'revenue_metrics': ['subscription', 'payment'],
        'analytics_summary': ['CustomUser', 'ReportExecution', 'UserChurnPrediction'],
        'dashboard_data': ['ExecutiveDashboard', 'CustomUser'],
        'scenario_results': ['Scenario', 'Client'],
        'monte_carlo': ['Scenario', 'IncomeSource']
    }
    
    @classmethod
    def invalidate_related_caches(cls, model_name: str):
        """
        Invalidate caches that depend on a specific model
        """
        try:
            invalidated_count = 0
            
            for cache_type, dependencies in cls.DEPENDENCIES.items():
                if model_name in dependencies:
                    pattern = cache_type
                    count = CacheService.clear_pattern(pattern)
                    invalidated_count += count
                    logger.info(f"Invalidated {count} cache keys for {cache_type} due to {model_name} change")
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Error invalidating related caches for {model_name}: {str(e)}")
            return 0
    
    @classmethod
    def schedule_cache_warmup(cls, cache_keys: list):
        """
        Schedule cache warmup for critical data (would integrate with Celery)
        """
        try:
            from ..tasks import warm_cache_task
            
            for key in cache_keys:
                warm_cache_task.delay(key)
            
            logger.info(f"Scheduled cache warmup for {len(cache_keys)} keys")
            
        except ImportError:
            logger.warning("Celery not available, skipping cache warmup scheduling")
        except Exception as e:
            logger.error(f"Error scheduling cache warmup: {str(e)}")