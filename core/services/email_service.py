"""
Email Service for CRM Integration
Handles Gmail, Outlook, and IMAP/SMTP email operations
"""

import base64
import email
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    pass

# Microsoft Graph imports
try:
    import msal
    import requests as http_requests
except ImportError:
    pass

# IMAP/SMTP imports
try:
    import imapclient
    import smtplib
    from email.utils import parseaddr, formataddr
except ImportError:
    pass

from ..models import EmailAccount, Communication, Client, Lead

logger = logging.getLogger(__name__)


class EmailServiceError(Exception):
    """Base exception for email service errors"""
    pass


class AuthenticationError(EmailServiceError):
    """Authentication-related errors"""
    pass


class SyncError(EmailServiceError):
    """Sync-related errors"""
    pass


class EmailService:
    """
    Comprehensive email service supporting Gmail, Outlook, and IMAP/SMTP
    """
    
    def __init__(self, email_account: EmailAccount):
        self.email_account = email_account
        self.provider = email_account.provider
        self.user = email_account.user
        
        # Initialize provider-specific clients
        self._gmail_service = None
        self._graph_client = None
        self._imap_client = None
        self._smtp_client = None
    
    # =============================================================================
    # AUTHENTICATION METHODS
    # =============================================================================
    
    def authenticate(self) -> bool:
        """
        Authenticate with the email provider
        Returns True if successful, raises AuthenticationError otherwise
        """
        try:
            if self.provider == 'gmail':
                return self._authenticate_gmail()
            elif self.provider == 'outlook':
                return self._authenticate_outlook()
            elif self.provider == 'imap':
                return self._authenticate_imap()
            else:
                raise AuthenticationError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Authentication failed for {self.email_account.email_address}: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def _authenticate_gmail(self) -> bool:
        """Authenticate with Gmail using OAuth2"""
        if not self.email_account.access_token:
            raise AuthenticationError("No access token available for Gmail")
        
        try:
            creds = Credentials.from_authorized_user_info({
                'token': self.email_account.access_token,
                'refresh_token': self.email_account.refresh_token,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            })
            
            # Refresh token if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._update_tokens(creds.token, creds.refresh_token, creds.expiry)
            
            self._gmail_service = build('gmail', 'v1', credentials=creds)
            return True
            
        except Exception as e:
            raise AuthenticationError(f"Gmail authentication failed: {str(e)}")
    
    def _authenticate_outlook(self) -> bool:
        """Authenticate with Outlook using MSAL"""
        if not self.email_account.access_token:
            raise AuthenticationError("No access token available for Outlook")
        
        try:
            app = msal.ClientApplication(
                client_id=settings.MICROSOFT_CLIENT_ID,
                client_credential=settings.MICROSOFT_CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/common"
            )
            
            # Try to refresh token if needed
            if self._is_token_expired():
                result = app.acquire_token_by_refresh_token(
                    refresh_token=self.email_account.refresh_token,
                    scopes=['https://graph.microsoft.com/.default']
                )
                
                if 'access_token' in result:
                    self._update_tokens(
                        result['access_token'],
                        result.get('refresh_token', self.email_account.refresh_token),
                        timezone.now() + timedelta(seconds=result.get('expires_in', 3600))
                    )
            
            return True
            
        except Exception as e:
            raise AuthenticationError(f"Outlook authentication failed: {str(e)}")
    
    def _authenticate_imap(self) -> bool:
        """Authenticate with IMAP/SMTP"""
        try:
            self._imap_client = imapclient.IMAPClient(
                self.email_account.imap_server,
                port=self.email_account.imap_port,
                ssl=self.email_account.use_ssl
            )
            
            # Use stored credentials (should be encrypted in production)
            self._imap_client.login(
                self.email_account.email_address,
                self.email_account.access_token  # Store password in access_token field for IMAP
            )
            
            return True
            
        except Exception as e:
            raise AuthenticationError(f"IMAP authentication failed: {str(e)}")
    
    def _update_tokens(self, access_token: str, refresh_token: str, expires_at: datetime):
        """Update stored OAuth tokens"""
        self.email_account.access_token = access_token
        self.email_account.refresh_token = refresh_token
        self.email_account.token_expires_at = expires_at
        self.email_account.save(update_fields=['access_token', 'refresh_token', 'token_expires_at'])
    
    def _is_token_expired(self) -> bool:
        """Check if the access token is expired"""
        if not self.email_account.token_expires_at:
            return True
        return timezone.now() >= self.email_account.token_expires_at - timedelta(minutes=5)
    
    # =============================================================================
    # EMAIL FETCHING METHODS
    # =============================================================================
    
    def fetch_emails(self, limit: int = 100, since_date: Optional[datetime] = None) -> List[Dict]:
        """
        Fetch emails from the provider
        Returns list of email dictionaries
        """
        if not self.authenticate():
            raise SyncError("Failed to authenticate")
        
        try:
            if self.provider == 'gmail':
                return self._fetch_gmail_emails(limit, since_date)
            elif self.provider == 'outlook':
                return self._fetch_outlook_emails(limit, since_date)
            elif self.provider == 'imap':
                return self._fetch_imap_emails(limit, since_date)
        except Exception as e:
            logger.error(f"Failed to fetch emails: {str(e)}")
            raise SyncError(f"Failed to fetch emails: {str(e)}")
    
    def _fetch_gmail_emails(self, limit: int, since_date: Optional[datetime]) -> List[Dict]:
        """Fetch emails from Gmail"""
        emails = []
        query = ""
        
        if since_date:
            query = f"after:{since_date.strftime('%Y/%m/%d')}"
        
        try:
            # Get message list
            results = self._gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            
            # Fetch full message details
            for msg in messages:
                try:
                    message = self._gmail_service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    email_data = self._parse_gmail_message(message)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch Gmail message {msg['id']}: {str(e)}")
                    continue
            
        except HttpError as e:
            logger.error(f"Gmail API error: {str(e)}")
            raise SyncError(f"Gmail API error: {str(e)}")
        
        return emails
    
    def _fetch_outlook_emails(self, limit: int, since_date: Optional[datetime]) -> List[Dict]:
        """Fetch emails from Outlook via Microsoft Graph"""
        emails = []
        
        headers = {
            'Authorization': f'Bearer {self.email_account.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = "https://graph.microsoft.com/v1.0/me/messages"
        params = {
            '$top': limit,
            '$orderby': 'receivedDateTime desc'
        }
        
        if since_date:
            params['$filter'] = f"receivedDateTime ge {since_date.isoformat()}"
        
        try:
            response = http_requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get('value', [])
            
            for message in messages:
                email_data = self._parse_outlook_message(message)
                if email_data:
                    emails.append(email_data)
                    
        except Exception as e:
            logger.error(f"Outlook Graph API error: {str(e)}")
            raise SyncError(f"Outlook Graph API error: {str(e)}")
        
        return emails
    
    def _fetch_imap_emails(self, limit: int, since_date: Optional[datetime]) -> List[Dict]:
        """Fetch emails via IMAP"""
        emails = []
        
        try:
            self._imap_client.select_folder('INBOX')
            
            # Build search criteria
            search_criteria = ['ALL']
            if since_date:
                search_criteria = ['SINCE', since_date.date()]
            
            # Search for messages
            message_ids = self._imap_client.search(search_criteria)
            
            # Limit results
            message_ids = message_ids[-limit:] if len(message_ids) > limit else message_ids
            
            # Fetch messages
            for msg_id in message_ids:
                try:
                    raw_message = self._imap_client.fetch(msg_id, ['RFC822'])[msg_id][b'RFC822']
                    email_data = self._parse_imap_message(raw_message, msg_id)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch IMAP message {msg_id}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"IMAP fetch error: {str(e)}")
            raise SyncError(f"IMAP fetch error: {str(e)}")
        
        return emails
    
    # =============================================================================
    # EMAIL PARSING METHODS
    # =============================================================================
    
    def _parse_gmail_message(self, message: Dict) -> Optional[Dict]:
        """Parse Gmail message into standard format"""
        try:
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            # Extract body
            body = self._extract_gmail_body(message['payload'])
            
            return {
                'provider_message_id': message['id'],
                'message_id_header': headers.get('Message-ID', ''),
                'thread_id': message.get('threadId', ''),
                'subject': headers.get('Subject', ''),
                'from_address': self._parse_email_address(headers.get('From', '')),
                'to_addresses': self._parse_email_addresses(headers.get('To', '')),
                'cc_addresses': self._parse_email_addresses(headers.get('Cc', '')),
                'bcc_addresses': self._parse_email_addresses(headers.get('Bcc', '')),
                'content': body,
                'sent_at': self._parse_gmail_date(headers.get('Date', '')),
                'in_reply_to': headers.get('In-Reply-To', ''),
                'labels': message.get('labelIds', []),
                'is_read': 'UNREAD' not in message.get('labelIds', []),
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse Gmail message: {str(e)}")
            return None
    
    def _parse_outlook_message(self, message: Dict) -> Optional[Dict]:
        """Parse Outlook message into standard format"""
        try:
            return {
                'provider_message_id': message['id'],
                'message_id_header': message.get('internetMessageId', ''),
                'thread_id': message.get('conversationId', ''),
                'subject': message.get('subject', ''),
                'from_address': message.get('from', {}).get('emailAddress', {}).get('address', ''),
                'to_addresses': [addr['emailAddress']['address'] for addr in message.get('toRecipients', [])],
                'cc_addresses': [addr['emailAddress']['address'] for addr in message.get('ccRecipients', [])],
                'bcc_addresses': [addr['emailAddress']['address'] for addr in message.get('bccRecipients', [])],
                'content': message.get('body', {}).get('content', ''),
                'sent_at': self._parse_outlook_date(message.get('sentDateTime', '')),
                'is_read': message.get('isRead', False),
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse Outlook message: {str(e)}")
            return None
    
    def _parse_imap_message(self, raw_message: bytes, msg_id: int) -> Optional[Dict]:
        """Parse IMAP message into standard format"""
        try:
            msg = email.message_from_bytes(raw_message)
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    elif part.get_content_type() == "text/html" and not body:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return {
                'provider_message_id': str(msg_id),
                'message_id_header': msg.get('Message-ID', ''),
                'thread_id': msg.get('Thread-Index', ''),
                'subject': msg.get('Subject', ''),
                'from_address': self._parse_email_address(msg.get('From', '')),
                'to_addresses': self._parse_email_addresses(msg.get('To', '')),
                'cc_addresses': self._parse_email_addresses(msg.get('Cc', '')),
                'bcc_addresses': self._parse_email_addresses(msg.get('Bcc', '')),
                'content': body,
                'sent_at': self._parse_email_date(msg.get('Date', '')),
                'in_reply_to': msg.get('In-Reply-To', ''),
                'is_read': True,  # IMAP doesn't provide unread status in this context
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse IMAP message: {str(e)}")
            return None
    
    def _extract_gmail_body(self, payload: Dict) -> str:
        """Extract body text from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and 'data' in part['body'] and not body:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif payload['mimeType'] == 'text/html' and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    # =============================================================================
    # EMAIL SENDING METHODS
    # =============================================================================
    
    def send_email(self, to_addresses: List[str], subject: str, body: str, 
                   cc_addresses: Optional[List[str]] = None, 
                   attachments: Optional[List[Dict]] = None) -> str:
        """
        Send an email
        Returns the message ID of the sent email
        """
        if not self.authenticate():
            raise EmailServiceError("Failed to authenticate")
        
        try:
            if self.provider == 'gmail':
                return self._send_gmail_email(to_addresses, subject, body, cc_addresses, attachments)
            elif self.provider == 'outlook':
                return self._send_outlook_email(to_addresses, subject, body, cc_addresses, attachments)
            elif self.provider == 'imap':
                return self._send_smtp_email(to_addresses, subject, body, cc_addresses, attachments)
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise EmailServiceError(f"Failed to send email: {str(e)}")
    
    def _send_gmail_email(self, to_addresses: List[str], subject: str, body: str,
                         cc_addresses: Optional[List[str]], attachments: Optional[List[Dict]]) -> str:
        """Send email via Gmail API"""
        message = MIMEMultipart()
        message['to'] = ', '.join(to_addresses)
        message['from'] = self.email_account.email_address
        message['subject'] = subject
        
        if cc_addresses:
            message['cc'] = ', '.join(cc_addresses)
        
        message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                self._add_attachment(message, attachment)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        try:
            sent_message = self._gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return sent_message['id']
            
        except HttpError as e:
            raise EmailServiceError(f"Gmail send error: {str(e)}")
    
    def _send_outlook_email(self, to_addresses: List[str], subject: str, body: str,
                           cc_addresses: Optional[List[str]], attachments: Optional[List[Dict]]) -> str:
        """Send email via Microsoft Graph"""
        headers = {
            'Authorization': f'Bearer {self.email_account.access_token}',
            'Content-Type': 'application/json'
        }
        
        email_data = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'HTML' if '<' in body else 'Text',
                    'content': body
                },
                'toRecipients': [{'emailAddress': {'address': addr}} for addr in to_addresses],
            }
        }
        
        if cc_addresses:
            email_data['message']['ccRecipients'] = [{'emailAddress': {'address': addr}} for addr in cc_addresses]
        
        if attachments:
            email_data['message']['attachments'] = []
            for attachment in attachments:
                email_data['message']['attachments'].append({
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': attachment['name'],
                    'contentBytes': attachment['content_base64']
                })
        
        try:
            response = http_requests.post(
                'https://graph.microsoft.com/v1.0/me/sendMail',
                headers=headers,
                json=email_data
            )
            response.raise_for_status()
            
            return response.headers.get('Message-Id', 'unknown')
            
        except Exception as e:
            raise EmailServiceError(f"Outlook send error: {str(e)}")
    
    def _send_smtp_email(self, to_addresses: List[str], subject: str, body: str,
                        cc_addresses: Optional[List[str]], attachments: Optional[List[Dict]]) -> str:
        """Send email via SMTP"""
        message = MIMEMultipart()
        message['From'] = self.email_account.email_address
        message['To'] = ', '.join(to_addresses)
        message['Subject'] = subject
        
        if cc_addresses:
            message['Cc'] = ', '.join(cc_addresses)
        
        message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                self._add_attachment(message, attachment)
        
        try:
            server = smtplib.SMTP(
                self.email_account.smtp_server,
                self.email_account.smtp_port
            )
            
            if self.email_account.use_ssl:
                server.starttls()
            
            server.login(
                self.email_account.email_address,
                self.email_account.access_token  # Password stored in access_token for IMAP/SMTP
            )
            
            all_recipients = to_addresses + (cc_addresses or [])
            server.send_message(message, to_addrs=all_recipients)
            server.quit()
            
            return message.get('Message-ID', 'unknown')
            
        except Exception as e:
            raise EmailServiceError(f"SMTP send error: {str(e)}")
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict):
        """Add attachment to email message"""
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(base64.b64decode(attachment['content_base64']))
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {attachment["name"]}'
        )
        message.attach(part)
    
    # =============================================================================
    # CLIENT MATCHING METHODS
    # =============================================================================
    
    def match_email_to_client_or_lead(self, email_data: Dict) -> Tuple[Optional[Client], Optional[Lead]]:
        """
        Match an email to a client or lead based on email addresses
        Returns (client, lead) tuple - one will be None
        """
        from_address = email_data.get('from_address', '')
        to_addresses = email_data.get('to_addresses', [])
        cc_addresses = email_data.get('cc_addresses', [])
        
        # Collect all email addresses from the email
        all_addresses = [from_address] + to_addresses + cc_addresses
        all_addresses = [addr.lower().strip() for addr in all_addresses if addr]
        
        # Remove the advisor's own email
        all_addresses = [addr for addr in all_addresses if addr != self.email_account.email_address.lower()]
        
        # Try to match with existing clients first
        for address in all_addresses:
            client = Client.objects.filter(
                advisor=self.user,
                email__iexact=address,
                is_deleted=False
            ).first()
            if client:
                return client, None
        
        # Try to match with leads
        for address in all_addresses:
            lead = Lead.objects.filter(
                advisor=self.user,
                email__iexact=address
            ).first()
            if lead:
                return None, lead
        
        return None, None
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _parse_email_address(self, email_str: str) -> str:
        """Parse email address from string"""
        if not email_str:
            return ""
        
        parsed = parseaddr(email_str)
        return parsed[1] if parsed[1] else ""
    
    def _parse_email_addresses(self, email_str: str) -> List[str]:
        """Parse multiple email addresses from string"""
        if not email_str:
            return []
        
        addresses = []
        for addr in email_str.split(','):
            parsed = parseaddr(addr.strip())
            if parsed[1]:
                addresses.append(parsed[1])
        
        return addresses
    
    def _parse_gmail_date(self, date_str: str) -> Optional[datetime]:
        """Parse Gmail date string"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return None
    
    def _parse_outlook_date(self, date_str: str) -> Optional[datetime]:
        """Parse Outlook ISO date string"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _parse_email_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return None
    
    # =============================================================================
    # SYNC METHODS
    # =============================================================================
    
    def sync_emails_to_crm(self, limit: int = 100) -> Dict[str, int]:
        """
        Sync emails from provider to CRM
        Returns stats about sync operation
        """
        stats = {
            'fetched': 0,
            'created': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            # Determine since date for incremental sync
            since_date = self.email_account.last_sync_at
            if not since_date:
                # Initial sync - get emails from last 30 days
                since_date = timezone.now() - timedelta(days=30)
            
            # Fetch emails from provider
            emails = self.fetch_emails(limit=limit, since_date=since_date)
            stats['fetched'] = len(emails)
            
            for email_data in emails:
                try:
                    # Check if email already exists
                    existing_comm = Communication.objects.filter(
                        advisor=self.user,
                        provider_message_id=email_data['provider_message_id']
                    ).first()
                    
                    if existing_comm:
                        # Update existing communication
                        self._update_communication(existing_comm, email_data)
                        stats['updated'] += 1
                    else:
                        # Create new communication
                        self._create_communication_from_email(email_data)
                        stats['created'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to sync email {email_data.get('provider_message_id')}: {str(e)}")
                    stats['errors'] += 1
            
            # Update last sync time
            self.email_account.last_sync_at = timezone.now()
            self.email_account.save(update_fields=['last_sync_at'])
            
        except Exception as e:
            logger.error(f"Email sync failed: {str(e)}")
            raise SyncError(f"Email sync failed: {str(e)}")
        
        return stats
    
    def _create_communication_from_email(self, email_data: Dict):
        """Create Communication record from email data"""
        client, lead = self.match_email_to_client_or_lead(email_data)
        
        # Determine direction based on from address
        direction = 'outbound' if email_data['from_address'].lower() == self.email_account.email_address.lower() else 'inbound'
        
        Communication.objects.create(
            advisor=self.user,
            client=client,
            lead=lead,
            communication_type='email',
            direction=direction,
            subject=email_data.get('subject', ''),
            content=email_data.get('content', ''),
            email_account=self.email_account,
            provider_message_id=email_data.get('provider_message_id', ''),
            message_id_header=email_data.get('message_id_header', ''),
            thread_id=email_data.get('thread_id', ''),
            in_reply_to=email_data.get('in_reply_to', ''),
            from_address=email_data.get('from_address', ''),
            to_addresses=email_data.get('to_addresses', []),
            cc_addresses=email_data.get('cc_addresses', []),
            bcc_addresses=email_data.get('bcc_addresses', []),
            is_read=email_data.get('is_read', False),
            sent_at=email_data.get('sent_at'),
            sync_status='synced',
            sync_direction='from_email'
        )
    
    def _update_communication(self, communication: Communication, email_data: Dict):
        """Update existing Communication record with email data"""
        communication.is_read = email_data.get('is_read', communication.is_read)
        communication.sync_status = 'synced'
        communication.save(update_fields=['is_read', 'sync_status', 'updated_at'])


class EmailSyncManager:
    """
    Manager class for coordinating email sync across multiple accounts
    """
    
    @staticmethod
    def sync_all_accounts(user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Sync all active email accounts
        If user_id provided, sync only that user's accounts
        """
        accounts_filter = EmailAccount.objects.filter(is_active=True, sync_enabled=True)
        if user_id:
            accounts_filter = accounts_filter.filter(user_id=user_id)
        
        results = {
            'accounts_processed': 0,
            'total_fetched': 0,
            'total_created': 0,
            'total_updated': 0,
            'total_errors': 0,
            'account_results': []
        }
        
        for account in accounts_filter:
            try:
                service = EmailService(account)
                stats = service.sync_emails_to_crm()
                
                account_result = {
                    'account': account.email_address,
                    'success': True,
                    **stats
                }
                
                results['total_fetched'] += stats['fetched']
                results['total_created'] += stats['created']
                results['total_updated'] += stats['updated']
                results['total_errors'] += stats['errors']
                
            except Exception as e:
                logger.error(f"Failed to sync account {account.email_address}: {str(e)}")
                account_result = {
                    'account': account.email_address,
                    'success': False,
                    'error': str(e)
                }
                results['total_errors'] += 1
            
            results['account_results'].append(account_result)
            results['accounts_processed'] += 1
        
        return results