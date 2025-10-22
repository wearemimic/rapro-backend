"""
Kajabi API Client for subscription verification and management.
"""
import requests
import logging
from django.conf import settings
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class KajabiAPIClient:
    """Client for interacting with the Kajabi API"""

    def __init__(self):
        self.api_key = settings.KAJABI_API_KEY
        self.base_url = settings.KAJABI_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make a request to the Kajabi API"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                timeout=10,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Kajabi API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Kajabi API request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Kajabi API request: {str(e)}")
            return None

    def get_member(self, member_id: str) -> Optional[Dict]:
        """
        Get member details from Kajabi.

        Args:
            member_id: The Kajabi member ID

        Returns:
            Dict with member data or None if error
        """
        return self._make_request('GET', f'members/{member_id}')

    def get_member_by_email(self, email: str) -> Optional[Dict]:
        """
        Get member by email address.

        Args:
            email: The member's email address

        Returns:
            Dict with member data or None if error
        """
        response = self._make_request('GET', 'members', params={'filter[email]': email})

        if response and 'data' in response and len(response['data']) > 0:
            return response['data'][0]

        return None

    def get_member_subscriptions(self, member_id: str) -> Optional[list]:
        """
        Get all subscriptions for a member.

        Args:
            member_id: The Kajabi member ID

        Returns:
            List of subscription dicts or None if error
        """
        response = self._make_request('GET', f'members/{member_id}/subscriptions')

        if response and 'data' in response:
            return response['data']

        return None

    def verify_subscription_status(self, kajabi_member_id: str, product_id: str = None) -> Dict:
        """
        Verify the current subscription status for a member.

        Args:
            kajabi_member_id: The Kajabi member ID
            product_id: Optional specific product ID to check

        Returns:
            Dict with verification results:
            {
                'is_active': bool,
                'subscription_status': str,
                'subscriptions': list,
                'member_info': dict,
                'error': str (if any)
            }
        """
        result = {
            'is_active': False,
            'subscription_status': 'unknown',
            'subscriptions': [],
            'member_info': None,
            'error': None
        }

        try:
            # Get member info
            member = self.get_member(kajabi_member_id)
            if not member:
                result['error'] = 'Member not found in Kajabi'
                return result

            result['member_info'] = member

            # Get subscriptions
            subscriptions = self.get_member_subscriptions(kajabi_member_id)
            if subscriptions is None:
                result['error'] = 'Could not retrieve subscriptions'
                return result

            result['subscriptions'] = subscriptions

            # Check if any subscription is active
            active_subscriptions = []

            for sub in subscriptions:
                # Filter by product if specified
                if product_id and sub.get('product_id') != product_id:
                    continue

                status = sub.get('status', '').lower()

                if status in ['active', 'trialing']:
                    active_subscriptions.append(sub)

            if active_subscriptions:
                result['is_active'] = True
                result['subscription_status'] = 'active'
            else:
                # Check if any are canceled but not yet expired
                for sub in subscriptions:
                    if product_id and sub.get('product_id') != product_id:
                        continue

                    status = sub.get('status', '').lower()
                    if status == 'canceled':
                        result['subscription_status'] = 'canceled'
                        break
                else:
                    result['subscription_status'] = 'inactive'

            logger.info(f"Verified Kajabi subscription for member {kajabi_member_id}: {result['subscription_status']}")

        except Exception as e:
            logger.error(f"Error verifying Kajabi subscription: {str(e)}", exc_info=True)
            result['error'] = str(e)

        return result

    def get_subscription_details(self, subscription_id: str) -> Optional[Dict]:
        """
        Get details for a specific subscription.

        Args:
            subscription_id: The Kajabi subscription ID

        Returns:
            Dict with subscription data or None if error
        """
        return self._make_request('GET', f'subscriptions/{subscription_id}')


# Singleton instance
kajabi_client = KajabiAPIClient()
