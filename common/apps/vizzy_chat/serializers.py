"""
Vizzy Chat DRF Serializers

Production-ready serializers with:
- Validation logic
- Nested relationships
- Performance optimizations
- Clean error messages
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    VizzyChatSession,
    VizzyChatMessage,
    VizzyUserProfile,
    VizzyMoodHistory,
    VizzyContextData
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested relationships"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']


class VizzyChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = VizzyChatMessage
        fields = [
            'id',
            'session',
            'role',
            'content',
            'has_images',
            'image_urls',
            'created_at',
            'tokens_used',
            'processing_time_ms',
            'detected_emotion',
            'mood_valence',
            'mood_arousal',
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_mood_valence(self, value):
        """Validate mood valence is within range"""
        if value is not None and not -1.0 <= value <= 1.0:
            raise serializers.ValidationError("Mood valence must be between -1.0 and 1.0")
        return value
    
    def validate_mood_arousal(self, value):
        """Validate mood arousal is within range"""
        if value is not None and not -1.0 <= value <= 1.0:
            raise serializers.ValidationError("Mood arousal must be between -1.0 and 1.0")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        if data.get('has_images') and not data.get('image_urls'):
            raise serializers.ValidationError({
                'image_urls': 'image_urls must be provided when has_images is True'
            })
        return data


class VizzyChatMessageCreateSerializer(serializers.ModelSerializer):
    """Optimized serializer for creating messages (excludes session from input)"""
    
    class Meta:
        model = VizzyChatMessage
        fields = [
            'role',
            'content',
            'has_images',
            'image_urls',
            'tokens_used',
            'processing_time_ms',
            'detected_emotion',
            'mood_valence',
            'mood_arousal',
        ]
    
    def validate_role(self, value):
        """Ensure role is valid"""
        valid_roles = ['user', 'assistant', 'system']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
        return value


class VizzyChatSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists"""
    user = UserBasicSerializer(read_only=True)
    recent_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = VizzyChatSession
        fields = [
            'id',
            'user',
            'title',
            'mode',
            'is_active',
            'created_at',
            'updated_at',
            'last_message_at',
            'message_count',
            'recent_messages',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_message_at', 'message_count']
    
    def get_recent_messages(self, obj):
        """Get last 3 messages for preview"""
        messages = obj.messages.order_by('-created_at')[:3]
        return VizzyChatMessageSerializer(messages, many=True).data


class VizzyChatSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual session with messages"""
    user = UserBasicSerializer(read_only=True)
    messages = serializers.SerializerMethodField()
    
    class Meta:
        model = VizzyChatSession
        fields = [
            'id',
            'user',
            'title',
            'mode',
            'is_active',
            'created_at',
            'updated_at',
            'closed_at',
            'last_message_at',
            'message_count',
            'messages',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'last_message_at', 'message_count', 'closed_at']
    
    def get_messages(self, obj):
        """Get all messages ordered chronologically"""
        # Limit to last 100 messages for performance
        limit = self.context.get('message_limit', 100)
        messages = obj.messages.order_by('created_at')[:limit]
        return VizzyChatMessageSerializer(messages, many=True).data


class VizzyChatSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new sessions"""
    
    class Meta:
        model = VizzyChatSession
        fields = ['title', 'mode']
    
    def validate_mode(self, value):
        """Validate mode is allowed"""
        valid_modes = ['home', 'enterprise']
        if value not in valid_modes:
            raise serializers.ValidationError(f"Mode must be one of: {', '.join(valid_modes)}")
        return value
    
    def create(self, validated_data):
        """Create session with user from context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class VizzyUserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = VizzyUserProfile
        fields = [
            'user',
            'aesthetic_palette',
            'mood_map',
            'story_markers',
            'device_context',
            'total_sessions',
            'total_messages',
            'last_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'total_sessions', 'total_messages', 'last_active', 'created_at', 'updated_at']
    
    def validate_aesthetic_palette(self, value):
        """Validate aesthetic palette structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("aesthetic_palette must be a dictionary")
        return value
    
    def validate_mood_map(self, value):
        """Validate mood map structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("mood_map must be a dictionary")
        return value
    
    def validate_story_markers(self, value):
        """Validate story markers structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("story_markers must be a list")
        return value
    
    def validate_device_context(self, value):
        """Validate device context structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("device_context must be a dictionary")
        return value


class VizzyMoodHistorySerializer(serializers.ModelSerializer):
    """Serializer for mood history entries"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = VizzyMoodHistory
        fields = [
            'id',
            'user',
            'session',
            'valence',
            'arousal',
            'emotion_label',
            'timestamp',
            'source',
            'confidence',
        ]
        read_only_fields = ['id', 'user', 'timestamp']
    
    def validate_valence(self, value):
        """Validate valence is within range"""
        if not -1.0 <= value <= 1.0:
            raise serializers.ValidationError("Valence must be between -1.0 and 1.0")
        return value
    
    def validate_arousal(self, value):
        """Validate arousal is within range"""
        if not -1.0 <= value <= 1.0:
            raise serializers.ValidationError("Arousal must be between -1.0 and 1.0")
        return value
    
    def validate_confidence(self, value):
        """Validate confidence is within range"""
        if value is not None and not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Confidence must be between 0.0 and 1.0")
        return value


class VizzyMoodHistoryCreateSerializer(serializers.ModelSerializer):
    """Optimized serializer for creating mood history entries"""
    
    class Meta:
        model = VizzyMoodHistory
        fields = [
            'session',
            'valence',
            'arousal',
            'emotion_label',
            'source',
            'confidence',
        ]
    
    def create(self, validated_data):
        """Create mood history with user from context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class VizzyContextDataSerializer(serializers.ModelSerializer):
    """Serializer for context data entries"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = VizzyContextData
        fields = [
            'id',
            'user',
            'context_type',
            'key',
            'value',
            'created_at',
            'accessed_at',
            'access_count',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'accessed_at', 'access_count']
    
    def validate_context_type(self, value):
        """Validate context type is allowed"""
        valid_types = ['preference', 'creation', 'interaction', 'knowledge', 'metadata']
        if value not in valid_types:
            raise serializers.ValidationError(f"Context type must be one of: {', '.join(valid_types)}")
        return value
    
    def validate_value(self, value):
        """Validate value is valid JSON"""
        if not isinstance(value, (dict, list, str, int, float, bool, type(None))):
            raise serializers.ValidationError("Value must be a valid JSON type")
        return value


class VizzyContextDataCreateSerializer(serializers.ModelSerializer):
    """Optimized serializer for creating context data"""
    
    class Meta:
        model = VizzyContextData
        fields = ['context_type', 'key', 'value']
    
    def create(self, validated_data):
        """Create context data with user from context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class VizzyUserContextSerializer(serializers.Serializer):
    """
    Comprehensive user context for AI processing
    
    This aggregates data from multiple models for FastAPI consumption
    """
    user_id = serializers.UUIDField()
    email = serializers.EmailField()
    
    # Profile data
    aesthetic_palette = serializers.JSONField()
    mood_map = serializers.JSONField()
    story_markers = serializers.JSONField()
    device_context = serializers.JSONField()
    
    # Recent activity
    recent_moods = VizzyMoodHistorySerializer(many=True, required=False)
    total_sessions = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    last_active = serializers.DateTimeField(allow_null=True)
    
    # Context data
    context_entries = VizzyContextDataSerializer(many=True, required=False)
