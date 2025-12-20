from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SequentialArtwork, SequentialArtworkIteration

User = get_user_model()

class SequentialArtworkIterationSerializer(serializers.ModelSerializer):
    # Explicitly override fields to make them optional
    artwork = serializers.PrimaryKeyRelatedField(
        queryset=SequentialArtwork.objects.all(),
        required=False,
        allow_null=True
    )
    generated_image_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    s3_image_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    s3_image_key = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    
    class Meta:
        model = SequentialArtworkIteration
        fields = [
            'id',
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
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SequentialArtworkListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
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
    """Detailed serializer with iterations"""
    iterations = SequentialArtworkIterationSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SequentialArtwork
        fields = [
            'id',
            'user',
            'user_username',
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
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class CreateSequentialArtworkSerializer(serializers.ModelSerializer):
    """Serializer for creating artwork sequences"""
    class Meta:
        model = SequentialArtwork
        fields = [
            'title',
            'description',
            'total_iterations',
            'sequence_images',
            's3_image_keys',
            'first_image_url',
            'last_image_url',
            'conversation_history'
        ]

class UpdateSequenceImageSerializer(serializers.Serializer):
    """Serializer for updating sequence images"""
    sequence_images = serializers.ListField(child=serializers.URLField())
    s3_image_keys = serializers.ListField(child=serializers.CharField(), required=False)
    total_iterations = serializers.IntegerField()
    first_image_url = serializers.URLField(required=False, allow_blank=True)
    last_image_url = serializers.URLField(required=False, allow_blank=True)