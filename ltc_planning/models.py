import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import Client


class LTCAssessment(models.Model):
    """
    Long-Term Care assessment for a client
    Captures ADL/IADL scores, health conditions, and care level recommendations
    """
    ASSESSMENT_TYPES = [
        ('manual', 'Manual Assessment'),
        ('ai_assisted', 'AI-Assisted Assessment'),
    ]

    CARE_LEVELS = [
        ('independent_with_monitoring', 'Independent with Monitoring'),
        ('in_home_care', 'In-Home Care'),
        ('adult_day_care', 'Adult Day Care'),
        ('assisted_living', 'Assisted Living'),
        ('memory_care', 'Memory Care'),
        ('skilled_nursing', 'Skilled Nursing / Nursing Home'),
    ]

    COGNITIVE_STATUS_CHOICES = [
        ('normal', 'Normal'),
        ('mild_impairment', 'Mild Cognitive Impairment'),
        ('moderate_impairment', 'Moderate Cognitive Impairment'),
        ('severe_impairment', 'Severe Cognitive Impairment'),
    ]

    LIVING_SITUATION_CHOICES = [
        ('alone', 'Lives Alone'),
        ('with_spouse', 'Lives with Spouse'),
        ('with_family', 'Lives with Family'),
        ('assisted_living', 'Assisted Living Facility'),
        ('nursing_home', 'Nursing Home'),
        ('unsafe', 'Unsafe Living Situation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ltc_assessments')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES, default='manual')
    care_level_recommendation = models.CharField(max_length=50, choices=CARE_LEVELS, blank=True)

    # ADL/IADL Assessment Scores (JSON fields for flexibility)
    assessment_score_adl = models.JSONField(
        default=dict,
        help_text="Activities of Daily Living scores: bathing, dressing, toileting, transferring, continence, eating"
    )
    assessment_score_iadl = models.JSONField(
        default=dict,
        help_text="Instrumental Activities of Daily Living scores: phone, shopping, food prep, housekeeping, laundry, transportation, medications, finances"
    )

    # Health and Living Situation
    health_conditions = models.JSONField(default=list, help_text="List of health conditions and diagnoses")
    cognitive_status = models.CharField(max_length=50, choices=COGNITIVE_STATUS_CHOICES, blank=True)
    living_situation = models.CharField(max_length=100, choices=LIVING_SITUATION_CHOICES, blank=True)

    # Geographic and Support Information
    geographic_location = models.JSONField(
        default=dict,
        help_text="Location data: city, state, zip code"
    )
    family_support = models.JSONField(
        default=dict,
        help_text="Family support availability and details"
    )

    # Financial and Preferences
    financial_capacity = models.JSONField(default=dict, help_text="Financial information for planning")
    preferences = models.JSONField(default=dict, help_text="Client preferences for care type, location, etc.")

    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'LTC Assessment'
        verbose_name_plural = 'LTC Assessments'

    def __str__(self):
        return f"LTC Assessment for {self.client} - {self.created_at.strftime('%Y-%m-%d')}"

    def calculate_adl_score(self):
        """Calculate total ADL impairment score (0-6)"""
        adl_items = ['bathing', 'dressing', 'toileting', 'transferring', 'continence', 'eating']
        score = 0
        for item in adl_items:
            if self.assessment_score_adl.get(item) in ['dependent', 'needs_assistance', 'assistance']:
                score += 1
        return score

    def calculate_iadl_score(self):
        """Calculate total IADL impairment score (0-8)"""
        iadl_items = ['phone', 'shopping', 'food_prep', 'housekeeping', 'laundry', 'transportation', 'medications', 'finances']
        score = 0
        for item in iadl_items:
            if self.assessment_score_iadl.get(item) in ['dependent', 'needs_assistance', 'assistance']:
                score += 1
        return score


class LTCCostProjection(models.Model):
    """
    Cost projection for long-term care based on assessment
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ltc_cost_projections')
    assessment = models.ForeignKey(LTCAssessment, on_delete=models.SET_NULL, null=True, blank=True, related_name='cost_projections')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    scenario_name = models.CharField(max_length=100, help_text="e.g., 'Standard Projection', 'Optimistic', 'Pessimistic'")
    scenario_type = models.CharField(
        max_length=50,
        choices=[
            ('optimistic', 'Optimistic'),
            ('likely', 'Likely'),
            ('pessimistic', 'Pessimistic'),
            ('custom', 'Custom')
        ],
        default='likely'
    )
    years_projected = models.IntegerField(default=20, validators=[MinValueValidator(1), MaxValueValidator(50)])
    start_age = models.IntegerField(default=65, help_text="Client's age at start of projection")
    care_level = models.CharField(
        max_length=50,
        choices=[
            ('independent_with_monitoring', 'Independent with Monitoring'),
            ('in_home_care', 'In-Home Care'),
            ('adult_day_care', 'Adult Day Care'),
            ('assisted_living', 'Assisted Living'),
            ('memory_care', 'Memory Care'),
            ('skilled_nursing', 'Skilled Nursing')
        ],
        default='assisted_living',
        help_text="Initial care level for projection"
    )

    # Cost Projection Data
    annual_cost_projections = models.JSONField(
        default=list,
        help_text="Year-by-year cost projections with care level, inflation, regional adjustments"
    )
    total_lifetime_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    care_progression = models.JSONField(
        default=list,
        help_text="Anticipated care level changes over time"
    )

    # Regional and Assumptions
    regional_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    state = models.CharField(max_length=2, blank=True, help_text="US state code for regional pricing")
    assumptions = models.JSONField(
        default=dict,
        help_text="Assumptions used in projection: inflation rates, data sources, etc."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'LTC Cost Projection'
        verbose_name_plural = 'LTC Cost Projections'

    def __str__(self):
        return f"Cost Projection for {self.client} - {self.scenario_name}"


class InsuranceProduct(models.Model):
    """
    Insurance product catalog (carriers, products, features)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    carrier = models.CharField(max_length=100, db_index=True)
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=50, help_text="e.g., 'traditional', 'hybrid', 'linked_benefit'")

    # Product Features
    features = models.JSONField(
        default=dict,
        help_text="Product features: benefit periods, elimination periods, inflation options, etc."
    )

    # Pricing Information
    premium_structure = models.JSONField(default=dict, help_text="Premium pricing by age, gender, health class")

    # Availability
    available_states = models.JSONField(default=list, help_text="List of state codes where product is available")
    is_active = models.BooleanField(default=True)

    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['carrier', 'product_name']
        verbose_name = 'Insurance Product'
        verbose_name_plural = 'Insurance Products'
        unique_together = ['carrier', 'product_name']

    def __str__(self):
        return f"{self.carrier} - {self.product_name}"


class InsuranceIllustration(models.Model):
    """
    Uploaded insurance illustration with parsed data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ltc_illustrations')
    product = models.ForeignKey(InsuranceProduct, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # File Information
    file_path = models.CharField(max_length=500, help_text="Path to uploaded PDF illustration")
    file_name = models.CharField(max_length=255)

    # Parsed Data
    carrier = models.CharField(max_length=100, blank=True)
    product_name = models.CharField(max_length=200, blank=True)
    parsed_data = models.JSONField(
        default=dict,
        help_text="Extracted structured data from illustration: premiums, benefits, coverage details"
    )

    # OCR/Extraction Metadata
    extraction_confidence = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(1.00)],
        help_text="Confidence score of data extraction (0.00 - 1.00)"
    )
    extraction_method = models.CharField(max_length=50, default='claude_llm', help_text="Method used for extraction")
    raw_ocr_text = models.TextField(blank=True, help_text="Raw OCR text from PDF")

    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Insurance Illustration'
        verbose_name_plural = 'Insurance Illustrations'

    def __str__(self):
        return f"Illustration for {self.client} - {self.carrier} {self.product_name}"


class LTCCostCoverageComparison(models.Model):
    """
    Comparison analysis between projected costs and insurance coverage
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cost_projection = models.ForeignKey(LTCCostProjection, on_delete=models.CASCADE, related_name='comparisons')
    insurance_illustration = models.ForeignKey(InsuranceIllustration, on_delete=models.CASCADE, related_name='comparisons')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Comparison Data
    comparison_data = models.JSONField(
        default=dict,
        help_text="Complete comparison: summary, yearly analysis, gap analysis, asset depletion, ROI"
    )

    # Key Metrics (denormalized for quick access)
    total_care_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_insurance_benefit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    out_of_pocket_gap = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coverage_ratio_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cost vs Coverage Comparison'
        verbose_name_plural = 'Cost vs Coverage Comparisons'

    def __str__(self):
        return f"Comparison for {self.cost_projection.client} - {self.created_at.strftime('%Y-%m-%d')}"


class LTCAIConversation(models.Model):
    """
    AI-assisted conversation for assessment
    Tracks conversation history and extracted data
    """
    INTENT_CHOICES = [
        ('needs_assessment', 'Needs Assessment'),
        ('cost_estimation', 'Cost Estimation'),
        ('insurance_analysis', 'Insurance Analysis'),
        ('medicaid_planning', 'Medicaid Planning'),
        ('facility_search', 'Facility Search'),
        ('crisis_response', 'Crisis Response'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ltc_ai_conversations')
    assessment = models.ForeignKey(LTCAssessment, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_conversations')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Conversation Data
    conversation_history = models.JSONField(
        default=list,
        help_text="Full conversation history with advisor and AI messages"
    )
    extracted_data = models.JSONField(
        default=dict,
        help_text="Data extracted from conversation: demographics, ADL/IADL, health conditions, etc."
    )

    # Intent Tracking
    current_intent = models.CharField(max_length=50, choices=INTENT_CHOICES, default='needs_assessment')

    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Conversation'
        verbose_name_plural = 'AI Conversations'

    def __str__(self):
        return f"AI Conversation for {self.client} - {self.current_intent}"


class LTCClientPresentation(models.Model):
    """
    Client presentation record for tracking what was shown to clients
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ltc_presentations')
    assessment = models.ForeignKey(LTCAssessment, on_delete=models.SET_NULL, null=True, blank=True)
    cost_projection = models.ForeignKey(LTCCostProjection, on_delete=models.SET_NULL, null=True, blank=True)
    comparison = models.ForeignKey(LTCCostCoverageComparison, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Presentation Details
    presentation_date = models.DateTimeField(default=timezone.now)
    presented_by = models.CharField(max_length=100, help_text="Advisor name")

    # Content
    slides_data = models.JSONField(
        default=list,
        help_text="Slide content for 5-slide presentation"
    )

    # Generated Reports
    pdf_report_path = models.CharField(max_length=500, blank=True, help_text="Path to generated PDF report")

    # Status
    status = models.CharField(
        max_length=50,
        choices=[
            ('draft', 'Draft'),
            ('presented', 'Presented to Client'),
            ('accepted', 'Client Accepted Recommendations'),
            ('declined', 'Client Declined'),
        ],
        default='draft'
    )

    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Client Presentation'
        verbose_name_plural = 'Client Presentations'

    def __str__(self):
        return f"Presentation for {self.client} - {self.presentation_date.strftime('%Y-%m-%d')}"


class LTCFacilityRecommendation(models.Model):
    """
    Recommended care facilities for a client
    """
    FACILITY_TYPES = [
        ('assisted_living', 'Assisted Living'),
        ('memory_care', 'Memory Care'),
        ('nursing_home', 'Nursing Home'),
        ('ccrc', 'Continuing Care Retirement Community'),
        ('in_home_agency', 'In-Home Care Agency'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ltc_facility_recommendations')
    assessment = models.ForeignKey(LTCAssessment, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Facility Information
    facility_name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=50, choices=FACILITY_TYPES)

    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Details
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    availability = models.CharField(max_length=100, blank=True, help_text="e.g., 'Available', 'Waitlist', 'No availability'")

    # Quality Metrics
    quality_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Rating out of 5.0")
    medicare_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Additional Info
    features = models.JSONField(default=list, help_text="List of amenities and features")
    contact_info = models.JSONField(default=dict, help_text="Phone, email, website")

    # Recommendation Details
    recommendation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Algorithmic score for how well facility matches client needs"
    )
    recommendation_notes = models.TextField(blank=True)

    # Status
    client_interest_level = models.CharField(
        max_length=50,
        choices=[
            ('not_viewed', 'Not Viewed'),
            ('viewed', 'Viewed'),
            ('interested', 'Interested'),
            ('touring', 'Scheduled Tour'),
            ('applied', 'Application Submitted'),
            ('enrolled', 'Enrolled'),
            ('not_interested', 'Not Interested'),
        ],
        default='not_viewed'
    )

    class Meta:
        ordering = ['-recommendation_score', 'facility_name']
        verbose_name = 'Facility Recommendation'
        verbose_name_plural = 'Facility Recommendations'

    def __str__(self):
        return f"{self.facility_name} - {self.facility_type} ({self.city}, {self.state})"