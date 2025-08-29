# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.utils import timezone
import uuid
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.core.exceptions import ValidationError



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