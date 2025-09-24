"""
Cookie-based Authentication Views
Secure authentication using httpOnly cookies
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .cookie_auth import set_auth_cookies, clear_auth_cookies, refresh_access_token
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def cookie_login(request):
    """
    Login endpoint that sets httpOnly cookies instead of returning tokens
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate user
    user = authenticate(request, username=email, password=password)

    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Create response with cookies
    response = Response(status=status.HTTP_200_OK)
    response = set_auth_cookies(response, user)

    # Set CSRF token
    response.set_cookie(
        key='csrftoken',
        value=get_token(request),
        max_age=60 * 60 * 24 * 7,  # 1 week
        httponly=False,  # Must be accessible to JavaScript for CSRF
        secure=True,
        samesite='Strict'
    )

    logger.info(f"User {user.email} logged in via cookie auth")

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def cookie_auth0_exchange(request):
    """
    Exchange Auth0 authorization code for cookies (instead of localStorage tokens)
    """
    import requests
    from django.conf import settings

    code = request.data.get('code')
    flow_type = request.data.get('flow_type', 'login')
    affiliate_code = request.data.get('affiliate_code')

    if not code:
        return Response(
            {'error': 'Authorization code required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Use the same logic as auth0_views but return cookies
        redirect_uri = f'{settings.FRONTEND_URL}/auth/callback'

        # Exchange code for tokens with Auth0
        domain = settings.AUTH0_DOMAIN
        client_id = settings.AUTH0_CLIENT_ID
        client_secret = settings.AUTH0_CLIENT_SECRET

        token_url = f'https://{domain}/oauth/token'
        token_payload = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }

        token_response = requests.post(token_url, json=token_payload)

        if token_response.status_code != 200:
            logger.error(f"Auth0 token exchange failed: {token_response.text}")
            return Response(
                {'error': 'Failed to exchange authorization code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tokens = token_response.json()
        access_token = tokens.get('access_token')

        # Get user info from Auth0
        user_info_url = f'https://{domain}/userinfo'
        user_info_response = requests.get(
            user_info_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if user_info_response.status_code != 200:
            logger.error(f"Failed to get user info from Auth0: {user_info_response.text}")
            return Response(
                {'error': 'Failed to get user information'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_info = user_info_response.json()
        email = user_info.get('email')

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'is_active': True
            }
        )

        # Create response with cookies
        response = Response(status=status.HTTP_200_OK)
        response = set_auth_cookies(response, user)

        # Set CSRF token
        response.set_cookie(
            key='csrftoken',
            value=get_token(request),
            max_age=60 * 60 * 24 * 7,
            httponly=False,
            secure=True,
            samesite='Strict'
        )

        logger.info(f"User {user.email} authenticated via Auth0 with cookie auth")

        return response

    except Exception as e:
        logger.error(f"Auth0 cookie exchange error: {str(e)}")
        return Response(
            {'error': 'Authentication failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cookie_logout(request):
    """
    Logout endpoint that clears httpOnly cookies and blacklists tokens
    """
    try:
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                logger.warning(f"Failed to blacklist token on logout: {str(e)}")

        # Clear cookies
        response = Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )
        response = clear_auth_cookies(response)

        logger.info(f"User {request.user.email} logged out")

        return response

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Still clear cookies even if blacklisting fails
        response = Response(
            {'message': 'Logged out'},
            status=status.HTTP_200_OK
        )
        response = clear_auth_cookies(response)
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def cookie_refresh(request):
    """
    Refresh access token using refresh token from cookie
    """
    try:
        response = refresh_access_token(request)
        return response
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response(
            {'error': 'Failed to refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_auth(request):
    """
    Verify if user is authenticated (cookie-based)
    """
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_staff': request.user.is_staff,
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Get CSRF token for forms
    """
    return JsonResponse({
        'csrfToken': get_token(request)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def migrate_to_cookie_auth(request):
    """
    One-time migration endpoint to convert localStorage tokens to cookies
    This helps transition existing users
    """
    access_token = request.data.get('access_token')
    refresh_token = request.data.get('refresh_token')

    if not access_token or not refresh_token:
        return Response(
            {'error': 'Both tokens required for migration'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Validate tokens
        from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

        access = AccessToken(access_token)
        refresh = RefreshToken(refresh_token)

        # Get user from token
        user_id = access.payload.get('user_id')
        user = User.objects.get(id=user_id)

        # Create response with cookies
        response = Response({
            'message': 'Successfully migrated to cookie authentication',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)

        # Set cookies
        from datetime import timedelta
        from django.conf import settings

        access_lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15))
        refresh_lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=1))

        response.set_cookie(
            key='access_token',
            value=access_token,
            max_age=int(access_lifetime.total_seconds()),
            httponly=True,
            secure=True,
            samesite='Strict',
            path='/'
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=int(refresh_lifetime.total_seconds()),
            httponly=True,
            secure=True,
            samesite='Strict',
            path='/api/token/'
        )

        # Set CSRF token
        response.set_cookie(
            key='csrftoken',
            value=get_token(request),
            max_age=60 * 60 * 24 * 7,
            httponly=False,
            secure=True,
            samesite='Strict'
        )

        logger.info(f"User {user.email} migrated to cookie auth")

        return response

    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        return Response(
            {'error': 'Failed to migrate authentication'},
            status=status.HTTP_400_BAD_REQUEST
        )