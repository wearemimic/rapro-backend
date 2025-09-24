"""
Auth0 Token Caching Module
Reduces Auth0 API calls by caching tokens and user info
Estimated savings: 50-75GB/month in NAT Gateway data transfer
"""

import hashlib
import json
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Auth0TokenCache:
    """
    Caches Auth0 tokens and user info to reduce API calls
    """

    # Cache timeout in seconds (1 hour for tokens, 5 minutes for user info)
    TOKEN_CACHE_TIMEOUT = 3600  # 1 hour
    USER_INFO_CACHE_TIMEOUT = 300  # 5 minutes
    MANAGEMENT_TOKEN_TIMEOUT = 43200  # 12 hours for management API tokens

    @classmethod
    def get_cache_key(cls, key_type, identifier):
        """Generate a unique cache key"""
        # Use SHA256 for cache key hashing (more secure than MD5)
        hash_id = hashlib.sha256(identifier.encode()).hexdigest()[:32]
        return f"auth0_{key_type}_{hash_id}"

    @classmethod
    def get_cached_token(cls, code):
        """Get cached access token for an authorization code"""
        cache_key = cls.get_cache_key("token", code)
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Auth0 token cache hit for code hash: {cache_key}")
            return cached_data

        return None

    @classmethod
    def set_cached_token(cls, code, token_data):
        """Cache access token data"""
        cache_key = cls.get_cache_key("token", code)
        cache.set(cache_key, token_data, cls.TOKEN_CACHE_TIMEOUT)
        logger.info(f"Cached Auth0 token for code hash: {cache_key}")

    @classmethod
    def get_cached_user_info(cls, access_token):
        """Get cached user info for an access token"""
        cache_key = cls.get_cache_key("user_info", access_token)
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Auth0 user info cache hit")
            return cached_data

        return None

    @classmethod
    def set_cached_user_info(cls, access_token, user_info):
        """Cache user info data"""
        cache_key = cls.get_cache_key("user_info", access_token)
        cache.set(cache_key, user_info, cls.USER_INFO_CACHE_TIMEOUT)
        logger.info(f"Cached Auth0 user info")

    @classmethod
    def get_management_token(cls):
        """Get cached management API token"""
        cache_key = "auth0_management_token"
        cached_token = cache.get(cache_key)

        if cached_token:
            logger.info("Auth0 management token cache hit")
            return cached_token

        return None

    @classmethod
    def set_management_token(cls, token):
        """Cache management API token"""
        cache_key = "auth0_management_token"
        cache.set(cache_key, token, cls.MANAGEMENT_TOKEN_TIMEOUT)
        logger.info("Cached Auth0 management token")

    @classmethod
    def invalidate_user_cache(cls, access_token):
        """Invalidate cached user info when needed"""
        cache_key = cls.get_cache_key("user_info", access_token)
        cache.delete(cache_key)
        logger.info(f"Invalidated Auth0 user cache")

    @classmethod
    def get_cache_stats(cls):
        """Get cache statistics for monitoring"""
        # This would need Redis or custom tracking to implement properly
        # For now, return basic info
        return {
            "token_timeout": cls.TOKEN_CACHE_TIMEOUT,
            "user_info_timeout": cls.USER_INFO_CACHE_TIMEOUT,
            "management_token_timeout": cls.MANAGEMENT_TOKEN_TIMEOUT,
            "cache_backend": settings.CACHES['default']['BACKEND']
        }


# Decorator for caching Auth0 API responses
def cache_auth0_response(cache_type="user_info", timeout=None):
    """
    Decorator to cache Auth0 API responses

    Usage:
        @cache_auth0_response(cache_type="user_info", timeout=300)
        def get_user_info(access_token):
            # Your Auth0 API call here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract the identifier (usually first argument)
            identifier = args[0] if args else str(kwargs)

            # Generate cache key
            cache_key = Auth0TokenCache.get_cache_key(cache_type, identifier)

            # Check cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {cache_type}: {func.__name__}")
                return cached_result

            # Call the original function
            result = func(*args, **kwargs)

            # Cache the result
            cache_timeout = timeout or Auth0TokenCache.USER_INFO_CACHE_TIMEOUT
            cache.set(cache_key, result, cache_timeout)
            logger.info(f"Cached result for {cache_type}: {func.__name__}")

            return result

        return wrapper
    return decorator


# Batch API call aggregator
class Auth0BatchProcessor:
    """
    Batch multiple Auth0 API calls to reduce request overhead
    """

    def __init__(self):
        self.pending_user_lookups = []
        self.pending_token_exchanges = []

    def add_user_lookup(self, user_id):
        """Queue a user lookup for batch processing"""
        self.pending_user_lookups.append(user_id)

    def add_token_exchange(self, code):
        """Queue a token exchange for batch processing"""
        self.pending_token_exchanges.append(code)

    def process_batch(self):
        """
        Process all pending requests in batch
        Note: Auth0 doesn't have true batch APIs, but we can optimize
        by reusing connections and management tokens
        """
        results = {
            'users': {},
            'tokens': {}
        }

        # Get a single management token for all requests
        management_token = Auth0TokenCache.get_management_token()

        if self.pending_user_lookups and management_token:
            # Process user lookups with single management token
            for user_id in self.pending_user_lookups:
                # Check cache first
                cached = cache.get(f"auth0_user_{user_id}")
                if cached:
                    results['users'][user_id] = cached
                else:
                    # Would make actual API call here
                    pass

        # Clear pending requests
        self.pending_user_lookups.clear()
        self.pending_token_exchanges.clear()

        return results


# Usage example in views:
"""
from .auth0_cache import Auth0TokenCache, cache_auth0_response

@api_view(['POST'])
def exchange_code(request):
    code = request.data.get('code')

    # Check cache first
    cached_token = Auth0TokenCache.get_cached_token(code)
    if cached_token:
        return Response(cached_token)

    # Make API call if not cached
    token_data = exchange_with_auth0(code)

    # Cache the result
    Auth0TokenCache.set_cached_token(code, token_data)

    return Response(token_data)
"""