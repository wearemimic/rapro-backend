"""
Serializers for Activity Log
"""
from rest_framework import serializers
from ..models import ActivityLog, Client, Lead


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    client_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'activity_type', 'activity_type_display', 'description',
            'user', 'user_name', 'user_email',
            'client', 'client_name',
            'lead', 'lead_name',
            'metadata', 'created_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_client_name(self, obj):
        """Get client full name"""
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        return None
    
    def get_lead_name(self, obj):
        """Get lead full name"""
        if obj.lead:
            return f"{obj.lead.first_name} {obj.lead.last_name}"
        return None
    
    def get_time_ago(self, obj):
        """Get human-readable time difference"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")


class ActivityStatsSerializer(serializers.Serializer):
    """Serializer for activity statistics"""
    
    total_30_days = serializers.IntegerField()
    by_type = serializers.DictField()
    today = serializers.IntegerField()
    this_week = serializers.IntegerField()