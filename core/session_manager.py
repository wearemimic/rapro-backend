"""
Session Management Module
Handles concurrent session limits and session tracking
"""

import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

logger = logging.getLogger(__name__)
User = get_user_model()


class SessionManager:
    """
    Manages user sessions and enforces concurrent session limits
    """

    # Maximum concurrent sessions per user (configurable)
    MAX_CONCURRENT_SESSIONS = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 3)
    SESSION_CACHE_TIMEOUT = 86400  # 24 hours

    @classmethod
    def get_user_sessions_key(cls, user_id):
        """Generate cache key for user sessions"""
        return f"user_sessions_{user_id}"

    @classmethod
    def register_session(cls, user, token_key, request=None):
        """
        Register a new session for the user
        Returns True if session registered, False if limit exceeded
        """
        cache_key = cls.get_user_sessions_key(user.id)
        sessions = cache.get(cache_key, [])

        # Create session info
        session_info = {
            'token_key': token_key,
            'created_at': datetime.now().isoformat(),
            'ip_address': request.META.get('REMOTE_ADDR', 'unknown') if request else 'unknown',
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown') if request else 'unknown',
        }

        # Check if we need to invalidate old sessions
        if len(sessions) >= cls.MAX_CONCURRENT_SESSIONS:
            # Remove the oldest session
            oldest_session = sessions[0]
            cls.invalidate_session(user, oldest_session['token_key'])
            sessions = sessions[1:]

            logger.info(f"Removed oldest session for user {user.email} due to concurrent session limit")

        # Add new session
        sessions.append(session_info)
        cache.set(cache_key, sessions, cls.SESSION_CACHE_TIMEOUT)

        logger.info(f"Registered new session for user {user.email}. Total sessions: {len(sessions)}")
        return True

    @classmethod
    def invalidate_session(cls, user, token_key):
        """
        Invalidate a specific session
        """
        try:
            # Blacklist the token
            token = OutstandingToken.objects.get(token=token_key, user=user)
            BlacklistedToken.objects.get_or_create(token=token)

            # Remove from cache
            cache_key = cls.get_user_sessions_key(user.id)
            sessions = cache.get(cache_key, [])
            sessions = [s for s in sessions if s.get('token_key') != token_key]
            cache.set(cache_key, sessions, cls.SESSION_CACHE_TIMEOUT)

            logger.info(f"Invalidated session for user {user.email}")
            return True
        except OutstandingToken.DoesNotExist:
            logger.warning(f"Token not found for invalidation: {token_key[:10]}...")
            return False
        except Exception as e:
            logger.error(f"Error invalidating session: {str(e)}")
            return False

    @classmethod
    def invalidate_all_sessions(cls, user):
        """
        Invalidate all sessions for a user (useful for password reset, security events)
        """
        try:
            # Blacklist all outstanding tokens for the user
            outstanding_tokens = OutstandingToken.objects.filter(user=user)
            for token in outstanding_tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            # Clear cache
            cache_key = cls.get_user_sessions_key(user.id)
            cache.delete(cache_key)

            logger.info(f"Invalidated all sessions for user {user.email}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating all sessions: {str(e)}")
            return False

    @classmethod
    def get_active_sessions(cls, user):
        """
        Get list of active sessions for a user
        """
        cache_key = cls.get_user_sessions_key(user.id)
        sessions = cache.get(cache_key, [])

        # Filter out expired sessions
        active_sessions = []
        for session in sessions:
            try:
                # Check if token is still valid (not blacklisted)
                token = OutstandingToken.objects.get(
                    token=session['token_key'],
                    user=user
                )
                if not hasattr(token, 'blacklistedtoken'):
                    active_sessions.append(session)
            except OutstandingToken.DoesNotExist:
                continue

        # Update cache if sessions were filtered
        if len(active_sessions) != len(sessions):
            cache.set(cache_key, active_sessions, cls.SESSION_CACHE_TIMEOUT)

        return active_sessions

    @classmethod
    def check_session_limit(cls, user):
        """
        Check if user has reached session limit
        Returns (allowed, current_count, max_limit)
        """
        sessions = cls.get_active_sessions(user)
        current_count = len(sessions)
        max_limit = cls.MAX_CONCURRENT_SESSIONS
        allowed = current_count < max_limit

        return allowed, current_count, max_limit

    @classmethod
    def enforce_session_limit(cls, user, new_token_key, request=None):
        """
        Enforce session limit when creating a new session
        Called during login to manage concurrent sessions
        """
        # Register the new session (will auto-remove oldest if needed)
        cls.register_session(user, new_token_key, request)

        # Log session status
        sessions = cls.get_active_sessions(user)
        logger.info(f"User {user.email} has {len(sessions)} active sessions")

        return True