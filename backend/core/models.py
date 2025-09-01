# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.utils import timezone
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
import json



# Custom user manager to use email instead of username
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    white_label_company_name = models.CharField(max_length=100, blank=True)
    white_label_support_email = models.EmailField(blank=True)
    primary_color = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    custom_disclosure = models.TextField(blank=True, help_text="Custom disclosure text to appear on scenario reports")

    # Stripe related fields
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    subscription_status = models.CharField(max_length=50, blank=True)
    subscription_plan = models.CharField(max_length=20, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    # Admin related fields
    is_platform_admin = models.BooleanField(default=False, help_text="Designates whether the user has admin access to platform management")
    admin_role = models.CharField(
        max_length=50, 
        blank=True,
        choices=[
            ('super_admin', 'Super Administrator'),
            ('admin', 'Administrator'),
            ('support', 'Support Staff'),
            ('analyst', 'Business Analyst'),
            ('billing', 'Billing Administrator'),
        ],
        help_text="Specific admin role defining access level"
    )
    admin_permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom permissions dictionary for granular access control"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email

    @property
    def is_subscription_active(self):
        return self.subscription_status == 'active' and (
            self.subscription_end_date is None or 
            self.subscription_end_date > timezone.now()
        )
    
    # Admin helper methods
    @property
    def is_admin_user(self):
        """Returns True if user has any admin privileges"""
        return self.is_platform_admin or self.is_superuser or self.is_staff
    
    def has_admin_permission(self, permission_key):
        """Check if user has specific admin permission"""
        if self.admin_role == 'super_admin':
            return True
        return self.admin_permissions.get(permission_key, False)
    
    def get_admin_role_display_name(self):
        """Get human-readable admin role name"""
        role_dict = dict(self._meta.get_field('admin_role').choices)
        return role_dict.get(self.admin_role, 'No Admin Role')
    
    def can_access_admin_section(self, section):
        """Check access to specific admin sections"""
        if not self.is_admin_user:
            return False
        
        # Super admins can access everything
        if self.admin_role == 'super_admin':
            return True
            
        # Define section permissions
        section_permissions = {
            'user_management': ['admin', 'support'],
            'billing': ['admin', 'billing'],
            'analytics': ['admin', 'analyst'],
            'system_monitoring': ['admin'],
            'support_tools': ['admin', 'support'],
        }
        
        allowed_roles = section_permissions.get(section, [])
        return self.admin_role in allowed_roles
    
class Client(models.Model):
    # advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients'
    )
    
    # Identifying information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    birthdate = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    tax_status = models.CharField(max_length=50, choices=[
        ('Single', 'Single'),
        ('Married Filing Jointly', 'Married Filing Jointly'),
        ('Married Filing Separately', 'Married Filing Separately'),
        ('Head of Household', 'Head of Household'),
        ('Qualifying Widow(er)', 'Qualifying Widow(er)')
    ])

    # Timestamps and notes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)
    
    # Portal Access Fields
    portal_access_enabled = models.BooleanField(default=False)
    portal_invitation_sent_at = models.DateTimeField(null=True, blank=True)
    portal_invitation_token = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    portal_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='client_portal_access'
    )
    portal_last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('reviewed', 'Reviewed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')


class Spouse(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='spouse')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        import datetime
        
        if self.birthdate:
            current_year = timezone.now().year
            min_year = 1900
            max_year = current_year
            
            if self.birthdate.year < min_year or self.birthdate.year > max_year:
                raise ValidationError(f'Spouse birthdate year must be between {min_year} and {max_year}')
                
            # Check reasonable age range (18-120 years old)
            age = current_year - self.birthdate.year
            if age < 18 or age > 120:
                raise ValidationError(f'Spouse age ({age}) must be between 18 and 120 years old')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Spouse of {self.client.first_name} {self.client.last_name}"
    
class Scenario(models.Model):
    client = models.ForeignKey(Client, related_name='scenarios', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    retirement_age = models.PositiveIntegerField(default=65)
    medicare_age = models.PositiveIntegerField(default=65)
    spouse_retirement_age = models.PositiveIntegerField(blank=True, null=True, default=65)
    spouse_medicare_age = models.PositiveIntegerField(blank=True, null=True, default=65)
    mortality_age = models.PositiveIntegerField(default=90)
    spouse_mortality_age = models.PositiveIntegerField(blank=True, null=True, default=90)
    retirement_year = models.PositiveIntegerField(default=2025)
    share_with_client = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    part_b_inflation_rate = models.FloatField(default=6.0)
    part_d_inflation_rate = models.FloatField(default=6.0)
    FRA_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roth_conversion_start_year = models.PositiveIntegerField(null=True, blank=True)
    roth_conversion_duration = models.PositiveIntegerField(null=True, blank=True)
    roth_conversion_annual_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    apply_standard_deduction = models.BooleanField(default=True, help_text="Apply IRS standard deduction in tax calculations.")
    income_vs_cost_percent = models.IntegerField(default=0, help_text="Percentage of federal tax + medicare to gross income")
    medicare_irmaa_percent = models.IntegerField(default=0, help_text="Percentage of IRMAA surcharges to total medicare costs")
    primary_state = models.CharField(max_length=50, blank=True, default='', help_text="Primary tax state for this scenario")
    
    # Social Security claiming strategy fields
    primary_ss_claiming_age = models.FloatField(null=True, blank=True, help_text="Primary client's Social Security claiming age")
    spouse_ss_claiming_age = models.FloatField(null=True, blank=True, help_text="Spouse's Social Security claiming age")
    ss_include_irmaa = models.BooleanField(default=False, help_text="Include IRMAA impact in Social Security analysis")
    
    # Social Security adjustment fields
    reduction_2030_ss = models.BooleanField(default=False, help_text="Apply Social Security benefit reduction")
    ss_adjustment_year = models.PositiveIntegerField(default=2030, help_text="Year to start Social Security adjustment")
    ss_adjustment_direction = models.CharField(max_length=20, default='decrease', help_text="Direction of SS adjustment")
    ss_adjustment_type = models.CharField(max_length=20, default='percentage', help_text="Type of SS adjustment")
    ss_adjustment_amount = models.FloatField(default=23.0, help_text="Amount of SS adjustment")
    
    # Tax Settings fields
    federal_standard_deduction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Federal standard deduction amount")
    state_standard_deduction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="State standard deduction amount")
    custom_annual_deduction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Custom annual deduction amount")
    primary_blind = models.BooleanField(default=False, help_text="Primary client is blind (additional deduction)")
    spouse_blind = models.BooleanField(default=False, help_text="Spouse is blind (additional deduction)")
    is_dependent = models.BooleanField(default=False, help_text="Filed as dependent (affects deduction limits)")

    def __str__(self):
        return f"{self.name} ({self.client.first_name})"


# IncomeSource model
class IncomeSource(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='income_sources')
    OWNED_BY_CHOICES = [
        ('primary', 'Primary'),
        ('spouse', 'Spouse')
    ]
    owned_by = models.CharField(max_length=10, choices=OWNED_BY_CHOICES)
    income_type = models.CharField(max_length=200)
    income_name = models.CharField(max_length=50)
    current_asset_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    age_to_begin_withdrawal = models.PositiveIntegerField(null=True, blank=True)
    age_to_end_withdrawal = models.PositiveIntegerField()
    rate_of_return = models.FloatField(default=0)
    cola = models.FloatField(default=0)
    exclusion_ratio = models.FloatField(default=0)
    tax_rate = models.FloatField(default=0)
    max_to_convert = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Maximum amount to convert to Roth")
    age_established = models.PositiveIntegerField(null=True, blank=True, help_text="Age when the asset was established")
    is_contributing = models.BooleanField(default=False, help_text="Currently contributing to this investment")
    employer_match = models.FloatField(default=0, help_text="Employer contribution match percentage")
    age_last_contribution = models.PositiveIntegerField(null=True, blank=True, help_text="Age when contributions will end")

    def __str__(self):
        return f"{self.income_type} for {self.scenario.name}"


# YearlyCalculation model
class YearlyCalculation(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='yearly_calculations')
    year = models.PositiveIntegerField()
    age = models.PositiveIntegerField()
    spouse_age = models.PositiveIntegerField(null=True, blank=True)
    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    taxable_income = models.DecimalField(max_digits=12, decimal_places=2)
    federal_tax = models.DecimalField(max_digits=12, decimal_places=2)
    medicare_base = models.DecimalField(max_digits=12, decimal_places=2)
    irmaa_surcharge = models.DecimalField(max_digits=12, decimal_places=2)
    net_income = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.year} - {self.scenario.name}"

class RealEstate(models.Model):
    client = models.ForeignKey(Client, related_name='real_estate', on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip} for {self.client}"

def template_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/templates/client_<id>/<uuid>_<filename>
    return f'templates/client_{instance.client.id}/{uuid.uuid4()}_{filename}'

def slide_thumbnail_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/templates/client_<id>/template_<id>/slides/<uuid>_<filename>
    return f'templates/client_{instance.template.client.id}/template_{instance.template.id}/slides/{uuid.uuid4()}_{filename}'

class ReportTemplate(models.Model):
    """Model for storing PowerPoint report templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=template_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.client.full_name}"

class TemplateSlide(models.Model):
    """Model for storing individual slides from a PowerPoint template"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='slides')
    thumbnail = models.ImageField(upload_to=slide_thumbnail_path)
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Slide {self.order} - {self.template.name}"


class ComparisonPreference(models.Model):
    """Store user's default scenario comparison selections for each client"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    scenario1 = models.ForeignKey('Scenario', on_delete=models.SET_NULL, null=True, blank=True, related_name='comparison_scenario1')
    scenario2 = models.ForeignKey('Scenario', on_delete=models.SET_NULL, null=True, blank=True, related_name='comparison_scenario2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'client']
        
    def __str__(self):
        return f"{self.user.email} - {self.client} comparison preferences"


# =============================================================================
# CRM MODELS - Phase 1 Implementation
# =============================================================================

class LeadSource(models.Model):
    """Model for tracking lead sources and campaign attribution"""
    SOURCE_TYPES = [
        ('facebook', 'Facebook Ad'),
        ('google', 'Google Ad'),
        ('email', 'Email Campaign'),
        ('referral', 'Referral'),
        ('website', 'Website'),
        ('social', 'Social Media'),
        ('direct', 'Direct'),
    ]
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_term = models.CharField(max_length=100, blank=True)
    utm_content = models.CharField(max_length=100, blank=True)
    facebook_campaign_id = models.CharField(max_length=100, blank=True)
    google_campaign_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['source_type']),
            models.Index(fields=['utm_campaign']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"


class Lead(models.Model):
    """Model for tracking prospects before they become clients"""
    STATUS_CHOICES = [
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted to Client'),
        ('lost', 'Lost'),
    ]
    
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leads'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    lead_source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True, blank=True)
    converted_client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conversion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['advisor', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"


class EmailAccount(models.Model):
    """Model for storing email account configurations (Gmail, Outlook, etc.)"""
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook/Office365'),
        ('imap', 'IMAP/SMTP'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_accounts'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    email_address = models.EmailField()
    display_name = models.CharField(max_length=100, blank=True)
    
    # OAuth2 tokens (encrypted in production)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # IMAP/SMTP settings (for non-OAuth providers)
    imap_server = models.CharField(max_length=100, blank=True)
    imap_port = models.IntegerField(null=True, blank=True)
    smtp_server = models.CharField(max_length=100, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    use_ssl = models.BooleanField(default=True)
    
    # Sync settings
    sync_enabled = models.BooleanField(default=True)
    sync_folders = models.JSONField(default=list, help_text="Folders/labels to sync")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_history_id = models.CharField(max_length=100, blank=True, help_text="For Gmail History API")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'email_address']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['provider']),
        ]
    
    def __str__(self):
        return f"{self.email_address} ({self.provider})"


class Communication(models.Model):
    """Model for tracking all client communications"""
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('call', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
        ('internal', 'Internal Note'),
    ]
    
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='communications'
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='communications', null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='communications', null=True, blank=True)
    
    communication_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    subject = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    
    # Email-specific fields
    email_account = models.ForeignKey(EmailAccount, on_delete=models.SET_NULL, null=True, blank=True)
    provider_message_id = models.CharField(max_length=255, blank=True, help_text="Gmail/Outlook message ID")
    message_id_header = models.CharField(max_length=255, blank=True, help_text="RFC822 Message-ID header")
    thread_id = models.CharField(max_length=255, blank=True)
    in_reply_to = models.CharField(max_length=255, blank=True)
    
    # Metadata
    from_address = models.EmailField(blank=True)
    to_addresses = models.JSONField(default=list)
    cc_addresses = models.JSONField(default=list)
    bcc_addresses = models.JSONField(default=list)
    
    # Tracking fields
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # AI Analysis fields
    ai_sentiment_score = models.FloatField(
        null=True, 
        blank=True,
        help_text="AI sentiment analysis score (-1.0 to 1.0, negative=negative, positive=positive)"
    )
    ai_sentiment_label = models.CharField(
        max_length=20,
        choices=[
            ('positive', 'Positive'),
            ('negative', 'Negative'),
            ('neutral', 'Neutral'),
            ('mixed', 'Mixed')
        ],
        blank=True
    )
    ai_urgency_score = models.FloatField(
        null=True,
        blank=True,
        help_text="AI urgency detection score (0.0 to 1.0)"
    )
    ai_priority_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Overall priority score combining sentiment, urgency, and client value"
    )
    ai_topics = models.JSONField(
        default=list,
        help_text="AI-detected topics/categories in the communication"
    )
    ai_suggested_response = models.TextField(
        blank=True,
        help_text="AI-generated suggested response"
    )
    ai_response_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence level of AI response suggestion (0.0 to 1.0)"
    )
    ai_analysis_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When AI analysis was performed"
    )
    ai_model_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Version of AI model used for analysis"
    )
    
    # Sync fields
    sync_status = models.CharField(
        max_length=20,
        choices=[('synced', 'Synced'), ('pending', 'Pending'), ('error', 'Error')],
        default='synced'
    )
    sync_direction = models.CharField(
        max_length=20,
        choices=[('from_email', 'From Email'), ('from_crm', 'From CRM')],
        blank=True
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['advisor', 'created_at']),
            models.Index(fields=['client', 'created_at']),
            models.Index(fields=['lead', 'created_at']),
            models.Index(fields=['communication_type', 'created_at']),
            models.Index(fields=['provider_message_id']),
            models.Index(fields=['thread_id']),
        ]
        ordering = ['-created_at']
    
    def clean(self):
        """Ensure either client or lead is specified"""
        if not self.client and not self.lead:
            raise ValidationError("Communication must be associated with either a client or lead")
        if self.client and self.lead:
            raise ValidationError("Communication cannot be associated with both client and lead")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        recipient = self.client or self.lead
        return f"{self.communication_type} - {recipient} ({self.created_at.strftime('%Y-%m-%d')})"


class SMSMessage(models.Model):
    """Model for SMS message tracking (Twilio integration)"""
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sms_messages'
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sms_messages', null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='sms_messages', null=True, blank=True)
    
    # Twilio fields
    twilio_sid = models.CharField(max_length=100, unique=True)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    body = models.TextField()
    status = models.CharField(max_length=20)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['advisor', 'created_at']),
            models.Index(fields=['client', 'created_at']),
            models.Index(fields=['lead', 'created_at']),
            models.Index(fields=['from_number', 'to_number']),
        ]
        ordering = ['-created_at']
    
    def clean(self):
        """Ensure either client or lead is specified"""
        if not self.client and not self.lead:
            raise ValidationError("SMS message must be associated with either a client or lead")
        if self.client and self.lead:
            raise ValidationError("SMS message cannot be associated with both client and lead")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        recipient = self.client or self.lead
        return f"SMS to {recipient} ({self.created_at.strftime('%Y-%m-%d')})"


class TwilioConfiguration(models.Model):
    """Model for storing Twilio account configurations"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='twilio_config'
    )
    account_sid = models.CharField(max_length=100)
    auth_token = models.CharField(max_length=100)  # Will be encrypted in production
    phone_number = models.CharField(max_length=20)
    webhook_url = models.URLField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Twilio config for {self.user.email}"


class ActivityLog(models.Model):
    """Model for tracking all CRM activities for the dashboard"""
    ACTIVITY_TYPES = [
        ('email_received', 'Email Received'),
        ('email_sent', 'Email Sent'),
        ('sms_received', 'SMS Received'),
        ('sms_sent', 'SMS Sent'),
        ('call_logged', 'Phone Call'),
        ('meeting_scheduled', 'Meeting Scheduled'),
        ('task_created', 'Task Created'),
        ('task_completed', 'Task Completed'),
        ('document_uploaded', 'Document Uploaded'),
        ('note_added', 'Note Added'),
        ('lead_converted', 'Lead Converted to Client'),
        ('scenario_created', 'Scenario Created'),
        ('report_generated', 'Report Generated'),
    ]
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict, help_text="Activity-specific data")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'user']),
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.activity_type} - {self.user.email} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class TaskTemplate(models.Model):
    """Template for creating recurring or standard tasks"""
    
    TRIGGER_CHOICES = [
        ('manual', 'Manual Creation'),
        ('client_created', 'Client Created'),
        ('scenario_completed', 'Scenario Completed'),
        ('meeting_scheduled', 'Meeting Scheduled'),
        ('communication_received', 'Communication Received'),
        ('deadline_approaching', 'Deadline Approaching'),
        ('periodic', 'Periodic (Recurring)'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Task defaults from template
    default_title = models.CharField(max_length=255)
    default_priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'), 
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        default='medium'
    )
    estimated_duration_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Estimated hours to complete"
    )
    
    # Template triggers
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES, default='manual')
    trigger_conditions = models.JSONField(
        default=dict,
        help_text="Conditions for automatic task creation"
    )
    
    # Auto-assignment rules
    auto_assign_to_creator = models.BooleanField(default=True)
    auto_assign_to_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='auto_assigned_task_templates'
    )
    
    # Template metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_task_templates'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['trigger_type', 'is_active']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.trigger_type})"


class Task(models.Model):
    """Individual task for user/client management"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting for Response'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic task information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Relationships
    template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks'
    )
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    # Timing
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Task metadata
    tags = models.JSONField(default=list, help_text="Task tags for organization")
    attachments = models.JSONField(default=list, help_text="File attachments metadata")
    notes = models.TextField(blank=True, help_text="Progress notes and updates")
    
    # Notification settings
    reminder_sent = models.BooleanField(default=False)
    overdue_notification_sent = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'status', 'due_date']),
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['priority', 'due_date']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.email} ({self.status})"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.due_date or self.status in ['completed', 'cancelled']:
            return False
        return timezone.now() > self.due_date
    
    @property
    def priority_score(self):
        """Get numeric priority for sorting"""
        priority_map = {'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
        return priority_map.get(self.priority, 2)
    
    def mark_completed(self, user=None):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if user:
            self.notes += f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] Completed by {user.email}"
        self.save(update_fields=['status', 'completed_at', 'notes'])
        
        # Log activity
        ActivityLog.objects.create(
            activity_type='task_completed',
            user=user or self.assigned_to,
            client=self.client,
            description=f"Completed task: {self.title}",
            metadata={
                'task_id': self.id,
                'task_title': self.title,
                'priority': self.priority
            }
        )
    
    def mark_started(self, user=None):
        """Mark task as started"""
        if self.status == 'pending':
            self.status = 'in_progress'
            self.started_at = timezone.now()
            if user:
                self.notes += f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] Started by {user.email}"
            self.save(update_fields=['status', 'started_at', 'notes'])


class TaskComment(models.Model):
    """Comments and updates on tasks"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    
    # Comment metadata
    is_internal = models.BooleanField(
        default=True,
        help_text="Internal comments not visible to clients"
    )
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='task_mentions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment on {self.task.title} by {self.user.email}"


# =============================================================================
# CALENDAR INTEGRATION MODELS
# =============================================================================

class CalendarAccount(models.Model):
    """Calendar account integration (Google Calendar, Outlook Calendar)"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook Calendar'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # Account identification
    external_account_id = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    
    # OAuth tokens
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account settings
    is_active = models.BooleanField(default=True)
    sync_enabled = models.BooleanField(default=True)
    primary_calendar = models.BooleanField(default=False)  # User's primary calendar
    
    # Sync settings
    sync_past_days = models.PositiveIntegerField(
        default=30,
        help_text="Number of past days to sync events"
    )
    sync_future_days = models.PositiveIntegerField(
        default=90,
        help_text="Number of future days to sync events"
    )
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_token = models.TextField(blank=True)  # For incremental sync
    
    # Metadata
    timezone = models.CharField(max_length=50, default='America/New_York')
    calendar_list = models.JSONField(default=list, blank=True)  # Available calendars
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'provider', 'external_account_id']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['provider', 'sync_enabled']),
            models.Index(fields=['last_sync_at']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.get_provider_display()})"
    
    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expires_at:
            return True
        return timezone.now() >= self.token_expires_at


class CalendarEvent(models.Model):
    """Calendar events synced from external calendars"""
    
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('tentative', 'Tentative'), 
        ('cancelled', 'Cancelled'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('confidential', 'Confidential'),
    ]
    
    calendar_account = models.ForeignKey(CalendarAccount, on_delete=models.CASCADE)
    
    # Event identification
    external_event_id = models.CharField(max_length=255)
    calendar_id = models.CharField(max_length=255)  # External calendar ID
    
    # Event details
    title = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=500, blank=True)
    
    # Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Event properties
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    is_recurring = models.BooleanField(default=False)
    recurring_event_id = models.CharField(max_length=255, blank=True)
    
    # Attendees and organizer
    organizer_email = models.EmailField(blank=True)
    organizer_name = models.CharField(max_length=255, blank=True)
    attendees = models.JSONField(default=list, blank=True)  # List of attendee objects
    
    # Integration fields
    client = models.ForeignKey(
        'Client', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Client this meeting is associated with"
    )
    lead = models.ForeignKey(
        'Lead', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Lead this meeting is associated with"
    )
    task = models.ForeignKey(
        'Task', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Task this meeting is associated with"
    )
    
    # Meeting details
    meeting_url = models.URLField(blank=True)  # Zoom, Meet, Teams link
    meeting_type = models.CharField(max_length=50, blank=True)  # zoom, meet, teams
    meeting_id = models.CharField(max_length=255, blank=True)  # External meeting ID
    
    # Sync metadata
    last_modified_external = models.DateTimeField(null=True, blank=True)
    etag = models.CharField(max_length=255, blank=True)  # For change detection
    is_synced = models.BooleanField(default=True)
    sync_errors = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['calendar_account', 'external_event_id']]
        indexes = [
            models.Index(fields=['calendar_account', 'start_datetime']),
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['client', 'start_datetime']),
            models.Index(fields=['lead', 'start_datetime']),
            models.Index(fields=['status', 'start_datetime']),
            models.Index(fields=['is_synced', 'last_modified_external']),
        ]
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration_minutes(self):
        """Calculate event duration in minutes"""
        if self.end_datetime and self.start_datetime:
            return int((self.end_datetime - self.start_datetime).total_seconds() / 60)
        return 0
    
    @property
    def is_today(self):
        """Check if event is happening today"""
        today = timezone.now().date()
        return self.start_datetime.date() == today
    
    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        return self.start_datetime > timezone.now()
    
    def get_attendee_emails(self):
        """Extract list of attendee email addresses"""
        return [attendee.get('email', '') for attendee in self.attendees if attendee.get('email')]


class MeetingTemplate(models.Model):
    """Templates for creating meetings with clients/leads"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Default meeting settings
    default_duration = models.PositiveIntegerField(default=60, help_text="Default duration in minutes")
    default_title = models.CharField(max_length=255, blank=True)
    default_description = models.TextField(blank=True)
    default_location = models.CharField(max_length=255, blank=True)
    
    # Meeting type settings
    include_video_link = models.BooleanField(default=True)
    preferred_meeting_type = models.CharField(
        max_length=20, 
        choices=[('zoom', 'Zoom'), ('meet', 'Google Meet'), ('teams', 'Microsoft Teams')],
        default='zoom'
    )
    
    # Automation settings
    send_calendar_invite = models.BooleanField(default=True)
    create_follow_up_task = models.BooleanField(default=True)
    follow_up_task_days = models.PositiveIntegerField(default=1)
    follow_up_task_title = models.CharField(max_length=255, default="Follow up on meeting")
    
    # Template metadata
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['-usage_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """Increment usage counter when template is used"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class CalendarEventReminder(models.Model):
    """Reminders for calendar events"""
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('popup', 'Popup'),
        ('sms', 'SMS'),
    ]
    
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    
    # Timing
    minutes_before = models.PositiveIntegerField(help_text="Minutes before event to send reminder")
    remind_at = models.DateTimeField()  # Calculated reminder time
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['remind_at', 'is_sent']),
            models.Index(fields=['event', 'reminder_type']),
        ]
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} reminder for {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Calculate remind_at time
        if not self.remind_at and self.event:
            self.remind_at = self.event.start_datetime - timezone.timedelta(minutes=self.minutes_before)
        super().save(*args, **kwargs)


# ============================================================================
# DOCUMENT MANAGEMENT MODELS - Phase 3.1
# ============================================================================

class DocumentCategory(models.Model):
    """Organized document categories for financial advisor workflows"""
    
    CATEGORY_TYPES = [
        ('client_docs', 'Client Documents'),
        ('financial_plans', 'Financial Plans'), 
        ('investment_statements', 'Investment Statements'),
        ('insurance_policies', 'Insurance Policies'),
        ('tax_documents', 'Tax Documents'),
        ('estate_planning', 'Estate Planning'),
        ('compliance', 'Compliance Documents'),
        ('marketing', 'Marketing Materials'),
        ('contracts', 'Client Contracts'),
        ('forms', 'Forms & Applications'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=30, choices=CATEGORY_TYPES)
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    default_retention_years = models.IntegerField(default=7)  # FINRA standard
    requires_encryption = models.BooleanField(default=True)
    advisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Document Categories"
        unique_together = ['advisor', 'name']
        indexes = [
            models.Index(fields=['advisor', 'category_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.advisor.email})"


class Document(models.Model):
    """Core document model with FINRA compliance and security features"""
    
    DOCUMENT_STATUS = [
        ('processing', 'Processing'),
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('quarantined', 'Quarantined'),  # Failed security scan
        ('deleted', 'Soft Deleted'),
    ]
    
    RETENTION_STATUS = [
        ('active', 'Active Retention'),
        ('extended', 'Extended Retention'),
        ('pending_disposal', 'Pending Disposal'),
        ('disposed', 'Disposed'),
    ]
    
    COMPLIANCE_TYPES = [
        ('finra_3110', 'FINRA Rule 3110 - Books & Records'),
        ('finra_4511', 'FINRA Rule 4511 - Customer Account Info'),
        ('sec_17a4', 'SEC Rule 17a-4 - Record Retention'), 
        ('ria_204', 'RIA Rule 204-2 - Investment Adviser Records'),
        ('privacy_reg_sp', 'Regulation S-P - Privacy'),
        ('none', 'No Specific Requirement'),
    ]
    
    # Core identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Relationships
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    advisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='documents')
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True)
    parent_document = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    
    # File metadata
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    mime_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=64, unique=True)  # SHA-256 for deduplication
    
    # Storage information
    s3_bucket = models.CharField(max_length=100)
    s3_key = models.CharField(max_length=500)
    s3_version_id = models.CharField(max_length=100, blank=True)
    storage_class = models.CharField(max_length=50, default='STANDARD')
    
    # Security & compliance
    is_encrypted = models.BooleanField(default=True)
    encryption_key_id = models.CharField(max_length=100, blank=True)  # KMS Key ID
    virus_scan_status = models.CharField(max_length=20, default='pending')
    virus_scan_date = models.DateTimeField(null=True, blank=True)
    compliance_type = models.CharField(max_length=30, choices=COMPLIANCE_TYPES, default='none')
    contains_pii = models.BooleanField(default=False)
    contains_phi = models.BooleanField(default=False)
    
    # Status and workflow
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS, default='processing')
    is_client_visible = models.BooleanField(default=False)
    requires_signature = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    # Retention and disposal
    retention_status = models.CharField(max_length=20, choices=RETENTION_STATUS, default='active')
    retention_end_date = models.DateField(null=True, blank=True)
    disposal_scheduled_date = models.DateField(null=True, blank=True)
    disposal_method = models.CharField(max_length=50, blank=True)
    
    # Processing metadata
    text_content = models.TextField(blank=True)  # Extracted text for search
    thumbnail_s3_key = models.CharField(max_length=500, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    extracted_metadata = models.JSONField(default=dict)  # EXIF, PDF metadata, etc.
    
    # Audit fields
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    last_modified = models.DateTimeField(auto_now=True)
    
    # Search optimization
    search_vector = models.TextField(blank=True)  # For full-text search
    tags = models.JSONField(default=list)  # User-defined tags
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['advisor', '-uploaded_at']),
            models.Index(fields=['client', '-uploaded_at']),
            models.Index(fields=['status', 'retention_status']),
            models.Index(fields=['file_hash']),  # For deduplication
            models.Index(fields=['retention_end_date']),  # For cleanup jobs
            models.Index(fields=['category', '-uploaded_at']),
            models.Index(fields=['compliance_type']),
            models.Index(fields=['contains_pii', 'contains_phi']),
        ]

    def __str__(self):
        return f"{self.title or self.original_filename}"
    
    @property
    def file_size_mb(self):
        """Return file size in MB for display"""
        return round(self.file_size / (1024 * 1024), 2)
    
    def is_expired(self):
        """Check if document has passed retention period"""
        return (self.retention_end_date and 
                self.retention_end_date < timezone.now().date())


class DocumentVersion(models.Model):
    """Complete version history for regulatory compliance"""
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    s3_key = models.CharField(max_length=500)
    s3_version_id = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    file_hash = models.CharField(max_length=64)
    
    # Change tracking
    change_description = models.TextField(blank=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Regulatory compliance
    is_regulatory_version = models.BooleanField(default=False)
    compliance_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['document', 'version_number']
        ordering = ['-version_number']
        indexes = [
            models.Index(fields=['document', '-version_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.document.title} v{self.version_number}"


class DocumentPermission(models.Model):
    """Granular document access control system"""
    
    PERMISSION_TYPES = [
        ('view', 'View Only'),
        ('download', 'Download'),
        ('edit_metadata', 'Edit Metadata'),
        ('share', 'Share with Others'),
        ('delete', 'Delete'),
        ('full_control', 'Full Control'),
    ]
    
    PERMISSION_SCOPE = [
        ('document', 'Single Document'),
        ('category', 'Document Category'),
        ('client_all', 'All Client Documents'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    
    # Permission details
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    user_email = models.EmailField(blank=True)  # For external sharing
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    permission_scope = models.CharField(max_length=20, choices=PERMISSION_SCOPE)
    
    # Access control
    granted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # External sharing (client portal)
    share_token = models.CharField(max_length=100, blank=True, unique=True)
    download_limit = models.IntegerField(null=True, blank=True)
    downloads_used = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['share_token']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['document', 'permission_type']),
        ]
    
    def __str__(self):
        target = self.document or self.category or self.client
        user = self.user or self.user_email
        return f"{user} - {self.get_permission_type_display()} on {target}"


class DocumentAuditLog(models.Model):
    """Complete audit trail for FINRA compliance"""
    
    ACTION_TYPES = [
        ('uploaded', 'Document Uploaded'),
        ('viewed', 'Document Viewed'),
        ('downloaded', 'Document Downloaded'),
        ('shared', 'Document Shared'),
        ('modified', 'Metadata Modified'),
        ('version_created', 'New Version Created'),
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
        ('archived', 'Document Archived'),
        ('deleted', 'Document Deleted'),
        ('restored', 'Document Restored'),
        ('retention_extended', 'Retention Period Extended'),
        ('disposal_scheduled', 'Disposal Scheduled'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_TYPES)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Action details
    details = models.JSONField(default=dict)  # Action-specific metadata
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Compliance tracking
    session_id = models.CharField(max_length=100, blank=True)
    client_involved = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    compliance_relevant = models.BooleanField(default=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['document', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['compliance_relevant', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.document.title} by {self.user}"


class DocumentTemplate(models.Model):
    """Reusable document templates for common advisor forms"""
    
    TEMPLATE_TYPES = [
        ('client_onboarding', 'Client Onboarding'),
        ('risk_assessment', 'Risk Assessment'),
        ('financial_plan', 'Financial Plan Template'),
        ('investment_policy', 'Investment Policy Statement'),
        ('service_agreement', 'Service Agreement'),
        ('disclosure', 'Disclosure Document'),
        ('form_adv', 'Form ADV'),
        ('privacy_notice', 'Privacy Notice'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    description = models.TextField()
    
    # Template content
    base_document = models.ForeignKey(Document, on_delete=models.CASCADE)
    variable_fields = models.JSONField(default=dict)  # Fields to be filled
    instructions = models.TextField(blank=True)
    
    # Usage tracking
    advisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    times_used = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['advisor', 'name']
        indexes = [
            models.Index(fields=['advisor', 'template_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-times_used']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.advisor.email})"
    
    def increment_usage(self):
        """Increment usage counter when template is used"""
        self.times_used += 1
        self.save(update_fields=['times_used'])


class DocumentRetentionPolicy(models.Model):
    """Automated retention and disposal policies for compliance"""
    
    TRIGGER_TYPES = [
        ('document_upload', 'When Document Uploaded'),
        ('client_termination', 'When Client Relationship Ends'),
        ('fixed_date', 'Fixed Date'),
        ('custom_event', 'Custom Business Event'),
    ]
    
    DISPOSAL_METHODS = [
        ('secure_delete', 'Secure Deletion'),
        ('archive_only', 'Archive (No Access)'),
        ('transfer_custody', 'Transfer to Client'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)
    advisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    # Policy rules
    retention_years = models.IntegerField()
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict)  # Trigger-specific settings
    
    # Disposal configuration
    disposal_method = models.CharField(max_length=30, choices=DISPOSAL_METHODS)
    auto_disposal_enabled = models.BooleanField(default=False)
    notification_before_days = models.IntegerField(default=30)
    
    # Compliance
    regulatory_basis = models.TextField()  # Legal justification for retention period
    requires_approval = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Document Retention Policies"
        indexes = [
            models.Index(fields=['advisor', 'is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['auto_disposal_enabled']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.retention_years} years"


# Admin Audit Logging Models

class AdminAuditLog(models.Model):
    """
    Comprehensive audit logging for all admin actions
    """
    ACTION_TYPES = [
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('user_impersonated', 'User Impersonated'),
        ('admin_role_granted', 'Admin Role Granted'),
        ('admin_role_revoked', 'Admin Role Revoked'),
        ('permission_changed', 'Permission Changed'),
        ('system_setting_changed', 'System Setting Changed'),
        ('bulk_action_performed', 'Bulk Action Performed'),
        ('data_exported', 'Data Exported'),
        ('password_reset', 'Password Reset'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('login_failed', 'Login Failed'),
        ('access_denied', 'Access Denied'),
    ]
    
    # Who performed the action
    admin_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='admin_actions_performed',
        help_text="The admin user who performed this action"
    )
    
    # What action was performed
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField(help_text="Human-readable description of the action")
    
    # Target of the action (if applicable)
    target_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='admin_actions_received',
        null=True, 
        blank=True,
        help_text="The user who was the target of this action"
    )
    target_user_email = models.EmailField(blank=True, help_text="Email of target user at time of action")
    
    # Context and metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    
    # Action details
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional context about the action (e.g., what fields changed)"
    )
    
    # Before/after state for changes
    previous_state = models.JSONField(
        default=dict, 
        blank=True,
        help_text="State before the change"
    )
    new_state = models.JSONField(
        default=dict, 
        blank=True,
        help_text="State after the change"
    )
    
    # Risk and compliance
    risk_level = models.CharField(
        max_length=20, 
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'), 
            ('high', 'High Risk'),
            ('critical', 'Critical Risk')
        ],
        default='medium'
    )
    
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_admin_actions'
    )
    approval_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_audit_log'
        indexes = [
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['target_user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['risk_level', '-timestamp']),
            models.Index(fields=['-timestamp']),  # Most common query
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        target_info = f" -> {self.target_user_email}" if self.target_user_email else ""
        return f"{self.admin_user.email}: {self.action_type}{target_info} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, admin_user, action_type, description, target_user=None, 
                   metadata=None, previous_state=None, new_state=None, 
                   ip_address=None, user_agent=None, risk_level='medium'):
        """
        Convenience method to create audit log entries
        """
        return cls.objects.create(
            admin_user=admin_user,
            action_type=action_type,
            description=description,
            target_user=target_user,
            target_user_email=target_user.email if target_user else '',
            metadata=metadata or {},
            previous_state=previous_state or {},
            new_state=new_state or {},
            ip_address=ip_address,
            user_agent=user_agent or '',
            risk_level=risk_level
        )


class UserImpersonationLog(models.Model):
    """
    Specialized logging for user impersonation sessions
    """
    # Who is doing the impersonation
    admin_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='impersonation_sessions_started',
        help_text="The admin user performing the impersonation"
    )
    
    # Who is being impersonated
    target_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='impersonation_sessions_received',
        help_text="The user being impersonated"
    )
    target_user_email = models.EmailField(help_text="Email of impersonated user at start of session")
    
    # Session details
    session_key = models.CharField(max_length=255, unique=True)
    start_timestamp = models.DateTimeField(auto_now_add=True)
    end_timestamp = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Technical details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Justification and approval
    reason = models.TextField(help_text="Business justification for impersonation")
    approved_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='impersonation_approvals_granted',
        help_text="Admin who approved this impersonation (if required)"
    )
    
    # Activity tracking during impersonation
    actions_performed = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of actions performed during impersonation"
    )
    pages_accessed = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of pages/endpoints accessed during session"
    )
    
    # Risk assessment
    risk_score = models.IntegerField(
        default=50, 
        help_text="Risk score 1-100 based on user privileges and session duration"
    )
    flagged_for_review = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='impersonation_reviews_performed'
    )
    review_timestamp = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_impersonation_log'
        indexes = [
            models.Index(fields=['admin_user', '-start_timestamp']),
            models.Index(fields=['target_user', '-start_timestamp']),
            models.Index(fields=['is_active']),
            models.Index(fields=['flagged_for_review']),
            models.Index(fields=['session_key']),
            models.Index(fields=['-start_timestamp']),
        ]
        ordering = ['-start_timestamp']
    
    def __str__(self):
        status = "Active" if self.is_active else "Ended"
        return f"{self.admin_user.email} -> {self.target_user_email} ({status})"
    
    def end_session(self, actions=None, pages=None):
        """
        End the impersonation session and record activity
        """
        self.end_timestamp = timezone.now()
        self.is_active = False
        
        if actions:
            self.actions_performed = actions
        if pages:
            self.pages_accessed = pages
            
        # Calculate risk score based on session duration and activity
        if self.end_timestamp and self.start_timestamp:
            duration_hours = (self.end_timestamp - self.start_timestamp).total_seconds() / 3600
            self.risk_score = min(100, max(10, 
                int(50 + (duration_hours * 10) + (len(self.actions_performed) * 2))
            ))
            
        # Auto-flag for review if high risk
        if self.risk_score > 80 or len(self.actions_performed) > 20:
            self.flagged_for_review = True
            
        self.save()
        
        # Create audit log entry
        AdminAuditLog.log_action(
            admin_user=self.admin_user,
            action_type='user_impersonated',
            description=f'Ended impersonation of {self.target_user_email}',
            target_user=self.target_user,
            metadata={
                'session_duration_minutes': int((self.end_timestamp - self.start_timestamp).total_seconds() / 60),
                'actions_count': len(self.actions_performed),
                'pages_count': len(self.pages_accessed),
                'risk_score': self.risk_score,
                'reason': self.reason
            },
            risk_level='high' if self.risk_score > 80 else 'medium'
        )
    
    def add_action(self, action_description, page_url=None, metadata=None):
        """
        Record an action performed during impersonation
        """
        action_data = {
            'timestamp': timezone.now().isoformat(),
            'action': action_description,
            'metadata': metadata or {}
        }
        
        if page_url:
            action_data['page_url'] = page_url
            
        # Add to actions list
        if not isinstance(self.actions_performed, list):
            self.actions_performed = []
        self.actions_performed.append(action_data)
        
        # Add to pages list if URL provided
        if page_url:
            if not isinstance(self.pages_accessed, list):
                self.pages_accessed = []
            if page_url not in self.pages_accessed:
                self.pages_accessed.append(page_url)
        
        self.save(update_fields=['actions_performed', 'pages_accessed'])
    
    @property
    def session_duration(self):
        """
        Get session duration as timedelta
        """
        end_time = self.end_timestamp or timezone.now()
        return end_time - self.start_timestamp
    
    @property
    def session_duration_minutes(self):
        """
        Get session duration in minutes
        """
        return int(self.session_duration.total_seconds() / 60)


# ============================================================================
# Phase 2: Analytics & Monitoring Models
# ============================================================================

class RevenueMetric(models.Model):
    """Track detailed revenue metrics over time"""
    METRIC_TYPES = [
        ('mrr', 'Monthly Recurring Revenue'),
        ('arr', 'Annual Recurring Revenue'),
        ('churn_rate', 'Churn Rate'),
        ('ltv', 'Lifetime Value'),
        ('arpu', 'Average Revenue Per User'),
        ('new_revenue', 'New Revenue'),
        ('expansion_revenue', 'Expansion Revenue'),
        ('contraction_revenue', 'Contraction Revenue')
    ]
    
    date = models.DateField()
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Segmentation fields
    plan_type = models.CharField(max_length=50, blank=True)  # monthly, annual
    cohort_month = models.DateField(null=True, blank=True)
    
    # Metadata
    stripe_data = models.JSONField(default=dict, blank=True)
    calculation_method = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['date', 'metric_type', 'plan_type', 'cohort_month']
        indexes = [
            models.Index(fields=['date', 'metric_type']),
            models.Index(fields=['metric_type', 'plan_type']),
        ]
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.date}: ${self.value}"


class UserEngagementMetric(models.Model):
    """Track user behavior and engagement metrics"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField()
    
    # Activity metrics
    login_count = models.IntegerField(default=0)
    session_duration_minutes = models.IntegerField(default=0)
    pages_viewed = models.IntegerField(default=0)
    actions_performed = models.IntegerField(default=0)
    
    # Feature usage metrics
    scenarios_created = models.IntegerField(default=0)
    scenarios_modified = models.IntegerField(default=0)
    reports_generated = models.IntegerField(default=0)
    clients_added = models.IntegerField(default=0)
    communications_sent = models.IntegerField(default=0)
    
    # Engagement score (0-100)
    engagement_score = models.IntegerField(default=0)
    
    # Risk indicators
    is_at_risk = models.BooleanField(default=False)
    risk_factors = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['date', 'engagement_score']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['is_at_risk']),
        ]
    
    def calculate_engagement_score(self):
        """Calculate engagement score based on various activities"""
        score = 0
        
        # Login frequency (max 20 points)
        score += min(self.login_count * 5, 20)
        
        # Session duration (max 15 points)
        if self.session_duration_minutes > 0:
            score += min(self.session_duration_minutes / 10, 15)
        
        # Page views (max 10 points)
        score += min(self.pages_viewed, 10)
        
        # Scenarios activity (max 25 points)
        scenario_score = (self.scenarios_created * 5) + (self.scenarios_modified * 2)
        score += min(scenario_score, 25)
        
        # Reports generated (max 15 points)
        score += min(self.reports_generated * 3, 15)
        
        # Client management (max 10 points)
        score += min(self.clients_added * 2, 10)
        
        # Communications (max 5 points)
        score += min(self.communications_sent, 5)
        
        self.engagement_score = min(int(score), 100)
        return self.engagement_score
    
    def assess_churn_risk(self):
        """Assess if user is at risk of churning"""
        risk_factors = []
        
        # Low engagement
        if self.engagement_score < 20:
            risk_factors.append('low_engagement_score')
        
        # No recent activity
        if self.login_count == 0:
            risk_factors.append('no_recent_login')
        
        # No content creation
        if self.scenarios_created == 0 and self.clients_added == 0:
            risk_factors.append('no_content_creation')
        
        # Short sessions
        avg_session = self.session_duration_minutes / max(self.login_count, 1)
        if avg_session < 5:
            risk_factors.append('short_session_duration')
        
        self.risk_factors = risk_factors
        self.is_at_risk = len(risk_factors) >= 2
        
        return self.is_at_risk
    
    def __str__(self):
        return f"{self.user.email} - {self.date} (Score: {self.engagement_score})"


class ClientPortfolioAnalytics(models.Model):
    """Analytics for client portfolios across all advisors"""
    date = models.DateField()
    
    # Portfolio aggregates
    total_clients = models.IntegerField(default=0)
    total_scenarios = models.IntegerField(default=0)
    total_assets_tracked = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Distribution metrics
    avg_clients_per_advisor = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    avg_scenarios_per_client = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    avg_assets_per_client = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Age demographics
    clients_under_50 = models.IntegerField(default=0)
    clients_50_to_65 = models.IntegerField(default=0)
    clients_over_65 = models.IntegerField(default=0)
    
    # Geographic distribution
    geographic_data = models.JSONField(default=dict, blank=True)
    
    # Feature adoption
    roth_conversion_usage = models.IntegerField(default=0)
    social_security_planning_usage = models.IntegerField(default=0)
    monte_carlo_usage = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Portfolio Analytics - {self.date}"


class SystemPerformanceMetric(models.Model):
    """System performance and health metrics"""
    METRIC_TYPES = [
        ('response_time', 'API Response Time'),
        ('error_rate', 'Error Rate'),
        ('uptime', 'System Uptime'),
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('database_connections', 'Database Connections'),
        ('active_users', 'Active Users'),
        ('request_volume', 'Request Volume')
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=12, decimal_places=4)
    unit = models.CharField(max_length=20)  # ms, %, count, etc.
    
    # Context information
    endpoint = models.CharField(max_length=200, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp', 'metric_type']),
            models.Index(fields=['metric_type', 'endpoint']),
        ]
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}{self.unit} at {self.timestamp}"


class SupportTicket(models.Model):
    """Support ticket system for user issues"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_user', 'Waiting for User'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    
    CATEGORY_CHOICES = [
        ('billing', 'Billing Issue'),
        ('technical', 'Technical Problem'),
        ('feature_request', 'Feature Request'),
        ('bug_report', 'Bug Report'),
        ('account', 'Account Issue'),
        ('data', 'Data Issue'),
        ('integration', 'Integration Problem'),
        ('other', 'Other')
    ]
    
    # Basic ticket info
    ticket_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    assigned_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tickets'
    )
    
    # Ticket details
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # SLA tracking
    created_at = models.DateTimeField(auto_now_add=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # SLA targets (in hours)
    response_sla_hours = models.IntegerField(default=24)
    resolution_sla_hours = models.IntegerField(default=72)
    
    # Additional metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Internal fields
    internal_notes = models.TextField(blank=True)
    escalated = models.BooleanField(default=False)
    customer_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5 rating
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['assigned_admin', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_ticket_id()
        super().save(*args, **kwargs)
    
    def generate_ticket_id(self):
        """Generate unique ticket ID"""
        import random
        import string
        while True:
            ticket_id = 'RAP-' + ''.join(random.choices(string.digits, k=6))
            if not SupportTicket.objects.filter(ticket_id=ticket_id).exists():
                return ticket_id
    
    @property
    def is_sla_breached(self):
        """Check if SLA has been breached"""
        now = timezone.now()
        
        # Check response SLA
        if not self.first_response_at:
            response_time = now - self.created_at
            if response_time.total_seconds() > (self.response_sla_hours * 3600):
                return True
        
        # Check resolution SLA
        if not self.resolved_at and self.status not in ['resolved', 'closed']:
            resolution_time = now - self.created_at
            if resolution_time.total_seconds() > (self.resolution_sla_hours * 3600):
                return True
        
        return False
    
    @property
    def time_to_first_response(self):
        """Get time to first response in hours"""
        if self.first_response_at:
            delta = self.first_response_at - self.created_at
            return delta.total_seconds() / 3600
        return None
    
    @property
    def time_to_resolution(self):
        """Get time to resolution in hours"""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return delta.total_seconds() / 3600
        return None
    
    def __str__(self):
        return f"{self.ticket_id}: {self.subject}"


class SupportTicketComment(models.Model):
    """Comments/responses on support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    content = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal admin notes
    is_automated = models.BooleanField(default=False)  # Automated responses
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['ticket', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_id} by {self.user.email}"


class AlertRule(models.Model):
    """Configurable alert rules for system monitoring"""
    ALERT_TYPES = [
        ('metric_threshold', 'Metric Threshold'),
        ('error_rate', 'Error Rate'),
        ('user_activity', 'User Activity'),
        ('revenue_change', 'Revenue Change'),
        ('system_health', 'System Health'),
        ('sla_breach', 'SLA Breach')
    ]
    
    NOTIFICATION_CHANNELS = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('webhook', 'Webhook'),
        ('sms', 'SMS')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    
    # Rule configuration
    is_active = models.BooleanField(default=True)
    conditions = models.JSONField(default=dict)  # Flexible condition definition
    threshold_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    comparison_operator = models.CharField(max_length=10, default='>')  # >, <, >=, <=, ==
    
    # Notification settings
    notification_channels = models.JSONField(default=list)
    recipients = models.JSONField(default=list)  # Email addresses, Slack channels, etc.
    
    # Timing settings
    check_interval_minutes = models.IntegerField(default=5)
    cooldown_minutes = models.IntegerField(default=60)  # Prevent spam
    
    # Alert history
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'alert_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_alert_type_display()})"


class AlertNotification(models.Model):
    """Record of sent alert notifications"""
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered')
    ]
    
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='notifications')
    
    # Alert details
    alert_message = models.TextField()
    alert_data = models.JSONField(default=dict)  # Context data that triggered alert
    severity = models.CharField(max_length=20, default='medium')
    
    # Notification details
    notification_channel = models.CharField(max_length=50)
    recipient = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    
    # Delivery tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['alert_rule', 'created_at']),
            models.Index(fields=['status', 'notification_channel']),
        ]
    
    def __str__(self):
        return f"Alert: {self.alert_rule.name} to {self.recipient}"


# ============= CONFIGURATION MANAGEMENT MODELS =============

class FeatureFlag(models.Model):
    """Feature flag management for gradual rollout and A/B testing"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    
    # Rollout configuration
    rollout_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    user_segments = models.JSONField(default=list)  # User groups to target
    
    # Environment controls
    enabled_in_dev = models.BooleanField(default=True)
    enabled_in_staging = models.BooleanField(default=False)
    enabled_in_prod = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval workflow
    approval_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_feature_flags')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'is_enabled']),
            models.Index(fields=['approval_status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Feature Flag: {self.name}"


class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    
    ENVIRONMENT_CHOICES = [
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
    ]
    
    # Configuration identification
    config_key = models.CharField(max_length=100, unique=True)
    config_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('system', 'System'),
        ('security', 'Security'),
        ('integration', 'Integration'),
        ('ui', 'User Interface'),
        ('performance', 'Performance'),
        ('billing', 'Billing'),
    ])
    
    # Value and type
    config_value = models.TextField()
    config_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('float', 'Float'),
    ], default='string')
    
    # Environment-specific overrides
    environment = models.CharField(max_length=20, choices=ENVIRONMENT_CHOICES, default='production')
    
    # Security and validation
    is_sensitive = models.BooleanField(default=False)  # For encrypted storage
    validation_rule = models.TextField(blank=True)  # Regex or custom validation
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval workflow
    approval_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_configurations')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('config_key', 'environment')
        indexes = [
            models.Index(fields=['category', 'environment']),
            models.Index(fields=['approval_status', 'updated_at']),
        ]
    
    def __str__(self):
        return f"{self.config_name} ({self.environment})"


class IntegrationSettings(models.Model):
    """Third-party integration configuration"""
    
    INTEGRATION_TYPES = [
        ('auth0', 'Auth0'),
        ('stripe', 'Stripe'), 
        ('aws', 'AWS'),
        ('twilio', 'Twilio'),
        ('sendgrid', 'SendGrid'),
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
    ]
    
    integration_name = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    environment = models.CharField(max_length=20, choices=[
        ('development', 'Development'),
        ('staging', 'Staging'),
        ('production', 'Production'),
    ])
    
    # Configuration data (encrypted)
    config_data = models.JSONField(default=dict)  # Will be encrypted
    
    # Connection status
    is_active = models.BooleanField(default=True)
    last_tested = models.DateTimeField(null=True, blank=True)
    test_status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='pending')
    test_error_message = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval workflow
    approval_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_integrations')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('integration_name', 'environment')
        indexes = [
            models.Index(fields=['integration_name', 'is_active']),
            models.Index(fields=['approval_status', 'updated_at']),
        ]
    
    def __str__(self):
        return f"{self.get_integration_name_display()} - {self.environment}"


class EmailTemplate(models.Model):
    """Email template management"""
    
    TEMPLATE_TYPES = [
        ('welcome', 'Welcome Email'),
        ('password_reset', 'Password Reset'),
        ('subscription_created', 'Subscription Created'),
        ('subscription_cancelled', 'Subscription Cancelled'),
        ('trial_expiring', 'Trial Expiring'),
        ('payment_failed', 'Payment Failed'),
        ('system_maintenance', 'System Maintenance'),
        ('newsletter', 'Newsletter'),
        ('custom', 'Custom'),
    ]
    
    template_name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)
    
    # Email content
    subject = models.CharField(max_length=200)
    html_body = models.TextField()
    text_body = models.TextField(blank=True)
    
    # Template variables and personalization
    variables = models.JSONField(default=list)  # Available variables for template
    default_sender_name = models.CharField(max_length=100, blank=True)
    default_sender_email = models.EmailField(blank=True)
    
    # Status and usage
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval workflow
    approval_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_email_templates')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['approval_status', 'updated_at']),
        ]
    
    def __str__(self):
        return f"Email Template: {self.template_name}"


class ConfigurationAuditLog(models.Model):
    """Audit trail for all configuration changes"""
    
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('activate', 'Activated'),
        ('deactivate', 'Deactivated'),
    ]
    
    OBJECT_TYPES = [
        ('feature_flag', 'Feature Flag'),
        ('system_config', 'System Configuration'),
        ('integration', 'Integration Setting'),
        ('email_template', 'Email Template'),
    ]
    
    # What changed
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    object_id = models.IntegerField()
    object_name = models.CharField(max_length=200)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    # Change details
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    change_reason = models.TextField(blank=True)
    
    # User and context
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Approval workflow tracking
    requires_approval = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, blank=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='configuration_approvals')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['approval_status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()}: {self.object_name} by {self.user}"


# ============= ADVANCED ANALYTICS & REPORTING MODELS =============

class CustomReport(models.Model):
    """Custom report builder for advanced analytics"""
    
    REPORT_TYPES = [
        ('user_analytics', 'User Analytics'),
        ('revenue_analytics', 'Revenue Analytics'),
        ('engagement_analytics', 'Engagement Analytics'),
        ('performance_analytics', 'Performance Analytics'),
        ('churn_analytics', 'Churn Analytics'),
        ('custom', 'Custom Query'),
    ]
    
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    report_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    
    # Report configuration
    data_sources = models.JSONField(default=list)  # Tables/models to query
    filters = models.JSONField(default=dict)  # Filter conditions
    grouping = models.JSONField(default=list)  # Group by fields
    aggregations = models.JSONField(default=list)  # Sum, count, avg, etc.
    sorting = models.JSONField(default=list)  # Sort order
    
    # Visualization settings
    chart_type = models.CharField(max_length=50, blank=True)  # line, bar, pie, table
    chart_config = models.JSONField(default=dict)  # Chart-specific settings
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_users = models.ManyToManyField(CustomUser, blank=True, related_name='accessible_reports')
    allowed_roles = models.JSONField(default=list)  # Admin roles that can access
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['report_type', 'created_by']),
            models.Index(fields=['is_public', '-created_at']),
        ]
    
    def __str__(self):
        return f"Report: {self.report_name}"


class ReportSchedule(models.Model):
    """Automated report scheduling and delivery"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('disabled', 'Disabled'),
    ]
    
    report = models.ForeignKey(CustomReport, on_delete=models.CASCADE, related_name='schedules')
    schedule_name = models.CharField(max_length=200)
    
    # Schedule configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    day_of_week = models.IntegerField(null=True, blank=True)  # 0-6 for weekly
    day_of_month = models.IntegerField(null=True, blank=True)  # 1-31 for monthly
    time_of_day = models.TimeField()  # When to run
    
    # Delivery configuration
    email_recipients = models.JSONField(default=list)  # Email addresses
    export_format = models.CharField(max_length=10, choices=CustomReport.EXPORT_FORMATS, default='pdf')
    include_charts = models.BooleanField(default=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()
    run_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'next_run']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"Schedule: {self.schedule_name} ({self.frequency})"


class ReportExecution(models.Model):
    """Track report execution history"""
    
    EXECUTION_STATUS = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    report = models.ForeignKey(CustomReport, on_delete=models.CASCADE, related_name='executions')
    schedule = models.ForeignKey(ReportSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Execution details
    status = models.CharField(max_length=20, choices=EXECUTION_STATUS, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.IntegerField(null=True, blank=True)  # Seconds
    
    # Results
    result_count = models.IntegerField(null=True, blank=True)  # Number of rows
    export_file_path = models.CharField(max_length=500, blank=True)
    export_file_size = models.IntegerField(null=True, blank=True)  # Bytes
    
    # Error handling
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    # User context
    executed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    execution_params = models.JSONField(default=dict)  # Runtime parameters
    
    class Meta:
        indexes = [
            models.Index(fields=['report', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"Execution: {self.report.report_name} at {self.started_at}"


class PredictiveAnalyticsModel(models.Model):
    """Predictive analytics models for churn prevention and CLV"""
    
    MODEL_TYPES = [
        ('churn_prediction', 'Churn Prediction'),
        ('clv_calculation', 'Customer Lifetime Value'),
        ('usage_forecasting', 'Usage Forecasting'),
        ('revenue_forecasting', 'Revenue Forecasting'),
    ]
    
    MODEL_STATUS = [
        ('training', 'Training'),
        ('ready', 'Ready'),
        ('deprecated', 'Deprecated'),
        ('failed', 'Failed'),
    ]
    
    model_name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    
    # Model configuration
    features = models.JSONField(default=list)  # Input features
    target_variable = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=50)  # sklearn, xgboost, etc.
    hyperparameters = models.JSONField(default=dict)
    
    # Model performance
    accuracy_score = models.FloatField(null=True, blank=True)
    precision_score = models.FloatField(null=True, blank=True)
    recall_score = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    # Model artifacts
    model_file_path = models.CharField(max_length=500, blank=True)
    feature_importance = models.JSONField(default=dict)
    training_data_size = models.IntegerField(null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=MODEL_STATUS, default='training')
    trained_at = models.DateTimeField(null=True, blank=True)
    last_prediction_at = models.DateTimeField(null=True, blank=True)
    prediction_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"Model: {self.model_name} ({self.model_type})"


class UserChurnPrediction(models.Model):
    """Churn prediction results for users"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='churn_predictions')
    model = models.ForeignKey(PredictiveAnalyticsModel, on_delete=models.CASCADE)
    
    # Prediction results
    churn_probability = models.FloatField()
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ])
    
    # Supporting data
    feature_values = models.JSONField(default=dict)  # Input feature values
    contributing_factors = models.JSONField(default=list)  # Top factors driving prediction
    recommendations = models.JSONField(default=list)  # Suggested interventions
    
    # Metadata
    predicted_at = models.DateTimeField(auto_now_add=True)
    prediction_horizon_days = models.IntegerField(default=30)  # Prediction window
    
    # Outcome tracking
    actual_churned = models.BooleanField(null=True, blank=True)
    churn_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-predicted_at']),
            models.Index(fields=['risk_level', '-predicted_at']),
            models.Index(fields=['churn_probability', '-predicted_at']),
        ]
    
    def __str__(self):
        return f"Churn Prediction: {self.user.email} ({self.risk_level})"


class CustomerLifetimeValue(models.Model):
    """Customer lifetime value calculations"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='clv_calculations')
    model = models.ForeignKey(PredictiveAnalyticsModel, on_delete=models.CASCADE)
    
    # CLV metrics
    predicted_clv = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    future_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Time-based projections
    clv_6_months = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    clv_1_year = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    clv_3_years = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Customer segmentation
    value_segment = models.CharField(max_length=20, choices=[
        ('high_value', 'High Value'),
        ('medium_value', 'Medium Value'),
        ('low_value', 'Low Value'),
        ('potential', 'High Potential'),
    ])
    
    # Supporting metrics
    predicted_lifetime_months = models.IntegerField()
    average_monthly_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    retention_probability = models.FloatField()
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculation_method = models.CharField(max_length=50)
    confidence_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-calculated_at']),
            models.Index(fields=['value_segment', '-predicted_clv']),
            models.Index(fields=['-predicted_clv']),
        ]
    
    def __str__(self):
        return f"CLV: {self.user.email} - ${self.predicted_clv}"


class ExecutiveDashboard(models.Model):
    """Executive dashboard configuration and KPIs"""
    
    dashboard_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Layout configuration
    layout_config = models.JSONField(default=dict)  # Widget positions, sizes
    refresh_interval = models.IntegerField(default=300)  # Seconds
    
    # KPI widgets
    widgets = models.JSONField(default=list)  # Widget configurations
    
    # Access control
    visible_to_roles = models.JSONField(default=list)  # Admin roles
    is_default = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_default', '-created_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"Dashboard: {self.dashboard_name}"


# ============= USER COMMUNICATION TOOLS MODELS =============

class BroadcastMessage(models.Model):
    """Broadcast messages to user segments"""
    
    MESSAGE_TYPES = [
        ('announcement', 'Announcement'),
        ('maintenance', 'Maintenance Alert'),
        ('feature_update', 'Feature Update'),
        ('promotion', 'Promotion'),
        ('urgent', 'Urgent Notice'),
        ('newsletter', 'Newsletter'),
    ]
    
    DELIVERY_METHODS = [
        ('in_app', 'In-App Notification'),
        ('email', 'Email'),
        ('both', 'In-App + Email'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, default='both')
    
    # Target audience configuration
    target_all_users = models.BooleanField(default=False)
    target_roles = models.JSONField(default=list)  # ['advisor', 'admin', etc.]
    target_user_segments = models.JSONField(default=dict)  # Complex segmentation rules
    specific_users = models.ManyToManyField(CustomUser, blank=True, related_name='targeted_broadcasts')
    
    # Scheduling
    send_immediately = models.BooleanField(default=True)
    scheduled_send_time = models.DateTimeField(null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(null=True, blank=True)
    total_recipients = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    
    # Rich content
    has_action_button = models.BooleanField(default=False)
    action_button_text = models.CharField(max_length=50, blank=True)
    action_button_url = models.URLField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_broadcasts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['message_type', '-sent_at']),
            models.Index(fields=['scheduled_send_time']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Broadcast: {self.title}"


class BroadcastDelivery(models.Model):
    """Track individual broadcast deliveries"""
    
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('failed', 'Failed'),
    ]
    
    broadcast = models.ForeignKey(BroadcastMessage, on_delete=models.CASCADE, related_name='deliveries')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='broadcast_deliveries')
    
    # Delivery tracking
    delivery_method = models.CharField(max_length=20, choices=BroadcastMessage.DELIVERY_METHODS)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    
    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Engagement tracking
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        unique_together = ['broadcast', 'user']
        indexes = [
            models.Index(fields=['broadcast', 'status']),
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['status', '-sent_at']),
        ]
    
    def __str__(self):
        return f"Delivery: {self.broadcast.title} to {self.user.email}"


class EmailCampaign(models.Model):
    """Email marketing campaigns with advanced features"""
    
    CAMPAIGN_TYPES = [
        ('marketing', 'Marketing'),
        ('educational', 'Educational'),
        ('onboarding', 'Onboarding'),
        ('retention', 'Retention'),
        ('win_back', 'Win-back'),
        ('newsletter', 'Newsletter'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    campaign_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    
    # Email content
    subject_line = models.CharField(max_length=200)
    preview_text = models.CharField(max_length=150, blank=True)
    email_content = models.TextField()  # HTML content
    plain_text_content = models.TextField(blank=True)
    
    # A/B Testing
    is_ab_test = models.BooleanField(default=False)
    ab_test_config = models.JSONField(default=dict)  # A/B test configuration
    
    # Target audience
    target_segments = models.JSONField(default=dict)  # Segmentation rules
    estimated_recipients = models.IntegerField(default=0)
    
    # Scheduling
    send_immediately = models.BooleanField(default=False)
    scheduled_send_time = models.DateTimeField(null=True, blank=True)
    
    # Sending configuration
    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    reply_to_email = models.EmailField(blank=True)
    
    # Status and analytics
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(null=True, blank=True)
    total_sent = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    unsubscribed_count = models.IntegerField(default=0)
    bounced_count = models.IntegerField(default=0)
    
    # Performance metrics
    open_rate = models.FloatField(null=True, blank=True)  # Calculated field
    click_rate = models.FloatField(null=True, blank=True)  # Calculated field
    click_through_rate = models.FloatField(null=True, blank=True)  # Calculated field
    unsubscribe_rate = models.FloatField(null=True, blank=True)  # Calculated field
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['campaign_type', '-sent_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def calculate_metrics(self):
        """Calculate performance metrics"""
        if self.total_sent > 0:
            self.open_rate = (self.opened_count / self.total_sent) * 100
            self.click_rate = (self.clicked_count / self.total_sent) * 100
            self.unsubscribe_rate = (self.unsubscribed_count / self.total_sent) * 100
            
            if self.opened_count > 0:
                self.click_through_rate = (self.clicked_count / self.opened_count) * 100
            
            self.save(update_fields=['open_rate', 'click_rate', 'click_through_rate', 'unsubscribe_rate'])
    
    def __str__(self):
        return f"Campaign: {self.campaign_name}"


class EmailCampaignDelivery(models.Model):
    """Track individual email campaign deliveries"""
    
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('unsubscribed', 'Unsubscribed'),
        ('complained', 'Spam Complaint'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='deliveries')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='campaign_deliveries')
    
    # Email details
    email_address = models.EmailField()
    subject_line = models.CharField(max_length=200)
    
    # Delivery tracking
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement tracking
    first_opened_at = models.DateTimeField(null=True, blank=True)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    open_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    
    # Device/client info
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    email_client = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    
    # Error handling
    bounce_reason = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    
    # A/B testing
    ab_variant = models.CharField(max_length=10, blank=True)  # 'A', 'B', etc.
    
    class Meta:
        unique_together = ['campaign', 'user']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['status', '-sent_at']),
            models.Index(fields=['ab_variant', 'campaign']),
        ]
    
    def __str__(self):
        return f"Delivery: {self.campaign.campaign_name} to {self.email_address}"


class InAppNotification(models.Model):
    """In-app notification system"""
    
    NOTIFICATION_TYPES = [
        ('system', 'System Notification'),
        ('feature', 'Feature Announcement'),
        ('reminder', 'Reminder'),
        ('warning', 'Warning'),
        ('success', 'Success Message'),
        ('info', 'Information'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Rich content
    has_action = models.BooleanField(default=False)
    action_text = models.CharField(max_length=50, blank=True)
    action_url = models.URLField(blank=True)
    action_data = models.JSONField(default=dict)  # Additional action data
    
    # Visual properties
    icon = models.CharField(max_length=50, blank=True)  # CSS class or icon name
    color = models.CharField(max_length=20, blank=True)  # Color theme
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_dismiss_after = models.IntegerField(null=True, blank=True)  # Seconds
    
    # Source tracking
    source_broadcast = models.ForeignKey(BroadcastMessage, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_notifications')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'priority', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def dismiss(self):
        """Dismiss notification"""
        if not self.is_dismissed:
            self.is_dismissed = True
            self.dismissed_at = timezone.now()
            self.save(update_fields=['is_dismissed', 'dismissed_at'])
    
    def __str__(self):
        return f"Notification: {self.title} for {self.user.email}"


class MaintenanceMode(models.Model):
    """System maintenance mode configuration"""
    
    MAINTENANCE_TYPES = [
        ('scheduled', 'Scheduled Maintenance'),
        ('emergency', 'Emergency Maintenance'),
        ('upgrade', 'System Upgrade'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    
    # Timing
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Status and configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    is_active = models.BooleanField(default=False)
    block_all_access = models.BooleanField(default=True)
    allow_admin_access = models.BooleanField(default=True)
    
    # User communication
    public_message = models.TextField(help_text="Message shown to users during maintenance")
    notification_sent = models.BooleanField(default=False)
    advance_notice_hours = models.IntegerField(default=24)
    
    # Progress tracking
    progress_percentage = models.IntegerField(default=0)
    progress_message = models.CharField(max_length=200, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Contact information
    contact_email = models.EmailField(blank=True)
    status_page_url = models.URLField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-scheduled_start']),
            models.Index(fields=['is_active', 'scheduled_start']),
            models.Index(fields=['-scheduled_start']),
        ]
        ordering = ['-scheduled_start']
    
    def activate(self):
        """Activate maintenance mode"""
        self.is_active = True
        self.status = 'active'
        self.actual_start = timezone.now()
        self.save(update_fields=['is_active', 'status', 'actual_start'])
    
    def deactivate(self):
        """Deactivate maintenance mode"""
        self.is_active = False
        self.status = 'completed'
        self.actual_end = timezone.now()
        self.save(update_fields=['is_active', 'status', 'actual_end'])
    
    def __str__(self):
        return f"Maintenance: {self.title}"


class UserFeedback(models.Model):
    """User feedback collection system"""
    
    FEEDBACK_TYPES = [
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('general_feedback', 'General Feedback'),
        ('complaint', 'Complaint'),
        ('compliment', 'Compliment'),
        ('suggestion', 'Suggestion'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('duplicate', 'Duplicate'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField()  # Allow anonymous feedback
    
    # Feedback content
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Classification
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Context information
    page_url = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    browser_info = models.JSONField(default=dict)
    screen_resolution = models.CharField(max_length=20, blank=True)
    
    # Attachments and screenshots
    has_attachments = models.BooleanField(default=False)
    attachment_paths = models.JSONField(default=list)
    
    # Tags and categorization
    tags = models.JSONField(default=list)
    category = models.CharField(max_length=100, blank=True)
    
    # Staff response
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_feedback')
    staff_notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    customer_satisfied = models.BooleanField(null=True, blank=True)
    satisfaction_rating = models.IntegerField(null=True, blank=True)  # 1-5 stars
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['feedback_type', 'priority']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
        ordering = ['-created_at']
    
    def assign_to_staff(self, staff_user):
        """Assign feedback to staff member"""
        self.assigned_to = staff_user
        self.status = 'in_review'
        self.save(update_fields=['assigned_to', 'status'])
    
    def mark_resolved(self, resolution_notes=''):
        """Mark feedback as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        self.save(update_fields=['status', 'resolved_at', 'resolution_notes'])
    
    def __str__(self):
        return f"Feedback: {self.title} from {self.email}"


class FeedbackResponse(models.Model):
    """Staff responses to user feedback"""
    
    feedback = models.ForeignKey(UserFeedback, on_delete=models.CASCADE, related_name='responses')
    staff_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedback_responses')
    
    # Response content
    message = models.TextField()
    is_internal_note = models.BooleanField(default=False)  # Internal staff note vs user-visible response
    
    # Visibility and notifications
    visible_to_user = models.BooleanField(default=True)
    user_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Attachments
    has_attachments = models.BooleanField(default=False)
    attachment_paths = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['feedback', '-created_at']),
            models.Index(fields=['staff_user', '-created_at']),
            models.Index(fields=['is_internal_note', '-created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        note_type = "Internal Note" if self.is_internal_note else "Response"
        return f"{note_type}: {self.feedback.title} by {self.staff_user.email}"

