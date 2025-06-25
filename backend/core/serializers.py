from .models import IncomeSource
# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, Client, Scenario, Spouse
import logging
from django.contrib.auth import get_user_model

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