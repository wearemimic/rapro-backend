"""
Health check endpoints for ECS/ALB monitoring
Optimized for fast response times and minimal resource usage
"""

from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.db import connection
from django.core.cache import cache
import time


@require_GET
@never_cache
def health_check(request):
    """
    Lightweight health check endpoint for ECS/ALB
    Returns quickly without any database writes or heavy operations

    This endpoint is called every 30 seconds by:
    - ECS container health checks
    - ALB target group health checks

    Requirements:
    - Must return in < 500ms
    - Must not write to database
    - Must not perform expensive operations
    """

    # Simple OK response for basic health check
    # This is all that's needed for ALB/ECS to know the service is alive
    return JsonResponse({
        'status': 'healthy',
        'service': 'backend',
        'timestamp': int(time.time())
    }, status=200)


@require_GET
@never_cache
def health_check_detailed(request):
    """
    Detailed health check endpoint for debugging and monitoring
    This endpoint performs actual checks but is NOT used for ALB/ECS

    Use this endpoint for:
    - Manual health verification
    - Monitoring dashboards
    - Debugging issues
    """

    health_status = {
        'status': 'healthy',
        'service': 'backend',
        'timestamp': int(time.time()),
        'checks': {
            'database': 'unknown',
            'cache': 'unknown'
        }
    }

    # Check database connectivity (read-only)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = 'unhealthy'
        health_status['status'] = 'degraded'

    # Check cache connectivity (read-only)
    try:
        cache_key = '_health_check_test'
        cache.get(cache_key)  # Just try to read, don't write
        health_status['checks']['cache'] = 'healthy'
    except Exception as e:
        health_status['checks']['cache'] = 'unhealthy'
        # Cache being down is not critical

    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503

    return JsonResponse(health_status, status=status_code)


@require_GET
@never_cache
def readiness_check(request):
    """
    Readiness check for Kubernetes/ECS
    Indicates if the service is ready to receive traffic

    Different from health check:
    - Health check: Is the container running?
    - Readiness check: Is the service ready to handle requests?
    """

    ready = True
    checks = {}

    # Quick database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = 'ready'
    except:
        checks['database'] = 'not_ready'
        ready = False

    return JsonResponse({
        'ready': ready,
        'checks': checks,
        'timestamp': int(time.time())
    }, status=200 if ready else 503)


@require_GET
@never_cache
def liveness_check(request):
    """
    Liveness check for Kubernetes/ECS
    Indicates if the container should be restarted

    This should only fail if the service is in an unrecoverable state
    """

    # For now, if we can respond, we're alive
    # In the future, could check for deadlocks, memory issues, etc.

    return JsonResponse({
        'alive': True,
        'timestamp': int(time.time())
    }, status=200)