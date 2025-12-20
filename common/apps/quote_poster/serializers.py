from rest_framework import serializers
from .models import Background, QuotePoster, PosterFeedback, PosterShare
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class BackgroundSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Background
        fields = [
            'id', 'user', 'session_id', 'image_uuid', 'prompt', 'width', 'height',
            'style_preset', 's3_url', 'local_url', 'url', 'service', 'model',
            'status', 'error_message', 'metadata', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_url(self, obj):
        """Return S3 URL if available, otherwise local URL"""
        return obj.get_url()


class QuotePosterSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    background = BackgroundSerializer(read_only=True)
    background_id = serializers.PrimaryKeyRelatedField(
        queryset=Background.objects.all(),
        write_only=True,
        required=False
    )
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = QuotePoster
        fields = [
            'id', 'user', 'session_id', 'background', 'background_id', 'quote_text',
            'font_family', 'font_size', 'font_color', 'alignment', 'orientation',
            'opacity', 'shadow', 's3_url', 'local_url', 'url', 'status', 'error_message',
            'metadata', 'is_public', 'share_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_url(self, obj):
        """Return S3 URL if available, otherwise local URL"""
        return obj.get_url()


class QuotePosterDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with related feedback"""
    user = UserSerializer(read_only=True)
    background = BackgroundSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    
    class Meta:
        model = QuotePoster
        fields = [
            'id', 'user', 'session_id', 'background', 'quote_text',
            'font_family', 'font_size', 'font_color', 'alignment', 'orientation',
            'opacity', 'shadow', 's3_url', 'local_url', 'url', 'status',
            'metadata', 'is_public', 'share_count', 'feedback', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_url(self, obj):
        return obj.get_url()
    
    def get_feedback(self, obj):
        feedback = obj.feedback.all()
        return PosterFeedbackSerializer(feedback, many=True).data


class PosterFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PosterFeedback
        fields = ['id', 'poster', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        """Override create to set user from request context"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PosterShareSerializer(serializers.ModelSerializer):
    poster = QuotePosterSerializer(read_only=True)
    poster_id = serializers.PrimaryKeyRelatedField(
        queryset=QuotePoster.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = PosterShare
        fields = [
            'id', 'poster', 'poster_id', 'shared_by', 'share_url', 'share_token',
            'view_count', 'is_active', 'created_at', 'updated_at', 'expires_at'
        ]
        read_only_fields = ['id', 'shared_by', 'share_url', 'share_token', 'view_count', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Override create to set shared_by from request context"""
        validated_data['shared_by'] = self.context['request'].user
        return super().create(validated_data)


class BackgroundCreateSerializer(serializers.Serializer):
    """Serializer for background creation from FastAPI"""
    user_id = serializers.CharField(max_length=255)
    session_id = serializers.CharField(max_length=255)
    image_uuid = serializers.CharField(max_length=255)
    prompt = serializers.CharField(required=False, allow_blank=True)
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)
    style_preset = serializers.CharField(max_length=100, required=False)
    s3_url = serializers.URLField(required=False, allow_blank=True)
    s3_key = serializers.CharField(max_length=500, required=False, allow_blank=True)
    local_url = serializers.URLField()
    service = serializers.CharField(max_length=50, required=False)
    model = serializers.CharField(max_length=100, required=False, allow_blank=True)
    status = serializers.CharField(max_length=20, default='completed')
    
    def create(self, validated_data):
        """Create background record"""
        from django.contrib.auth.models import User
        
        user_id = validated_data.pop('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User {user_id} not found")
        
        background = Background.objects.create(user=user, **validated_data)
        return background


class QuotePosterCreateSerializer(serializers.Serializer):
    """Serializer for poster creation from FastAPI"""
    user_id = serializers.CharField(max_length=255)
    session_id = serializers.CharField(max_length=255)
    background_uuid = serializers.CharField(max_length=255)
    quote_text = serializers.CharField()
    font_family = serializers.CharField(max_length=100, required=False)
    font_size = serializers.IntegerField(required=False)
    font_color = serializers.CharField(max_length=7, required=False)
    alignment = serializers.CharField(max_length=10, required=False)
    orientation = serializers.CharField(max_length=15, required=False)
    s3_url = serializers.URLField(required=False, allow_blank=True)
    s3_key = serializers.CharField(max_length=500, required=False, allow_blank=True)
    local_url = serializers.URLField()
    status = serializers.CharField(max_length=20, default='completed')
    
    def create(self, validated_data):
        """Create poster record"""
        from django.contrib.auth.models import User
        
        user_id = validated_data.pop('user_id')
        background_uuid = validated_data.pop('background_uuid')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User {user_id} not found")
        
        try:
            background = Background.objects.get(image_uuid=background_uuid)
        except Background.DoesNotExist:
            raise serializers.ValidationError(f"Background {background_uuid} not found")
        
        poster = QuotePoster.objects.create(
            user=user,
            background=background,
            **validated_data
        )
        return poster