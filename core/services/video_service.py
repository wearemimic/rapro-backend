"""
Video Conferencing Service for Zoom, Google Meet, Microsoft Teams, and Jump.ai Integration
Handles meeting creation, link generation, and participant management
"""

import json
import logging
import secrets
import hashlib
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

# Zoom SDK imports
try:
    import jwt
    import requests
except ImportError:
    pass

from ..models import CalendarEvent, MeetingTemplate, CalendarAccount

logger = logging.getLogger(__name__)


class VideoConferenceError(Exception):
    """Video conference-related errors"""
    pass


class VideoConferenceService:
    """
    Service for handling video conference operations across Zoom, Google Meet, Microsoft Teams, and Jump.ai
    """
    
    # Zoom API Configuration
    ZOOM_API_BASE_URL = "https://api.zoom.us/v2"
    ZOOM_OAUTH_URL = "https://zoom.us/oauth"
    
    # Jump.ai API Configuration  
    JUMP_AI_API_BASE_URL = "https://api.jump.ai/v1"
    JUMP_AI_OAUTH_URL = "https://jump.ai/oauth"
    
    # Google Meet doesn't have a direct API - it's created through Calendar API
    # Microsoft Teams uses Graph API through Calendar integration
    
    def __init__(self, user):
        self.user = user
    
    # =============================================================================
    # ZOOM INTEGRATION
    # =============================================================================
    
    def create_zoom_meeting(self, event: CalendarEvent, template: Optional[MeetingTemplate] = None) -> Dict:
        """
        Create a Zoom meeting for a calendar event
        """
        try:
            # Get Zoom access token
            access_token = self._get_zoom_access_token()
            if not access_token:
                raise VideoConferenceError("Unable to obtain Zoom access token")
            
            # Prepare meeting data
            meeting_data = self._prepare_zoom_meeting_data(event, template)
            
            # Create meeting via Zoom API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.ZOOM_API_BASE_URL}/users/me/meetings",
                headers=headers,
                json=meeting_data
            )
            
            if response.status_code == 201:
                zoom_data = response.json()
                
                # Update event with Zoom details
                event.meeting_url = zoom_data.get('join_url')
                event.meeting_type = 'zoom'
                event.meeting_id = str(zoom_data.get('id'))
                event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
                
                return {
                    'success': True,
                    'meeting_url': zoom_data.get('join_url'),
                    'meeting_id': zoom_data.get('id'),
                    'host_url': zoom_data.get('start_url'),
                    'password': zoom_data.get('password'),
                    'dial_in': zoom_data.get('settings', {}).get('global_dial_in_numbers', [])
                }
            else:
                error_msg = response.json().get('message', 'Unknown error')
                raise VideoConferenceError(f"Zoom API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to create Zoom meeting: {str(e)}")
            raise VideoConferenceError(f"Failed to create Zoom meeting: {str(e)}")
    
    def _get_zoom_access_token(self) -> Optional[str]:
        """
        Get Zoom access token using Server-to-Server OAuth
        """
        try:
            # Check if we have Zoom credentials configured
            zoom_account_id = getattr(settings, 'ZOOM_ACCOUNT_ID', None)
            zoom_client_id = getattr(settings, 'ZOOM_CLIENT_ID', None)
            zoom_client_secret = getattr(settings, 'ZOOM_CLIENT_SECRET', None)
            
            if not all([zoom_account_id, zoom_client_id, zoom_client_secret]):
                logger.warning("Zoom credentials not configured")
                return None
            
            # Request access token
            auth = base64.b64encode(f"{zoom_client_id}:{zoom_client_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'account_credentials',
                'account_id': zoom_account_id
            }
            
            response = requests.post(
                f"{self.ZOOM_OAUTH_URL}/token",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                logger.error(f"Failed to get Zoom access token: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Zoom access token: {str(e)}")
            return None
    
    def _prepare_zoom_meeting_data(self, event: CalendarEvent, template: Optional[MeetingTemplate] = None) -> Dict:
        """
        Prepare meeting data for Zoom API
        """
        # Calculate duration in minutes
        duration = event.duration_minutes or 60
        
        # Get attendee emails
        attendee_emails = event.get_attendee_emails() if event.attendees else []
        
        meeting_data = {
            'topic': event.title,
            'type': 2,  # Scheduled meeting
            'start_time': event.start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'duration': duration,
            'timezone': event.timezone or 'America/New_York',
            'agenda': event.description,
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'watermark': False,
                'use_pmi': False,
                'approval_type': 0,  # Automatically approve
                'registration_type': 1,  # Attendees register once
                'audio': 'both',  # Both telephony and VoIP
                'auto_recording': 'none',
                'waiting_room': True,
                'meeting_authentication': False,
            }
        }
        
        # Add password if configured
        if getattr(settings, 'ZOOM_REQUIRE_PASSWORD', True):
            meeting_data['password'] = self._generate_meeting_password()
        
        # Add alternative hosts if specified
        if attendee_emails:
            # First attendee can be alternative host
            meeting_data['settings']['alternative_hosts'] = ','.join(attendee_emails[:1])
        
        return meeting_data
    
    def _generate_meeting_password(self) -> str:
        """Generate a secure meeting password"""
        # Zoom password requirements: 1-10 characters, alphanumeric
        return secrets.token_urlsafe(6)[:8]
    
    def update_zoom_meeting(self, event: CalendarEvent) -> Dict:
        """
        Update an existing Zoom meeting
        """
        try:
            if not event.meeting_id or event.meeting_type != 'zoom':
                raise VideoConferenceError("Event does not have a Zoom meeting")
            
            access_token = self._get_zoom_access_token()
            if not access_token:
                raise VideoConferenceError("Unable to obtain Zoom access token")
            
            # Prepare updated meeting data
            meeting_data = self._prepare_zoom_meeting_data(event)
            
            # Update meeting via Zoom API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(
                f"{self.ZOOM_API_BASE_URL}/meetings/{event.meeting_id}",
                headers=headers,
                json=meeting_data
            )
            
            if response.status_code == 204:
                return {'success': True, 'message': 'Zoom meeting updated successfully'}
            else:
                error_msg = response.json().get('message', 'Unknown error')
                raise VideoConferenceError(f"Zoom API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to update Zoom meeting: {str(e)}")
            raise VideoConferenceError(f"Failed to update Zoom meeting: {str(e)}")
    
    def delete_zoom_meeting(self, event: CalendarEvent) -> bool:
        """
        Delete a Zoom meeting
        """
        try:
            if not event.meeting_id or event.meeting_type != 'zoom':
                return False
            
            access_token = self._get_zoom_access_token()
            if not access_token:
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.delete(
                f"{self.ZOOM_API_BASE_URL}/meetings/{event.meeting_id}",
                headers=headers
            )
            
            if response.status_code == 204:
                # Clear meeting data from event
                event.meeting_url = ''
                event.meeting_type = ''
                event.meeting_id = ''
                event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete Zoom meeting: {str(e)}")
            return False
    
    # =============================================================================
    # JUMP.AI INTEGRATION
    # =============================================================================
    
    def create_jump_ai_meeting(self, event: CalendarEvent, template: Optional[MeetingTemplate] = None) -> Dict:
        """
        Create a Jump.ai meeting for a calendar event
        """
        try:
            # Get Jump.ai access token
            access_token = self._get_jump_ai_access_token()
            if not access_token:
                raise VideoConferenceError("Unable to obtain Jump.ai access token")
            
            # Prepare meeting data
            meeting_data = self._prepare_jump_ai_meeting_data(event, template)
            
            # Create meeting via Jump.ai API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.JUMP_AI_API_BASE_URL}/meetings",
                headers=headers,
                json=meeting_data
            )
            
            if response.status_code == 201:
                jump_data = response.json()
                
                # Update event with Jump.ai details
                event.meeting_url = jump_data.get('join_url')
                event.meeting_type = 'jump_ai'
                event.meeting_id = jump_data.get('meeting_id')
                event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
                
                return {
                    'success': True,
                    'meeting_url': jump_data.get('join_url'),
                    'meeting_id': jump_data.get('meeting_id'),
                    'host_url': jump_data.get('host_url'),
                    'room_name': jump_data.get('room_name'),
                    'ai_features': jump_data.get('ai_features', {})
                }
            else:
                error_msg = response.json().get('message', 'Unknown error')
                raise VideoConferenceError(f"Jump.ai API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to create Jump.ai meeting: {str(e)}")
            raise VideoConferenceError(f"Failed to create Jump.ai meeting: {str(e)}")
    
    def _get_jump_ai_access_token(self) -> Optional[str]:
        """
        Get Jump.ai access token using OAuth2
        """
        try:
            # Check if we have Jump.ai credentials configured
            jump_ai_client_id = getattr(settings, 'JUMP_AI_CLIENT_ID', None)
            jump_ai_client_secret = getattr(settings, 'JUMP_AI_CLIENT_SECRET', None)
            
            if not all([jump_ai_client_id, jump_ai_client_secret]):
                logger.warning("Jump.ai credentials not configured")
                return None
            
            # Request access token
            auth = base64.b64encode(f"{jump_ai_client_id}:{jump_ai_client_secret}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'scope': 'meetings:create meetings:manage'
            }
            
            response = requests.post(
                f"{self.JUMP_AI_OAUTH_URL}/token",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                logger.error(f"Failed to get Jump.ai access token: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get Jump.ai access token: {str(e)}")
            return None
    
    def _prepare_jump_ai_meeting_data(self, event: CalendarEvent, template: Optional[MeetingTemplate] = None) -> Dict:
        """
        Prepare meeting data for Jump.ai API
        """
        meeting_data = {
            'topic': event.title,
            'start_time': event.start_time.isoformat(),
            'duration_minutes': int((event.end_time - event.start_time).total_seconds() / 60),
            'description': event.description or '',
            'settings': {
                'ai_assistant_enabled': True,
                'auto_transcription': True,
                'auto_summary': True,
                'waiting_room': True,
                'mute_participants_on_join': False,
                'allow_recording': True,
                'ai_insights': True
            }
        }
        
        # Apply template settings if provided
        if template:
            template_settings = template.settings or {}
            meeting_data['settings'].update(template_settings.get('jump_ai', {}))
        
        # Add attendees if available
        if hasattr(event, 'attendees') and event.attendees:
            meeting_data['attendees'] = [
                {'email': attendee.email, 'name': getattr(attendee, 'name', attendee.email)}
                for attendee in event.attendees.all()
            ]
        
        return meeting_data
    
    def update_jump_ai_meeting(self, event: CalendarEvent, updates: Dict) -> Dict:
        """
        Update an existing Jump.ai meeting
        """
        try:
            if not event.meeting_id or event.meeting_type != 'jump_ai':
                raise VideoConferenceError("Event is not associated with a Jump.ai meeting")
            
            access_token = self._get_jump_ai_access_token()
            if not access_token:
                raise VideoConferenceError("Unable to obtain Jump.ai access token")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(
                f"{self.JUMP_AI_API_BASE_URL}/meetings/{event.meeting_id}",
                headers=headers,
                json=updates
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                error_msg = response.json().get('message', 'Unknown error')
                raise VideoConferenceError(f"Jump.ai API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to update Jump.ai meeting: {str(e)}")
            raise VideoConferenceError(f"Failed to update Jump.ai meeting: {str(e)}")
    
    def delete_jump_ai_meeting(self, event: CalendarEvent) -> bool:
        """
        Delete a Jump.ai meeting
        """
        try:
            if not event.meeting_id or event.meeting_type != 'jump_ai':
                return True  # Nothing to delete
            
            access_token = self._get_jump_ai_access_token()
            if not access_token:
                logger.warning("Unable to obtain Jump.ai access token for deletion")
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.delete(
                f"{self.JUMP_AI_API_BASE_URL}/meetings/{event.meeting_id}",
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                # Clear meeting details from event
                event.meeting_url = None
                event.meeting_type = None
                event.meeting_id = None
                event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
                return True
            else:
                logger.error(f"Jump.ai deletion failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete Jump.ai meeting: {str(e)}")
            return False
    
    def get_jump_ai_meeting_insights(self, event: CalendarEvent) -> Dict:
        """
        Get AI insights and analytics from a completed Jump.ai meeting
        """
        try:
            if not event.meeting_id or event.meeting_type != 'jump_ai':
                raise VideoConferenceError("Event is not associated with a Jump.ai meeting")
            
            access_token = self._get_jump_ai_access_token()
            if not access_token:
                raise VideoConferenceError("Unable to obtain Jump.ai access token")
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # Get meeting insights
            response = requests.get(
                f"{self.JUMP_AI_API_BASE_URL}/meetings/{event.meeting_id}/insights",
                headers=headers
            )
            
            if response.status_code == 200:
                insights_data = response.json()
                return {
                    'success': True,
                    'transcript': insights_data.get('transcript', ''),
                    'summary': insights_data.get('summary', ''),
                    'action_items': insights_data.get('action_items', []),
                    'key_topics': insights_data.get('key_topics', []),
                    'sentiment_analysis': insights_data.get('sentiment_analysis', {}),
                    'participant_insights': insights_data.get('participant_insights', {}),
                    'recording_url': insights_data.get('recording_url', None)
                }
            else:
                error_msg = response.json().get('message', 'Insights not available')
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Failed to get Jump.ai meeting insights: {str(e)}")
            return {'success': False, 'error': str(e)}

    # =============================================================================
    # GOOGLE MEET INTEGRATION
    # =============================================================================
    
    def create_google_meet_link(self, event: CalendarEvent) -> Dict:
        """
        Create a Google Meet link for a calendar event
        Note: Google Meet links are automatically created when creating Google Calendar events
        with conferenceData parameter
        """
        try:
            # Find user's Google calendar account
            google_calendar = CalendarAccount.objects.filter(
                user=self.user,
                provider='google',
                is_active=True
            ).first()
            
            if not google_calendar:
                # Generate a static Meet link (requires Google account to create actual meeting)
                meet_code = self._generate_meet_code()
                meet_url = f"https://meet.google.com/{meet_code}"
                
                # Update event with Meet details
                event.meeting_url = meet_url
                event.meeting_type = 'meet'
                event.meeting_id = meet_code
                event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
                
                return {
                    'success': True,
                    'meeting_url': meet_url,
                    'meeting_id': meet_code,
                    'note': 'Google Meet link generated. Host must have Google account to start meeting.'
                }
            
            # If user has Google Calendar, create event with conferenceData
            from .calendar_service import CalendarService
            
            # This would be implemented in calendar_service.py
            # For now, generate a Meet link
            meet_code = self._generate_meet_code()
            meet_url = f"https://meet.google.com/{meet_code}"
            
            event.meeting_url = meet_url
            event.meeting_type = 'meet'
            event.meeting_id = meet_code
            event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
            
            return {
                'success': True,
                'meeting_url': meet_url,
                'meeting_id': meet_code
            }
            
        except Exception as e:
            logger.error(f"Failed to create Google Meet link: {str(e)}")
            raise VideoConferenceError(f"Failed to create Google Meet link: {str(e)}")
    
    def _generate_meet_code(self) -> str:
        """
        Generate a Google Meet-style code (xxx-xxxx-xxx format)
        """
        # Generate random alphanumeric code
        chars = 'abcdefghijklmnopqrstuvwxyz'
        part1 = ''.join(secrets.choice(chars) for _ in range(3))
        part2 = ''.join(secrets.choice(chars) for _ in range(4))
        part3 = ''.join(secrets.choice(chars) for _ in range(3))
        
        return f"{part1}-{part2}-{part3}"
    
    # =============================================================================
    # MICROSOFT TEAMS INTEGRATION
    # =============================================================================
    
    def create_teams_meeting(self, event: CalendarEvent) -> Dict:
        """
        Create a Microsoft Teams meeting for a calendar event
        Note: Teams meetings are created through Microsoft Graph API
        """
        try:
            # Find user's Outlook calendar account
            outlook_calendar = CalendarAccount.objects.filter(
                user=self.user,
                provider='outlook',
                is_active=True
            ).first()
            
            if not outlook_calendar:
                raise VideoConferenceError("Microsoft account not connected. Please connect Outlook Calendar first.")
            
            # Refresh token if needed
            if outlook_calendar.is_token_expired():
                from .calendar_service import CalendarService
                service = CalendarService(self.user)
                if not service._refresh_outlook_calendar_token(outlook_calendar):
                    raise VideoConferenceError("Failed to refresh Microsoft access token")
            
            # Create Teams meeting via Graph API
            headers = {
                'Authorization': f'Bearer {outlook_calendar.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare meeting data
            meeting_data = self._prepare_teams_meeting_data(event)
            
            response = requests.post(
                'https://graph.microsoft.com/v1.0/me/onlineMeetings',
                headers=headers,
                json=meeting_data
            )
            
            if response.status_code == 201:
                teams_data = response.json()
                
                # Update event with Teams details
                event.meeting_url = teams_data.get('joinWebUrl')
                event.meeting_type = 'teams'
                event.meeting_id = teams_data.get('id')
                event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
                
                return {
                    'success': True,
                    'meeting_url': teams_data.get('joinWebUrl'),
                    'meeting_id': teams_data.get('id'),
                    'audio_conferencing': teams_data.get('audioConferencing', {}),
                    'join_information': teams_data.get('joinInformation', {})
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                raise VideoConferenceError(f"Microsoft Graph API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to create Teams meeting: {str(e)}")
            raise VideoConferenceError(f"Failed to create Teams meeting: {str(e)}")
    
    def _prepare_teams_meeting_data(self, event: CalendarEvent) -> Dict:
        """
        Prepare meeting data for Microsoft Teams API
        """
        start_time = event.start_datetime.isoformat()
        end_time = event.end_datetime.isoformat()
        
        meeting_data = {
            'subject': event.title,
            'startDateTime': start_time,
            'endDateTime': end_time,
            'participants': {
                'attendees': []
            }
        }
        
        # Add attendees
        for attendee in event.attendees or []:
            if attendee.get('email'):
                meeting_data['participants']['attendees'].append({
                    'identity': {
                        'user': {
                            'displayName': attendee.get('displayName', ''),
                            'id': attendee.get('email')
                        }
                    }
                })
        
        # Add meeting description
        if event.description:
            meeting_data['chatInfo'] = {
                'threadId': None,
                'messageId': '0'
            }
        
        return meeting_data
    
    # =============================================================================
    # GENERIC VIDEO MEETING OPERATIONS
    # =============================================================================
    
    def create_video_meeting(self, event: CalendarEvent, meeting_type: str = 'zoom', 
                           template: Optional[MeetingTemplate] = None) -> Dict:
        """
        Create a video meeting based on the specified type
        """
        if meeting_type == 'zoom':
            return self.create_zoom_meeting(event, template)
        elif meeting_type == 'jump_ai':
            return self.create_jump_ai_meeting(event, template)
        elif meeting_type == 'meet':
            return self.create_google_meet_link(event)
        elif meeting_type == 'teams':
            return self.create_teams_meeting(event)
        else:
            raise VideoConferenceError(f"Unsupported meeting type: {meeting_type}")
    
    def update_video_meeting(self, event: CalendarEvent, updates: Dict = None) -> Dict:
        """
        Update a video meeting based on its type
        """
        if event.meeting_type == 'zoom':
            return self.update_zoom_meeting(event)
        elif event.meeting_type == 'jump_ai':
            return self.update_jump_ai_meeting(event, updates or {})
        elif event.meeting_type == 'meet':
            # Google Meet links don't need updating - they're static
            return {'success': True, 'message': 'Google Meet links do not require updating'}
        elif event.meeting_type == 'teams':
            # Teams meetings are updated through calendar event updates
            return {'success': True, 'message': 'Teams meeting will be updated with calendar event'}
        else:
            raise VideoConferenceError(f"Unsupported meeting type: {event.meeting_type}")
    
    def delete_video_meeting(self, event: CalendarEvent) -> bool:
        """
        Delete a video meeting based on its type
        """
        if event.meeting_type == 'zoom':
            return self.delete_zoom_meeting(event)
        elif event.meeting_type == 'jump_ai':
            return self.delete_jump_ai_meeting(event)
        elif event.meeting_type in ['meet', 'teams']:
            # Clear meeting data for Meet and Teams
            event.meeting_url = ''
            event.meeting_type = ''
            event.meeting_id = ''
            event.save(update_fields=['meeting_url', 'meeting_type', 'meeting_id'])
            return True
        
        return False
    
    def get_meeting_join_info(self, event: CalendarEvent) -> Dict:
        """
        Get joining information for a video meeting
        """
        if not event.meeting_url:
            return {
                'has_meeting': False,
                'message': 'No video meeting associated with this event'
            }
        
        join_info = {
            'has_meeting': True,
            'meeting_url': event.meeting_url,
            'meeting_type': event.meeting_type,
            'meeting_id': event.meeting_id
        }
        
        # Add type-specific information
        if event.meeting_type == 'zoom':
            join_info['instructions'] = (
                'Click the link to join the Zoom meeting. '
                'You may need to download the Zoom client if not already installed.'
            )
        elif event.meeting_type == 'meet':
            join_info['instructions'] = (
                'Click the link to join with Google Meet. '
                'Works best in Chrome browser. No download required.'
            )
        elif event.meeting_type == 'teams':
            join_info['instructions'] = (
                'Click the link to join the Teams meeting. '
                'You can join from browser or Teams app.'
            )
        
        return join_info


# =============================================================================
# VIDEO MEETING REMINDER SERVICE
# =============================================================================

class MeetingReminderService:
    """
    Service for sending meeting reminders
    """
    
    def __init__(self):
        pass
    
    def send_meeting_reminder(self, event: CalendarEvent, reminder_minutes: int = 15) -> bool:
        """
        Send meeting reminder to participants
        """
        try:
            from ..tasks import send_meeting_reminder_email
            
            # Calculate reminder time
            reminder_time = event.start_datetime - timedelta(minutes=reminder_minutes)
            
            # Schedule reminder task
            send_meeting_reminder_email.apply_async(
                args=[event.id],
                eta=reminder_time
            )
            
            logger.info(f"Scheduled meeting reminder for event {event.id} at {reminder_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule meeting reminder: {str(e)}")
            return False
    
    def send_immediate_reminder(self, event: CalendarEvent) -> bool:
        """
        Send immediate meeting reminder (for meetings starting soon)
        """
        try:
            # Get meeting join information
            video_service = VideoConferenceService(event.calendar_account.user)
            join_info = video_service.get_meeting_join_info(event)
            
            if not join_info.get('has_meeting'):
                return False
            
            # Prepare reminder content
            reminder_data = {
                'event_title': event.title,
                'start_time': event.start_datetime,
                'meeting_url': join_info.get('meeting_url'),
                'meeting_type': join_info.get('meeting_type'),
                'instructions': join_info.get('instructions'),
                'attendees': event.get_attendee_emails()
            }
            
            # Send reminder emails (would integrate with email service)
            from .email_service import EmailService
            # Implementation would send emails to attendees
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send immediate reminder: {str(e)}")
            return False


# =============================================================================
# SETTINGS VALIDATION
# =============================================================================

def validate_video_settings() -> Dict[str, bool]:
    """
    Validate that required video conferencing settings are configured
    """
    result = {
        'zoom_configured': False,
        'google_meet_available': True,  # Always available through browser
        'teams_configured': False,
        'errors': []
    }
    
    # Check Zoom settings
    try:
        zoom_account_id = getattr(settings, 'ZOOM_ACCOUNT_ID', None)
        zoom_client_id = getattr(settings, 'ZOOM_CLIENT_ID', None)
        zoom_client_secret = getattr(settings, 'ZOOM_CLIENT_SECRET', None)
        
        if all([zoom_account_id, zoom_client_id, zoom_client_secret]):
            result['zoom_configured'] = True
        else:
            result['errors'].append("Zoom API credentials not configured")
    
    except Exception as e:
        result['errors'].append(f"Zoom configuration error: {str(e)}")
    
    # Check Microsoft Teams (through Outlook Calendar)
    try:
        from .calendar_service import CalendarService
        
        # Teams is available if Outlook Calendar is configured
        outlook_client_id = getattr(settings, 'MICROSOFT_CLIENT_ID', None)
        outlook_client_secret = getattr(settings, 'MICROSOFT_CLIENT_SECRET', None)
        
        if outlook_client_id and outlook_client_secret:
            result['teams_configured'] = True
        else:
            result['errors'].append("Microsoft Teams requires Outlook Calendar configuration")
    
    except Exception as e:
        result['errors'].append(f"Teams configuration error: {str(e)}")
    
    return result