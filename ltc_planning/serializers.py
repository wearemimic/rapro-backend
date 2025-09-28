from rest_framework import serializers
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


class LTCAssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for LTC Assessment with ADL/IADL validation
    """
    adl_score = serializers.SerializerMethodField()
    iadl_score = serializers.SerializerMethodField()

    class Meta:
        model = LTCAssessment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_adl_score(self, obj):
        """Calculate ADL score"""
        return obj.calculate_adl_score()

    def get_iadl_score(self, obj):
        """Calculate IADL score"""
        return obj.calculate_iadl_score()

    def validate_assessment_score_adl(self, value):
        """Validate ADL assessment structure"""
        required_keys = ['bathing', 'dressing', 'toileting', 'transferring', 'continence', 'eating']
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError(
                f"Missing required ADL keys. Required: {', '.join(required_keys)}"
            )
        return value

    def validate_assessment_score_iadl(self, value):
        """Validate IADL assessment structure"""
        required_keys = ['phone', 'shopping', 'food_prep', 'housekeeping', 'laundry', 'transportation', 'medications', 'finances']
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError(
                f"Missing required IADL keys. Required: {', '.join(required_keys)}"
            )
        return value


class LTCCostProjectionSerializer(serializers.ModelSerializer):
    """
    Serializer for cost projections
    """
    class Meta:
        model = LTCCostProjection
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_years_projected(self, value):
        """Validate years projected is reasonable"""
        if value < 1 or value > 50:
            raise serializers.ValidationError("Years projected must be between 1 and 50")
        return value

    def validate_annual_cost_projections(self, value):
        """Validate structure of annual projections"""
        if not isinstance(value, list):
            raise serializers.ValidationError("annual_cost_projections must be a list")

        # Validate each year's data has required fields
        required_fields = ['year', 'age', 'care_level', 'total_cost']
        for projection in value:
            if not all(field in projection for field in required_fields):
                raise serializers.ValidationError(
                    f"Each projection must contain: {', '.join(required_fields)}"
                )

        return value


class InsuranceProductSerializer(serializers.ModelSerializer):
    """
    Serializer for insurance products
    """
    class Meta:
        model = InsuranceProduct
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Validate unique carrier/product combination"""
        carrier = data.get('carrier')
        product_name = data.get('product_name')

        if carrier and product_name:
            # Check for duplicates (excluding current instance if updating)
            queryset = InsuranceProduct.objects.filter(carrier=carrier, product_name=product_name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    f"Insurance product '{product_name}' from '{carrier}' already exists"
                )

        return data


class InsuranceIllustrationSerializer(serializers.ModelSerializer):
    """
    Serializer for insurance illustrations with OCR data
    """
    class Meta:
        model = InsuranceIllustration
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_extraction_confidence(self, value):
        """Validate extraction confidence is between 0 and 1"""
        if value < 0.0 or value > 1.0:
            raise serializers.ValidationError("Extraction confidence must be between 0.00 and 1.00")
        return value

    def validate_parsed_data(self, value):
        """Validate parsed data has minimum required fields"""
        if not value:
            return value

        # Recommended fields for a complete illustration
        recommended_fields = ['daily_benefit', 'benefit_period_years', 'annual_premium', 'total_benefit_pool']
        missing_fields = [field for field in recommended_fields if field not in value]

        if missing_fields:
            # Warning, not error - some illustrations may not have all fields
            pass

        return value


class LTCCostCoverageComparisonSerializer(serializers.ModelSerializer):
    """
    Serializer for cost vs coverage comparison
    """
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = LTCCostCoverageComparison
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_client_name(self, obj):
        """Get client name from cost projection"""
        if obj.cost_projection and obj.cost_projection.client:
            client = obj.cost_projection.client
            return f"{client.first_name} {client.last_name}" if hasattr(client, 'first_name') else str(client)
        return None

    def validate(self, data):
        """Validate that cost projection and illustration belong to same client"""
        cost_projection = data.get('cost_projection')
        insurance_illustration = data.get('insurance_illustration')

        if cost_projection and insurance_illustration:
            if cost_projection.client_id != insurance_illustration.client_id:
                raise serializers.ValidationError(
                    "Cost projection and insurance illustration must belong to the same client"
                )

        return data


class LTCAIConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for AI conversations
    """
    message_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = LTCAIConversation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_message_count(self, obj):
        """Get total message count in conversation"""
        return len(obj.conversation_history) if obj.conversation_history else 0

    def get_completion_percentage(self, obj):
        """Estimate completion percentage based on extracted data"""
        if not obj.extracted_data:
            return 0

        # Required fields for complete assessment
        required_fields = [
            'age', 'gender', 'location', 'living_situation',
            'assessment_score_adl', 'assessment_score_iadl',
            'health_conditions', 'cognitive_status'
        ]

        completed_fields = sum(1 for field in required_fields if field in obj.extracted_data and obj.extracted_data[field])
        percentage = (completed_fields / len(required_fields)) * 100

        return round(percentage, 1)

    def validate_conversation_history(self, value):
        """Validate conversation history structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("conversation_history must be a list")

        for message in value:
            if not isinstance(message, dict):
                raise serializers.ValidationError("Each message must be a dictionary")

            required_keys = ['role', 'message', 'timestamp']
            if not all(key in message for key in required_keys):
                raise serializers.ValidationError(
                    f"Each message must contain: {', '.join(required_keys)}"
                )

            if message['role'] not in ['advisor', 'assistant', 'system']:
                raise serializers.ValidationError("Message role must be 'advisor', 'assistant', or 'system'")

        return value


class LTCClientPresentationSerializer(serializers.ModelSerializer):
    """
    Serializer for client presentations
    """
    class Meta:
        model = LTCClientPresentation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_slides_data(self, value):
        """Validate slides data structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("slides_data must be a list")

        # Optionally validate slide structure
        for slide in value:
            if not isinstance(slide, dict):
                raise serializers.ValidationError("Each slide must be a dictionary")

            if 'slide_number' not in slide or 'content' not in slide:
                raise serializers.ValidationError("Each slide must have 'slide_number' and 'content'")

        return value


class LTCFacilityRecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer for facility recommendations
    """
    distance_from_client = serializers.SerializerMethodField()

    class Meta:
        model = LTCFacilityRecommendation
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_distance_from_client(self, obj):
        """
        Calculate distance from client location (if available)
        Returns distance in miles or None
        """
        # This would require client location data
        # Placeholder for future implementation
        return None

    def validate_quality_rating(self, value):
        """Validate quality rating is 0-5"""
        if value is not None and (value < 0 or value > 5.0):
            raise serializers.ValidationError("Quality rating must be between 0 and 5.0")
        return value

    def validate_medicare_rating(self, value):
        """Validate Medicare rating is 1-5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Medicare rating must be between 1 and 5")
        return value

    def validate(self, data):
        """Validate location data"""
        state = data.get('state')
        if state and len(state) != 2:
            raise serializers.ValidationError("State must be a 2-letter state code")

        return data


# List serializers for collection endpoints
class LTCAssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing assessments"""
    adl_score = serializers.SerializerMethodField()
    iadl_score = serializers.SerializerMethodField()

    class Meta:
        model = LTCAssessment
        fields = ['id', 'client', 'assessment_type', 'care_level_recommendation', 'cognitive_status', 'adl_score', 'iadl_score', 'created_at']
        read_only_fields = ('id', 'created_at')

    def get_adl_score(self, obj):
        return obj.calculate_adl_score()

    def get_iadl_score(self, obj):
        return obj.calculate_iadl_score()


class LTCCostProjectionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing cost projections"""
    class Meta:
        model = LTCCostProjection
        fields = ['id', 'client', 'scenario_name', 'total_lifetime_cost', 'years_projected', 'created_at']
        read_only_fields = ('id', 'created_at')