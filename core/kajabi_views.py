"""
Views for handling Kajabi/NSSA user authentication and setup.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

from .cookie_auth import create_jwt_pair_for_user, set_auth_cookies

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def setup_password(request):
    """
    Set up password for first-time NSSA/Kajabi user access.
    Validates the password setup token and activates the user account.
    """
    email = request.data.get('email')
    token = request.data.get('token')
    password = request.data.get('password')

    if not all([email, token, password]):
        return Response(
            {'error': 'Email, token, and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters long'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Find user by email
        user = User.objects.get(email=email, auth_provider='kajabi')

        # Verify token
        if not user.metadata or not user.metadata.get('password_setup_token'):
            logger.warning(f"No password setup token found for {email}")
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        stored_token = user.metadata.get('password_setup_token')
        token_expires = user.metadata.get('password_setup_token_expires')

        if stored_token != token:
            logger.warning(f"Token mismatch for {email}")
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if token is expired
        if token_expires:
            expires_dt = parse_datetime(token_expires)
            if expires_dt and expires_dt < timezone.now():
                logger.warning(f"Expired token for {email}")
                return Response(
                    {'error': 'Token has expired. Please request a new setup link.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Set the password
        user.set_password(password)
        user.is_active = True  # Activate the account

        # Clear the password setup token
        user.metadata['password_setup_token'] = None
        user.metadata['password_setup_token_expires'] = None
        user.metadata['password_setup_completed_at'] = timezone.now().isoformat()

        user.save()

        logger.info(f"✅ Password setup completed for NSSA user: {email}")

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
