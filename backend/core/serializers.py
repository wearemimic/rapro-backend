from .models import IncomeSource
# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, Client, Scenario, Spouse
import logging

logger = logging.getLogger(__name__)

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
    profile = CustomUserSerializer()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    
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
            if spouse_data and any(spouse_data.values()):
                spouse, _ = Spouse.objects.get_or_create(client=instance)
                for attr, value in spouse_data.items():
                    setattr(spouse, attr, value)
                spouse.save()
        else:
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
        fields = ['id', 'name', 'updated_at']  # Adjust as needed

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
            'spouse_mortality_age', 'retirement_year', 'share_with_client', 'income_sources'
        ]

    def create(self, validated_data):
        income_data = validated_data.pop('income_sources', [])
        scenario = Scenario.objects.create(**validated_data)
        for income in income_data:
            IncomeSource.objects.create(scenario=scenario, **income)
        return scenario