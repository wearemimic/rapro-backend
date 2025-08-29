from .models import IncomeSource
# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    CustomUser, Client, Scenario, Spouse, RealEstate, ReportTemplate, TemplateSlide,
    EmailAccount, Communication, Lead, LeadSource, SMSMessage, TwilioConfiguration, ActivityLog,
    Task, TaskTemplate, TaskComment, CalendarAccount, CalendarEvent, MeetingTemplate, CalendarEventReminder,
    Document, DocumentCategory, DocumentVersion, DocumentPermission, DocumentAuditLog, 
    DocumentTemplate, DocumentRetentionPolicy
)
import logging
from django.contrib.auth import get_user_model
import json

logger = logging.getLogger(__name__)

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'company_name', 'website_url', 'address', 'city', 'state',
            'zip_code', 'white_label_company_name', 'white_label_support_email',
            'primary_color', 'logo'
        ]
        read_only_fields = ['id', 'email']  # Optional: disable email edit

class UserSerializer(serializers.ModelSerializer):
    website_url = serializers.URLField(
        required=False, 
        allow_blank=True,
        error_messages={
            'invalid': 'Please enter a valid URL including http:// or https://'
        }
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'company_name', 'website_url', 'address', 'city', 'state',
            'zip_code', 'white_label_company_name', 'white_label_support_email',
            'primary_color', 'logo', 'custom_disclosure'
        ]
        read_only_fields = ['id', 'username', 'email']

class SpouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spouse
        fields = ['first_name', 'last_name', 'birthdate', 'gender']

class ClientCreateSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(required=False)

    class Meta:
        model = Client
        fields = [
            "id", "first_name", "last_name", "email", "birthdate", "gender",
            "tax_status", "status", "notes", "spouse"
        ]
        extra_kwargs = {
            "advisor": {"read_only": True}
        }

    def create(self, validated_data):
        request = self.context.get('request')
        advisor = request.user

        # if not advisor or not advisor.is_authenticated:
            # raise serializers.ValidationError({"advisor": ["Invalid or missing advisor."]})
        
        validated_data.pop("advisor", None)

        spouse_data = validated_data.pop('spouse', None)
        client = Client.objects.create(advisor=advisor, **validated_data)

        if spouse_data:
            try:
                Spouse.objects.create(client=client, **spouse_data)
            except Exception as e:
                logger.error(f"Error saving spouse info for client {client.id}: {e}")
                # raise serializers.ValidationError({"spouse": f"Error saving spouse info: {str(e)}"})

        return client
    
class ClientSerializer(serializers.ModelSerializer):
    advisor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    spouse_first_name = serializers.CharField(required=False, allow_blank=True)
    spouse_last_name = serializers.CharField(required=False, allow_blank=True)
    spouse_birthdate = serializers.DateField(required=False)
    spouse_gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], required=False)
    notes = serializers.CharField(required=False, allow_blank=True, style={'base_template': 'textarea.html'})

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'birthdate', 'gender',
            'tax_status', 'spouse_first_name', 'spouse_last_name',
            'spouse_birthdate', 'spouse_gender', 'notes', 'status', 'advisor',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'advisor', 'created_at', 'updated_at']

class ClientEditSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'birthdate', 'gender',
            'tax_status', 'status', 'notes', 'spouse'
        ]
        read_only_fields = ['id', 'advisor', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        spouse_data = validated_data.pop('spouse', None)

        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle spouse logic only if not single
        if instance.tax_status.lower() != 'single':
            required_spouse_fields = ['first_name', 'last_name', 'birthdate', 'gender']
            print('DEBUG spouse_data:', spouse_data)
            print('DEBUG required fields check:', [spouse_data.get(f) not in [None, ''] for f in required_spouse_fields] if spouse_data else None)
            if spouse_data and all(spouse_data.get(f) not in [None, ''] for f in required_spouse_fields):
                print('DEBUG: Creating or updating spouse')
                try:
                    spouse = Spouse.objects.get(client=instance)
                    for attr, value in spouse_data.items():
                        setattr(spouse, attr, value)
                    spouse.save()
                except Spouse.DoesNotExist:
                    Spouse.objects.create(client=instance, **spouse_data)
            else:
                print('DEBUG: Spouse data incomplete, deleting spouse if exists')
                # If spouse data is incomplete, delete spouse if exists
                try:
                    if instance.spouse:
                        instance.spouse.delete()
                except Spouse.DoesNotExist:
                    pass
        else:
            print('DEBUG: Tax status is single, deleting spouse if exists')
            # If single and spouse exists, delete it
            try:
                if instance.spouse:
                    instance.spouse.delete()
            except Spouse.DoesNotExist:
                pass

        return instance


class ScenarioSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = [
            'id', 'name', 'updated_at', 'apply_standard_deduction',
            'retirement_age', 'medicare_age', 'spouse_retirement_age', 'spouse_medicare_age',
            'mortality_age', 'spouse_mortality_age', 'retirement_year', 'share_with_client',
            'part_b_inflation_rate', 'part_d_inflation_rate', 'income_vs_cost_percent', 'medicare_irmaa_percent'
        ]

class ClientDetailSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(read_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    scenarios = ScenarioSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'birthdate',
            'gender',
            'tax_status',
            'notes',
            'status',
            'spouse',
            'scenarios',
            # Client Portal Fields
            'portal_access_enabled',
            'portal_invitation_sent_at',
            'portal_last_login',
            'portal_user'
        ]


# --- Additional serializers for IncomeSource and Scenario creation ---

class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        exclude = ['scenario']


class ScenarioCreateSerializer(serializers.ModelSerializer):
    income_sources = IncomeSourceSerializer(many=True, required=False)

    class Meta:
        model = Scenario
        fields = [
            'id', 'client', 'name', 'description', 'retirement_age', 'medicare_age',
            'spouse_retirement_age', 'spouse_medicare_age', 'mortality_age',
            'spouse_mortality_age', 'retirement_year', 'share_with_client', 'income_sources',
            'part_b_inflation_rate', 'part_d_inflation_rate', 'apply_standard_deduction', 'primary_state',
            'reduction_2030_ss', 'ss_adjustment_year', 'ss_adjustment_direction', 
            'ss_adjustment_type', 'ss_adjustment_amount',
            'federal_standard_deduction', 'state_standard_deduction', 'custom_annual_deduction',
            'primary_blind', 'spouse_blind', 'is_dependent'
        ]

    def create(self, validated_data):
        income_data = validated_data.pop('income_sources', [])
        scenario = Scenario.objects.create(**validated_data)
        for income in income_data:
            IncomeSource.objects.create(scenario=scenario, **income)
        return scenario

class ScenarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = [
            'id', 'name', 'description', 'retirement_age', 'medicare_age',
            'spouse_retirement_age', 'spouse_medicare_age', 'mortality_age',
            'spouse_mortality_age', 'retirement_year', 'share_with_client',
            'part_b_inflation_rate', 'part_d_inflation_rate', 'apply_standard_deduction',
            'roth_conversion_start_year', 'roth_conversion_duration', 'roth_conversion_annual_amount',
            'income_vs_cost_percent', 'medicare_irmaa_percent', 'primary_state',
            'reduction_2030_ss', 'ss_adjustment_year', 'ss_adjustment_direction', 
            'ss_adjustment_type', 'ss_adjustment_amount',
            'federal_standard_deduction', 'state_standard_deduction', 'custom_annual_deduction',
            'primary_blind', 'spouse_blind', 'is_dependent'
        ]

class IncomeSourceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        fields = [
            'id', 'owned_by', 'income_type', 'income_name', 'current_asset_balance',
            'monthly_amount', 'monthly_contribution', 'age_to_begin_withdrawal',
            'age_to_end_withdrawal', 'rate_of_return', 'cola', 'exclusion_ratio',
            'tax_rate', 'scenario_id', 'max_to_convert'
        ]
        read_only_fields = ['scenario_id']

class AdvisorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    licenses = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'password',
            'first_name', 'last_name',
            'phone_number', 'company_name',
            'website_url', 'address', 'city',
            'state', 'zip_code', 'licenses'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
        }

    def create(self, validated_data):
        licenses = validated_data.pop('licenses', '')
        user = User.objects.create_user(
            **validated_data
        )
        # Store licenses in a custom field or separate model if needed
        return user

class RealEstateSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        logger = logging.getLogger(__name__)
        logger.warning(f"RealEstateSerializer input data: {data}")
        data = data.copy()
        data.pop('client', None)
        return super().to_internal_value(data)

    class Meta:
        model = RealEstate
        fields = [
            'id', 'client', 'address', 'city', 'state', 'zip', 'value', 'image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']

class TemplateSlideSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateSlide
        fields = ['id', 'order', 'thumbnail_url']
    
    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

class ReportTemplateSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    slides_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = ['id', 'name', 'file_url', 'created_at', 'updated_at', 'slides_count']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_slides_count(self, obj):
        return obj.slides.count()

class ReportTemplateDetailSerializer(ReportTemplateSerializer):
    slides = TemplateSlideSerializer(many=True, read_only=True)
    
    class Meta(ReportTemplateSerializer.Meta):
        fields = ReportTemplateSerializer.Meta.fields + ['slides']


# =============================================================================
# CRM SERIALIZERS - Phase 1 Implementation
# =============================================================================

class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = [
            'id', 'name', 'source_type', 'utm_source', 'utm_medium', 
            'utm_campaign', 'utm_term', 'utm_content', 'facebook_campaign_id', 
            'google_campaign_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LeadSerializer(serializers.ModelSerializer):
    lead_source = LeadSourceSerializer(read_only=True)
    lead_source_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    converted_client = serializers.StringRelatedField(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 
            'status', 'lead_source', 'lead_source_id', 'converted_client', 
            'notes', 'created_at', 'updated_at', 'conversion_date'
        ]
        read_only_fields = ['id', 'advisor', 'converted_client', 'created_at', 'updated_at', 'conversion_date']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def validate_email(self, value):
        """Ensure email is unique within advisor's leads and clients"""
        user = self.context['request'].user
        
        # Check for existing lead with same email (excluding current instance if updating)
        lead_query = Lead.objects.filter(advisor=user, email__iexact=value)
        if self.instance:
            lead_query = lead_query.exclude(pk=self.instance.pk)
        
        if lead_query.exists():
            raise serializers.ValidationError("A lead with this email already exists.")
        
        # Check for existing client with same email
        if Client.objects.filter(advisor=user, email__iexact=value, is_deleted=False).exists():
            raise serializers.ValidationError("A client with this email already exists.")
        
        return value


class LeadCreateSerializer(LeadSerializer):
    class Meta(LeadSerializer.Meta):
        fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'status', 'lead_source_id', 'notes'
        ]


class EmailAccountSerializer(serializers.ModelSerializer):
    is_token_expired = serializers.SerializerMethodField()
    last_sync_display = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailAccount
        fields = [
            'id', 'provider', 'email_address', 'display_name', 
            'sync_enabled', 'is_active', 'last_sync_at', 'last_sync_display',
            'is_token_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'access_token', 'refresh_token', 'token_expires_at',
            'sync_history_id', 'created_at', 'updated_at'
        ]
    
    def get_is_token_expired(self, obj):
        if not obj.token_expires_at:
            return True
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() >= obj.token_expires_at - timedelta(minutes=5)
    
    def get_last_sync_display(self, obj):
        if obj.last_sync_at:
            from django.utils import timezone
            now = timezone.now()
            diff = now - obj.last_sync_at
            
            if diff.total_seconds() < 60:
                return "Just now"
            elif diff.total_seconds() < 3600:
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif diff.total_seconds() < 86400:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(diff.total_seconds() / 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
        return "Never"


class CommunicationSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    recipient_type = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    email_account = EmailAccountSerializer(read_only=True)
    subject_preview = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Communication
        fields = [
            'id', 'communication_type', 'direction', 'subject', 'subject_preview',
            'content', 'content_preview', 'client', 'client_name', 'lead', 'lead_name',
            'recipient_type', 'recipient_name', 'email_account', 'from_address',
            'to_addresses', 'cc_addresses', 'is_read', 'sent_at', 'created_at',
            'updated_at', 'sync_status',
            # AI Analysis fields
            'ai_sentiment_score', 'ai_sentiment_label', 'ai_urgency_score',
            'ai_priority_score', 'ai_topics', 'ai_suggested_response',
            'ai_response_confidence', 'ai_analysis_date', 'ai_model_version'
        ]
        read_only_fields = [
            'id', 'advisor', 'provider_message_id', 'message_id_header', 'thread_id',
            'in_reply_to', 'bcc_addresses', 'read_at', 'sync_direction', 
            'created_at', 'updated_at',
            # AI Analysis fields are read-only (set by AI service)
            'ai_sentiment_score', 'ai_sentiment_label', 'ai_urgency_score',
            'ai_priority_score', 'ai_topics', 'ai_suggested_response',
            'ai_response_confidence', 'ai_analysis_date', 'ai_model_version'
        ]
    
    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None
    
    def get_lead_name(self, obj):
        return str(obj.lead) if obj.lead else None
    
    def get_recipient_type(self, obj):
        if obj.client:
            return 'client'
        elif obj.lead:
            return 'lead'
        return None
    
    def get_recipient_name(self, obj):
        if obj.client:
            return str(obj.client)
        elif obj.lead:
            return str(obj.lead)
        return None
    
    def get_subject_preview(self, obj):
        if obj.subject and len(obj.subject) > 50:
            return obj.subject[:50] + '...'
        return obj.subject
    
    def get_content_preview(self, obj):
        if obj.content:
            # Remove HTML tags for preview
            import re
            clean_content = re.sub(r'<[^>]+>', '', obj.content)
            if len(clean_content) > 100:
                return clean_content[:100] + '...'
            return clean_content
        return ''


class CommunicationCreateSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(required=False, allow_null=True)
    lead_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Communication
        fields = [
            'communication_type', 'direction', 'subject', 'content',
            'client_id', 'lead_id'
        ]
    
    def validate(self, data):
        """Ensure either client_id or lead_id is provided, but not both"""
        client_id = data.get('client_id')
        lead_id = data.get('lead_id')
        
        if not client_id and not lead_id:
            raise serializers.ValidationError("Either client_id or lead_id must be provided")
        
        if client_id and lead_id:
            raise serializers.ValidationError("Cannot specify both client_id and lead_id")
        
        return data
    
    def create(self, validated_data):
        client_id = validated_data.pop('client_id', None)
        lead_id = validated_data.pop('lead_id', None)
        
        user = self.context['request'].user
        
        communication = Communication(
            advisor=user,
            **validated_data
        )
        
        if client_id:
            try:
                client = Client.objects.get(id=client_id, advisor=user, is_deleted=False)
                communication.client = client
            except Client.DoesNotExist:
                raise serializers.ValidationError("Invalid client_id")
        
        if lead_id:
            try:
                lead = Lead.objects.get(id=lead_id, advisor=user)
                communication.lead = lead
            except Lead.DoesNotExist:
                raise serializers.ValidationError("Invalid lead_id")
        
        communication.save()
        return communication


class SMSMessageSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    recipient_type = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    body_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'direction', 'from_number', 'to_number', 'body', 'body_preview',
            'status', 'client', 'client_name', 'lead', 'lead_name',
            'recipient_type', 'recipient_name', 'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'advisor', 'twilio_sid', 'sent_at', 'created_at']
    
    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None
    
    def get_lead_name(self, obj):
        return str(obj.lead) if obj.lead else None
    
    def get_recipient_type(self, obj):
        if obj.client:
            return 'client'
        elif obj.lead:
            return 'lead'
        return None
    
    def get_recipient_name(self, obj):
        if obj.client:
            return str(obj.client)
        elif obj.lead:
            return str(obj.lead)
        return None
    
    def get_body_preview(self, obj):
        if obj.body and len(obj.body) > 50:
            return obj.body[:50] + '...'
        return obj.body


class TwilioConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwilioConfiguration
        fields = [
            'id', 'account_sid', 'phone_number', 'webhook_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'webhook_url', 'created_at', 'updated_at']
        extra_kwargs = {
            'auth_token': {'write_only': True}
        }


class ActivityLogSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    description_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'activity_type', 'user_name', 'description', 'description_preview',
            'client', 'client_name', 'lead', 'lead_name', 'target_type', 'target_name',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None
    
    def get_lead_name(self, obj):
        return str(obj.lead) if obj.lead else None
    
    def get_target_type(self, obj):
        if obj.client:
            return 'client'
        elif obj.lead:
            return 'lead'
        return None
    
    def get_target_name(self, obj):
        if obj.client:
            return str(obj.client)
        elif obj.lead:
            return str(obj.lead)
        return None
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def get_description_preview(self, obj):
        if obj.description and len(obj.description) > 75:
            return obj.description[:75] + '...'
        return obj.description


# =============================================================================
# EMAIL SENDING SERIALIZERS
# =============================================================================

class EmailSendSerializer(serializers.Serializer):
    to_addresses = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1,
        max_length=10
    )
    cc_addresses = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True,
        max_length=10
    )
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField()
    email_account_id = serializers.IntegerField()
    client_id = serializers.IntegerField(required=False, allow_null=True)
    lead_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validate email sending request"""
        client_id = data.get('client_id')
        lead_id = data.get('lead_id')
        
        if client_id and lead_id:
            raise serializers.ValidationError("Cannot specify both client_id and lead_id")
        
        return data
    
    def validate_email_account_id(self, value):
        """Validate email account belongs to user and is active"""
        user = self.context['request'].user
        
        try:
            account = EmailAccount.objects.get(id=value, user=user, is_active=True)
            return value
        except EmailAccount.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive email account")


class EmailAttachmentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    content_base64 = serializers.CharField()
    content_type = serializers.CharField(required=False)
    
    def validate_content_base64(self, value):
        """Validate base64 content"""
        import base64
        try:
            base64.b64decode(value, validate=True)
            return value
        except Exception:
            raise serializers.ValidationError("Invalid base64 content")


class EmailComposeSerializer(EmailSendSerializer):
    attachments = EmailAttachmentSerializer(many=True, required=False, allow_empty=True)
    
    def validate_attachments(self, value):
        """Validate attachments don't exceed size limit"""
        total_size = 0
        max_size = 25 * 1024 * 1024  # 25MB total limit
        
        for attachment in value:
            import base64
            content = attachment['content_base64']
            # Base64 encoding increases size by ~33%
            actual_size = len(base64.b64decode(content))
            total_size += actual_size
            
            if total_size > max_size:
                raise serializers.ValidationError("Total attachment size exceeds 25MB limit")
        
        return value


# =============================================================================
# TASK MANAGEMENT SERIALIZERS
# =============================================================================

class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'content', 'user', 'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = [
            'id', 'name', 'description', 'default_title', 'default_description',
            'default_priority', 'estimated_duration', 'trigger_type', 'trigger_conditions',
            'auto_assign_to_creator', 'auto_assign_to_client_owner', 'default_assignees',
            'client_type_restrictions', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    time_to_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'client', 'client_name', 'scenario',
            'template', 'template_name', 'due_date', 'completed_at',
            'estimated_duration_hours', 'actual_duration_hours',
            'tags', 'notes', 'reminder_sent', 'is_overdue', 'time_to_due',
            'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'completed_at', 'actual_duration_hours', 'created_at', 'updated_at']
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.email
        return None
    
    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
    
    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None
    
    def get_template_name(self, obj):
        return obj.template.name if obj.template else None
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_is_overdue(self, obj):
        if obj.due_date and obj.status != 'completed':
            from django.utils import timezone
            return obj.due_date < timezone.now()
        return False
    
    def get_time_to_due(self, obj):
        if obj.due_date and obj.status != 'completed':
            from django.utils import timezone
            delta = obj.due_date - timezone.now()
            if delta.total_seconds() > 0:
                days = delta.days
                if days > 0:
                    return f"{days} day{'s' if days != 1 else ''}"
                else:
                    hours = delta.total_seconds() // 3600
                    return f"{int(hours)} hour{'s' if hours != 1 else ''}"
            return "Overdue"
        return None
    


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'assigned_to',
            'client', 'scenario', 'template',
            'due_date', 'estimated_duration_hours', 'tags', 'notes'
        ]
    
    def validate(self, data):
        # Basic validation - can add more specific validation here if needed
        return data


class TaskDetailSerializer(TaskSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['comments']


# =============================================================================
# CALENDAR MANAGEMENT SERIALIZERS
# =============================================================================

class CalendarAccountSerializer(serializers.ModelSerializer):
    is_token_expired = serializers.SerializerMethodField()
    provider_display = serializers.SerializerMethodField()
    calendar_count = serializers.SerializerMethodField()
    last_sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarAccount
        fields = [
            'id', 'provider', 'provider_display', 'display_name', 'email_address',
            'is_active', 'sync_enabled', 'primary_calendar', 'sync_past_days', 'sync_future_days',
            'last_sync_at', 'timezone', 'calendar_count', 'is_token_expired',
            'last_sync_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'external_account_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
            'token_expires_at': {'write_only': True},
            'last_sync_token': {'write_only': True}
        }
    
    def get_is_token_expired(self, obj):
        return obj.is_token_expired()
    
    def get_provider_display(self, obj):
        return obj.get_provider_display()
    
    def get_calendar_count(self, obj):
        return len(obj.calendar_list) if obj.calendar_list else 0
    
    def get_last_sync_status(self, obj):
        if not obj.last_sync_at:
            return 'never'
        
        from django.utils import timezone
        delta = timezone.now() - obj.last_sync_at
        
        if delta.total_seconds() < 3600:  # Less than 1 hour
            return 'recent'
        elif delta.total_seconds() < 86400:  # Less than 24 hours
            return 'today'
        elif delta.total_seconds() < 604800:  # Less than 1 week
            return 'this_week'
        else:
            return 'outdated'


class CalendarEventSerializer(serializers.ModelSerializer):
    calendar_account_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    task_title = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    is_today = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    attendee_count = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    meeting_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'external_event_id', 'calendar_id', 'title', 'description', 'location',
            'start_datetime', 'end_datetime', 'all_day', 'timezone', 'status', 'status_display',
            'privacy', 'is_recurring', 'organizer_email', 'organizer_name', 'attendees', 'attendee_count',
            'client', 'client_name', 'lead', 'lead_name', 'task', 'task_title',
            'meeting_url', 'meeting_type', 'meeting_type_display', 'duration_minutes',
            'is_today', 'is_upcoming', 'calendar_account_name', 'last_modified_external',
            'is_synced', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'external_event_id', 'calendar_id', 'last_modified_external',
            'etag', 'is_synced', 'sync_errors', 'created_at', 'updated_at'
        ]
    
    def get_calendar_account_name(self, obj):
        return obj.calendar_account.display_name
    
    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None
    
    def get_lead_name(self, obj):
        return str(obj.lead) if obj.lead else None
    
    def get_task_title(self, obj):
        return obj.task.title if obj.task else None
    
    def get_duration_minutes(self, obj):
        return obj.duration_minutes
    
    def get_is_today(self, obj):
        return obj.is_today
    
    def get_is_upcoming(self, obj):
        return obj.is_upcoming
    
    def get_attendee_count(self, obj):
        return len(obj.attendees) if obj.attendees else 0
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_meeting_type_display(self, obj):
        if obj.meeting_type == 'zoom':
            return 'Zoom'
        elif obj.meeting_type == 'meet':
            return 'Google Meet'
        elif obj.meeting_type == 'teams':
            return 'Microsoft Teams'
        elif obj.meeting_url:
            return 'Video Meeting'
        return None


class MeetingTemplateSerializer(serializers.ModelSerializer):
    preferred_meeting_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MeetingTemplate
        fields = [
            'id', 'name', 'description', 'default_duration', 'default_title',
            'default_description', 'default_location', 'include_video_link',
            'preferred_meeting_type', 'preferred_meeting_type_display',
            'send_calendar_invite', 'create_follow_up_task', 'follow_up_task_days',
            'follow_up_task_title', 'is_active', 'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'usage_count', 'created_at', 'updated_at']
    
    def get_preferred_meeting_type_display(self, obj):
        return obj.get_preferred_meeting_type_display()


class CalendarEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'location', 'start_datetime', 'end_datetime',
            'all_day', 'client', 'lead', 'task', 'attendees'
        ]
    
    def validate(self, data):
        # Validate start/end times
        if data['end_datetime'] <= data['start_datetime']:
            raise serializers.ValidationError("End time must be after start time")
        
        # Validate client/lead association
        client = data.get('client')
        lead = data.get('lead')
        if client and lead:
            raise serializers.ValidationError("Event cannot be associated with both client and lead")
        
        return data


class CalendarEventReminderSerializer(serializers.ModelSerializer):
    reminder_type_display = serializers.SerializerMethodField()
    event_title = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarEventReminder
        fields = [
            'id', 'reminder_type', 'reminder_type_display', 'minutes_before',
            'remind_at', 'is_sent', 'sent_at', 'error_message', 'event_title', 'created_at'
        ]
        read_only_fields = ['id', 'remind_at', 'is_sent', 'sent_at', 'error_message', 'created_at']
    
    def get_reminder_type_display(self, obj):
        return obj.get_reminder_type_display()
    
    def get_event_title(self, obj):
        return obj.event.title


class MeetingScheduleSerializer(serializers.Serializer):
    """Serializer for scheduling meetings through templates"""
    
    template_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    start_datetime = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(required=False)
    
    client_id = serializers.IntegerField(required=False, allow_null=True)
    lead_id = serializers.IntegerField(required=False, allow_null=True)
    
    attendee_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        allow_empty=True
    )
    
    include_video_link = serializers.BooleanField(required=False)
    meeting_type = serializers.ChoiceField(
        choices=[('zoom', 'Zoom'), ('meet', 'Google Meet'), ('teams', 'Microsoft Teams')],
        required=False
    )
    
    def validate(self, data):
        # Validate template exists
        template_id = data.get('template_id')
        if template_id:
            from django.shortcuts import get_object_or_404
            template = get_object_or_404(MeetingTemplate, id=template_id, user=self.context['request'].user)
            data['template'] = template
        
        # Validate client/lead
        client_id = data.get('client_id')
        lead_id = data.get('lead_id')
        if client_id and lead_id:
            raise serializers.ValidationError("Meeting cannot be associated with both client and lead")
        
        return data


# =============================================================================
# DOCUMENT MANAGEMENT SERIALIZERS
# =============================================================================

# Import document serializers from the dedicated module
from .serializers.document_serializers import (
    DocumentSerializer, DocumentListSerializer, DocumentCreateSerializer,
    DocumentCategorySerializer, DocumentVersionSerializer, DocumentPermissionSerializer,
    DocumentAuditLogSerializer, DocumentTemplateSerializer, DocumentRetentionPolicySerializer,
    DocumentUploadSerializer, DocumentStatsSerializer, DocumentShareSerializer
)

