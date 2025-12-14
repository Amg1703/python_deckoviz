from rest_framework import serializers
from .models import MusicTask, Lyrics, MusicVideo


class MusicTaskSerializer(serializers.ModelSerializer):
    """Full serializer for MusicTask"""
    
    class Meta:
        model = MusicTask
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class MusicTaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MusicTask"""
    
    class Meta:
        model = MusicTask
        fields = [
            'request_id', 'task_id', 'user_id', 'type', 'lyrics_id',
            'status', 'prompt', 'style', 'vocal_gender', 'instrumental', 'model'
        ]


class MusicTaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating MusicTask"""
    
    class Meta:
        model = MusicTask
        fields = ['status', 'songs', 'progress', 'error', 'updated_at']
        read_only_fields = ('updated_at',)


class LyricsSerializer(serializers.ModelSerializer):
    """Full serializer for Lyrics"""
    
    class Meta:
        model = Lyrics
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class LyricsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Lyrics"""
    
    class Meta:
        model = Lyrics
        fields = ['lyrics_id', 'user_id', 'prompt', 'lyrics', 'status']


class LyricsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Lyrics"""
    
    class Meta:
        model = Lyrics
        fields = ['music_generated', 'music_request_id']


class MusicVideoSerializer(serializers.ModelSerializer):
    """Full serializer for MusicVideo"""
    
    class Meta:
        model = MusicVideo
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class MusicVideoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating MusicVideo"""
    
    class Meta:
        model = MusicVideo
        fields = [
            'video_id', 'user_id', 'request_id', 'task_id', 'audio_id',
            'author', 'domain_name', 'status', 'video_url'
        ]


class MusicVideoUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating MusicVideo"""
    
    class Meta:
        model = MusicVideo
        fields = ['status', 'video_url', 'updated_at']
        read_only_fields = ('updated_at',)
