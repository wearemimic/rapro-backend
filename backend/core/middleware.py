from django.http import JsonResponse
from django.urls import resolve
from django.conf import settings

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require subscription check
        self.public_urls = [
            'login',
            'register_advisor',
            'complete_registration',
            'token_obtain_pair',
            'token_refresh',
            'stripe_webhook',
            'embedded_signup',        # Auth0 embedded registration
            'create_account',         # Auth0 account creation only
            'exchange_code',          # Auth0 code exchange
            'logout',                # Auth0 logout
            'validate_coupon',       # Coupon validation during registration
        ]

    def __call__(self, request):
        # Skip middleware for public URLs
        current_url_name = resolve(request.path_info).url_name
        if current_url_name in self.public_urls:
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Check subscription status
        if not self.has_active_subscription(request.user):
            return JsonResponse({
                'error': 'Subscription required',
                'message': 'Your subscription is inactive or has expired.',
                'code': 'subscription_required'
            }, status=403)

        return self.get_response(request)

    def has_active_subscription(self, user):
        # Allow superusers to bypass subscription check
        if user.is_superuser:
            return True

        # Check if user has an active subscription
        return (
            user.subscription_status == 'active' and
            (user.subscription_end_date is None or user.is_subscription_active)
        )


class AdminAccessMiddleware:
    """
    Middleware to handle admin-only URL access control and add admin context to requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Admin URL patterns that require admin access
        self.admin_url_patterns = [
            '/api/admin/',
            '/api/admin-',
        ]
        
        # URLs that don't require admin checks even if they match admin patterns
        self.admin_exempt_urls = [
            'admin_login',
            'admin_debug',
        ]

    def __call__(self, request):
        # Check if this is an admin URL
        is_admin_url = any(request.path.startswith(pattern) for pattern in self.admin_url_patterns)
        
        if is_admin_url:
            current_url_name = resolve(request.path_info).url_name
            
            # Skip check for exempt URLs
            if current_url_name in self.admin_exempt_urls:
                return self.get_response(request)
            
            # Check if user is authenticated
            print(f"🏭 Middleware auth check for {request.path}")
            print(f"  - request.user: {request.user}")
            print(f"  - is_authenticated: {request.user.is_authenticated}")
            if request.user.is_authenticated:
                print(f"  - user.id: {request.user.id}")
                print(f"  - user.email: {request.user.email}")
                print(f"  - user.is_admin_user: {request.user.is_admin_user}")
                print(f"  - user.is_superuser: {request.user.is_superuser}")
                print(f"  - user.is_platform_admin: {request.user.is_platform_admin}")
                print(f"  - user.admin_role: {request.user.admin_role}")
            
            if not request.user.is_authenticated:
                print("❌ Middleware: User not authenticated")
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'Admin access requires authentication.',
                    'code': 'admin_auth_required'
                }, status=401)
            
            # Check if user has admin access
            if not request.user.is_admin_user:
                print(f"❌ Middleware: User {request.user.email} is not admin user")
            else:
                print(f"✅ Middleware: User {request.user.email} has admin access")
                
            if not request.user.is_admin_user:
                return JsonResponse({
                    'error': 'Admin access required',
                    'message': 'You do not have permission to access admin features.',
                    'code': 'admin_access_denied'
                }, status=403)
        
        # Add admin context to request
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.admin_context = {
                'is_admin': request.user.is_admin_user,
                'admin_role': request.user.admin_role,
                'admin_permissions': request.user.admin_permissions,
                'accessible_sections': self._get_accessible_sections(request.user),
            }
        else:
            request.admin_context = {
                'is_admin': False,
                'admin_role': None,
                'admin_permissions': {},
                'accessible_sections': [],
            }

        return self.get_response(request)

    def _get_accessible_sections(self, user):
        """Get list of admin sections user can access"""
        if not user.is_admin_user:
            return []
        
        sections = ['user_management', 'billing', 'analytics', 'system_monitoring', 'support_tools']
        accessible_sections = []
        
        for section in sections:
            if user.can_access_admin_section(section):
                accessible_sections.append(section)
        
        return accessible_sections


class AdminAuditMiddleware:
    """
    Middleware to log admin actions for audit purposes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Methods that should be audited
        self.audit_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        # URL patterns to audit
        self.audit_patterns = [
            '/api/admin/',
            '/api/users/',
            '/api/clients/',
        ]

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only audit admin users and specific methods
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            request.user.is_admin_user and
            request.method in self.audit_methods):
            
            # Check if URL should be audited
            should_audit = any(request.path.startswith(pattern) for pattern in self.audit_patterns)
            
            if should_audit:
                self._log_admin_action(request, response)
        
        return response

    def _log_admin_action(self, request, response):
        """Log admin action for audit trail"""
        import logging
        
        audit_logger = logging.getLogger('admin_audit')
        
        log_data = {
            'user_id': request.user.id,
            'user_email': request.user.email,
            'admin_role': request.user.admin_role,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # Add request data for certain operations
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
            # Don't log sensitive data
            safe_data = {}
            if hasattr(request, 'data') and request.data:
                for key, value in request.data.items():
                    if 'password' not in key.lower() and 'token' not in key.lower():
                        safe_data[key] = value
            log_data['request_data'] = safe_data
        
        audit_logger.info(f"Admin action: {log_data}")

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip