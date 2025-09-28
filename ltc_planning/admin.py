from django.contrib import admin
from .models import (
    LTCAssessment,
    LTCCostProjection,
    InsuranceProduct,
    InsuranceIllustration,
    LTCCostCoverageComparison,
    LTCAIConversation,
    LTCClientPresentation,
    LTCFacilityRecommendation,
)


@admin.register(LTCAssessment)
class LTCAssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'assessment_type', 'care_level_recommendation', 'cognitive_status', 'created_at']
    list_filter = ['assessment_type', 'care_level_recommendation', 'cognitive_status', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'client', 'assessment_type', 'care_level_recommendation', 'created_at', 'updated_at')
        }),
        ('Assessment Scores', {
            'fields': ('assessment_score_adl', 'assessment_score_iadl')
        }),
        ('Health & Living', {
            'fields': ('health_conditions', 'cognitive_status', 'living_situation')
        }),
        ('Location & Support', {
            'fields': ('geographic_location', 'family_support')
        }),
        ('Financial & Preferences', {
            'fields': ('financial_capacity', 'preferences')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(LTCCostProjection)
class LTCCostProjectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'scenario_name', 'total_lifetime_cost', 'years_projected', 'state', 'created_at']
    list_filter = ['scenario_name', 'state', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'scenario_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'client', 'assessment', 'scenario_name', 'created_at', 'updated_at')
        }),
        ('Projection Parameters', {
            'fields': ('years_projected', 'state', 'regional_multiplier')
        }),
        ('Cost Data', {
            'fields': ('total_lifetime_cost', 'annual_cost_projections', 'assumptions')
        }),
    )


@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ['carrier', 'product_name', 'product_type', 'is_active', 'created_at']
    list_filter = ['carrier', 'product_type', 'is_active', 'created_at']
    search_fields = ['carrier', 'product_name', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'carrier', 'product_name', 'product_type', 'is_active', 'created_at', 'updated_at')
        }),
        ('Product Details', {
            'fields': ('features', 'premium_structure', 'available_states')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(InsuranceIllustration)
class InsuranceIllustrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'carrier', 'product_name', 'extraction_confidence', 'extraction_method', 'created_at']
    list_filter = ['carrier', 'extraction_method', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'carrier', 'product_name', 'file_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'client', 'product', 'created_at', 'updated_at')
        }),
        ('File Information', {
            'fields': ('file_path', 'file_name')
        }),
        ('Extracted Data', {
            'fields': ('carrier', 'product_name', 'parsed_data')
        }),
        ('Extraction Metadata', {
            'fields': ('extraction_confidence', 'extraction_method', 'raw_ocr_text')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(LTCCostCoverageComparison)
class LTCCostCoverageComparisonAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_client', 'total_care_cost', 'total_insurance_benefit', 'out_of_pocket_gap', 'coverage_ratio_percent', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'cost_projection', 'insurance_illustration', 'created_at', 'updated_at')
        }),
        ('Key Metrics', {
            'fields': ('total_care_cost', 'total_insurance_benefit', 'out_of_pocket_gap', 'coverage_ratio_percent')
        }),
        ('Detailed Analysis', {
            'fields': ('comparison_data',)
        }),
    )

    def get_client(self, obj):
        return obj.cost_projection.client if obj.cost_projection else None
    get_client.short_description = 'Client'


@admin.register(LTCAIConversation)
class LTCAIConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'current_intent', 'is_completed', 'created_at', 'completed_at']
    list_filter = ['current_intent', 'is_completed', 'created_at']
    search_fields = ['client__first_name', 'client__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'client', 'assessment', 'created_at', 'updated_at')
        }),
        ('Conversation Data', {
            'fields': ('current_intent', 'conversation_history', 'extracted_data')
        }),
        ('Status', {
            'fields': ('is_completed', 'completed_at')
        }),
    )


@admin.register(LTCClientPresentation)
class LTCClientPresentationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'presentation_date', 'presented_by', 'status', 'created_at']
    list_filter = ['status', 'presentation_date', 'created_at']
    search_fields = ['client__first_name', 'client__last_name', 'presented_by', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'presentation_date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'client', 'created_at', 'updated_at')
        }),
        ('Related Records', {
            'fields': ('assessment', 'cost_projection', 'comparison')
        }),
        ('Presentation Details', {
            'fields': ('presentation_date', 'presented_by', 'status')
        }),
        ('Content', {
            'fields': ('slides_data', 'pdf_report_path')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(LTCFacilityRecommendation)
class LTCFacilityRecommendationAdmin(admin.ModelAdmin):
    list_display = ['facility_name', 'facility_type', 'city', 'state', 'monthly_cost', 'quality_rating', 'client_interest_level', 'recommendation_score']
    list_filter = ['facility_type', 'state', 'client_interest_level', 'created_at']
    search_fields = ['facility_name', 'client__first_name', 'client__last_name', 'city', 'state']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'client', 'assessment', 'created_at', 'updated_at')
        }),
        ('Facility Details', {
            'fields': ('facility_name', 'facility_type', 'monthly_cost', 'capacity', 'availability')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code', 'latitude', 'longitude')
        }),
        ('Quality & Features', {
            'fields': ('quality_rating', 'medicare_rating', 'features', 'contact_info')
        }),
        ('Recommendation', {
            'fields': ('recommendation_score', 'recommendation_notes', 'client_interest_level')
        }),
    )