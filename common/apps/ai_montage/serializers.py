from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Montage, UploadedImage, MontageStatus

User = get_user_model()


class UploadedImageSerializer(serializers.ModelSerializer):
    """Serializer for uploaded images"""
    
    class Meta:
        model = UploadedImage
        fields = [
            'id', 'user', 'montage', 'filename', 'original_filename',
            'file_path', 'file_size', 'mime_type', 'width', 'height',
            'url', 'thumbnail_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MontageSerializer(serializers.ModelSerializer):
    """Serializer for montage objects"""
    
    uploaded_images = UploadedImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Montage
        fields = [
            'id', 'user', 'prompt', 'mood', 'status',
            'theme', 'music_style', 'music_tags',
            'selected_image_paths', 'music_url', 'music_title',
            'music_artist', 'music_license', 'music_attribution',
            'video_path', 'video_duration', 'thumbnail_path',
            'output_video_url', 'total_images_uploaded', 'images_used',
            'error_message', 'created_at', 'updated_at', 'uploaded_images'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MontageCreateRequestSerializer(serializers.Serializer):
    """Serializer for creating a montage"""
    
    user_id = serializers.CharField(required=True)
    prompt = serializers.CharField(max_length=500, required=True)
    mood = serializers.CharField(max_length=100, required=False, allow_blank=True)
    total_images_uploaded = serializers.IntegerField(required=True)


class MontageStatusResponseSerializer(serializers.Serializer):
    """Serializer for montage status response"""
    
    id = serializers.CharField()
    status = serializers.ChoiceField(choices=MontageStatus.choices)
    progress_percentage = serializers.IntegerField()
    current_step = serializers.CharField()
    error_message = serializers.CharField(allow_null=True)


class MontageUpdateSerializer(serializers.Serializer):
    """Serializer for updating montage status and fields"""
    
    status = serializers.ChoiceField(choices=MontageStatus.choices, required=False)
    theme = serializers.CharField(max_length=255, required=False, allow_blank=True)
    music_style = serializers.CharField(max_length=255, required=False, allow_blank=True)
    music_tags = serializers.JSONField(required=False, allow_null=True)
    selected_image_paths = serializers.JSONField(required=False, allow_null=True)
    music_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    music_title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    music_artist = serializers.CharField(max_length=255, required=False, allow_blank=True)
    music_license = serializers.CharField(max_length=500, required=False, allow_blank=True)
    music_attribution = serializers.CharField(required=False, allow_blank=True)
    video_path = serializers.CharField(max_length=500, required=False, allow_blank=True)
    video_duration = serializers.FloatField(required=False, allow_null=True)
    thumbnail_path = serializers.CharField(max_length=500, required=False, allow_blank=True)
    output_video_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    images_used = serializers.IntegerField(required=False)
    error_message = serializers.CharField(required=False, allow_blank=True)


class ImageUploadRequestSerializer(serializers.Serializer):
    """Serializer for image upload request"""
    
    user_id = serializers.CharField(required=True)
    montage_id = serializers.CharField(required=False, allow_null=True)
    filename = serializers.CharField(max_length=500, required=True)
    original_filename = serializers.CharField(max_length=500, required=True)
    file_path = serializers.CharField(max_length=1000, required=True)
    file_size = serializers.IntegerField(required=False)
    mime_type = serializers.CharField(max_length=100, required=False)
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)
    url = serializers.CharField(max_length=1000, required=True)
    thumbnail_url = serializers.CharField(max_length=1000, required=False, allow_blank=True)
