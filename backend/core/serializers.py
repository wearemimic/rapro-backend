# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, Client, Scenario 

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
        model = Client
        fields = ['spouse_first_name', 'spouse_last_name', 'spouse_birthdate', 'spouse_gender']

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




class ScenarioSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'name', 'status', 'last_updated']  # Adjust as needed

class ClientDetailSerializer(ClientSerializer):
    scenarios = ScenarioSummarySerializer(many=True, read_only=True, source='scenario_set')

    class Meta(ClientSerializer.Meta):
        fields = ClientSerializer.Meta.fields + ['scenarios']