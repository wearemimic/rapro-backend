from .models import IncomeSource
# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, Client, Scenario, Spouse, RealEstate, ReportTemplate, TemplateSlide
import logging
from django.contrib.auth import get_user_model
import json

logger = logging.getLogger(__name__)

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'company_name', 'website_url', 'address', 'city', 'state',
            'zip_code', 'white_label_company_name', 'white_label_support_email',
            'primary_color', 'logo'
        ]
        read_only_fields = ['id', 'email']  # Optional: disable email edit

class UserSerializer(serializers.ModelSerializer):
    website_url = serializers.URLField(
        required=False, 
        allow_blank=True,
        error_messages={
            'invalid': 'Please enter a valid URL including http:// or https://'
        }
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'company_name', 'website_url', 'address', 'city', 'state',
            'zip_code', 'white_label_company_name', 'white_label_support_email',
            'primary_color', 'logo'
        ]
        read_only_fields = ['id', 'username', 'email']

class SpouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spouse
        fields = ['first_name', 'last_name', 'birthdate', 'gender']

class ClientCreateSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(required=False)

    class Meta:
        model = Client
        fields = [
            "id", "first_name", "last_name", "email", "birthdate", "gender",
            "tax_status", "status", "notes", "spouse"
        ]
        extra_kwargs = {
            "advisor": {"read_only": True}
        }

    def create(self, validated_data):
        request = self.context.get('request')
        advisor = request.user

        # if not advisor or not advisor.is_authenticated:
            # raise serializers.ValidationError({"advisor": ["Invalid or missing advisor."]})
        
        validated_data.pop("advisor", None)

        spouse_data = validated_data.pop('spouse', None)
        client = Client.objects.create(advisor=advisor, **validated_data)

        if spouse_data:
            try:
                Spouse.objects.create(client=client, **spouse_data)
            except Exception as e:
                logger.error(f"Error saving spouse info for client {client.id}: {e}")
                # raise serializers.ValidationError({"spouse": f"Error saving spouse info: {str(e)}"})

        return client
    
class ClientSerializer(serializers.ModelSerializer):
    advisor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    spouse_first_name = serializers.CharField(required=False, allow_blank=True)
    spouse_last_name = serializers.CharField(required=False, allow_blank=True)
    spouse_birthdate = serializers.DateField(required=False)
    spouse_gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], required=False)
    notes = serializers.CharField(required=False, allow_blank=True, style={'base_template': 'textarea.html'})

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'birthdate', 'gender',
            'tax_status', 'spouse_first_name', 'spouse_last_name',
            'spouse_birthdate', 'spouse_gender', 'notes', 'status', 'advisor',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'advisor', 'created_at', 'updated_at']

class ClientEditSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'birthdate', 'gender',
            'tax_status', 'status', 'notes', 'spouse'
        ]
        read_only_fields = ['id', 'advisor', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        spouse_data = validated_data.pop('spouse', None)

        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle spouse logic only if not single
        if instance.tax_status.lower() != 'single':
            required_spouse_fields = ['first_name', 'last_name', 'birthdate', 'gender']
            print('DEBUG spouse_data:', spouse_data)
            print('DEBUG required fields check:', [spouse_data.get(f) not in [None, ''] for f in required_spouse_fields] if spouse_data else None)
            if spouse_data and all(spouse_data.get(f) not in [None, ''] for f in required_spouse_fields):
                print('DEBUG: Creating or updating spouse')
                try:
                    spouse = Spouse.objects.get(client=instance)
                    for attr, value in spouse_data.items():
                        setattr(spouse, attr, value)
                    spouse.save()
                except Spouse.DoesNotExist:
                    Spouse.objects.create(client=instance, **spouse_data)
            else:
                print('DEBUG: Spouse data incomplete, deleting spouse if exists')
                # If spouse data is incomplete, delete spouse if exists
                try:
                    if instance.spouse:
                        instance.spouse.delete()
                except Spouse.DoesNotExist:
                    pass
        else:
            print('DEBUG: Tax status is single, deleting spouse if exists')
            # If single and spouse exists, delete it
            try:
                if instance.spouse:
                    instance.spouse.delete()
            except Spouse.DoesNotExist:
                pass

        return instance


class ScenarioSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = [
            'id', 'name', 'updated_at', 'apply_standard_deduction',
            'retirement_age', 'medicare_age', 'spouse_retirement_age', 'spouse_medicare_age',
            'mortality_age', 'spouse_mortality_age', 'retirement_year', 'share_with_client',
            'part_b_inflation_rate', 'part_d_inflation_rate'
        ]

class ClientDetailSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(read_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    scenarios = ScenarioSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'birthdate',
            'gender',
            'tax_status',
            'notes',
            'status',
            'spouse',
            'scenarios'
        ]


# --- Additional serializers for IncomeSource and Scenario creation ---

class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        exclude = ['scenario']


class ScenarioCreateSerializer(serializers.ModelSerializer):
    income_sources = IncomeSourceSerializer(many=True, required=False)

    class Meta:
        model = Scenario
        fields = [
            'id', 'client', 'name', 'description', 'retirement_age', 'medicare_age',
            'spouse_retirement_age', 'spouse_medicare_age', 'mortality_age',
            'spouse_mortality_age', 'retirement_year', 'share_with_client', 'income_sources',
            'part_b_inflation_rate', 'part_d_inflation_rate', 'apply_standard_deduction'
        ]

    def create(self, validated_data):
        income_data = validated_data.pop('income_sources', [])
        scenario = Scenario.objects.create(**validated_data)
        for income in income_data:
            IncomeSource.objects.create(scenario=scenario, **income)
        return scenario

class ScenarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = [
            'id', 'name', 'description', 'retirement_age', 'medicare_age',
            'spouse_retirement_age', 'spouse_medicare_age', 'mortality_age',
            'spouse_mortality_age', 'retirement_year', 'share_with_client',
            'part_b_inflation_rate', 'part_d_inflation_rate', 'apply_standard_deduction',
            'roth_conversion_start_year', 'roth_conversion_duration', 'roth_conversion_annual_amount'
        ]

class IncomeSourceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        fields = [
            'id', 'owned_by', 'income_type', 'income_name', 'current_asset_balance',
            'monthly_amount', 'monthly_contribution', 'age_to_begin_withdrawal',
            'age_to_end_withdrawal', 'rate_of_return', 'cola', 'exclusion_ratio',
            'tax_rate', 'scenario_id', 'max_to_convert'
        ]
        read_only_fields = ['scenario_id']

class AdvisorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    licenses = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'password',
            'first_name', 'last_name',
            'phone_number', 'company_name',
            'website_url', 'address', 'city',
            'state', 'zip_code', 'licenses'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True},
        }

    def create(self, validated_data):
        licenses = validated_data.pop('licenses', '')
        user = User.objects.create_user(
            **validated_data
        )
        # Store licenses in a custom field or separate model if needed
        return user

class RealEstateSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        logger = logging.getLogger(__name__)
        logger.warning(f"RealEstateSerializer input data: {data}")
        data = data.copy()
        data.pop('client', None)
        return super().to_internal_value(data)

    class Meta:
        model = RealEstate
        fields = [
            'id', 'client', 'address', 'city', 'state', 'zip', 'value', 'image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']

class TemplateSlideSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateSlide
        fields = ['id', 'order', 'thumbnail_url']
    
    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

class ReportTemplateSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    slides_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = ['id', 'name', 'file_url', 'created_at', 'updated_at', 'slides_count']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_slides_count(self, obj):
        return obj.slides.count()

class ReportTemplateDetailSerializer(ReportTemplateSerializer):
    slides = TemplateSlideSerializer(many=True, read_only=True)
    
    class Meta(ReportTemplateSerializer.Meta):
        fields = ReportTemplateSerializer.Meta.fields + ['slides']