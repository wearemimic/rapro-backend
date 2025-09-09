# permissions.py
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access certain views.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is an admin"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is Django staff or has platform admin flag
        return (
            request.user.is_staff or 
            getattr(request.user, 'is_platform_admin', False) or
            getattr(request.user, 'admin_role', None) is not None
        )
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        return self.has_permission(request, view)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to view/edit it.
    """
    
    def has_permission(self, request, view):
        """Allow authenticated users"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user owns the object or is admin"""
        # Admin users have full access
        if request.user.is_staff or getattr(request.user, 'is_platform_admin', False):
            return True
        
        # Check if object has a user field and matches current user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object has an owner field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # For affiliate objects, check if user has affiliate account
        if hasattr(obj, 'affiliate'):
            try:
                from .affiliate_models import Affiliate
                user_affiliate = Affiliate.objects.get(user=request.user)
                return obj.affiliate == user_affiliate
            except:
                return False
        
        return False


class IsAffiliateOrAdmin(permissions.BasePermission):
    """
    Custom permission for affiliate-specific views.
    Allows access to users who have an affiliate account or are admins.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has affiliate account or is admin"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users have full access
        if request.user.is_staff or getattr(request.user, 'is_platform_admin', False):
            return True
        
        # Check if user has an affiliate account
        try:
            from .affiliate_models import Affiliate
            Affiliate.objects.get(user=request.user, status='active')
            return True
        except:
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for affiliates"""
        # Admin users have full access
        if request.user.is_staff or getattr(request.user, 'is_platform_admin', False):
            return True
        
        # Check if user's affiliate account matches the object
        try:
            from .affiliate_models import Affiliate
            user_affiliate = Affiliate.objects.get(user=request.user)
            
            # If object is an Affiliate, check if it's the user's own
            if hasattr(obj, 'id') and isinstance(obj, Affiliate):
                return obj == user_affiliate
            
            # If object has affiliate field, check if it matches
            if hasattr(obj, 'affiliate'):
                return obj.affiliate == user_affiliate
            
        except:
            return False
        
        return False