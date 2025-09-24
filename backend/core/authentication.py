"""
Client Portal Authentication System

This module provides authentication functionality specifically for client portal access,
separate from advisor authentication. It includes token-based authentication,
invitation system, and client session management.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from django.utils import timezone
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import exceptions
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Client


class ClientPortalBackend(BaseBackend):
    """
    Custom authentication backend for client portal access.
    Authenticates clients using their email and a temporary token system.
    """
    
    def authenticate(self, request, email=None, token=None, **kwargs):
        """
        Authenticate client using email and invitation token
        """
        if not email or not token:
            return None
            
        try:
            client = Client.objects.get(
                email=email,
                portal_access_enabled=True,
                portal_invitation_token=token
            )
            
            # Check if token is still valid (24 hours)
            if client.portal_invitation_sent_at:
                token_age = timezone.now() - client.portal_invitation_sent_at
                if token_age > timedelta(hours=24):
                    return None
            
            # Create or get portal user
            if not client.portal_user:
                portal_user = User.objects.create_user(
                    username=f"client_{client.id}",
                    email=client.email,
                    first_name=client.first_name,
                    last_name=client.last_name,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False
                )
                client.portal_user = portal_user
                client.save()
            
            # Update last login
            client.portal_last_login = timezone.now()
            client.save()
            
            return client.portal_user
            
        except Client.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class ClientPortalTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication for client portal API access.
    Extends DRF TokenAuthentication to work with client portal users.
    """
    
    def authenticate_credentials(self, key):
        """
        Override to check if user is a client portal user
        """
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        
        # Check if this is a client portal user
        try:
            client = Client.objects.get(portal_user=token.user)
            if not client.portal_access_enabled:
                raise exceptions.AuthenticationFailed('Client portal access disabled.')
        except Client.DoesNotExist:
            # Not a client portal user, allow regular authentication
            pass

        return (token.user, token)


class ClientInvitationManager:
    """
    Manages client portal invitations and onboarding flow
    """
    
    @staticmethod
    def generate_invitation_token():
        """Generate a secure invitation token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def send_portal_invitation(cls, client):
        """
        Send portal access invitation to client
        """
        if not client.portal_access_enabled:
            raise ValueError("Portal access must be enabled before sending invitation")
        
        # Generate new invitation token
        client.portal_invitation_token = cls.generate_invitation_token()
        client.portal_invitation_sent_at = timezone.now()
        client.save()
        
        # Prepare invitation email
        invitation_url = f"{settings.FRONTEND_URL}/portal/login?email={client.email}&token={client.portal_invitation_token}"
        
        context = {
            'client': client,
            'advisor_name': f"{client.advisor.first_name} {client.advisor.last_name}",
            'invitation_url': invitation_url,
            'expires_at': client.portal_invitation_sent_at + timedelta(hours=24)
        }
        
        # Send invitation email
        subject = f"Welcome to Your Financial Advisor Portal - {client.advisor.first_name} {client.advisor.last_name}"
        
        html_message = render_to_string('emails/client_portal_invitation.html', context)
        text_message = render_to_string('emails/client_portal_invitation.txt', context)
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return invitation_url
    
    @classmethod
    def activate_client_portal_access(cls, client, password=None):
        """
        Activate client portal access and create user account
        """
        if not client.portal_access_enabled:
            raise ValueError("Portal access is not enabled for this client")
        
        if client.portal_user:
            # User already exists, just activate if needed
            client.portal_user.is_active = True
            client.portal_user.save()
        else:
            # Create new portal user
            username = f"client_{client.id}_{client.email.split('@')[0]}"
            
            portal_user = User.objects.create_user(
                username=username,
                email=client.email,
                first_name=client.first_name,
                last_name=client.last_name,
                password=password or User.objects.make_random_password(),
                is_active=True,
                is_staff=False,
                is_superuser=False
            )
            
            client.portal_user = portal_user
            client.save()
            
            # Create API token for client
            Token.objects.get_or_create(user=portal_user)
        
        return client.portal_user
    
    @classmethod
    def revoke_portal_access(cls, client):
        """
        Revoke client portal access
        """
        client.portal_access_enabled = False
        client.portal_invitation_token = None
        client.portal_invitation_sent_at = None
        
        # Deactivate portal user if exists
        if client.portal_user:
            client.portal_user.is_active = False
            client.portal_user.save()
            
            # Revoke API tokens
            Token.objects.filter(user=client.portal_user).delete()
        
        client.save()


class ClientSessionManager:
    """
    Manages client portal sessions and security
    """
    
    @staticmethod
    def create_client_session(client, request=None):
        """
        Create a new client portal session
        """
        if not client.portal_user:
            raise ValueError("Client must have portal user account")
        
        # Create or get existing token
        token, created = Token.objects.get_or_create(user=client.portal_user)
        
        # Update last login
        client.portal_last_login = timezone.now()
        client.save()
        
        return {
            'token': token.key,
            'user': {
                'id': client.portal_user.id,
                'email': client.email,
                'first_name': client.first_name,
                'last_name': client.last_name
            },
            'client_id': client.id,
            'expires_at': timezone.now() + timedelta(days=30)  # 30-day session
        }
    
    @staticmethod
    def validate_client_session(token):
        """
        Validate client portal session token
        """
        try:
            token_obj = Token.objects.select_related('user').get(key=token)
            client = Client.objects.get(
                portal_user=token_obj.user,
                portal_access_enabled=True
            )
            
            return {
                'valid': True,
                'client': client,
                'user': token_obj.user
            }
        except (Token.DoesNotExist, Client.DoesNotExist):
            return {
                'valid': False,
                'client': None,
                'user': None
            }
    
    @classmethod
    def terminate_client_session(cls, client):
        """
        Terminate client portal session
        """
        if client.portal_user:
            Token.objects.filter(user=client.portal_user).delete()


class ClientPortalSecurity:
    """
    Security utilities for client portal
    """
    
    @staticmethod
    def log_client_activity(client, activity, request=None):
        """
        Log client portal activity for security auditing
        """
        # Implementation would log to a security audit table
        pass
    
    @staticmethod
    def check_client_access_permissions(client, resource):
        """
        Check if client has permission to access specific resource
        """
        if not client.portal_access_enabled:
            return False
        
        # Additional permission checks based on resource type
        return True
    
    @staticmethod
    def validate_client_ip(client, request):
        """
        Validate client IP address for additional security
        """
        # Implementation for IP-based access controls
        return True


# Admin Authentication System
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer - admin claims removed for security"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Only include non-sensitive user claims
        # Admin claims should be fetched server-side, not stored in JWT
        token['user_id'] = user.id
        token['email'] = user.email
        token['company_name'] = user.company_name or ''
        token['subscription_status'] = user.subscription_status or ''

        # Add a flag to indicate if user has admin privileges
        # But don't include the actual permissions in the token
        token['has_admin_access'] = user.is_admin_user

        return token


class CustomRefreshToken(RefreshToken):
    """Custom refresh token - admin claims removed for security"""

    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization grant token for the given user that will be
        provided after authenticating the user's credentials.
        """
        token = cls()
        token[cls.token_type] = cls.token_type
        token['user_id'] = user.pk

        # Only include non-sensitive claims
        token['email'] = user.email
        token['company_name'] = user.company_name or ''
        token['subscription_status'] = user.subscription_status or ''

        # Simple flag for admin access, not the actual permissions
        token['has_admin_access'] = user.is_admin_user

        return token


def create_jwt_pair_for_user(user):
    """
    Helper function to create JWT token pair with admin claims
    """
    refresh = CustomRefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads admin claims from token
    and applies them to the user object during authentication
    """
    
    def authenticate(self, request):
        """Override to add debugging"""
        print(f"🔐 CustomJWTAuthentication.authenticate called")
        result = super().authenticate(request)
        print(f"🔐 Authentication result: {result}")
        return result
    
    def get_user(self, validated_token):
        """
        Override to fetch fresh admin claims from database (not from token for security)
        """
        print(f"🎫 CustomJWTAuthentication.get_user called")
        user = super().get_user(validated_token)
        print(f"👤 Retrieved user: {user.id} ({user.email})")

        # Check if user has admin access flag in token
        has_admin_access = validated_token.get('has_admin_access', False)

        if has_admin_access:
            # Fetch fresh admin claims from database (not from token)
            # This prevents token manipulation attacks
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                fresh_user = User.objects.get(pk=user.pk)

                # Use actual database values for admin permissions
                user.is_platform_admin = fresh_user.is_platform_admin
                user.admin_role = fresh_user.admin_role
                user.admin_permissions = fresh_user.admin_permissions

                print(f"✅ Admin claims fetched from database for user {user.email}")
            except Exception as e:
                print(f"⚠️ Error fetching admin claims: {str(e)}")
                # Default to no admin access if fetch fails
                user.is_platform_admin = False
                user.admin_role = None
                user.admin_permissions = {}

        return user


def get_enhanced_user_data(user):
    """
    Get comprehensive user data including admin information for API responses
    """
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'company_name': user.company_name,
        'website_url': user.website_url,
        'address': user.address,
        'city': user.city,
        'state': user.state,
        'zip_code': user.zip_code,
        'white_label_company_name': user.white_label_company_name,
        'white_label_support_email': user.white_label_support_email,
        'primary_color': user.primary_color,
        'logo': user.logo.url if user.logo else None,
        'custom_disclosure': user.custom_disclosure,
        'subscription_status': user.subscription_status,
        'subscription_plan': user.subscription_plan,
        'is_subscription_active': user.is_subscription_active,
        'auth_provider': user.auth_provider,
        # Admin fields
        'is_admin_user': user.is_admin_user,
        'admin_role': user.admin_role,
        'admin_role_display': user.get_admin_role_display_name(),
        'admin_permissions': user.admin_permissions,
    }