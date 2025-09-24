"""
Report Center Permission Classes
Custom permissions for report center functionality with advisor-only access
"""

from rest_framework import permissions
from django.contrib.auth import get_user_model
from core.models import Client

User = get_user_model()


class IsAdvisorUser(permissions.BasePermission):
    """
    Permission to only allow advisor users (not client portal users) to access views.
    Denies access to client portal users who are created for client access.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if this user is a client portal user
        try:
            client = Client.objects.get(portal_user=request.user)
            # If we found a client record with this user as portal_user, deny access
            return False
        except Client.DoesNotExist:
            # User is not a client portal user, allow access for advisors
            return True


class IsActiveSubscriptionUser(permissions.BasePermission):
    """
    Permission to only allow users with active subscriptions to access views.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has an active subscription
        return getattr(request.user, 'is_subscription_active', False)


class IsAdvisorWithActiveSubscription(permissions.BasePermission):
    """
    Combined permission: must be advisor user with active subscription
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if this user is a client portal user
        try:
            client = Client.objects.get(portal_user=request.user)
            # If we found a client record with this user as portal_user, deny access
            return False
        except Client.DoesNotExist:
            pass
        
        # Check if user has an active subscription
        return getattr(request.user, 'is_subscription_active', False)


class CanAccessReportCenter(permissions.BasePermission):
    """
    Main permission class for Report Center access.
    Requires user to be:
    1. Authenticated
    2. Not a client portal user
    3. Have active subscription
    4. Have report center access enabled (if implemented)
    """
    
    message = "Report Center access requires an active advisor subscription."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            self.message = "Authentication required."
            return False
        
        # Check if this user is a client portal user
        try:
            client = Client.objects.get(portal_user=request.user)
            # If we found a client record with this user as portal_user, deny access
            self.message = "Client portal users cannot access Report Center."
            return False
        except Client.DoesNotExist:
            pass
        
        # Check if user has an active subscription
        if not getattr(request.user, 'is_subscription_active', False):
            self.message = "Report Center access requires an active subscription."
            return False
        
        # Future: Check for specific report center feature flag
        # if not getattr(request.user, 'has_report_center_access', True):
        #     self.message = "Report Center access not enabled for your account."
        #     return False
        
        return True


class CanManageReportTemplates(CanAccessReportCenter):
    """
    Permission for managing report templates.
    Extends base Report Center access with template management rights.
    """
    
    message = "Template management requires Report Center access and appropriate permissions."
    
    def has_permission(self, request, view):
        # First check base Report Center access
        if not super().has_permission(request, view):
            return False
        
        # Additional checks for template management could go here
        # For now, all Report Center users can manage templates
        
        return True


class CanGenerateReports(CanAccessReportCenter):
    """
    Permission for generating reports.
    Could include usage limits or tier-based restrictions.
    """
    
    message = "Report generation requires Report Center access."
    
    def has_permission(self, request, view):
        # First check base Report Center access
        if not super().has_permission(request, view):
            return False
        
        # Future: Check for generation limits based on subscription tier
        # monthly_limit = getattr(request.user, 'monthly_report_limit', 50)
        # current_month_usage = get_user_monthly_report_count(request.user)
        # if current_month_usage >= monthly_limit:
        #     self.message = f"Monthly report generation limit ({monthly_limit}) reached."
        #     return False
        
        return True


class CanShareReports(CanAccessReportCenter):
    """
    Permission for sharing reports with clients or external users.
    """
    
    message = "Report sharing requires Report Center access and sharing permissions."
    
    def has_permission(self, request, view):
        # First check base Report Center access
        if not super().has_permission(request, view):
            return False
        
        # Future: Check for sharing feature based on subscription tier
        # if not getattr(request.user, 'can_share_reports', True):
        #     self.message = "Report sharing not available in your subscription plan."
        #     return False
        
        return True


class IsReportOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of a report to edit it.
    Others get read-only access if they have basic Report Center access.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed if user has Report Center access
        if request.method in permissions.SAFE_METHODS:
            return CanAccessReportCenter().has_permission(request, view)
        
        # Write permissions are only allowed to the owner of the report
        return obj.created_by == request.user


class IsTemplateOwnerOrPublic(permissions.BasePermission):
    """
    Object-level permission for report templates:
    - Owners can always access their templates
    - Others can only access public templates
    """
    
    def has_object_permission(self, request, view, obj):
        # Always allow access to public templates
        if obj.is_public:
            return True
        
        # Only allow access to private templates by their owner
        return obj.created_by == request.user


# Utility functions for permission checking

def get_user_monthly_report_count(user):
    """
    Get the number of reports generated by user in current month.
    Used for usage limits.
    """
    from django.utils import timezone
    from .models import Report
    
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    return Report.objects.filter(
        created_by=user,
        created_at__gte=current_month_start,
        status='completed'
    ).count()


def check_user_subscription_features(user):
    """
    Check what Report Center features are available based on user's subscription.
    Returns a dict of feature flags.
    """
    features = {
        'basic_reports': False,
        'advanced_templates': False,
        'batch_generation': False,
        'report_sharing': False,
        'custom_branding': False,
        'api_access': False,
    }
    
    if not user.is_authenticated:
        return features
    
    subscription_plan = getattr(user, 'subscription_plan', '')
    
    if subscription_plan in ['basic', 'professional', 'enterprise']:
        features['basic_reports'] = True
        features['report_sharing'] = True
    
    if subscription_plan in ['professional', 'enterprise']:
        features['advanced_templates'] = True
        features['batch_generation'] = True
        features['api_access'] = True
    
    if subscription_plan == 'enterprise':
        features['custom_branding'] = True
    
    return features


def get_user_report_limits(user):
    """
    Get user's report generation limits based on subscription tier.
    """
    subscription_plan = getattr(user, 'subscription_plan', '')
    
    limits = {
        'monthly_reports': 10,
        'concurrent_generations': 1,
        'template_count': 5,
        'storage_mb': 100,
    }
    
    if subscription_plan == 'professional':
        limits.update({
            'monthly_reports': 50,
            'concurrent_generations': 3,
            'template_count': 25,
            'storage_mb': 500,
        })
    elif subscription_plan == 'enterprise':
        limits.update({
            'monthly_reports': 500,
            'concurrent_generations': 10,
            'template_count': 100,
            'storage_mb': 2000,
        })
    
    return limits