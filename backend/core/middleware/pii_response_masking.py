"""
Middleware for masking PII in API responses

This middleware can be enabled to automatically mask sensitive data
in all API responses for non-admin users.
"""

import json
import logging
from django.conf import settings
from django.http import JsonResponse
from core.pii_protection import PIIMaskingService

logger = logging.getLogger(__name__)


class PIIResponseMaskingMiddleware:
    """
    Middleware to mask PII in API responses based on user permissions
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.masking_service = PIIMaskingService()

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Only process JSON responses
        if not self._should_mask_response(request, response):
            return response

        try:
            # Parse response content
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                data = json.loads(content)

                # Check if user can see full PII
                if self._user_can_see_pii(request):
                    return response

                # Mask PII in response
                masked_data = self.masking_service.mask_data(data, deep=True)

                # Create new response with masked data
                response = JsonResponse(masked_data, safe=False)
                response.status_code = response.status_code

        except (json.JSONDecodeError, UnicodeDecodeError):
            # If we can't parse the response, leave it as is
            pass
        except Exception as e:
            logger.error(f"Error masking PII in response: {str(e)}")

        return response

    def _should_mask_response(self, request, response):
        """Check if response should be masked"""
        # Only mask if configured
        if not getattr(settings, 'PII_MASK_IN_RESPONSES', False):
            return False

        # Only mask API responses
        if not request.path.startswith('/api/'):
            return False

        # Only mask successful responses
        if response.status_code >= 400:
            return False

        # Check content type
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return False

        return True

    def _user_can_see_pii(self, request):
        """Check if user has permission to see full PII"""
        if not hasattr(request, 'user'):
            return False

        user = request.user

        # Anonymous users can't see PII
        if not user.is_authenticated:
            return False

        # Superusers and staff can see PII
        if user.is_superuser or user.is_staff:
            return True

        # Users can see their own PII (handled at view level)
        # This middleware provides an additional layer of protection

        return False