"""
Admin views for managing NSSA/Kajabi users and subscriptions.
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import logging

from .kajabi_api import kajabi_client

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAdminUser])
def verify_kajabi_subscription(request, user_id):
    """
    Admin endpoint to verify a user's Kajabi subscription status.
    Checks the current status in Kajabi and compares with database.

    Returns comparison data and recommended actions.
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)

        # Check if user is from Kajabi/NSSA
        if user.auth_provider != 'kajabi':
            return Response({
                'error': 'This user is not a Kajabi/NSSA user',
                'user': {
                    'email': user.email,
                    'auth_provider': user.auth_provider
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get Kajabi member ID from metadata
        kajabi_member_id = user.metadata.get('kajabi_member_id') if user.metadata else None

        if not kajabi_member_id:
            return Response({
                'error': 'No Kajabi member ID found in user metadata',
                'user': {
                    'email': user.email,
                    'metadata': user.metadata
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify subscription status with Kajabi API
        kajabi_status = kajabi_client.verify_subscription_status(kajabi_member_id)

        # Compare with database
        db_status = {
            'subscription_status': user.subscription_status,
            'subscription_plan': user.subscription_plan,
            'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
            'is_active': user.is_active,
        }

        # Determine if there's a mismatch
        mismatch = False
        recommended_action = None

        if kajabi_status['is_active'] and user.subscription_status != 'active':
            mismatch = True
            recommended_action = 'Update database to mark subscription as active'
        elif not kajabi_status['is_active'] and user.subscription_status == 'active':
            mismatch = True
            recommended_action = f"Update database to mark subscription as {kajabi_status['subscription_status']}"

        response_data = {
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'partner': user.metadata.get('partner') if user.metadata else None,
                'kajabi_member_id': kajabi_member_id,
            },
            'database_status': db_status,
            'kajabi_status': {
                'is_active': kajabi_status['is_active'],
                'status': kajabi_status['subscription_status'],
                'subscriptions': kajabi_status['subscriptions'],
                'error': kajabi_status.get('error'),
            },
            'mismatch': mismatch,
            'recommended_action': recommended_action,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({
            'error': f'User with ID {user_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error verifying Kajabi subscription: {str(e)}", exc_info=True)
        return Response({
            'error': 'An error occurred while verifying subscription',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_nssa_users(request):
    """
    Admin endpoint to list all NSSA/Kajabi users.
    Supports filtering and pagination.
    """
    try:
        # Get all users with partner=NSSA
        nssa_users = User.objects.filter(
            metadata__partner='NSSA'
        ).order_by('-date_joined')

        # Apply filters
        subscription_status = request.query_params.get('subscription_status')
        if subscription_status:
            nssa_users = nssa_users.filter(subscription_status=subscription_status)

        is_active = request.query_params.get('is_active')
        if is_active is not None:
            nssa_users = nssa_users.filter(is_active=is_active.lower() == 'true')

        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size

        total_count = nssa_users.count()
        users_page = nssa_users[start:end]

        # Serialize user data
        users_data = []
        for user in users_page:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'is_active': user.is_active,
                'subscription_status': user.subscription_status,
                'subscription_plan': user.subscription_plan,
                'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                'kajabi_member_id': user.metadata.get('kajabi_member_id') if user.metadata else None,
                'signup_date': user.metadata.get('signup_date') if user.metadata else None,
            })

        return Response({
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'users': users_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error listing NSSA users: {str(e)}", exc_info=True)
        return Response({
            'error': 'An error occurred while listing users',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def sync_kajabi_subscription(request, user_id):
    """
    Admin endpoint to sync a user's subscription status from Kajabi to database.
    Updates the database to match Kajabi's current status.
    """
    try:
        user = User.objects.get(id=user_id)

        if user.auth_provider != 'kajabi':
            return Response({
                'error': 'This user is not a Kajabi/NSSA user'
            }, status=status.HTTP_400_BAD_REQUEST)

        kajabi_member_id = user.metadata.get('kajabi_member_id') if user.metadata else None

        if not kajabi_member_id:
            return Response({
                'error': 'No Kajabi member ID found'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get current status from Kajabi
        kajabi_status = kajabi_client.verify_subscription_status(kajabi_member_id)

        if kajabi_status.get('error'):
            return Response({
                'error': f"Failed to fetch Kajabi data: {kajabi_status['error']}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update database to match Kajabi
        old_status = user.subscription_status
        user.subscription_status = kajabi_status['subscription_status']

        if kajabi_status['is_active']:
            user.is_active = True
        elif kajabi_status['subscription_status'] in ['canceled', 'expired']:
            # Keep is_active if subscription is just canceled but not expired
            if kajabi_status['subscription_status'] == 'expired':
                user.is_active = False

        user.save()

        logger.info(f"Synced Kajabi subscription for {user.email}: {old_status} → {user.subscription_status}")

        return Response({
            'success': True,
            'message': 'Subscription status synced successfully',
            'old_status': old_status,
            'new_status': user.subscription_status,
            'is_active': user.is_active,
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({
            'error': f'User with ID {user_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error syncing Kajabi subscription: {str(e)}", exc_info=True)
        return Response({
            'error': 'An error occurred while syncing subscription',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
