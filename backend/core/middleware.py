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