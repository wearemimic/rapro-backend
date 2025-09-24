from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class ReportTemplate(models.Model):
    """
    Report templates for creating standardized professional presentations.
    Supports system templates, user-created templates, and firm-level templates.
    """
    TEMPLATE_TYPES = [
        ('system', 'System Template'),
        ('user', 'User Template'),
        ('firm', 'Firm Template'),
    ]
    
    CATEGORY_CHOICES = [
        ('retirement', 'Retirement Planning'),
        ('tax', 'Tax Strategy'),
        ('comparison', 'Scenario Comparison'),
        ('irmaa', 'IRMAA Analysis'),
        ('roth', 'Roth Conversion'),
        ('general', 'General Purpose'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    is_system_template = models.BooleanField(default=False)
    
    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_templates',
        null=True,
        blank=True
    )
    firm = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='firm_templates',
        null=True,
        blank=True,
        help_text="For firm-level templates, references the firm owner/admin"
    )
    
    # Configuration and metadata
    template_config = models.JSONField(
        help_text="Template structure, layout, and settings in JSON format"
    )
    preview_image = models.ImageField(
        upload_to='report_center/template_previews/',
        null=True,
        blank=True
    )
    tags = models.JSONField(
        default=list,
        help_text="Searchable tags as JSON array"
    )
    usage_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_templates'
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_by']),
            models.Index(fields=['firm']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Report(models.Model):
    """
    Report instances created from templates with specific client data.
    Handles generation, sharing, and analytics for individual reports.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generating', 'Generating'),
        ('ready', 'Ready'),
        ('shared', 'Shared'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    
    # Basic information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    
    # Configuration and data
    report_config = models.JSONField(
        help_text="Report-specific customizations and settings"
    )
    data_snapshot = models.JSONField(
        help_text="Cached data at time of generation (client, scenario, calculations)"
    )
    
    # Generated files
    pdf_file = models.FileField(
        upload_to='report_center/generated_reports/pdf/',
        null=True,
        blank=True
    )
    pptx_file = models.FileField(
        upload_to='report_center/generated_reports/pptx/',
        null=True,
        blank=True
    )
    
    # Sharing and client access
    shared_with_client = models.BooleanField(default=False)
    client_access_token = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Secure token for client portal access"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Client access expiration time"
    )
    
    # Timestamps
    generated_at = models.DateTimeField(null=True, blank=True)
    shared_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['advisor']),
            models.Index(fields=['client']),
            models.Index(fields=['template']),
            models.Index(fields=['status']),
            models.Index(fields=['shared_with_client']),
            models.Index(fields=['created_at']),
            models.Index(fields=['generated_at']),
        ]
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
    
    def __str__(self):
        client_name = f" - {self.client.first_name} {self.client.last_name}" if self.client else ""
        return f"{self.name}{client_name}"


class ReportSection(models.Model):
    """
    Modular sections that make up report templates.
    Allows for flexible report building with reusable components.
    """
    SECTION_TYPES = [
        ('cover', 'Cover Page'),
        ('summary', 'Executive Summary'),
        ('charts', 'Charts & Visualizations'),
        ('data_table', 'Data Tables'),
        ('text', 'Text Content'),
        ('scenarios', 'Scenario Analysis'),
        ('recommendations', 'Recommendations'),
        ('irmaa', 'IRMAA Analysis'),
        ('roth', 'Roth Conversion'),
        ('tax_strategy', 'Tax Strategy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    
    # Section configuration
    section_type = models.CharField(max_length=100, choices=SECTION_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order_index = models.PositiveIntegerField(help_text="Order within the template")
    is_required = models.BooleanField(
        default=False,
        help_text="Required sections cannot be removed from reports"
    )
    
    # Section-specific configuration
    section_config = models.JSONField(
        help_text="Section-specific configuration (layout, styling, data binding)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_sections'
        indexes = [
            models.Index(fields=['template']),
            models.Index(fields=['section_type']),
            models.Index(fields=['order_index']),
        ]
        ordering = ['order_index']
        verbose_name = 'Report Section'
        verbose_name_plural = 'Report Sections'
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"


class ReportShare(models.Model):
    """
    Handles report sharing with clients and tracking access analytics.
    Manages permissions, access tokens, and engagement metrics.
    """
    SHARE_TYPES = [
        ('client', 'Client Access'),
        ('colleague', 'Colleague Sharing'),
        ('public', 'Public Link'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    
    # Recipient information
    recipient_email = models.EmailField()
    access_token = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique token for accessing shared report"
    )
    share_type = models.CharField(max_length=50, choices=SHARE_TYPES)
    
    # Permissions and access control
    permissions = models.JSONField(
        default=dict,
        help_text="View, download, comment permissions"
    )
    
    # Analytics and tracking
    accessed_at = models.DateTimeField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_shares'
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['access_token']),
            models.Index(fields=['recipient_email']),
            models.Index(fields=['share_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = 'Report Share'
        verbose_name_plural = 'Report Shares'
    
    def __str__(self):
        return f"{self.report.name} shared with {self.recipient_email}"
    
    @property
    def is_expired(self):
        """Check if the share link has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class TemplateAnalytics(models.Model):
    """
    Analytics tracking for template usage and performance.
    Helps optimize templates and understand user behavior.
    """
    ACTION_CHOICES = [
        ('viewed', 'Viewed'),
        ('used', 'Used in Report'),
        ('customized', 'Customized'),
        ('shared', 'Shared'),
        ('downloaded', 'Downloaded'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='template_analytics'
    )
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    metadata = models.JSONField(
        default=dict,
        help_text="Additional action-specific data"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'template_analytics'
        indexes = [
            models.Index(fields=['template']),
            models.Index(fields=['advisor']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Template Analytics'
        verbose_name_plural = 'Template Analytics'
    
    def __str__(self):
        return f"{self.advisor.email} {self.action} {self.template.name}"


class ReportComment(models.Model):
    """
    Client comments and feedback on shared reports.
    Enables collaboration between advisors and clients.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    share = models.ForeignKey(
        ReportShare,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The share link this comment was made through"
    )
    
    # Comment content
    content = models.TextField()
    section_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to specific report section if applicable"
    )
    
    # Commenter information (from share link, not registered user)
    commenter_email = models.EmailField()
    commenter_name = models.CharField(max_length=255, blank=True)
    
    # Status and workflow
    is_resolved = models.BooleanField(default=False)
    advisor_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_comments'
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['share']),
            models.Index(fields=['commenter_email']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Report Comment'
        verbose_name_plural = 'Report Comments'
    
    def __str__(self):
        return f"Comment on {self.report.name} by {self.commenter_email}"


class ReportGeneration(models.Model):
    """
    Tracks report generation processes for monitoring and debugging.
    Stores generation metadata, performance metrics, and error details.
    """
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='generations'
    )
    
    # Generation details
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='queued')
    generation_type = models.CharField(
        max_length=50,
        choices=[('pdf', 'PDF'), ('pptx', 'PowerPoint'), ('both', 'Both')],
        default='both'
    )
    
    # Performance metrics
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(
        default=dict,
        help_text="Detailed error information for debugging"
    )
    
    # Configuration snapshot
    generation_config = models.JSONField(
        default=dict,
        help_text="Configuration used for this generation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_generations'
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['status']),
            models.Index(fields=['generation_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Report Generation'
        verbose_name_plural = 'Report Generations'
    
    def __str__(self):
        return f"Generation of {self.report.name} - {self.status}"
    
    @property
    def duration(self):
        """Calculate generation duration if available"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class BulkExportJob(models.Model):
    """
    Tracks bulk export operations for multiple reports.
    Handles batch processing with progress monitoring and error tracking.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('completed_with_errors', 'Completed with Errors'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bulk_export_jobs'
    )
    
    # Job configuration
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    export_config = models.JSONField(
        help_text="Export configuration including format, options, filters"
    )
    
    # Target data configuration
    client_ids = models.JSONField(
        default=list,
        help_text="List of client IDs to export"
    )
    scenario_ids = models.JSONField(
        default=list,
        help_text="List of scenario IDs to export"
    )
    template_ids = models.JSONField(
        default=list,
        help_text="List of template IDs to use"
    )
    
    # Progress tracking
    total_items = models.PositiveIntegerField(default=0)
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )
    successful_exports = models.PositiveIntegerField(null=True, blank=True)
    failed_exports = models.PositiveIntegerField(null=True, blank=True)
    
    # File output
    file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to the generated export file (ZIP for multiple files)"
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed error information for failed individual exports"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'bulk_export_jobs'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['completed_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Bulk Export Job'
        verbose_name_plural = 'Bulk Export Jobs'
    
    def __str__(self):
        return f"Bulk export {self.id} by {self.user.email} - {self.status}"
    
    @property
    def duration(self):
        """Calculate job duration if available"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_completed(self):
        """Check if job is in a completed state"""
        return self.status in ['completed', 'completed_with_errors', 'failed', 'cancelled']


class ReportSchedule(models.Model):
    """
    Scheduled report generation system.
    Handles recurring report generation with flexible scheduling options.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('disabled', 'Disabled'),
        ('completed', 'Completed'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('powerpoint', 'PowerPoint'),
        ('both', 'PDF + PowerPoint'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_schedules'
    )
    
    # Basic information
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    
    # Template and target configuration
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='report_schedules',
        null=True,
        blank=True,
        help_text="Specific client for the report (if not bulk)"
    )
    scenario = models.ForeignKey(
        'core.Scenario',
        on_delete=models.CASCADE,
        related_name='report_schedules',
        null=True,
        blank=True,
        help_text="Specific scenario for the report"
    )
    
    # Bulk scheduling configuration
    client_filter = models.JSONField(
        null=True,
        blank=True,
        help_text="Client filtering criteria for bulk scheduling"
    )
    
    # Scheduling configuration
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    frequency_config = models.JSONField(
        default=dict,
        help_text="Detailed frequency configuration (day of week, day of month, etc.)"
    )
    
    # Time configuration
    scheduled_time = models.TimeField(
        help_text="Time of day to generate the report"
    )
    timezone = models.CharField(
        max_length=100,
        default='UTC',
        help_text="Timezone for scheduling"
    )
    
    # Generation options
    format = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='pdf')
    generation_options = models.JSONField(
        default=dict,
        help_text="Report generation options (page size, orientation, etc.)"
    )
    
    # Delivery configuration
    auto_email = models.BooleanField(
        default=False,
        help_text="Automatically email the report when generated"
    )
    email_recipients = models.JSONField(
        default=list,
        help_text="List of email addresses to send the report to"
    )
    email_subject_template = models.CharField(
        max_length=255,
        blank=True,
        help_text="Email subject template with variables"
    )
    email_body_template = models.TextField(
        blank=True,
        help_text="Email body template with variables"
    )
    
    # Execution tracking
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Next scheduled execution time"
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last execution time"
    )
    run_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this schedule has run"
    )
    success_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of successful executions"
    )
    failure_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of failed executions"
    )
    
    # End date configuration
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional end date for the schedule"
    )
    max_runs = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of runs (optional)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_schedules'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['next_run']),
            models.Index(fields=['frequency']),
            models.Index(fields=['template']),
            models.Index(fields=['client']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"
    
    @property
    def is_active(self):
        """Check if the schedule is currently active"""
        if self.status != 'active':
            return False
        
        if self.end_date and timezone.now() > self.end_date:
            return False
        
        if self.max_runs and self.run_count >= self.max_runs:
            return False
        
        return True
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.run_count == 0:
            return 0
        return round((self.success_count / self.run_count) * 100, 1)


class ReportScheduleExecution(models.Model):
    """
    Individual execution record for scheduled reports.
    Tracks the results of each scheduled report generation.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    schedule = models.ForeignKey(
        ReportSchedule,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    # Execution details
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    scheduled_for = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    generated_reports = models.JSONField(
        default=list,
        help_text="List of generated report IDs or file paths"
    )
    emails_sent = models.PositiveIntegerField(
        default=0,
        help_text="Number of emails sent for this execution"
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed error information"
    )
    
    # Performance metrics
    execution_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Total execution time in seconds"
    )
    reports_generated = models.PositiveIntegerField(
        default=0,
        help_text="Number of reports generated in this execution"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_schedule_executions'
        indexes = [
            models.Index(fields=['schedule']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-scheduled_for']
        verbose_name = 'Report Schedule Execution'
        verbose_name_plural = 'Report Schedule Executions'
    
    def __str__(self):
        return f"Execution of {self.schedule.name} - {self.scheduled_for}"
    
    @property
    def duration(self):
        """Calculate execution duration if available"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class AIUsageTracking(models.Model):
    """
    Track AI API usage for cost management and analytics
    """
    AI_FEATURES = [
        ('executive_summary', 'Executive Summary Generation'),
        ('slide_recommendations', 'Slide Order Recommendations'),
        ('content_risk_explanation', 'Risk Explanation Content'),
        ('content_irmaa_impact', 'IRMAA Impact Content'),
        ('content_roth_strategy', 'Roth Strategy Content'),
        ('content_tax_optimization', 'Tax Optimization Content'),
        ('content_social_security', 'Social Security Content'),
        ('content_monte_carlo_interpretation', 'Monte Carlo Interpretation'),
        ('client_insights', 'Client Insights Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feature = models.CharField(max_length=100, choices=AI_FEATURES)
    
    # Usage metrics
    tokens_used = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=4, help_text="Cost in USD")
    model_used = models.CharField(max_length=100, default='gpt-4-turbo-preview')
    
    # Tracking information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_usage'
    )
    report = models.ForeignKey(
        'Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_usage'
    )
    
    # Metadata
    request_metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional context about the request"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_ai_usage'
        indexes = [
            models.Index(fields=['feature']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['cost']),
        ]
        ordering = ['-timestamp']
        verbose_name = 'AI Usage Record'
        verbose_name_plural = 'AI Usage Records'
    
    def __str__(self):
        return f"{self.feature} - {self.tokens_used} tokens - ${self.cost}"
    
    @classmethod
    def get_total_cost_for_user(cls, user, start_date=None, end_date=None):
        """Get total AI cost for a user in a date range"""
        queryset = cls.objects.filter(user=user)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset.aggregate(
            total_cost=models.Sum('cost'),
            total_tokens=models.Sum('tokens_used')
        )
    
    @classmethod
    def get_usage_by_feature(cls, start_date=None, end_date=None):
        """Get usage statistics grouped by feature"""
        queryset = cls.objects.all()
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        return queryset.values('feature').annotate(
            total_cost=models.Sum('cost'),
            total_tokens=models.Sum('tokens_used'),
            usage_count=models.Count('id')
        ).order_by('-total_cost')