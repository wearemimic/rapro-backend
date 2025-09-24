"""
Example PII-protected serializers

These serializers demonstrate how to use the PII protection features
to mask sensitive data in API responses.
"""

from rest_framework import serializers
from core.models import Client, CustomUser
from core.pii_protection import PIIMaskingService, PIIProtectedSerializer


class PIIProtectedClientSerializer(PIIProtectedSerializer, serializers.ModelSerializer):
    """
    Client serializer that automatically masks PII for unauthorized users
    """

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'birthdate',
            'gender', 'tax_status', 'notes', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        """Override to apply PII masking based on permissions"""
        data = super().to_representation(instance)

        # The PIIProtectedSerializer mixin handles the masking logic
        # It checks user permissions and applies appropriate masking

        return data


class SafeClientListSerializer(serializers.ModelSerializer):
    """
    Serializer that only returns non-PII fields for list views
    """

    # Computed fields that don't expose PII
    full_name_masked = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'full_name_masked', 'age', 'tax_status',
            'created_at', 'updated_at'
        ]

    def get_full_name_masked(self, obj):
        """Return masked version of full name"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name[0]}*** {obj.last_name[0]}***"
        return "Anonymous"

    def get_age(self, obj):
        """Calculate age without exposing exact birthdate"""
        if obj.birthdate:
            from datetime import date
            today = date.today()
            age = today.year - obj.birthdate.year
            # Adjust if birthday hasn't occurred this year
            if (today.month, today.day) < (obj.birthdate.month, obj.birthdate.day):
                age -= 1
            return age
        return None


class DetailedClientSerializer(serializers.ModelSerializer):
    """
    Serializer with conditional PII exposure based on user role
    """

    class Meta:
        model = Client
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if not request or not hasattr(request, 'user'):
            # No request context, mask everything
            return PIIMaskingService.mask_data(data, deep=True)

        user = request.user

        # Different levels of access
        if user.is_superuser:
            # Superuser sees everything
            return data
        elif user.is_staff:
            # Staff sees everything except some highly sensitive fields
            sensitive_fields = ['ssn', 'bank_account', 'routing_number']
            for field in sensitive_fields:
                if field in data:
                    data[field] = '***REDACTED***'
            return data
        elif hasattr(instance, 'advisor') and instance.advisor == user:
            # Advisor can see their own clients' data
            return data
        else:
            # Everyone else gets masked data
            return PIIMaskingService.mask_data(data, deep=True)


class AuditSafeSerializer(serializers.ModelSerializer):
    """
    Serializer for audit logs that never exposes PII
    """

    user_identifier = serializers.SerializerMethodField()
    action_summary = serializers.SerializerMethodField()

    class Meta:
        model = Client  # Can be any model
        fields = ['id', 'user_identifier', 'action_summary', 'created_at']

    def get_user_identifier(self, obj):
        """Return a safe identifier that doesn't expose PII"""
        import hashlib
        if hasattr(obj, 'email'):
            # Create a consistent hash of the email
            email_hash = hashlib.sha256(obj.email.encode()).hexdigest()[:8]
            return f"User_{email_hash}"
        return f"User_{obj.id}"

    def get_action_summary(self, obj):
        """Return action without PII details"""
        # This would typically come from an audit log
        return "Data access"