"""
HTML Sanitization for Backend
Prevents XSS attacks by sanitizing user-generated content
"""

import bleach
from django.core.serializers.json import DjangoJSONEncoder
import json


class HTMLSanitizer:
    """Sanitize HTML content to prevent XSS attacks"""

    # Safe tags for general content
    ALLOWED_TAGS = [
        'p', 'br', 'span', 'div',
        'strong', 'b', 'em', 'i', 'u',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li',
        'blockquote', 'code', 'pre',
        'a',
        'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]

    # Safe attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target', 'rel'],
        'div': ['class', 'id'],
        'span': ['class', 'id'],
        'p': ['class'],
        'code': ['class'],
        'pre': ['class'],
        'table': ['class'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan']
    }

    # Allowed protocols for links
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

    @classmethod
    def sanitize(cls, content, strict=False):
        """
        Sanitize HTML content

        Args:
            content: The potentially dangerous content
            strict: If True, strips ALL HTML tags

        Returns:
            Sanitized content
        """
        if not content:
            return ''

        # Convert to string if needed
        if not isinstance(content, str):
            content = str(content)

        if strict:
            # Strip all HTML for strict mode
            return bleach.clean(
                content,
                tags=[],  # No tags allowed
                attributes={},
                strip=True
            )
        else:
            # Allow basic formatting
            cleaned = bleach.clean(
                content,
                tags=cls.ALLOWED_TAGS,
                attributes=cls.ALLOWED_ATTRIBUTES,
                protocols=cls.ALLOWED_PROTOCOLS,
                strip=True
            )

            # Ensure all links have rel="noopener noreferrer"
            if '<a ' in cleaned:
                cleaned = bleach.linkify(
                    cleaned,
                    callbacks=[cls.add_link_attributes]
                )

            return cleaned

    @staticmethod
    def add_link_attributes(attrs, new=False):
        """Add security attributes to links"""
        attrs[(None, 'target')] = '_blank'
        attrs[(None, 'rel')] = 'noopener noreferrer'
        return attrs

    @classmethod
    def sanitize_dict(cls, data, fields_to_sanitize=None, strict_fields=None):
        """
        Sanitize specific fields in a dictionary

        Args:
            data: Dictionary containing data
            fields_to_sanitize: List of field names to sanitize
            strict_fields: List of fields to sanitize strictly (no HTML)

        Returns:
            Dictionary with sanitized fields
        """
        if not isinstance(data, dict):
            return data

        # Default fields that commonly contain user content
        if fields_to_sanitize is None:
            fields_to_sanitize = [
                'name', 'first_name', 'last_name', 'title',
                'description', 'notes', 'content', 'message',
                'subject', 'body', 'text', 'comment'
            ]

        if strict_fields is None:
            strict_fields = ['first_name', 'last_name', 'email', 'username']

        result = data.copy()

        for field in fields_to_sanitize:
            if field in result and result[field]:
                strict = field in strict_fields
                result[field] = cls.sanitize(result[field], strict=strict)

        return result

    @classmethod
    def sanitize_json_field(cls, json_data):
        """
        Sanitize content within JSON fields

        Args:
            json_data: JSON data (string or dict)

        Returns:
            Sanitized JSON data
        """
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError:
                return json_data
        else:
            data = json_data

        if isinstance(data, dict):
            data = cls.sanitize_dict(data)
        elif isinstance(data, list):
            data = [cls.sanitize_dict(item) if isinstance(item, dict) else item for item in data]

        return json.dumps(data, cls=DjangoJSONEncoder) if isinstance(json_data, str) else data


class ModelSanitizerMixin:
    """
    Mixin for Django models to automatically sanitize fields
    """

    # Override in subclass to specify which fields to sanitize
    SANITIZE_FIELDS = []
    STRICT_SANITIZE_FIELDS = []

    def save(self, *args, **kwargs):
        """Sanitize fields before saving"""
        sanitizer = HTMLSanitizer()

        for field in self.SANITIZE_FIELDS:
            if hasattr(self, field):
                value = getattr(self, field)
                if value:
                    strict = field in self.STRICT_SANITIZE_FIELDS
                    setattr(self, field, sanitizer.sanitize(value, strict=strict))

        super().save(*args, **kwargs)


class SerializerSanitizerMixin:
    """
    Mixin for Django REST Framework serializers to sanitize output
    """

    # Override in subclass to specify which fields to sanitize
    SANITIZE_FIELDS = []
    STRICT_SANITIZE_FIELDS = []

    def to_representation(self, instance):
        """Sanitize fields in serializer output"""
        data = super().to_representation(instance)
        sanitizer = HTMLSanitizer()

        all_fields = self.SANITIZE_FIELDS or ['name', 'first_name', 'last_name', 'description', 'notes']
        strict_fields = self.STRICT_SANITIZE_FIELDS or ['first_name', 'last_name', 'email']

        return sanitizer.sanitize_dict(data, all_fields, strict_fields)


def sanitize_user_input(text, allow_html=False):
    """
    Convenience function to sanitize user input

    Args:
        text: User input text
        allow_html: If True, allows basic HTML formatting

    Returns:
        Sanitized text
    """
    if not text:
        return text

    return HTMLSanitizer.sanitize(text, strict=not allow_html)


def contains_dangerous_content(content):
    """
    Check if content contains potentially dangerous HTML/JavaScript

    Args:
        content: Content to check

    Returns:
        True if dangerous content detected
    """
    if not content:
        return False

    content_lower = str(content).lower()

    dangerous_patterns = [
        '<script', '</script',
        'javascript:', 'data:text/html',
        'onerror=', 'onclick=', 'onload=', 'onmouseover=',
        '<iframe', '<object', '<embed', '<applet',
        'eval(', 'setTimeout(', 'setInterval(',
        'document.cookie', 'document.write',
        '.innerHTML', '.outerHTML',
        'vbscript:', 'file://'
    ]

    return any(pattern in content_lower for pattern in dangerous_patterns)