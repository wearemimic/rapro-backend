"""
Secure Cookie-based JWT Authentication
Replaces localStorage with httpOnly cookies to prevent XSS token theft
"""

from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication using httpOnly cookies instead of Authorization header
    """

    def authenticate(self, request):
        """
        Authenticate request using JWT from httpOnly cookie
        """
        # Try cookie-based authentication first
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            # Fall back to header-based auth for backward compatibility
            return super().authenticate(request)

        # Validate the token
        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)

        return (user, validated_token)


def set_auth_cookies(response, user):
    """
    Set httpOnly cookies for JWT tokens

    Args:
        response: Django HTTP response object
        user: User object to generate tokens for

    Returns:
        Modified response with cookies set
    """
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # Get token lifetimes from settings
    access_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15))
    refresh_lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=1))

    # Set httpOnly cookies
    response.set_cookie(
        key='access_token',
        value=str(access),
        max_age=int(access_lifetime.total_seconds()),
        httponly=True,  # Prevents JavaScript access
        secure=True,    # HTTPS only in production
        samesite='Strict',  # CSRF protection
        path='/'
    )

    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        max_age=int(refresh_lifetime.total_seconds()),
        httponly=True,
        secure=True,
        samesite='Strict',
        path='/api/token/'  # Limit refresh token to token endpoints
    )

    # Also return tokens in response for initial setup
    # (Frontend will NOT store these)
    response.data = {
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
        },
        'message': 'Authentication successful'
    }

    return response


def clear_auth_cookies(response):
    """
    Clear authentication cookies on logout

    Args:
        response: Django HTTP response object

    Returns:
        Modified response with cookies cleared
    """
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/api/token/')
    response.delete_cookie('csrftoken', path='/')

    return response


def refresh_access_token(request):
    """
    Refresh access token using refresh token from cookie

    Args:
        request: Django HTTP request object

    Returns:
        New access token or error
    """
    refresh_token = request.COOKIES.get('refresh_token')

    if not refresh_token:
        raise exceptions.AuthenticationFailed('No refresh token provided')

    try:
        # Validate refresh token
        refresh = RefreshToken(refresh_token)

        # Generate new access token
        access = refresh.access_token

        # Create response
        response = JsonResponse({
            'message': 'Token refreshed successfully'
        })

        # Set new access token cookie
        access_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15))
        response.set_cookie(
            key='access_token',
            value=str(access),
            max_age=int(access_lifetime.total_seconds()),
            httponly=True,
            secure=True,
            samesite='Strict',
            path='/'
        )

        # Rotate refresh token if configured
        if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
            refresh.blacklist()
            new_refresh = RefreshToken.for_user(refresh.user)

            refresh_lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=1))
            response.set_cookie(
                key='refresh_token',
                value=str(new_refresh),
                max_age=int(refresh_lifetime.total_seconds()),
                httponly=True,
                secure=True,
                samesite='Strict',
                path='/api/token/'
            )

        return response

    except TokenError as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise exceptions.AuthenticationFailed('Invalid refresh token')


class CookieTokenMiddleware:
    """
    Middleware to handle cookie-based JWT authentication
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if access token cookie exists and add to header
        access_token = request.COOKIES.get('access_token')

        if access_token and 'Authorization' not in request.headers:
            # Add token to Authorization header for DRF compatibility
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

        response = self.get_response(request)
        return response


def validate_csrf_token(request):
    """
    Validate CSRF token for state-changing requests

    Args:
        request: Django HTTP request object

    Returns:
        True if valid, raises exception otherwise
    """
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        csrf_token = request.headers.get('X-CSRFToken') or request.POST.get('csrfmiddlewaretoken')
        cookie_token = request.COOKIES.get('csrftoken')

        if not csrf_token or not cookie_token:
            raise exceptions.PermissionDenied('CSRF token missing')

        if csrf_token != cookie_token:
            raise exceptions.PermissionDenied('CSRF token invalid')

    return True