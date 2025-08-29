"""
Client Portal API Views

This module provides API endpoints specifically for client portal functionality,
including authentication, data access, and client-specific operations.
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Client, Scenario, Document
from .authentication import (
    ClientPortalBackend, 
    ClientInvitationManager, 
    ClientSessionManager,
    ClientPortalSecurity
)
from .serializers_main import ScenarioSummarySerializer


class ClientPortalAuthView(APIView):
    """
    Handle client portal authentication
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Authenticate client using email and invitation token
        """
        email = request.data.get('email')
        token = request.data.get('token')
        
        if not email or not token:
            return Response({
                'error': 'Email and token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate using custom backend
        backend = ClientPortalBackend()
        user = backend.authenticate(request, email=email, token=token)
        
        if not user:
            return Response({
                'error': 'Invalid credentials or expired invitation'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get client
        try:
            client = Client.objects.get(portal_user=user)
        except Client.DoesNotExist:
            return Response({
                'error': 'Client not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create session
        session_data = ClientSessionManager.create_client_session(client, request)
        
        # Log activity
        ClientPortalSecurity.log_client_activity(
            client, 
            'login', 
            request
        )
        
        return Response({
            'success': True,
            'session': session_data,
            'client': {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email
            }
        }, status=status.HTTP_200_OK)


class ClientPortalPasswordSetupView(APIView):
    """
    Handle client password setup after invitation
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Set up client portal password
        """
        email = request.data.get('email')
        token = request.data.get('token')
        password = request.data.get('password')
        
        if not all([email, token, password]):
            return Response({
                'error': 'Email, token, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = Client.objects.get(
                email=email,
                portal_access_enabled=True,
                portal_invitation_token=token
            )
            
            # Validate invitation is not expired
            if client.portal_invitation_sent_at:
                from datetime import timedelta
                token_age = timezone.now() - client.portal_invitation_sent_at
                if token_age > timedelta(hours=24):
                    return Response({
                        'error': 'Invitation has expired'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Activate client portal access
            portal_user = ClientInvitationManager.activate_client_portal_access(
                client, 
                password=password
            )
            
            # Clear invitation token after successful setup
            client.portal_invitation_token = None
            client.save()
            
            # Create session
            session_data = ClientSessionManager.create_client_session(client, request)
            
            return Response({
                'success': True,
                'message': 'Portal access activated successfully',
                'session': session_data
            }, status=status.HTTP_200_OK)
            
        except Client.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ClientPortalDashboardView(APIView):
    """
    Client portal dashboard data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get client portal dashboard data
        """
        try:
            client = Client.objects.get(portal_user=request.user)
        except Client.DoesNotExist:
            return Response({
                'error': 'Client not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get shared scenarios
        shared_scenarios = Scenario.objects.filter(
            client=client,
            share_with_client=True
        ).order_by('-updated_at')
        
        # Get shared documents
        shared_documents = Document.objects.filter(
            client=client,
            is_client_visible=True
        ).order_by('-created_at')
        
        return Response({
            'client': {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email
            },
            'advisor': {
                'first_name': client.advisor.first_name,
                'last_name': client.advisor.last_name,
                'email': client.advisor.email
            },
            'shared_scenarios': ScenarioSummarySerializer(shared_scenarios, many=True).data,
            'shared_documents': [{
                'id': doc.id,
                'title': doc.title,
                'file_name': doc.file_name,
                'file_size': doc.file_size,
                'content_type': doc.content_type,
                'uploaded_at': doc.uploaded_at,
                'category': doc.category.name if doc.category else None
            } for doc in shared_documents],
            'last_login': client.portal_last_login,
            'stats': {
                'shared_scenarios_count': shared_scenarios.count(),
                'shared_documents_count': shared_documents.count()
            }
        })


class ClientPortalScenariosView(APIView):
    """
    Client portal scenarios access
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, scenario_id=None):
        """
        Get shared scenarios for client
        """
        try:
            client = Client.objects.get(portal_user=request.user)
        except Client.DoesNotExist:
            return Response({
                'error': 'Client not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if scenario_id:
            # Get specific scenario
            scenario = get_object_or_404(
                Scenario,
                id=scenario_id,
                client=client,
                share_with_client=True
            )
            
            # Log access
            ClientPortalSecurity.log_client_activity(
                client, 
                f'viewed_scenario_{scenario_id}', 
                request
            )
            
            return Response({
                'scenario': ScenarioSummarySerializer(scenario).data
            })
        else:
            # Get all shared scenarios
            scenarios = Scenario.objects.filter(
                client=client,
                share_with_client=True
            ).order_by('-updated_at')
            
            return Response({
                'scenarios': ScenarioSummarySerializer(scenarios, many=True).data,
                'count': scenarios.count()
            })


class ClientPortalDocumentsView(APIView):
    """
    Client portal document access
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, document_id=None):
        """
        Get shared documents for client
        """
        try:
            client = Client.objects.get(portal_user=request.user)
        except Client.DoesNotExist:
            return Response({
                'error': 'Client not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if document_id:
            # Get specific document
            document = get_object_or_404(
                Document,
                id=document_id,
                client=client,
                is_client_visible=True
            )
            
            # Log access
            ClientPortalSecurity.log_client_activity(
                client, 
                f'viewed_document_{document_id}', 
                request
            )
            
            return Response({
                'document': {
                    'id': document.id,
                    'title': document.title,
                    'file_name': document.file_name,
                    'file_size': document.file_size,
                    'content_type': document.content_type,
                    'uploaded_at': document.uploaded_at,
                    'category': document.category.name if document.category else None,
                    'download_url': f'/api/client-portal/documents/{document.id}/download/'
                }
            })
        else:
            # Get all shared documents
            documents = Document.objects.filter(
                client=client,
                is_client_visible=True
            ).order_by('-uploaded_at')
            
            return Response({
                'documents': [{
                    'id': doc.id,
                    'title': doc.title,
                    'file_name': doc.file_name,
                    'file_size': doc.file_size,
                    'content_type': doc.content_type,
                    'uploaded_at': doc.uploaded_at,
                    'category': doc.category.name if doc.category else None
                } for doc in documents],
                'count': documents.count()
            })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def client_portal_logout(request):
    """
    Log out client from portal
    """
    try:
        client = Client.objects.get(portal_user=request.user)
        ClientSessionManager.terminate_client_session(client)
        
        # Log activity
        ClientPortalSecurity.log_client_activity(
            client, 
            'logout', 
            request
        )
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Client.DoesNotExist:
        return Response({
            'error': 'Client not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def client_portal_session_validate(request):
    """
    Validate client portal session
    """
    try:
        client = Client.objects.get(portal_user=request.user)
        
        if not client.portal_access_enabled:
            return Response({
                'valid': False,
                'error': 'Portal access disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'valid': True,
            'client': {
                'id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email
            }
        })
    except Client.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Client not found'
        }, status=status.HTTP_404_NOT_FOUND)


# Advisor-side client portal management endpoints

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enable_client_portal_access(request, client_id):
    """
    Enable portal access for a client (advisor endpoint)
    """
    try:
        client = get_object_or_404(Client, id=client_id, advisor=request.user)
        
        with transaction.atomic():
            client.portal_access_enabled = True
            client.save()
        
        return Response({
            'success': True,
            'message': 'Portal access enabled successfully',
            'client': {
                'id': client.id,
                'portal_access_enabled': client.portal_access_enabled
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_client_portal_access(request, client_id):
    """
    Revoke portal access for a client (advisor endpoint)
    """
    try:
        client = get_object_or_404(Client, id=client_id, advisor=request.user)
        
        ClientInvitationManager.revoke_portal_access(client)
        
        return Response({
            'success': True,
            'message': 'Portal access revoked successfully',
            'client': {
                'id': client.id,
                'portal_access_enabled': client.portal_access_enabled
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_client_portal_invitation(request, client_id):
    """
    Send portal invitation to client (advisor endpoint)
    """
    try:
        client = get_object_or_404(Client, id=client_id, advisor=request.user)
        
        invitation_url = ClientInvitationManager.send_portal_invitation(client)
        
        return Response({
            'success': True,
            'message': 'Invitation sent successfully',
            'client': {
                'id': client.id,
                'portal_invitation_sent_at': client.portal_invitation_sent_at,
                'invitation_url': invitation_url
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)