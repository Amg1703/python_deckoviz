from rest_framework import serializers
from .models import CollectionNarration


class CollectionNarrationSerializer(serializers.ModelSerializer):
    """Serializer for CollectionNarration model"""
    
    class Meta:
        model = CollectionNarration
        fields = [
            'narration_id',
            'user_id',
            'product_name',
            'product_description',
            'status',
            'input_type',
            'script',
            'audio_path',
            'video_path',
            'final_video_path',
            'audio_duration',
            'video_duration',
            'download_url',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['narration_id', 'created_at', 'updated_at']


class CollectionNarrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a narration"""
    
    class Meta:
        model = CollectionNarration
        fields = [
            'narration_id',
            'user_id',
            'product_name',
            'product_description',
            'status',
            'input_type',
        ]
        read_only_fields = ['narration_id']


class CollectionNarrationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a narration"""
    
    class Meta:
        model = CollectionNarration
        fields = [
            'status',
            'script',
            'audio_path',
            'input_type',
            'video_path',
            'final_video_path',
            'audio_duration',
            'video_duration',
            'download_url',
            'error_message',
        ]
