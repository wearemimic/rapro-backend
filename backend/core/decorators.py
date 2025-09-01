"""
Admin Authentication Decorators

This module provides decorators for protecting admin-only API endpoints
and enforcing role-based access control.
"""

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdminUser(BasePermission):
    """
    Permission class to check if user is an admin user
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin_user


class HasAdminRole(BasePermission):
    """
    Permission class to check if user has specific admin role
    """
    
    def __init__(self, required_roles=None):
        self.required_roles = required_roles or []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_admin_user:
            return False
        
        if request.user.admin_role == 'super_admin':
            return True
        
        return request.user.admin_role in self.required_roles


class CanAccessAdminSection(BasePermission):
    """
    Permission class to check if user can access specific admin section
    """
    
    def __init__(self, section):
        self.section = section
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.can_access_admin_section(self.section)


def admin_required(roles=None, section=None, permission=None):
    """
    Decorator to require admin access for function-based views
    
    Args:
        roles: List of required admin roles (optional)
        section: Admin section to check access for (optional)
        permission: Specific permission to check (optional)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=401
                )
            
            # Check if user has admin privileges
            if not request.user.is_admin_user:
                return JsonResponse(
                    {'error': 'Admin access required'}, 
                    status=403
                )
            
            # Check specific role requirements
            if roles:
                if request.user.admin_role == 'super_admin':
                    # Super admin can access everything
                    pass
                elif request.user.admin_role not in roles:
                    return JsonResponse(
                        {'error': f'Access denied. Required roles: {roles}'}, 
                        status=403
                    )
            
            # Check section access
            if section:
                if not request.user.can_access_admin_section(section):
                    return JsonResponse(
                        {'error': f'Access denied to {section} section'}, 
                        status=403
                    )
            
            # Check specific permission
            if permission:
                if not request.user.has_admin_permission(permission):
                    return JsonResponse(
                        {'error': f'Permission denied: {permission}'}, 
                        status=403
                    )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def super_admin_required(view_func):
    """
    Decorator that requires super admin role
    """
    return admin_required(roles=['super_admin'])(view_func)


def admin_or_support_required(view_func):
    """
    Decorator that requires admin or support role
    """
    return admin_required(roles=['admin', 'support'])(view_func)


def billing_admin_required(view_func):
    """
    Decorator that requires admin or billing role
    """
    return admin_required(roles=['admin', 'billing'])(view_func)


def user_management_access_required(view_func):
    """
    Decorator that requires access to user management section
    """
    return admin_required(section='user_management')(view_func)


def billing_access_required(view_func):
    """
    Decorator that requires access to billing section
    """
    return admin_required(section='billing')(view_func)


def analytics_access_required(view_func):
    """
    Decorator that requires access to analytics section
    """
    return admin_required(section='analytics')(view_func)


# DRF ViewSet Mixin for admin access
class AdminRequiredMixin:
    """
    Mixin for DRF ViewSets that require admin access
    """
    
    def get_permissions(self):
        """
        Override to add admin permission check
        """
        permissions = super().get_permissions()
        permissions.append(IsAdminUser())
        return permissions


class AdminRoleMixin:
    """
    Mixin for DRF ViewSets that require specific admin roles
    """
    admin_roles = []  # Override this in your ViewSet
    
    def get_permissions(self):
        """
        Override to add role-based permission check
        """
        permissions = super().get_permissions()
        if hasattr(self, 'admin_roles') and self.admin_roles:
            permissions.append(HasAdminRole(self.admin_roles))
        return permissions


class AdminSectionMixin:
    """
    Mixin for DRF ViewSets that require access to specific admin section
    """
    admin_section = None  # Override this in your ViewSet
    
    def get_permissions(self):
        """
        Override to add section access permission check
        """
        permissions = super().get_permissions()
        if hasattr(self, 'admin_section') and self.admin_section:
            permissions.append(CanAccessAdminSection(self.admin_section))
        return permissions


# Utility functions for checking admin permissions
def check_admin_permission(user, permission_key):
    """
    Check if user has specific admin permission
    """
    if not user.is_authenticated or not user.is_admin_user:
        return False
    
    return user.has_admin_permission(permission_key)


def check_admin_section_access(user, section):
    """
    Check if user can access specific admin section
    """
    if not user.is_authenticated or not user.is_admin_user:
        return False
    
    return user.can_access_admin_section(section)


def get_user_admin_permissions(user):
    """
    Get list of admin sections user can access
    """
    if not user.is_authenticated or not user.is_admin_user:
        return []
    
    sections = ['user_management', 'billing', 'analytics', 'system_monitoring', 'support_tools']
    accessible_sections = []
    
    for section in sections:
        if user.can_access_admin_section(section):
            accessible_sections.append(section)
    
    return accessible_sections


# Custom exception for admin access denied
class AdminAccessDenied(Exception):
    """Exception raised when admin access is denied"""
    
    def __init__(self, message="Admin access required", required_role=None, required_section=None):
        self.message = message
        self.required_role = required_role
        self.required_section = required_section
        super().__init__(self.message)