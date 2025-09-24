# affiliate_serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .affiliate_models import (
    Affiliate,
    AffiliateLink,
    AffiliateClick,
    AffiliateConversion,
    Commission,
    AffiliatePayout,
    AffiliateDiscountCode
)

User = get_user_model()


class AffiliateSerializer(serializers.ModelSerializer):
    """Serializer for Affiliate model with comprehensive details"""
    
    total_clicks = serializers.IntegerField(read_only=True)
    total_conversions = serializers.IntegerField(read_only=True)
    total_revenue_generated = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_commissions_earned = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    pending_commission_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Affiliate
        fields = [
            'id', 'affiliate_code', 'business_name', 'contact_name', 'email', 
            'phone', 'website_url', 'address', 'city', 'state', 'zip_code', 
            'country', 'tax_id', 'tax_form_on_file', 'commission_type',
            'commission_rate_first_month', 'commission_rate_recurring',
            'flat_rate_amount', 'custom_commission_terms', 'payment_method',
            'payment_details', 'minimum_payout', 'status', 'approved_at',
            'total_clicks', 'total_conversions', 'total_revenue_generated',
            'total_commissions_earned', 'total_commissions_paid',
            'pending_commission_balance', 'promotional_methods', 'admin_notes',
            'created_at', 'updated_at', 'last_activity_at'
        ]
        read_only_fields = ['id', 'affiliate_code', 'approved_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'payment_details': {'write_only': True},  # Sensitive information
            'tax_id': {'write_only': True},  # Sensitive information
        }


class AffiliateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing affiliates"""
    
    class Meta:
        model = Affiliate
        fields = [
            'id', 'affiliate_code', 'business_name', 'email', 'status',
            'total_conversions', 'total_commissions_earned', 'created_at'
        ]
        read_only_fields = fields


class AffiliateLinkSerializer(serializers.ModelSerializer):
    """Serializer for affiliate tracking links"""
    
    full_url = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_max_uses_reached = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AffiliateLink
        fields = [
            'id', 'affiliate', 'campaign_name', 'tracking_code', 
            'destination_url', 'short_url', 'full_url', 'discount_code',
            'utm_source', 'utm_medium', 'utm_campaign', 'is_active',
            'max_uses', 'current_uses', 'expires_at', 'is_expired',
            'is_max_uses_reached', 'total_clicks', 'unique_clicks',
            'conversions', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tracking_code', 'full_url', 'current_uses', 
            'total_clicks', 'unique_clicks', 'conversions', 
            'created_at', 'updated_at'
        ]
    
    def get_full_url(self, obj):
        return obj.get_full_url()


class AffiliateClickSerializer(serializers.ModelSerializer):
    """Serializer for click tracking data"""
    
    class Meta:
        model = AffiliateClick
        fields = [
            'id', 'affiliate', 'link', 'session_id', 'tracking_code',
            'ip_address', 'user_agent', 'referrer', 'country_code',
            'region', 'city', 'is_mobile', 'device_type', 'browser',
            'os', 'is_bot', 'is_valid', 'converted', 'conversion_date',
            'clicked_at'
        ]
        read_only_fields = fields


class AffiliateConversionSerializer(serializers.ModelSerializer):
    """Serializer for conversion tracking"""
    
    user_email = serializers.EmailField(read_only=True)
    
    class Meta:
        model = AffiliateConversion
        fields = [
            'id', 'affiliate', 'click', 'user', 'user_email',
            'stripe_subscription_id', 'stripe_customer_id',
            'subscription_plan', 'subscription_amount', 'mrr_value',
            'attribution_type', 'discount_code_used', 'is_valid',
            'is_refunded', 'refunded_at', 'conversion_date', 'updated_at'
        ]
        read_only_fields = fields


class CommissionSerializer(serializers.ModelSerializer):
    """Serializer for commission records"""
    
    affiliate_name = serializers.CharField(source='affiliate.business_name', read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id', 'affiliate', 'affiliate_name', 'conversion',
            'commission_type', 'description', 'base_amount',
            'commission_rate', 'commission_amount', 'period_start',
            'period_end', 'status', 'payout', 'adjustment_reason',
            'created_at', 'updated_at', 'approved_at', 'paid_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'approved_at', 'paid_at'
        ]


class AffiliatePayoutSerializer(serializers.ModelSerializer):
    """Serializer for payout records"""
    
    affiliate_name = serializers.CharField(source='affiliate.business_name', read_only=True)
    commissions = CommissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = AffiliatePayout
        fields = [
            'id', 'affiliate', 'affiliate_name', 'payout_period_start',
            'payout_period_end', 'total_commissions', 'adjustments',
            'fees', 'net_payout', 'payment_method', 'payment_reference',
            'status', 'processed_by', 'notes', 'error_message',
            'tax_form_sent', 'tax_year', 'created_at', 'processed_at',
            'completed_at', 'commissions'
        ]
        read_only_fields = [
            'id', 'created_at', 'processed_at', 'completed_at'
        ]


class AffiliateDiscountCodeSerializer(serializers.ModelSerializer):
    """Serializer for discount codes"""
    
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AffiliateDiscountCode
        fields = [
            'id', 'affiliate', 'code', 'description', 'discount_type',
            'discount_value', 'max_uses', 'max_uses_per_customer',
            'current_uses', 'is_active', 'is_valid', 'valid_from',
            'expires_at', 'applicable_plans', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_uses', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        """Ensure discount code is unique and uppercase"""
        value = value.upper()
        if self.instance is None:  # Creating new code
            if AffiliateDiscountCode.objects.filter(code=value).exists():
                raise serializers.ValidationError("This discount code already exists.")
        return value


class AffiliateDashboardSerializer(serializers.ModelSerializer):
    """Comprehensive dashboard data for affiliates"""
    
    recent_clicks = serializers.SerializerMethodField()
    recent_conversions = serializers.SerializerMethodField()
    pending_commissions = serializers.SerializerMethodField()
    active_links = serializers.SerializerMethodField()
    performance_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = Affiliate
        fields = [
            'id', 'affiliate_code', 'business_name', 'status',
            'total_clicks', 'total_conversions', 'total_revenue_generated',
            'total_commissions_earned', 'pending_commission_balance',
            'recent_clicks', 'recent_conversions', 'pending_commissions',
            'active_links', 'performance_metrics'
        ]
    
    def get_recent_clicks(self, obj):
        """Get last 10 clicks"""
        clicks = obj.clicks.order_by('-clicked_at')[:10]
        return AffiliateClickSerializer(clicks, many=True).data
    
    def get_recent_conversions(self, obj):
        """Get last 10 conversions"""
        conversions = obj.conversions.order_by('-conversion_date')[:10]
        return AffiliateConversionSerializer(conversions, many=True).data
    
    def get_pending_commissions(self, obj):
        """Get pending commissions"""
        commissions = obj.commissions.filter(status='pending')
        return CommissionSerializer(commissions, many=True).data
    
    def get_active_links(self, obj):
        """Get active tracking links"""
        links = obj.links.filter(is_active=True)
        return AffiliateLinkSerializer(links, many=True).data
    
    def get_performance_metrics(self, obj):
        """Calculate performance metrics"""
        from django.db.models import Avg, Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate metrics for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        clicks_30d = obj.clicks.filter(clicked_at__gte=thirty_days_ago).count()
        conversions_30d = obj.conversions.filter(conversion_date__gte=thirty_days_ago).count()
        revenue_30d = obj.conversions.filter(
            conversion_date__gte=thirty_days_ago
        ).aggregate(total=Sum('subscription_amount'))['total'] or 0
        
        conversion_rate = 0
        if clicks_30d > 0:
            conversion_rate = (conversions_30d / clicks_30d) * 100
        
        return {
            'clicks_last_30_days': clicks_30d,
            'conversions_last_30_days': conversions_30d,
            'revenue_last_30_days': str(revenue_30d),
            'conversion_rate': round(conversion_rate, 2),
            'average_order_value': str(
                obj.conversions.aggregate(avg=Avg('subscription_amount'))['avg'] or 0
            )
        }


class CreateAffiliateLinkSerializer(serializers.ModelSerializer):
    """Serializer for creating new tracking links"""
    
    class Meta:
        model = AffiliateLink
        fields = [
            'campaign_name', 'destination_url', 'discount_code',
            'utm_source', 'utm_medium', 'utm_campaign', 'max_uses',
            'expires_at'
        ]
    
    def create(self, validated_data):
        """Create new tracking link with auto-generated tracking code"""
        # The tracking_code is auto-generated by the model's default
        return super().create(validated_data)


class TrackClickSerializer(serializers.Serializer):
    """Serializer for tracking click events"""
    
    tracking_code = serializers.CharField(required=True)
    session_id = serializers.CharField(required=True)
    ip_address = serializers.IPAddressField(required=False)
    user_agent = serializers.CharField(required=False)
    referrer = serializers.URLField(required=False, allow_blank=True)
    
    def validate_tracking_code(self, value):
        """Validate that tracking code exists"""
        if not AffiliateLink.objects.filter(tracking_code=value).exists():
            raise serializers.ValidationError("Invalid tracking code.")
        return value