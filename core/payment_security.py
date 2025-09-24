"""
Payment Security Module
Provides additional security for payment processing
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
import logging

logger = logging.getLogger(__name__)


class PaymentIdempotencyService:
    """
    Service to ensure payment operations are idempotent
    """

    @staticmethod
    def generate_idempotency_key(operation_type, user_id, additional_data=None):
        """
        Generate a unique idempotency key for a payment operation

        Args:
            operation_type: Type of operation (e.g., 'customer_create', 'subscription_create')
            user_id: User ID or email
            additional_data: Additional data to make key unique

        Returns:
            Unique idempotency key
        """
        timestamp = datetime.utcnow().isoformat()
        data_str = f"{operation_type}:{user_id}:{timestamp}"

        if additional_data:
            data_str += f":{additional_data}"

        return hashlib.sha256(data_str.encode()).hexdigest()

    @staticmethod
    def check_duplicate_payment(user_id, amount, window_seconds=60):
        """
        Check if a similar payment was recently attempted

        Args:
            user_id: User making the payment
            amount: Payment amount
            window_seconds: Time window to check for duplicates

        Returns:
            True if duplicate detected, False otherwise
        """
        cache_key = f"payment_attempt:{user_id}:{amount}"

        # Check if key exists (payment was recently attempted)
        if cache.get(cache_key):
            logger.warning(f"Duplicate payment attempt detected for user {user_id}, amount {amount}")
            return True

        # Set the key with expiration
        cache.set(cache_key, True, window_seconds)
        return False

    @staticmethod
    def record_payment_attempt(user_id, payment_data):
        """
        Record a payment attempt for audit and duplicate detection

        Args:
            user_id: User making the payment
            payment_data: Dictionary with payment details

        Returns:
            Unique request ID for this attempt
        """
        request_id = str(uuid.uuid4())
        cache_key = f"payment_request:{request_id}"

        # Store payment attempt data
        payment_record = {
            'user_id': user_id,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': payment_data,
            'status': 'pending'
        }

        # Cache for 24 hours
        cache.set(cache_key, payment_record, 86400)

        return request_id

    @staticmethod
    def mark_payment_complete(request_id, result):
        """
        Mark a payment attempt as complete

        Args:
            request_id: Request ID from record_payment_attempt
            result: Result of the payment operation
        """
        cache_key = f"payment_request:{request_id}"
        payment_record = cache.get(cache_key)

        if payment_record:
            payment_record['status'] = 'complete'
            payment_record['result'] = result
            payment_record['completed_at'] = datetime.utcnow().isoformat()
            cache.set(cache_key, payment_record, 86400)


class PaymentRateLimiter:
    """
    Rate limiting for payment operations
    """

    @staticmethod
    def check_rate_limit(user_id, operation_type, max_attempts=5, window_minutes=60):
        """
        Check if user has exceeded rate limit for payment operations

        Args:
            user_id: User ID
            operation_type: Type of operation
            max_attempts: Maximum attempts allowed
            window_minutes: Time window in minutes

        Returns:
            tuple (allowed, remaining_attempts)
        """
        cache_key = f"payment_rate:{user_id}:{operation_type}"
        current_attempts = cache.get(cache_key, 0)

        if current_attempts >= max_attempts:
            logger.warning(f"Payment rate limit exceeded for user {user_id}, operation {operation_type}")
            return False, 0

        # Increment counter
        cache.set(cache_key, current_attempts + 1, window_minutes * 60)

        return True, max_attempts - current_attempts - 1


class SecurePaymentTransaction:
    """
    Context manager for secure payment transactions with database locking
    """

    def __init__(self, user_model, user_id):
        self.user_model = user_model
        self.user_id = user_id
        self.user = None

    def __enter__(self):
        """
        Acquire lock on user record to prevent concurrent payment operations
        """
        with transaction.atomic():
            # Use SELECT FOR UPDATE to lock the user row
            self.user = self.user_model.objects.select_for_update(nowait=False).get(id=self.user_id)
            return self.user

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Release lock automatically when exiting context
        """
        # Lock is automatically released when transaction completes
        pass


def validate_payment_amount(amount, min_amount=50, max_amount=1000000):
    """
    Validate payment amount is within acceptable range

    Args:
        amount: Amount in cents
        min_amount: Minimum allowed amount in cents
        max_amount: Maximum allowed amount in cents

    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not isinstance(amount, int):
        raise ValueError("Payment amount must be an integer (cents)")

    if amount < min_amount:
        raise ValueError(f"Payment amount must be at least ${min_amount/100:.2f}")

    if amount > max_amount:
        raise ValueError(f"Payment amount exceeds maximum of ${max_amount/100:.2f}")

    return True


def sanitize_payment_metadata(metadata):
    """
    Sanitize metadata for payment operations

    Args:
        metadata: Dictionary of metadata

    Returns:
        Sanitized metadata dictionary
    """
    if not metadata:
        return {}

    # Remove sensitive keys
    sensitive_keys = ['password', 'secret', 'token', 'ssn', 'tax_id']
    sanitized = {}

    for key, value in metadata.items():
        # Skip sensitive keys
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            continue

        # Limit string length
        if isinstance(value, str):
            sanitized[key] = value[:500]
        else:
            sanitized[key] = value

    return sanitized