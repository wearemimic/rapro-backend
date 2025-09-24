"""
PII (Personally Identifiable Information) Protection Module

This module provides utilities for:
1. Masking PII in API responses
2. Filtering PII from logs
3. Secure data deletion
4. Field-level encryption for sensitive data
"""

import re
import logging
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os


class PIIMaskingService:
    """Service for masking PII in data structures"""

    # Fields that should always be masked
    SENSITIVE_FIELDS = {
        'ssn', 'social_security_number', 'tax_id', 'ein',
        'bank_account', 'routing_number', 'credit_card',
        'card_number', 'cvv', 'security_code',
        'password', 'secret', 'api_key', 'token',
        'birthdate', 'date_of_birth', 'dob',
        'driver_license', 'passport_number',
        'medical_record', 'health_information'
    }

    # Fields that should be partially masked
    PARTIAL_MASK_FIELDS = {
        'email': lambda x: PIIMaskingService.mask_email(x),
        'phone': lambda x: PIIMaskingService.mask_phone(x),
        'phone_number': lambda x: PIIMaskingService.mask_phone(x),
        'address': lambda x: PIIMaskingService.mask_address(x),
        'street_address': lambda x: PIIMaskingService.mask_address(x),
    }

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address keeping first character and domain"""
        if not email or '@' not in email:
            return '***@***.***'

        parts = email.split('@')
        username = parts[0]
        domain = parts[1] if len(parts) > 1 else '***.***'

        if len(username) > 1:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = '*'

        return f"{masked_username}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number keeping area code"""
        if not phone:
            return '***-***-****'

        # Remove non-digits
        digits = re.sub(r'\D', '', phone)

        if len(digits) >= 10:
            return f"({digits[:3]}) ***-**{digits[-2:]}"
        elif len(digits) >= 7:
            return f"***-**{digits[-2:]}"
        else:
            return '*' * len(digits)

    @staticmethod
    def mask_address(address: str) -> str:
        """Mask street address keeping city and state"""
        if not address:
            return '*** ***'

        # Keep only first word and mask the rest
        words = address.split()
        if len(words) > 1:
            return words[0] + ' ' + '*' * 10
        return '*' * len(address)

    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """Mask SSN keeping last 4 digits"""
        if not ssn:
            return '***-**-****'

        # Remove non-digits
        digits = re.sub(r'\D', '', ssn)

        if len(digits) >= 9:
            return f"***-**-{digits[-4:]}"
        else:
            return '*' * len(digits)

    @classmethod
    def mask_data(cls, data: Any, deep: bool = True) -> Any:
        """
        Recursively mask PII in data structures

        Args:
            data: Data to mask (dict, list, or primitive)
            deep: Whether to recurse into nested structures

        Returns:
            Masked version of the data
        """
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                key_lower = key.lower()

                # Check if field should be completely masked
                if any(sensitive in key_lower for sensitive in cls.SENSITIVE_FIELDS):
                    masked[key] = '***REDACTED***'
                # Check if field should be partially masked
                elif key_lower in cls.PARTIAL_MASK_FIELDS:
                    if isinstance(value, str):
                        masked[key] = cls.PARTIAL_MASK_FIELDS[key_lower](value)
                    else:
                        masked[key] = '***REDACTED***'
                # Recurse if deep masking
                elif deep:
                    masked[key] = cls.mask_data(value, deep=True)
                else:
                    masked[key] = value

            return masked

        elif isinstance(data, list):
            if deep:
                return [cls.mask_data(item, deep=True) for item in data]
            return data

        elif isinstance(data, (date, datetime)):
            # Mask birthdates but keep year for age calculations
            return f"****-**-{data.year}" if hasattr(data, 'year') else '***'

        else:
            return data

    @classmethod
    def get_safe_fields(cls, model_instance: models.Model) -> Dict[str, Any]:
        """
        Get only safe (non-PII) fields from a model instance

        Args:
            model_instance: Django model instance

        Returns:
            Dictionary of safe fields
        """
        safe_fields = {}

        for field in model_instance._meta.fields:
            field_name = field.name
            field_value = getattr(model_instance, field_name)

            # Skip sensitive fields entirely
            if any(sensitive in field_name.lower() for sensitive in cls.SENSITIVE_FIELDS):
                continue

            # Partial mask certain fields
            if field_name.lower() in cls.PARTIAL_MASK_FIELDS:
                if isinstance(field_value, str):
                    safe_fields[field_name] = cls.PARTIAL_MASK_FIELDS[field_name.lower()](field_value)
            else:
                safe_fields[field_name] = field_value

        return safe_fields


class PIILoggingFilter(logging.Filter):
    """Logging filter to remove PII from log records"""

    PII_PATTERNS = [
        # SSN patterns
        (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),
        (r'\b\d{9}\b', '*********'),

        # Credit card patterns
        (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****'),
        (r'\b\d{15,16}\b', '****************'),

        # Email patterns
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),

        # Phone patterns
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****'),
        (r'\b\(\d{3}\)\s?\d{3}-\d{4}\b', '(***) ***-****'),

        # Date of birth patterns (common formats)
        (r'\b\d{1,2}/\d{1,2}/\d{4}\b', '**/**/****'),
        (r'\b\d{4}-\d{2}-\d{2}\b', '****-**-**'),
    ]

    def filter(self, record):
        """Filter PII from log records"""
        # Mask the message
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            for pattern, replacement in self.PII_PATTERNS:
                msg = re.sub(pattern, replacement, msg)
            record.msg = msg

        # Mask the arguments
        if hasattr(record, 'args') and record.args:
            masked_args = []
            for arg in record.args:
                arg_str = str(arg)
                for pattern, replacement in self.PII_PATTERNS:
                    arg_str = re.sub(pattern, replacement, arg_str)
                masked_args.append(arg_str)
            record.args = tuple(masked_args)

        return True


class SecureDataDeletion:
    """Service for secure deletion of sensitive data"""

    @staticmethod
    def secure_delete_model(instance: models.Model,
                           overwrite_fields: Optional[List[str]] = None) -> None:
        """
        Securely delete a model instance by overwriting sensitive fields

        Args:
            instance: Model instance to delete
            overwrite_fields: Specific fields to overwrite before deletion
        """
        if not overwrite_fields:
            # Default sensitive fields to overwrite
            overwrite_fields = ['ssn', 'birthdate', 'email', 'phone',
                              'bank_account', 'routing_number']

        with transaction.atomic():
            # Overwrite sensitive fields with random data
            for field_name in overwrite_fields:
                if hasattr(instance, field_name):
                    field = instance._meta.get_field(field_name)

                    if isinstance(field, models.CharField):
                        setattr(instance, field_name, 'DELETED_' + os.urandom(8).hex())
                    elif isinstance(field, models.EmailField):
                        setattr(instance, field_name, f'deleted_{os.urandom(4).hex()}@example.com')
                    elif isinstance(field, models.DateField):
                        setattr(instance, field_name, date(1900, 1, 1))
                    elif isinstance(field, models.DecimalField):
                        setattr(instance, field_name, Decimal('0.00'))
                    elif isinstance(field, models.IntegerField):
                        setattr(instance, field_name, 0)

            # Save the overwritten data
            instance.save(update_fields=overwrite_fields)

            # Now delete the record
            instance.delete()

    @staticmethod
    def anonymize_user_data(user_id: int) -> None:
        """
        Anonymize user data for GDPR compliance

        Args:
            user_id: ID of user to anonymize
        """
        from core.models import CustomUser, Client

        try:
            user = CustomUser.objects.get(id=user_id)

            # Generate anonymous identifiers
            anon_id = hashlib.sha256(f"{user_id}{datetime.now()}".encode()).hexdigest()[:8]

            # Anonymize user data
            user.first_name = 'Anonymous'
            user.last_name = f'User_{anon_id}'
            user.email = f'anon_{anon_id}@deleted.example.com'
            user.username = f'deleted_user_{anon_id}'
            user.is_active = False
            user.save()

            # Anonymize related client data
            Client.objects.filter(advisor=user).update(
                first_name='Anonymous',
                last_name=f'Client_{anon_id}',
                email=f'anon_client_{anon_id}@deleted.example.com',
                birthdate=date(1900, 1, 1),
                notes='Data anonymized for privacy'
            )

        except CustomUser.DoesNotExist:
            raise ValidationError(f"User {user_id} not found")


class FieldEncryption:
    """Service for field-level encryption of sensitive data"""

    def __init__(self):
        # Generate or load encryption key
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_str = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)

        if not key_str:
            # Generate a new key if not configured
            # In production, this should be stored securely
            salt = b'stable_salt_for_pii_encryption'  # Use a stable salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(settings.SECRET_KEY.encode()[:32])
            )
            return key

        return key_str.encode()

    def encrypt_field(self, value: str) -> str:
        """Encrypt a field value"""
        if not value:
            return value

        encrypted = self.cipher.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a field value"""
        if not encrypted_value:
            return encrypted_value

        try:
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            # Return the original value if decryption fails
            return encrypted_value


class PIIProtectedSerializer:
    """Mixin for serializers that need PII protection"""

    def to_representation(self, instance):
        """Override to mask PII in responses"""
        data = super().to_representation(instance)

        # Check if user has permission to view full PII
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Admin users can see full data
            if request.user.is_staff or request.user.is_superuser:
                return data

            # Check if viewing own data
            if hasattr(instance, 'advisor') and instance.advisor == request.user:
                return data

        # Mask PII for others
        return PIIMaskingService.mask_data(data, deep=True)


def setup_pii_logging_filter():
    """Setup PII filter for all loggers"""
    pii_filter = PIILoggingFilter()

    # Add filter to all handlers
    for handler in logging.root.handlers:
        handler.addFilter(pii_filter)

    # Add to specific loggers
    for logger_name in ['django', 'celery', 'core']:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.addFilter(pii_filter)