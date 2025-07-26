from rest_framework import serializers
from .models import FeatureUsage, UserSession, DailyUserStats, FeaturePricing
from django.contrib.auth import get_user_model

User = get_user_model()


class FeatureUsageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    feature_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FeatureUsage
        fields = [
            'id', 'user', 'username', 'feature_name', 'feature_display_name',
            'feature_category', 'session_id', 'status', 'credits_used',
            'input_data', 'output_data', 'processing_time', 'endpoint_path',
            'error_message', 'error_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at']
    
    def get_feature_display_name(self, obj):
        """Get human-readable feature name"""
        feature_choices = dict(FeatureUsage.AI_FEATURES)
        return feature_choices.get(obj.feature_name, obj.feature_name.replace('_', ' ').title())


class UserSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    duration = serializers.SerializerMethodField()
    platform_display = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'username', 'session_id', 'platform', 'platform_display',
            'start_time', 'last_activity', 'end_time', 'is_active', 'duration',
            'ip_address', 'device_info', 'total_ai_features_used',
            'total_credits_spent', 'total_requests'
        ]
        read_only_fields = ['id', 'user', 'username']
    
    def get_duration(self, obj):
        """Calculate session duration"""
        if obj.end_time:
            delta = obj.end_time - obj.start_time
            return delta.total_seconds()
        elif obj.is_active:
            from django.utils import timezone
            delta = timezone.now() - obj.start_time
            return delta.total_seconds()
        return None
    
    def get_platform_display(self, obj):
        """Get human-readable platform name"""
        platform_choices = dict(UserSession.PLATFORM_CHOICES)
        return platform_choices.get(obj.platform, obj.platform)


class DailyUserStatsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    success_rate = serializers.SerializerMethodField()
    average_credits_per_request = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyUserStats
        fields = [
            'id', 'user', 'username', 'date', 'total_ai_requests',
            'unique_features_used', 'total_credits_spent', 'total_session_time',
            'successful_requests', 'failed_requests', 'success_rate',
            'average_credits_per_request', 'feature_usage_breakdown',
            'category_usage_breakdown'
        ]
        read_only_fields = ['id', 'user', 'username']
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        total = obj.total_ai_requests
        if total == 0:
            return 0.0
        return round((obj.successful_requests / total) * 100, 2)
    
    def get_average_credits_per_request(self, obj):
        """Calculate average credits spent per request"""
        if obj.total_ai_requests == 0:
            return 0.0
        return round(obj.total_credits_spent / obj.total_ai_requests, 2)


class FeaturePricingSerializer(serializers.ModelSerializer):
    feature_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FeaturePricing
        fields = [
            'id', 'feature_name', 'feature_display_name', 'base_credits',
            'per_unit_credits', 'description', 'tier_1_limit', 'tier_1_price',
            'tier_2_price', 'tier_3_price', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_feature_display_name(self, obj):
        """Get human-readable feature name"""
        feature_choices = dict(FeatureUsage.AI_FEATURES)
        return feature_choices.get(obj.feature_name, obj.feature_name.replace('_', ' ').title())


# Serializers for API communication between FastAPI and Django

class UsageTrackingStartSerializer(serializers.Serializer):
    """Serializer for starting usage tracking"""
    user_id = serializers.UUIDField()
    feature_name = serializers.CharField(max_length=50)
    input_data = serializers.JSONField(required=False, allow_null=True)
    session_id = serializers.CharField(max_length=255, required=False, allow_null=True)
    endpoint_path = serializers.CharField(max_length=255, required=False, allow_blank=True)
    user_agent = serializers.CharField(max_length=500, required=False, allow_blank=True)
    ip_address = serializers.IPAddressField(required=False, allow_null=True)


class UsageTrackingCompleteSerializer(serializers.Serializer):
    """Serializer for completing usage tracking"""
    usage_id = serializers.UUIDField()
    output_data = serializers.JSONField(required=False, allow_null=True)
    processing_time = serializers.FloatField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=['completed', 'failed'], 
        default='completed'
    )


class UsageTrackingFailSerializer(serializers.Serializer):
    """Serializer for failing usage tracking"""
    usage_id = serializers.UUIDField()
    error_message = serializers.CharField(max_length=1000)
    error_code = serializers.CharField(max_length=50, default='API_ERROR')
    refund_credits = serializers.BooleanField(default=True)


class UserUsageSummarySerializer(serializers.Serializer):
    """Serializer for user usage summary"""
    period_days = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    total_credits_spent = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    failed_requests = serializers.IntegerField()
    success_rate = serializers.FloatField()
    unique_features_used = serializers.IntegerField()
    feature_usage_breakdown = serializers.DictField()
    daily_stats = serializers.ListField()


class PlatformAnalyticsSerializer(serializers.Serializer):
    """Serializer for platform analytics"""
    period_days = serializers.IntegerField()
    total_active_users = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    total_credits_spent = serializers.IntegerField()
    average_requests_per_user = serializers.FloatField()
    average_credits_per_user = serializers.FloatField()
    popular_features = serializers.ListField()
    category_usage = serializers.ListField()


class CreateUserSessionSerializer(serializers.Serializer):
    """Serializer for creating user sessions"""
    platform = serializers.ChoiceField(
        choices=UserSession.PLATFORM_CHOICES,
        default='web'
    )
    device_info = serializers.JSONField(required=False, default=dict)


class FeatureCostSerializer(serializers.Serializer):
    """Serializer for feature cost information"""
    feature_name = serializers.CharField()
    base_credits = serializers.IntegerField()
    calculated_cost = serializers.IntegerField()
    user_tier = serializers.IntegerField()
    description = serializers.CharField()
