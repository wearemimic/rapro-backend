"""
Views for handling Kajabi/NSSA user authentication and setup.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging
import requests
from auth0.management import Auth0

from .authentication import create_jwt_pair_for_user
from .cookie_auth import set_auth_cookies

logger = logging.getLogger(__name__)
User = get_user_model()


def get_auth0_management_token():
    """Get Auth0 Management API access token"""
    domain = settings.AUTH0_DOMAIN
    client_id = settings.AUTH0_MANAGEMENT_CLIENT_ID  # Use Management API credentials
    client_secret = settings.AUTH0_MANAGEMENT_CLIENT_SECRET  # Use Management API credentials

    token_url = f'https://{domain}/oauth/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'audience': f'https://{domain}/api/v2/'
    }

    token_response = requests.post(token_url, json=token_data)
    token_response.raise_for_status()
    return token_response.json()['access_token']


def create_auth0_user(email, password, first_name, last_name):
    """
    Create a user in Auth0 with email/password authentication.
    Returns the Auth0 user_id on success.
    """
    try:
        domain = settings.AUTH0_DOMAIN
        access_token = get_auth0_management_token()
        auth0_client = Auth0(domain, access_token)

        # Create user in Auth0
        user_data = {
            'email': email,
            'password': password,
            'connection': 'Username-Password-Authentication',
            'email_verified': True,  # Skip email verification for NSSA users
            'name': f'{first_name} {last_name}',
            'given_name': first_name,
            'family_name': last_name,
            'user_metadata': {
                'partner': 'NSSA',
                'source': 'kajabi'
            },
            'app_metadata': {
                'subscription_plan': 'nssa_annual',
                'subscription_status': 'active'
            }
        }

        auth0_user = auth0_client.users.create(user_data)
        logger.info(f"✅ Created Auth0 user: {email} (ID: {auth0_user['user_id']})")
        return auth0_user['user_id']

    except Exception as e:
        logger.error(f"❌ Failed to create Auth0 user for {email}: {str(e)}")
        raise


@api_view(['GET'])
@authentication_classes([])  # Disable authentication - public endpoint
@permission_classes([AllowAny])
def validate_token(request):
    """
    Validate a password setup token and return associated email.
    This allows the frontend to display the email without passing it in the URL.

    Note: This endpoint must be publicly accessible (no authentication required).
    """
    token = request.query_params.get('token')

    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Find user with this token in metadata
        users = User.objects.filter(
            auth_provider='kajabi',
            is_active=False,
            metadata__password_setup_token=token
        )

        if not users.exists():
            logger.warning(f"No user found with token: {token[:8]}...")
            return Response(
                {'valid': False, 'error': 'Invalid or expired token'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = users.first()

        # Check if token is expired
        token_expires = user.metadata.get('password_setup_token_expires')
        if token_expires:
            expires_dt = parse_datetime(token_expires)
            if expires_dt and expires_dt < timezone.now():
                logger.warning(f"Expired token for {user.email}")
                return Response(
                    {'valid': False, 'error': 'Token has expired'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Token is valid
        return Response({
            'valid': True,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"❌ Error validating token: {str(e)}", exc_info=True)
        return Response(
            {'valid': False, 'error': 'An error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@authentication_classes([])  # Disable authentication - public endpoint
@permission_classes([AllowAny])
def setup_password(request):
    """
    Set up password for first-time NSSA/Kajabi user access.
    Validates the password setup token and activates the user account.

    Can be called with:
    - token + password (recommended - more secure, no email in URL)
    - email + token + password (legacy support)
    """
    email = request.data.get('email')
    token = request.data.get('token')
    password = request.data.get('password')

    if not token or not password:
        return Response(
            {'error': 'Token and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Find user by token (more secure - no email needed)
        if not email:
            users = User.objects.filter(
                auth_provider='kajabi',
                is_active=False,
                metadata__password_setup_token=token
            )
            if not users.exists():
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user = users.first()
        else:
            # Legacy support: find by email
            user = User.objects.get(email=email, auth_provider='kajabi')

        # Verify token
        if not user.metadata or not user.metadata.get('password_setup_token'):
            logger.warning(f"No password setup token found for {user.email}")
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        stored_token = user.metadata.get('password_setup_token')
        token_expires = user.metadata.get('password_setup_token_expires')

        if stored_token != token:
            logger.warning(f"Token mismatch for {user.email}")
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if token is expired
        if token_expires:
            expires_dt = parse_datetime(token_expires)
            if expires_dt and expires_dt < timezone.now():
                logger.warning(f"Expired token for {user.email}")
                return Response(
                    {'error': 'Token has expired. Please request a new setup link.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Create Auth0 user first
        try:
            auth0_user_id = create_auth0_user(
                email=user.email,
                password=password,
                first_name=user.first_name,
                last_name=user.last_name
            )
            user.auth0_user_id = auth0_user_id
            logger.info(f"✅ Auth0 user created: {auth0_user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create Auth0 user: {str(e)}")
            return Response(
                {'error': 'Failed to create authentication account. Please try again or contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Set the password in Django (for backup/legacy)
        user.set_password(password)
        user.is_active = True  # Activate the account

        # Clear the password setup token
        user.metadata['password_setup_token'] = None
        user.metadata['password_setup_token_expires'] = None
        user.metadata['password_setup_completed_at'] = timezone.now().isoformat()

        user.save()

        logger.info(f"✅ Password setup completed for NSSA user: {user.email}")

        # Create JWT tokens and set cookies
        jwt_tokens = create_jwt_pair_for_user(user)

        response = Response({
            'success': True,
            'message': 'Password set successfully. Welcome to Retirement Advisor Pro!',
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'partner': user.metadata.get('partner', 'NSSA'),
            }
        }, status=status.HTTP_200_OK)

        # Set httpOnly cookies with auth tokens
        response = set_auth_cookies(response, user)

        return response

    except User.DoesNotExist:
        logger.warning(f"User not found for password setup: {email}")
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"❌ Error in password setup: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An error occurred during password setup'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@authentication_classes([])  # Disable authentication - public endpoint
@permission_classes([AllowAny])
def resend_setup_email(request):
    """
    Resend the password setup email to a Kajabi user.
    """
    email = request.data.get('email')

    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email, auth_provider='kajabi', is_active=False)

        # Generate new token
        from .webhooks import generate_password_setup_token, send_nssa_welcome_email
        new_token = generate_password_setup_token(user)

        # Resend welcome email
        send_nssa_welcome_email(user, new_token)

        logger.info(f"📧 Password setup email resent to: {email}")

        return Response({
            'success': True,
            'message': 'Setup email has been resent. Please check your inbox.'
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        # Don't reveal if user exists or not (security)
        return Response({
            'success': True,
            'message': 'If an account exists with that email, a setup link will be sent.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error resending setup email: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
