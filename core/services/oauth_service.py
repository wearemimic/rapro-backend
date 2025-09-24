"""
OAuth2 Service for Email Provider Authentication
Handles Gmail and Outlook OAuth2 flows
"""

import json
import logging
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError

# Google OAuth imports
try:
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    pass

# Microsoft OAuth imports
try:
    import msal
    import requests
except ImportError:
    pass

from ..models import EmailAccount

logger = logging.getLogger(__name__)


class OAuthError(Exception):
    """OAuth-related errors"""
    pass


class EmailOAuthService:
    """
    Service for handling OAuth2 flows for email providers
    """
    
    # OAuth Scopes
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.send',
        'https://mail.google.com/'
    ]
    
    OUTLOOK_SCOPES = [
        'https://graph.microsoft.com/Mail.ReadWrite',
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/User.Read'
    ]
    
    def __init__(self, user, request=None):
        self.user = user
        self.request = request
    
    # =============================================================================
    # GMAIL OAUTH2 FLOW
    # =============================================================================
    
    def get_gmail_auth_url(self, state: Optional[str] = None) -> str:
        """
        Generate Gmail OAuth2 authorization URL
        """
        try:
            # Create flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self._get_gmail_redirect_uri()]
                    }
                },
                scopes=self.GMAIL_SCOPES
            )
            
            flow.redirect_uri = self._get_gmail_redirect_uri()
            
            # Generate authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state or f"user_{self.user.id}",
                prompt='consent'  # Force consent screen to get refresh token
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Failed to generate Gmail auth URL: {str(e)}")
            raise OAuthError(f"Failed to generate Gmail auth URL: {str(e)}")
    
    def handle_gmail_callback(self, authorization_code: str, state: str) -> EmailAccount:
        """
        Handle Gmail OAuth2 callback and create/update EmailAccount
        """
        try:
            # Create flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self._get_gmail_redirect_uri()]
                    }
                },
                scopes=self.GMAIL_SCOPES,
                state=state
            )
            
            flow.redirect_uri = self._get_gmail_redirect_uri()
            
            # Exchange code for tokens
            flow.fetch_token(code=authorization_code)
            
            credentials = flow.credentials
            
            # Get user info to determine email address
            email_address = self._get_gmail_user_email(credentials)
            
            # Create or update EmailAccount
            email_account, created = EmailAccount.objects.get_or_create(
                user=self.user,
                email_address=email_address,
                defaults={
                    'provider': 'gmail',
                    'display_name': email_address,
                }
            )
            
            # Update tokens
            email_account.access_token = credentials.token
            email_account.refresh_token = credentials.refresh_token
            email_account.token_expires_at = credentials.expiry
            email_account.is_active = True
            email_account.sync_enabled = True
            email_account.save()
            
            logger.info(f"Gmail account linked successfully: {email_address}")
            return email_account
            
        except Exception as e:
            logger.error(f"Failed to handle Gmail callback: {str(e)}")
            raise OAuthError(f"Failed to handle Gmail callback: {str(e)}")
    
    def _get_gmail_user_email(self, credentials: Credentials) -> str:
        """Get user's Gmail email address"""
        try:
            from googleapiclient.discovery import build
            
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            return profile['emailAddress']
            
        except Exception as e:
            logger.error(f"Failed to get Gmail user email: {str(e)}")
            raise OAuthError(f"Failed to get Gmail user email: {str(e)}")
    
    def _get_gmail_redirect_uri(self) -> str:
        """Get Gmail OAuth2 redirect URI"""
        if self.request:
            return self.request.build_absolute_uri(reverse('gmail_oauth_callback'))
        return f"{settings.BASE_URL}/api/email/gmail/callback/"
    
    # =============================================================================
    # OUTLOOK OAUTH2 FLOW
    # =============================================================================
    
    def get_outlook_auth_url(self, state: Optional[str] = None) -> str:
        """
        Generate Outlook OAuth2 authorization URL
        """
        try:
            # Create MSAL app
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority="https://login.microsoftonline.com/common"
            )
            
            # Generate authorization URL
            auth_url = app.get_authorization_request_url(
                scopes=self.OUTLOOK_SCOPES,
                redirect_uri=self._get_outlook_redirect_uri(),
                state=state or f"user_{self.user.id}"
            )
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate Outlook auth URL: {str(e)}")
            raise OAuthError(f"Failed to generate Outlook auth URL: {str(e)}")
    
    def handle_outlook_callback(self, authorization_code: str, state: str) -> EmailAccount:
        """
        Handle Outlook OAuth2 callback and create/update EmailAccount
        """
        try:
            # Create MSAL app
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority="https://login.microsoftonline.com/common"
            )
            
            # Exchange code for tokens
            result = app.acquire_token_by_authorization_code(
                code=authorization_code,
                scopes=self.OUTLOOK_SCOPES,
                redirect_uri=self._get_outlook_redirect_uri()
            )
            
            if "error" in result:
                raise OAuthError(f"Outlook OAuth error: {result.get('error_description', result['error'])}")
            
            access_token = result['access_token']
            refresh_token = result.get('refresh_token')
            expires_at = timezone.now() + timedelta(seconds=result.get('expires_in', 3600))
            
            # Get user info to determine email address
            email_address = self._get_outlook_user_email(access_token)
            
            # Create or update EmailAccount
            email_account, created = EmailAccount.objects.get_or_create(
                user=self.user,
                email_address=email_address,
                defaults={
                    'provider': 'outlook',
                    'display_name': email_address,
                }
            )
            
            # Update tokens
            email_account.access_token = access_token
            email_account.refresh_token = refresh_token
            email_account.token_expires_at = expires_at
            email_account.is_active = True
            email_account.sync_enabled = True
            email_account.save()
            
            logger.info(f"Outlook account linked successfully: {email_address}")
            return email_account
            
        except Exception as e:
            logger.error(f"Failed to handle Outlook callback: {str(e)}")
            raise OAuthError(f"Failed to handle Outlook callback: {str(e)}")
    
    def _get_outlook_user_email(self, access_token: str) -> str:
        """Get user's Outlook email address"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers=headers
            )
            response.raise_for_status()
            
            user_data = response.json()
            return user_data['mail'] or user_data['userPrincipalName']
            
        except Exception as e:
            logger.error(f"Failed to get Outlook user email: {str(e)}")
            raise OAuthError(f"Failed to get Outlook user email: {str(e)}")
    
    def _get_outlook_redirect_uri(self) -> str:
        """Get Outlook OAuth2 redirect URI"""
        if self.request:
            return self.request.build_absolute_uri(reverse('outlook_oauth_callback'))
        return f"{settings.BASE_URL}/api/email/outlook/callback/"
    
    # =============================================================================
    # TOKEN REFRESH
    # =============================================================================
    
    def refresh_gmail_token(self, email_account: EmailAccount) -> bool:
        """
        Refresh Gmail access token
        """
        try:
            if not email_account.refresh_token:
                raise OAuthError("No refresh token available")
            
            credentials = Credentials.from_authorized_user_info({
                'refresh_token': email_account.refresh_token,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            })
            
            credentials.refresh(Request())
            
            # Update stored tokens
            email_account.access_token = credentials.token
            if credentials.refresh_token:  # Refresh token might be updated
                email_account.refresh_token = credentials.refresh_token
            email_account.token_expires_at = credentials.expiry
            email_account.save(update_fields=['access_token', 'refresh_token', 'token_expires_at'])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh Gmail token: {str(e)}")
            return False
    
    def refresh_outlook_token(self, email_account: EmailAccount) -> bool:
        """
        Refresh Outlook access token
        """
        try:
            if not email_account.refresh_token:
                raise OAuthError("No refresh token available")
            
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority="https://login.microsoftonline.com/common"
            )
            
            result = app.acquire_token_by_refresh_token(
                refresh_token=email_account.refresh_token,
                scopes=self.OUTLOOK_SCOPES
            )
            
            if "error" in result:
                raise OAuthError(f"Token refresh error: {result.get('error_description', result['error'])}")
            
            # Update stored tokens
            email_account.access_token = result['access_token']
            if 'refresh_token' in result:  # New refresh token might be provided
                email_account.refresh_token = result['refresh_token']
            email_account.token_expires_at = timezone.now() + timedelta(seconds=result.get('expires_in', 3600))
            email_account.save(update_fields=['access_token', 'refresh_token', 'token_expires_at'])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh Outlook token: {str(e)}")
            return False
    
    # =============================================================================
    # ACCOUNT MANAGEMENT
    # =============================================================================
    
    def disconnect_account(self, email_account: EmailAccount) -> bool:
        """
        Disconnect an email account (revoke tokens and deactivate)
        """
        try:
            if email_account.provider == 'gmail':
                self._revoke_gmail_token(email_account)
            elif email_account.provider == 'outlook':
                # Microsoft doesn't provide a simple token revocation endpoint
                pass
            
            # Deactivate account
            email_account.is_active = False
            email_account.sync_enabled = False
            email_account.access_token = ''
            email_account.refresh_token = ''
            email_account.token_expires_at = None
            email_account.save()
            
            logger.info(f"Email account disconnected: {email_account.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect account: {str(e)}")
            return False
    
    def _revoke_gmail_token(self, email_account: EmailAccount):
        """Revoke Gmail access token"""
        try:
            if email_account.access_token:
                revoke_url = f"https://oauth2.googleapis.com/revoke?token={email_account.access_token}"
                response = requests.post(revoke_url)
                response.raise_for_status()
        except Exception as e:
            logger.warning(f"Failed to revoke Gmail token: {str(e)}")
    
    # =============================================================================
    # VALIDATION
    # =============================================================================
    
    def validate_account(self, email_account: EmailAccount) -> Dict[str, any]:
        """
        Validate an email account connection
        Returns validation status and details
        """
        result = {
            'is_valid': False,
            'can_send': False,
            'can_receive': False,
            'token_valid': False,
            'error': None
        }
        
        try:
            from .email_service import EmailService
            
            service = EmailService(email_account)
            
            # Test authentication
            if service.authenticate():
                result['token_valid'] = True
                
                # Test basic functionality
                try:
                    # Try to fetch a small number of emails
                    emails = service.fetch_emails(limit=1)
                    result['can_receive'] = True
                except:
                    pass
                
                # For now, assume send capability if authentication works
                # TODO: Add actual send test with a test email
                result['can_send'] = True
                
                result['is_valid'] = result['can_receive'] or result['can_send']
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Account validation failed for {email_account.email_address}: {str(e)}")
        
        return result


# =============================================================================
# SETTINGS VALIDATION
# =============================================================================

def validate_oauth_settings() -> Dict[str, bool]:
    """
    Validate that required OAuth settings are configured
    """
    result = {
        'gmail_configured': False,
        'outlook_configured': False,
        'errors': []
    }
    
    # Check Gmail settings
    try:
        gmail_client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
        gmail_client_secret = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', None)
        
        if gmail_client_id and gmail_client_secret:
            result['gmail_configured'] = True
        else:
            result['errors'].append("Gmail OAuth2 credentials not configured")
    
    except Exception as e:
        result['errors'].append(f"Gmail configuration error: {str(e)}")
    
    # Check Outlook settings
    try:
        outlook_client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', None)
        outlook_client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', None)
        
        if outlook_client_id and outlook_client_secret:
            result['outlook_configured'] = True
        else:
            result['errors'].append("Outlook OAuth2 credentials not configured")
    
    except Exception as e:
        result['errors'].append(f"Outlook configuration error: {str(e)}")
    
    return result