from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Client, Scenario
from .models import (
    ReportTemplate, Report, ReportSection, ReportShare, 
    ReportComment, TemplateAnalytics, ReportGeneration
)

User = get_user_model()


class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_config',
            'preview_image', 'is_public', 'is_active', 'created_by', 
            'created_by_name', 'created_at', 'updated_at', 'usage_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_usage_count(self, obj):
        return obj.reports.count()


class ReportSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSection
        fields = [
            'id', 'report', 'section_type', 'title', 'content_config',
            'order', 'is_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    sections = ReportSectionSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    scenario_name = serializers.CharField(source='scenario.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'client', 'client_name', 'scenario', 'scenario_name',
            'template', 'template_name', 'report_config', 'status', 'file_path',
            'generation_started_at', 'generation_completed_at', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'sections'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ReportShareSerializer(serializers.ModelSerializer):
    report_title = serializers.CharField(source='report.title', read_only=True)
    shared_by_name = serializers.CharField(source='shared_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportShare
        fields = [
            'id', 'report', 'report_title', 'share_type', 'recipient_email',
            'access_level', 'expires_at', 'is_active', 'shared_by',
            'shared_by_name', 'created_at', 'last_accessed'
        ]
        read_only_fields = ['id', 'created_at', 'shared_by']


class ReportCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = ReportComment
        fields = [
            'id', 'report', 'content', 'author', 'author_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']


class TemplateAnalyticsSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = TemplateAnalytics
        fields = [
            'id', 'template', 'template_name', 'usage_count', 'average_generation_time',
            'last_used', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportGenerationSerializer(serializers.ModelSerializer):
    report_title = serializers.CharField(source='report.title', read_only=True)
    
    class Meta:
        model = ReportGeneration
        fields = [
            'id', 'report', 'report_title', 'generation_status', 'started_at',
            'completed_at', 'error_message', 'file_size', 'processing_time'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']