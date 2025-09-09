# affiliate_models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import secrets
import string

User = get_user_model()


def generate_affiliate_code():
    """Generate a unique 8-character affiliate code"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(8))
        if not Affiliate.objects.filter(affiliate_code=code).exists():
            return code


def generate_tracking_code():
    """Generate a unique tracking code for links"""
    return secrets.token_urlsafe(16)


class Affiliate(models.Model):
    """Main affiliate account model"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ]
    
    COMMISSION_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('flat', 'Flat Rate'),
        ('tiered', 'Tiered'),
    ]
    
    # Account Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='affiliate_account')
    affiliate_code = models.CharField(max_length=20, unique=True, default=generate_affiliate_code, db_index=True)
    
    # Business Information
    business_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    website_url = models.URLField(blank=True)
    
    # Address Information
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='United States')
    
    # Tax Information
    tax_id = models.CharField(max_length=50, blank=True, help_text="SSN or EIN for tax reporting")
    tax_form_on_file = models.BooleanField(default=False, help_text="W-9 or W-8 form received")
    
    # Commission Settings
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPE_CHOICES, default='percentage')
    commission_rate_first_month = models.DecimalField(
        max_digits=5, decimal_places=2, default=20.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Commission rate for first month (percentage)"
    )
    commission_rate_recurring = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Commission rate for recurring months (percentage)"
    )
    flat_rate_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Flat rate commission amount (if applicable)"
    )
    custom_commission_terms = models.JSONField(
        default=dict, blank=True,
        help_text="Custom commission structure for special arrangements"
    )
    
    # Payment Settings
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('stripe_connect', 'Stripe Connect'),
            ('paypal', 'PayPal'),
            ('ach', 'ACH Transfer'),
            ('wire', 'Wire Transfer'),
            ('check', 'Check'),
        ],
        default='stripe_connect'
    )
    payment_details = models.JSONField(
        default=dict, blank=True,
        help_text="Payment method specific details (encrypted)"
    )
    minimum_payout = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00,
        help_text="Minimum balance required for payout"
    )
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_affiliates')
    
    # Performance Metrics (denormalized for efficiency)
    total_clicks = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)
    total_revenue_generated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_commissions_earned = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_commissions_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pending_commission_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Promotional Methods and Notes
    promotional_methods = models.TextField(
        blank=True,
        help_text="Description of how the affiliate plans to promote the service"
    )
    admin_notes = models.TextField(blank=True, help_text="Internal notes about this affiliate")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'affiliates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['affiliate_code']),
        ]
    
    def __str__(self):
        return f"{self.business_name} ({self.affiliate_code})"
    
    def get_commission_rate(self, is_first_month=True):
        """Get the applicable commission rate"""
        if self.commission_type == 'flat':
            return self.flat_rate_amount
        elif self.commission_type == 'percentage':
            return self.commission_rate_first_month if is_first_month else self.commission_rate_recurring
        else:
            # Handle tiered or custom commission structures
            return self.commission_rate_first_month if is_first_month else self.commission_rate_recurring


class AffiliateLink(models.Model):
    """Tracking links created by affiliates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='links')
    
    # Link Information
    campaign_name = models.CharField(max_length=255, help_text="Internal name for this campaign/link")
    tracking_code = models.CharField(max_length=50, unique=True, default=generate_tracking_code, db_index=True)
    destination_url = models.URLField(default='/', help_text="Where the link should redirect to")
    short_url = models.CharField(max_length=255, blank=True, help_text="Optional custom short URL")
    
    # Campaign Settings
    discount_code = models.CharField(max_length=50, blank=True, help_text="Optional discount code to apply")
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    # Status and Limits
    is_active = models.BooleanField(default=True)
    max_uses = models.IntegerField(null=True, blank=True, help_text="Maximum number of times this link can be used")
    current_uses = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics
    total_clicks = models.IntegerField(default=0)
    unique_clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'affiliate_links'
        ordering = ['-created_at']
        unique_together = [['affiliate', 'campaign_name']]
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['affiliate', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.campaign_name} - {self.tracking_code}"
    
    def get_full_url(self):
        """Get the full tracking URL"""
        from django.conf import settings
        base_url = getattr(settings, 'AFFILIATE_BASE_URL', 'http://localhost:3000')
        return f"{base_url}/r/{self.tracking_code}"
    
    @property
    def is_expired(self):
        """Check if the link has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_max_uses_reached(self):
        """Check if max uses have been reached"""
        if self.max_uses:
            return self.current_uses >= self.max_uses
        return False


class AffiliateClick(models.Model):
    """Track individual clicks on affiliate links"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='clicks')
    link = models.ForeignKey(AffiliateLink, on_delete=models.CASCADE, related_name='click_events', null=True, blank=True)
    
    # Click Information
    session_id = models.CharField(max_length=255, db_index=True, help_text="Session identifier for attribution")
    tracking_code = models.CharField(max_length=100, db_index=True)
    
    # User Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True, max_length=1000)
    
    # Location Information
    country_code = models.CharField(max_length=2, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Device Information
    is_mobile = models.BooleanField(default=False)
    device_type = models.CharField(max_length=50, blank=True)  # desktop, mobile, tablet
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    # Validation
    is_bot = models.BooleanField(default=False, help_text="Detected as bot traffic")
    is_valid = models.BooleanField(default=True, help_text="Valid click for commission purposes")
    
    # Conversion Tracking
    converted = models.BooleanField(default=False)
    conversion_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamp
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'affiliate_clicks'
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['affiliate', 'clicked_at']),
            models.Index(fields=['session_id', 'clicked_at']),
            models.Index(fields=['tracking_code']),
            models.Index(fields=['converted', 'clicked_at']),
        ]
    
    def __str__(self):
        return f"Click by {self.affiliate.business_name} at {self.clicked_at}"


class AffiliateConversion(models.Model):
    """Track conversions attributed to affiliates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='conversions')
    click = models.ForeignKey(AffiliateClick, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversion')
    
    # User Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='affiliate_conversions')
    user_email = models.EmailField(help_text="Store email for reference even if user is deleted")
    
    # Subscription Information
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255)
    subscription_plan = models.CharField(max_length=50)  # monthly, annual
    
    # Financial Information
    subscription_amount = models.DecimalField(max_digits=10, decimal_places=2)
    mrr_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Monthly Recurring Revenue value"
    )
    
    # Attribution Information
    attribution_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Click'),
            ('cookie', 'Cookie Attribution'),
            ('discount_code', 'Discount Code'),
            ('manual', 'Manual Attribution'),
        ],
        default='direct'
    )
    discount_code_used = models.CharField(max_length=50, blank=True)
    
    # Status
    is_valid = models.BooleanField(default=True, help_text="Valid for commission calculation")
    is_refunded = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    conversion_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'affiliate_conversions'
        ordering = ['-conversion_date']
        indexes = [
            models.Index(fields=['affiliate', 'conversion_date']),
            models.Index(fields=['stripe_subscription_id']),
            models.Index(fields=['user', 'conversion_date']),
            models.Index(fields=['is_valid', 'is_refunded']),
        ]
    
    def __str__(self):
        return f"Conversion for {self.affiliate.business_name} - {self.user_email}"


class Commission(models.Model):
    """Track commission earnings and payouts"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('adjusted', 'Adjusted'),
    ]
    
    COMMISSION_TYPE_CHOICES = [
        ('first_month', 'First Month'),
        ('recurring', 'Recurring'),
        ('bonus', 'Bonus'),
        ('adjustment', 'Adjustment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='commissions')
    conversion = models.ForeignKey(AffiliateConversion, on_delete=models.CASCADE, related_name='commissions', null=True, blank=True)
    
    # Commission Details
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    
    # Financial Information
    base_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Base amount used for commission calculation"
    )
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        help_text="Commission rate applied (as decimal, e.g., 0.20 for 20%)"
    )
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Billing Period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Status and Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    payout = models.ForeignKey('AffiliatePayout', on_delete=models.SET_NULL, null=True, blank=True, related_name='commissions')
    
    # Adjustments
    adjustment_reason = models.TextField(blank=True)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='commission_adjustments')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'commissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['affiliate', 'status', 'created_at']),
            models.Index(fields=['status', 'period_start']),
            models.Index(fields=['payout']),
        ]
    
    def __str__(self):
        return f"Commission for {self.affiliate.business_name} - ${self.commission_amount}"


class AffiliatePayout(models.Model):
    """Track batch payouts to affiliates"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='payouts')
    
    # Payout Period
    payout_period_start = models.DateField()
    payout_period_end = models.DateField()
    
    # Financial Information
    total_commissions = models.DecimalField(max_digits=10, decimal_places=2)
    adjustments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_payout = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Information
    payment_method = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=255, blank=True, help_text="Transaction ID or check number")
    payment_details = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Processing Information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payouts')
    notes = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Tax Information
    tax_form_sent = models.BooleanField(default=False)
    tax_year = models.IntegerField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'affiliate_payouts'
        ordering = ['-created_at']
        unique_together = [['affiliate', 'payout_period_start', 'payout_period_end']]
        indexes = [
            models.Index(fields=['affiliate', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['tax_year']),
        ]
    
    def __str__(self):
        return f"Payout to {self.affiliate.business_name} - ${self.net_payout}"


class AffiliateDiscountCode(models.Model):
    """Discount codes linked to affiliates"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='discount_codes')
    
    # Code Information
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=255)
    
    # Discount Settings
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('fixed_amount', 'Fixed Amount'),
            ('trial_extension', 'Trial Extension'),
        ]
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage Limits
    max_uses = models.IntegerField(null=True, blank=True)
    max_uses_per_customer = models.IntegerField(default=1)
    current_uses = models.IntegerField(default=0)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Plan Restrictions
    applicable_plans = models.JSONField(
        default=list, blank=True,
        help_text="List of plan IDs this code applies to (empty = all plans)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'affiliate_discount_codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['affiliate', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.affiliate.business_name}"
    
    @property
    def is_valid(self):
        """Check if the discount code is currently valid"""
        now = timezone.now()
        
        # Check if active
        if not self.is_active:
            return False
        
        # Check validity period
        if self.valid_from > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        
        # Check usage limits
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True