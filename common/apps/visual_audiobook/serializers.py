from rest_framework import serializers
from .models import VisualAudiobook

class VisualAudiobookSerializer(serializers.ModelSerializer):
    """Serializer for VisualAudiobook"""
    
    class Meta:
        model = VisualAudiobook
        fields = [
            'id', 'book_title', 'voice', 'art_style', 'num_frames',
            'status', 'video_url', 'video_duration', 'video_size_mb',
            'error_message', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'video_url', 'video_duration', 'video_size_mb',
            'error_message', 'created_at', 'updated_at', 'completed_at'
        ]

class CreateVisualAudiobookSerializer(serializers.Serializer):
    """Request serializer for creating audiobook"""
    user = serializers.CharField()
    book_title = serializers.CharField(max_length=255)
    voice = serializers.CharField(max_length=50)
    art_style = serializers.CharField(max_length=100)
    num_frames = serializers.IntegerField(min_value=1, max_value=100)