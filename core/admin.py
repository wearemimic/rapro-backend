from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    CustomUser, Client, LeadSource, Lead, EmailAccount, 
    Communication, SMSMessage, TwilioConfiguration, ActivityLog
)

# =============================================================================
# EXISTING MODEL ADMIN
# =============================================================================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'advisor', 'status', 'created_at')
    list_filter = ('status', 'gender', 'tax_status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'advisor__email')
    date_hierarchy = 'created_at'
    
# =============================================================================
# CRM MODEL ADMIN - Phase 1 Implementation
# =============================================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'phone_number', 'company_name', 'city', 'state', 'zip_code',
        'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'state')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'phone_number',
                'company_name', 'website_url', 'address', 'city',
                'state', 'zip_code',
                'white_label_company_name', 'white_label_support_email',
                'primary_color', 'logo'
            )
        }),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'phone_number', 'company_name',
                'website_url', 'address', 'city', 'state', 'zip_code',
                'white_label_company_name', 'white_label_support_email',
                'primary_color', 'logo', 'is_staff', 'is_active'
            ),
        }),
    )

    search_fields = ('email', 'username', 'first_name', 'last_name', 'company_name')
    ordering = ('email',)


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'utm_campaign', 'utm_source', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('name', 'utm_campaign', 'utm_source')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'source_type')
        }),
        ('UTM Parameters', {
            'fields': ('utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'),
            'classes': ('collapse',)
        }),
        ('Campaign IDs', {
            'fields': ('facebook_campaign_id', 'google_campaign_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status', 'advisor', 'lead_source_name', 'created_at')
    list_filter = ('status', 'lead_source__source_type', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'advisor__email')
    date_hierarchy = 'created_at'
    raw_id_fields = ('advisor', 'lead_source', 'converted_client')
    readonly_fields = ('created_at', 'updated_at', 'conversion_date')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Lead Management', {
            'fields': ('advisor', 'status', 'lead_source', 'converted_client', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'conversion_date'),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    
    def lead_source_name(self, obj):
        return obj.lead_source.name if obj.lead_source else '-'
    lead_source_name.short_description = 'Source'


@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'provider', 'user', 'sync_enabled', 'is_active', 'last_sync_at')
    list_filter = ('provider', 'sync_enabled', 'is_active', 'created_at')
    search_fields = ('email_address', 'user__email', 'display_name')
    readonly_fields = ('created_at', 'updated_at', 'last_sync_at', 'token_expires_at')
    
    fieldsets = (
        ('Account Details', {
            'fields': ('user', 'provider', 'email_address', 'display_name')
        }),
        ('OAuth2 Settings', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',),
            'description': 'OAuth2 tokens for Gmail/Outlook integration'
        }),
        ('IMAP/SMTP Settings', {
            'fields': ('imap_server', 'imap_port', 'smtp_server', 'smtp_port', 'use_ssl'),
            'classes': ('collapse',),
            'description': 'Manual IMAP/SMTP configuration for non-OAuth providers'
        }),
        ('Sync Configuration', {
            'fields': ('sync_enabled', 'sync_folders', 'sync_history_id', 'last_sync_at')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('subject_truncated', 'communication_type', 'direction', 'recipient', 'advisor', 'created_at', 'sync_status')
    list_filter = ('communication_type', 'direction', 'sync_status', 'created_at', 'is_read')
    search_fields = ('subject', 'content', 'from_address', 'advisor__email')
    date_hierarchy = 'created_at'
    raw_id_fields = ('advisor', 'client', 'lead', 'email_account')
    readonly_fields = ('created_at', 'updated_at', 'read_at', 'sent_at')
    
    fieldsets = (
        ('Communication Details', {
            'fields': ('communication_type', 'direction', 'subject', 'content')
        }),
        ('Participants', {
            'fields': ('advisor', 'client', 'lead')
        }),
        ('Email Details', {
            'fields': ('email_account', 'from_address', 'to_addresses', 'cc_addresses', 'bcc_addresses'),
            'classes': ('collapse',)
        }),
        ('Email Tracking', {
            'fields': ('provider_message_id', 'message_id_header', 'thread_id', 'in_reply_to'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'sent_at', 'sync_status', 'sync_direction')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def subject_truncated(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_truncated.short_description = 'Subject'
    
    def recipient(self, obj):
        if obj.client:
            return f"Client: {obj.client}"
        elif obj.lead:
            return f"Lead: {obj.lead}"
        return "-"
    recipient.short_description = 'Recipient'


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ('body_truncated', 'direction', 'recipient', 'from_number', 'to_number', 'status', 'created_at')
    list_filter = ('direction', 'status', 'created_at')
    search_fields = ('body', 'from_number', 'to_number', 'twilio_sid')
    date_hierarchy = 'created_at'
    raw_id_fields = ('advisor', 'client', 'lead')
    readonly_fields = ('created_at', 'sent_at', 'twilio_sid')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('direction', 'from_number', 'to_number', 'body', 'status')
        }),
        ('Recipients', {
            'fields': ('advisor', 'client', 'lead')
        }),
        ('Twilio Data', {
            'fields': ('twilio_sid', 'sent_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
    
    def body_truncated(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_truncated.short_description = 'Message'
    
    def recipient(self, obj):
        if obj.client:
            return f"Client: {obj.client}"
        elif obj.lead:
            return f"Lead: {obj.lead}"
        return "-"
    recipient.short_description = 'Recipient'


@admin.register(TwilioConfiguration)
class TwilioConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'phone_number', 'account_sid')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Account Details', {
            'fields': ('user', 'account_sid', 'auth_token', 'phone_number')
        }),
        ('Configuration', {
            'fields': ('webhook_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'user', 'target', 'description_truncated', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('description', 'user__email')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'client', 'lead')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('activity_type', 'user', 'description', 'metadata')
        }),
        ('Related Objects', {
            'fields': ('client', 'lead')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def description_truncated(self, obj):
        return obj.description[:75] + '...' if len(obj.description) > 75 else obj.description
    description_truncated.short_description = 'Description'
    
    def target(self, obj):
        if obj.client:
            return f"Client: {obj.client}"
        elif obj.lead:
            return f"Lead: {obj.lead}"
        return "-"
    target.short_description = 'Target'