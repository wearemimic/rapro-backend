"""
Access Control Security Module
Provides comprehensive access control validation
"""

import logging
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class AccessControlValidator:
    """
    Service to validate access control for resources
    """

    @staticmethod
    def validate_ownership(user, resource, owner_field='advisor'):
        """
        Validate that a user owns a resource

        Args:
            user: User making the request
            resource: Resource being accessed
            owner_field: Field name that contains the owner

        Returns:
            bool: True if user owns resource

        Raises:
            PermissionDenied: If user doesn't own resource
        """
        owner = getattr(resource, owner_field, None)

        # Handle different owner field types
        if hasattr(owner, 'id'):
            owner_id = owner.id
        else:
            owner_id = owner

        if owner_id != user.id:
            logger.warning(f"User {user.id} attempted to access resource owned by {owner_id}")
            raise PermissionDenied("You don't have permission to access this resource")

        return True

    @staticmethod
    def validate_client_access(user, client):
        """
        Validate that a user can access a specific client

        Args:
            user: User making the request
            client: Client being accessed

        Returns:
            bool: True if access allowed

        Raises:
            PermissionDenied: If access denied
        """
        # Check if user is the advisor for this client
        if client.advisor_id != user.id:
            # Check if user is an admin with appropriate permissions
            if not (hasattr(user, 'is_admin_user') and user.is_admin_user):
                logger.warning(f"User {user.id} attempted to access client {client.id} owned by {client.advisor_id}")
                raise PermissionDenied("You don't have permission to access this client")

        return True

    @staticmethod
    def validate_scenario_access(user, scenario):
        """
        Validate that a user can access a specific scenario

        Args:
            user: User making the request
            scenario: Scenario being accessed

        Returns:
            bool: True if access allowed

        Raises:
            PermissionDenied: If access denied
        """
        # Check through client relationship
        if scenario.client and scenario.client.advisor_id != user.id:
            if not (hasattr(user, 'is_admin_user') and user.is_admin_user):
                logger.warning(f"User {user.id} attempted to access scenario {scenario.id}")
                raise PermissionDenied("You don't have permission to access this scenario")

        return True

    @staticmethod
    def filter_queryset_by_ownership(queryset, user, owner_field='advisor'):
        """
        Filter a queryset to only include resources owned by the user

        Args:
            queryset: Django queryset
            user: User making the request
            owner_field: Field name that contains the owner

        Returns:
            Filtered queryset
        """
        # Build filter condition
        filter_kwargs = {owner_field: user}

        # Apply filter
        return queryset.filter(**filter_kwargs)

    @staticmethod
    def check_horizontal_access(user, target_user_id):
        """
        Check for horizontal privilege escalation attempts

        Args:
            user: User making the request
            target_user_id: ID of user being accessed

        Returns:
            bool: True if access allowed

        Raises:
            PermissionDenied: If horizontal access attempted
        """
        if user.id != target_user_id:
            # Check if user is admin
            if not (hasattr(user, 'is_admin_user') and user.is_admin_user):
                logger.warning(f"Horizontal access attempt: User {user.id} tried to access user {target_user_id}")
                raise PermissionDenied("You can only access your own data")

        return True

    @staticmethod
    def check_vertical_access(user, required_role):
        """
        Check for vertical privilege escalation attempts

        Args:
            user: User making the request
            required_role: Required role for access

        Returns:
            bool: True if access allowed

        Raises:
            PermissionDenied: If insufficient privileges
        """
        user_role = getattr(user, 'admin_role', None)

        # Define role hierarchy
        role_hierarchy = {
            'super_admin': 3,
            'admin': 2,
            'support': 1,
            None: 0
        }

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        if user_level < required_level:
            logger.warning(f"Vertical access attempt: User {user.id} with role {user_role} tried to access {required_role} resource")
            raise PermissionDenied(f"This action requires {required_role} privileges")

        return True


def require_ownership(owner_field='advisor'):
    """
    Decorator to require ownership of a resource

    Args:
        owner_field: Field name that contains the owner
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Get the resource
            if hasattr(self, 'get_object'):
                resource = self.get_object()
                AccessControlValidator.validate_ownership(request.user, resource, owner_field)

            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_client_access():
    """
    Decorator to require access to a client
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Get client from kwargs or request
            client_id = kwargs.get('client_id') or request.data.get('client_id')

            if client_id:
                from .models import Client
                try:
                    client = Client.objects.get(id=client_id)
                    AccessControlValidator.validate_client_access(request.user, client)
                except Client.DoesNotExist:
                    return Response(
                        {'error': 'Client not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_admin_role(required_role='admin'):
    """
    Decorator to require admin role

    Args:
        required_role: Minimum required admin role
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            AccessControlValidator.check_vertical_access(request.user, required_role)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


class SecureQuerysetMixin:
    """
    Mixin to automatically filter querysets by ownership
    """

    owner_field = 'advisor'  # Override in subclass if different

    def get_queryset(self):
        """
        Filter queryset to only show owned resources
        """
        queryset = super().get_queryset()

        # Skip filtering for admins
        if hasattr(self.request.user, 'is_admin_user') and self.request.user.is_admin_user:
            return queryset

        # Filter by ownership
        return AccessControlValidator.filter_queryset_by_ownership(
            queryset,
            self.request.user,
            self.owner_field
        )


class DataScopeValidator:
    """
    Validate data scope for multi-tenant access
    """

    @staticmethod
    def validate_data_scope(user, data, scope_field='advisor_id'):
        """
        Validate that data belongs to user's scope

        Args:
            user: User making the request
            data: Data dictionary
            scope_field: Field that defines scope

        Returns:
            bool: True if in scope

        Raises:
            PermissionDenied: If out of scope
        """
        scope_value = data.get(scope_field)

        if scope_value and scope_value != user.id:
            # Check admin override
            if not (hasattr(user, 'is_admin_user') and user.is_admin_user):
                logger.warning(f"Data scope violation: User {user.id} tried to access data with {scope_field}={scope_value}")
                raise PermissionDenied("Data is outside your access scope")

        return True

    @staticmethod
    def enforce_data_isolation(queryset, user, isolation_field='advisor'):
        """
        Enforce complete data isolation between users

        Args:
            queryset: Base queryset
            user: User making request
            isolation_field: Field for isolation

        Returns:
            Isolated queryset
        """
        # Build isolation filter
        isolation_filter = Q(**{isolation_field: user})

        # Add public data if applicable
        if hasattr(queryset.model, 'is_public'):
            isolation_filter |= Q(is_public=True)

        return queryset.filter(isolation_filter)