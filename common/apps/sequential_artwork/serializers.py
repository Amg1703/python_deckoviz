from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SequentialArtwork, SequentialArtworkIteration

User = get_user_model()


class SequentialArtworkIterationSerializer(serializers.ModelSerializer):
    # ✅ Make artwork optional and nullable
    artwork = serializers.PrimaryKeyRelatedField(
        queryset=SequentialArtwork.objects.all(),
        required=False,  # ✅ Set to False
        allow_null=True   # ✅ Allow null
    )
    
    # ✅ Use CharField instead of URLField for better compatibility
    generated_image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=2000,
        default=None
    )
    
    s3_image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=2000,
        default=None
    )
    
    s3_image_key = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=1000,
        default=None
    )
    
    generated_image_path = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500,
        default=None
    )
    
    reference_image_path = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=500,
        default=None
    )
    
    user_id = serializers.CharField(
        required=False,
        max_length=255
    )
    
    # ✅ Make these optional too
    user_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000
    )
    
    assistant_response = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10000
    )
    
    image_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10000
    )
    
    iteration_number = serializers.IntegerField(required=False)
    
    def validate_generated_image_url(self, value):
        """Convert empty string to None"""
        if not value or not str(value).strip():
            return None
        return str(value).strip()
    
    def validate_s3_image_url(self, value):
        """Convert empty string to None"""
        if not value or not str(value).strip():
            return None
        return str(value).strip()
    
    def validate_s3_image_key(self, value):
        """Convert empty string to None"""
        if not value or not str(value).strip():
            return None
        return str(value).strip()
    
    def create(self, validated_data):
        """Create iteration with user lookup"""
        user_id = validated_data.pop('user_id', None)
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                validated_data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User {user_id} not found")
        
        return super().create(validated_data)
    
    class Meta:
        model = SequentialArtworkIteration
        fields = [
            'id',
            'user_id',
            'artwork',
            'iteration_number',
            'user_prompt',
            'assistant_response',
            'image_prompt',
            'reference_image_path',
            'generated_image_url',
            'generated_image_path',
            's3_image_url',
            's3_image_key',
            'is_saved',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SequentialArtworkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequentialArtwork
        fields = [
            'id',
            'title',
            'description',
            'total_iterations',
            'first_image_url',
            'last_image_url',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SequentialArtworkDetailSerializer(serializers.ModelSerializer):
    iterations = SequentialArtworkIterationSerializer(many=True, read_only=True)
    
    class Meta:
        model = SequentialArtwork
        fields = [
            'id',
            'title',
            'description',
            'total_iterations',
            'sequence_images',
            's3_image_keys',
            'first_image_url',
            'last_image_url',
            'conversation_history',
            'iterations',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateSequentialArtworkSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)


class UpdateSequenceImageSerializer(serializers.Serializer):
    # ✅ Use CharField instead of URLField
    sequence_images = serializers.ListField(
        child=serializers.CharField(max_length=2000),
        required=True
    )
    s3_image_keys = serializers.ListField(
        child=serializers.CharField(max_length=1000),
        required=False
    )
    total_iterations = serializers.IntegerField(required=True)
    first_image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=2000
    )
    last_image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=2000
    )