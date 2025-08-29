"""
Calendar Service for Google Calendar and Microsoft Outlook Calendar Integration
Handles OAuth2 flows, event synchronization, and meeting creation
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError

# Google Calendar imports
try:
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    pass

# Microsoft Graph imports
try:
    import msal
    import requests
except ImportError:
    pass

from ..models import CalendarAccount, CalendarEvent, MeetingTemplate, CalendarEventReminder

logger = logging.getLogger(__name__)


class CalendarError(Exception):
    """Calendar-related errors"""
    pass


class CalendarService:
    """
    Service for handling calendar operations across Google Calendar and Outlook Calendar
    """
    
    # OAuth Scopes
    GOOGLE_CALENDAR_SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    OUTLOOK_CALENDAR_SCOPES = [
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/User.Read'
    ]
    
    def __init__(self, user, request=None):
        self.user = user
        self.request = request
    
    # =============================================================================
    # GOOGLE CALENDAR OAUTH2 FLOW
    # =============================================================================
    
    def get_google_calendar_auth_url(self, state: Optional[str] = None) -> str:
        """Generate Google Calendar OAuth2 authorization URL"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self._get_google_calendar_redirect_uri()]
                    }
                },
                scopes=self.GOOGLE_CALENDAR_SCOPES
            )
            
            flow.redirect_uri = self._get_google_calendar_redirect_uri()
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state or f"user_{self.user.id}",
                prompt='consent'
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Failed to generate Google Calendar auth URL: {str(e)}")
            raise CalendarError(f"Failed to generate Google Calendar auth URL: {str(e)}")
    
    def handle_google_calendar_callback(self, authorization_code: str, state: str) -> CalendarAccount:
        """Handle Google Calendar OAuth2 callback and create/update CalendarAccount"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self._get_google_calendar_redirect_uri()]
                    }
                },
                scopes=self.GOOGLE_CALENDAR_SCOPES,
                state=state
            )
            
            flow.redirect_uri = self._get_google_calendar_redirect_uri()
            flow.fetch_token(code=authorization_code)
            
            credentials = flow.credentials
            
            # Get user info and calendar list
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get primary calendar info
            calendar_list = service.calendarList().list().execute()
            primary_calendar = None
            for calendar_item in calendar_list.get('items', []):
                if calendar_item.get('primary', False):
                    primary_calendar = calendar_item
                    break
            
            if not primary_calendar:
                raise CalendarError("No primary calendar found")
            
            # Create or update CalendarAccount
            calendar_account, created = CalendarAccount.objects.get_or_create(
                user=self.user,
                provider='google',
                external_account_id=primary_calendar['id'],
                defaults={
                    'display_name': primary_calendar.get('summary', 'Primary Calendar'),
                    'email_address': primary_calendar.get('id', ''),
                    'calendar_list': calendar_list.get('items', []),
                    'timezone': primary_calendar.get('timeZone', 'America/New_York'),
                }
            )
            
            # Update tokens
            calendar_account.access_token = credentials.token
            calendar_account.refresh_token = credentials.refresh_token
            calendar_account.token_expires_at = credentials.expiry
            calendar_account.is_active = True
            calendar_account.sync_enabled = True
            calendar_account.save()
            
            logger.info(f"Google Calendar account linked successfully: {calendar_account.display_name}")
            return calendar_account
            
        except Exception as e:
            logger.error(f"Failed to handle Google Calendar callback: {str(e)}")
            raise CalendarError(f"Failed to handle Google Calendar callback: {str(e)}")
    
    def _get_google_calendar_redirect_uri(self) -> str:
        """Get Google Calendar OAuth2 redirect URI"""
        if self.request:
            return self.request.build_absolute_uri(reverse('google_calendar_oauth_callback'))
        return f"{settings.BASE_URL}/api/calendar/google/callback/"
    
    # =============================================================================
    # OUTLOOK CALENDAR OAUTH2 FLOW
    # =============================================================================
    
    def get_outlook_calendar_auth_url(self, state: Optional[str] = None) -> str:
        """Generate Outlook Calendar OAuth2 authorization URL"""
        try:
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority="https://login.microsoftonline.com/common"
            )
            
            auth_url = app.get_authorization_request_url(
                scopes=self.OUTLOOK_CALENDAR_SCOPES,
                redirect_uri=self._get_outlook_calendar_redirect_uri(),
                state=state or f"user_{self.user.id}"
            )
            
            return auth_url
            
        except Exception as e:
            logger.error(f"Failed to generate Outlook Calendar auth URL: {str(e)}")
            raise CalendarError(f"Failed to generate Outlook Calendar auth URL: {str(e)}")
    
    def handle_outlook_calendar_callback(self, authorization_code: str, state: str) -> CalendarAccount:
        """Handle Outlook Calendar OAuth2 callback and create/update CalendarAccount"""
        try:
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority="https://login.microsoftonline.com/common"
            )
            
            result = app.acquire_token_by_authorization_code(
                code=authorization_code,
                scopes=self.OUTLOOK_CALENDAR_SCOPES,
                redirect_uri=self._get_outlook_calendar_redirect_uri()
            )
            
            if "error" in result:
                raise CalendarError(f"Outlook Calendar OAuth error: {result.get('error_description', result['error'])}")
            
            access_token = result['access_token']
            refresh_token = result.get('refresh_token')
            expires_at = timezone.now() + timedelta(seconds=result.get('expires_in', 3600))
            
            # Get user info and calendar list
            user_info = self._get_outlook_user_info(access_token)
            calendars = self._get_outlook_calendars(access_token)
            
            # Find primary calendar
            primary_calendar = None
            for calendar in calendars:
                if calendar.get('isDefaultCalendar', False):
                    primary_calendar = calendar
                    break
            
            if not primary_calendar and calendars:
                primary_calendar = calendars[0]  # Use first available calendar
            
            if not primary_calendar:
                raise CalendarError("No calendars found")
            
            # Create or update CalendarAccount
            calendar_account, created = CalendarAccount.objects.get_or_create(
                user=self.user,
                provider='outlook',
                external_account_id=primary_calendar['id'],
                defaults={
                    'display_name': primary_calendar.get('name', 'Primary Calendar'),
                    'email_address': user_info.get('mail') or user_info.get('userPrincipalName', ''),
                    'calendar_list': calendars,
                    'timezone': 'America/New_York',  # Default, will be updated during sync
                }
            )
            
            # Update tokens
            calendar_account.access_token = access_token
            calendar_account.refresh_token = refresh_token
            calendar_account.token_expires_at = expires_at
            calendar_account.is_active = True
            calendar_account.sync_enabled = True
            calendar_account.save()
            
            logger.info(f"Outlook Calendar account linked successfully: {calendar_account.display_name}")
            return calendar_account
            
        except Exception as e:
            logger.error(f"Failed to handle Outlook Calendar callback: {str(e)}")
            raise CalendarError(f"Failed to handle Outlook Calendar callback: {str(e)}")
    
    def _get_outlook_calendar_redirect_uri(self) -> str:
        """Get Outlook Calendar OAuth2 redirect URI"""
        if self.request:
            return self.request.build_absolute_uri(reverse('outlook_calendar_oauth_callback'))
        return f"{settings.BASE_URL}/api/calendar/outlook/callback/"
    
    def _get_outlook_user_info(self, access_token: str) -> Dict:
        """Get Outlook user information"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def _get_outlook_calendars(self, access_token: str) -> List[Dict]:
        """Get list of Outlook calendars"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me/calendars',
            headers=headers
        )
        response.raise_for_status()
        return response.json().get('value', [])
    
    # =============================================================================
    # CALENDAR SYNCHRONIZATION
    # =============================================================================
    
    def sync_calendar_events(self, calendar_account: CalendarAccount) -> Dict[str, int]:
        """Sync events from external calendar to local database"""
        try:
            if calendar_account.provider == 'google':
                return self._sync_google_calendar_events(calendar_account)
            elif calendar_account.provider == 'outlook':
                return self._sync_outlook_calendar_events(calendar_account)
            else:
                raise CalendarError(f"Unsupported calendar provider: {calendar_account.provider}")
        
        except Exception as e:
            logger.error(f"Failed to sync calendar events for {calendar_account}: {str(e)}")
            raise CalendarError(f"Failed to sync calendar events: {str(e)}")
    
    def _sync_google_calendar_events(self, calendar_account: CalendarAccount) -> Dict[str, int]:
        """Sync Google Calendar events"""
        # Refresh token if needed
        if calendar_account.is_token_expired():
            if not self._refresh_google_calendar_token(calendar_account):
                raise CalendarError("Failed to refresh Google Calendar token")
        
        credentials = Credentials.from_authorized_user_info({
            'refresh_token': calendar_account.refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'token': calendar_account.access_token,
        })
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Calculate sync window
        now = timezone.now()
        time_min = now - timedelta(days=calendar_account.sync_past_days)
        time_max = now + timedelta(days=calendar_account.sync_future_days)
        
        # Build query parameters
        events_query = {
            'calendarId': 'primary',
            'timeMin': time_min.isoformat(),
            'timeMax': time_max.isoformat(),
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        
        # Use sync token for incremental sync if available
        if calendar_account.last_sync_token:
            events_query['syncToken'] = calendar_account.last_sync_token
            events_query.pop('timeMin', None)
            events_query.pop('timeMax', None)
        
        events_result = service.events().list(**events_query).execute()
        events = events_result.get('items', [])
        
        created_count = 0
        updated_count = 0
        deleted_count = 0
        
        for event_data in events:
            if event_data.get('status') == 'cancelled':
                # Handle deleted event
                deleted_count += self._handle_deleted_event(calendar_account, event_data.get('id'))
                continue
            
            # Create or update event
            event, created = self._create_or_update_calendar_event(
                calendar_account, event_data, 'google'
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        # Update sync metadata
        calendar_account.last_sync_at = timezone.now()
        if 'nextSyncToken' in events_result:
            calendar_account.last_sync_token = events_result['nextSyncToken']
        calendar_account.save()
        
        return {
            'created': created_count,
            'updated': updated_count,
            'deleted': deleted_count
        }
    
    def _sync_outlook_calendar_events(self, calendar_account: CalendarAccount) -> Dict[str, int]:
        """Sync Outlook Calendar events"""
        # Refresh token if needed
        if calendar_account.is_token_expired():
            if not self._refresh_outlook_calendar_token(calendar_account):
                raise CalendarError("Failed to refresh Outlook Calendar token")
        
        headers = {
            'Authorization': f'Bearer {calendar_account.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Calculate sync window
        now = timezone.now()
        time_min = now - timedelta(days=calendar_account.sync_past_days)
        time_max = now + timedelta(days=calendar_account.sync_future_days)
        
        # Build query
        url = f"https://graph.microsoft.com/v1.0/me/calendars/{calendar_account.external_account_id}/events"
        params = {
            '$filter': f"start/dateTime ge '{time_min.isoformat()}' and start/dateTime le '{time_max.isoformat()}'",
            '$orderby': 'start/dateTime',
            '$top': 250
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        events_data = response.json()
        events = events_data.get('value', [])
        
        created_count = 0
        updated_count = 0
        
        for event_data in events:
            # Create or update event
            event, created = self._create_or_update_calendar_event(
                calendar_account, event_data, 'outlook'
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        # Update sync metadata
        calendar_account.last_sync_at = timezone.now()
        calendar_account.save()
        
        return {
            'created': created_count,
            'updated': updated_count,
            'deleted': 0
        }
    
    def _create_or_update_calendar_event(self, calendar_account: CalendarAccount, event_data: Dict, provider: str) -> Tuple[CalendarEvent, bool]:
        """Create or update a calendar event from external data"""
        if provider == 'google':
            return self._process_google_event(calendar_account, event_data)
        elif provider == 'outlook':
            return self._process_outlook_event(calendar_account, event_data)
    
    def _process_google_event(self, calendar_account: CalendarAccount, event_data: Dict) -> Tuple[CalendarEvent, bool]:
        """Process Google Calendar event data"""
        event_id = event_data.get('id')
        
        # Extract start and end times
        start_data = event_data.get('start', {})
        end_data = event_data.get('end', {})
        
        if 'dateTime' in start_data:
            start_datetime = datetime.fromisoformat(start_data['dateTime'].replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(end_data['dateTime'].replace('Z', '+00:00'))
            all_day = False
        else:
            # All-day event
            start_datetime = datetime.fromisoformat(start_data['date'] + 'T00:00:00+00:00')
            end_datetime = datetime.fromisoformat(end_data['date'] + 'T23:59:59+00:00')
            all_day = True
        
        # Extract attendees
        attendees = []
        for attendee in event_data.get('attendees', []):
            attendees.append({
                'email': attendee.get('email', ''),
                'displayName': attendee.get('displayName', ''),
                'responseStatus': attendee.get('responseStatus', 'needsAction'),
                'optional': attendee.get('optional', False)
            })
        
        # Create or update event
        event, created = CalendarEvent.objects.update_or_create(
            calendar_account=calendar_account,
            external_event_id=event_id,
            defaults={
                'calendar_id': 'primary',
                'title': event_data.get('summary', ''),
                'description': event_data.get('description', ''),
                'location': event_data.get('location', ''),
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'all_day': all_day,
                'timezone': start_data.get('timeZone', ''),
                'status': event_data.get('status', 'confirmed'),
                'organizer_email': event_data.get('organizer', {}).get('email', ''),
                'organizer_name': event_data.get('organizer', {}).get('displayName', ''),
                'attendees': attendees,
                'is_recurring': 'recurringEventId' in event_data,
                'recurring_event_id': event_data.get('recurringEventId', ''),
                'last_modified_external': datetime.fromisoformat(event_data.get('updated', timezone.now().isoformat()).replace('Z', '+00:00')),
                'etag': event_data.get('etag', ''),
                'meeting_url': self._extract_meeting_url(event_data.get('description', '') + ' ' + event_data.get('location', '')),
            }
        )
        
        return event, created
    
    def _process_outlook_event(self, calendar_account: CalendarAccount, event_data: Dict) -> Tuple[CalendarEvent, bool]:
        """Process Outlook Calendar event data"""
        event_id = event_data.get('id')
        
        # Extract start and end times
        start_data = event_data.get('start', {})
        end_data = event_data.get('end', {})
        
        start_datetime = datetime.fromisoformat(start_data.get('dateTime', '') + '+00:00')
        end_datetime = datetime.fromisoformat(end_data.get('dateTime', '') + '+00:00')
        all_day = event_data.get('isAllDay', False)
        
        # Extract attendees
        attendees = []
        for attendee in event_data.get('attendees', []):
            email_address = attendee.get('emailAddress', {})
            attendees.append({
                'email': email_address.get('address', ''),
                'displayName': email_address.get('name', ''),
                'responseStatus': attendee.get('status', {}).get('response', 'none'),
                'optional': attendee.get('type') == 'optional'
            })
        
        # Create or update event
        event, created = CalendarEvent.objects.update_or_create(
            calendar_account=calendar_account,
            external_event_id=event_id,
            defaults={
                'calendar_id': calendar_account.external_account_id,
                'title': event_data.get('subject', ''),
                'description': event_data.get('body', {}).get('content', ''),
                'location': event_data.get('location', {}).get('displayName', ''),
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'all_day': all_day,
                'timezone': start_data.get('timeZone', ''),
                'status': 'confirmed' if not event_data.get('isCancelled') else 'cancelled',
                'privacy': event_data.get('sensitivity', 'normal'),
                'organizer_email': event_data.get('organizer', {}).get('emailAddress', {}).get('address', ''),
                'organizer_name': event_data.get('organizer', {}).get('emailAddress', {}).get('name', ''),
                'attendees': attendees,
                'is_recurring': event_data.get('recurrence') is not None,
                'last_modified_external': datetime.fromisoformat(event_data.get('lastModifiedDateTime', timezone.now().isoformat()).replace('Z', '+00:00')),
                'meeting_url': self._extract_meeting_url(event_data.get('body', {}).get('content', '') + ' ' + event_data.get('location', {}).get('displayName', '')),
            }
        )
        
        return event, created
    
    def _extract_meeting_url(self, text: str) -> str:
        """Extract meeting URL from text"""
        import re
        
        # Common meeting URL patterns
        patterns = [
            r'https://[\w\-\.]+\.zoom\.us/j/[\d\w\?\&\=\-]+',
            r'https://meet\.google\.com/[\w\-]+',
            r'https://teams\.microsoft\.com/l/meetup-join/[\w\d\-\%\.]+',
            r'https://[\w\-\.]*\.webex\.com/[\w\d\-\/\?\&\=]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return ''
    
    def _handle_deleted_event(self, calendar_account: CalendarAccount, event_id: str) -> int:
        """Handle deleted calendar event"""
        deleted_count = CalendarEvent.objects.filter(
            calendar_account=calendar_account,
            external_event_id=event_id
        ).delete()[0]
        
        return deleted_count
    
    # =============================================================================
    # TOKEN REFRESH
    # =============================================================================
    
    def _refresh_google_calendar_token(self, calendar_account: CalendarAccount) -> bool:
        """Refresh Google Calendar access token"""
        try:
            if not calendar_account.refresh_token:
                return False
            
            credentials = Credentials.from_authorized_user_info({
                'refresh_token': calendar_account.refresh_token,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            })
            
            credentials.refresh(Request())
            
            # Update stored tokens
            calendar_account.access_token = credentials.token
            if credentials.refresh_token:
                calendar_account.refresh_token = credentials.refresh_token
            calendar_account.token_expires_at = credentials.expiry
            calendar_account.save(update_fields=['access_token', 'refresh_token', 'token_expires_at'])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh Google Calendar token: {str(e)}")
            return False
    
    def _refresh_outlook_calendar_token(self, calendar_account: CalendarAccount) -> bool:
        """Refresh Outlook Calendar access token"""
        try:
            if not calendar_account.refresh_token:
                return False
            
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority="https://login.microsoftonline.com/common"
            )
            
            result = app.acquire_token_by_refresh_token(
                refresh_token=calendar_account.refresh_token,
                scopes=self.OUTLOOK_CALENDAR_SCOPES
            )
            
            if "error" in result:
                return False
            
            # Update stored tokens
            calendar_account.access_token = result['access_token']
            if 'refresh_token' in result:
                calendar_account.refresh_token = result['refresh_token']
            calendar_account.token_expires_at = timezone.now() + timedelta(seconds=result.get('expires_in', 3600))
            calendar_account.save(update_fields=['access_token', 'refresh_token', 'token_expires_at'])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh Outlook Calendar token: {str(e)}")
            return False


# =============================================================================
# CALENDAR SETTINGS VALIDATION
# =============================================================================

def validate_calendar_settings() -> Dict[str, bool]:
    """
    Validate that required calendar OAuth settings are configured
    """
    result = {
        'google_calendar_configured': False,
        'outlook_calendar_configured': False,
        'errors': []
    }
    
    # Check Google Calendar settings
    try:
        google_client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
        google_client_secret = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', None)
        
        if google_client_id and google_client_secret:
            result['google_calendar_configured'] = True
        else:
            result['errors'].append("Google Calendar OAuth2 credentials not configured")
    
    except Exception as e:
        result['errors'].append(f"Google Calendar configuration error: {str(e)}")
    
    # Check Outlook Calendar settings
    try:
        outlook_client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', None)
        outlook_client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', None)
        
        if outlook_client_id and outlook_client_secret:
            result['outlook_calendar_configured'] = True
        else:
            result['errors'].append("Outlook Calendar OAuth2 credentials not configured")
    
    except Exception as e:
        result['errors'].append(f"Outlook Calendar configuration error: {str(e)}")
    
    return result