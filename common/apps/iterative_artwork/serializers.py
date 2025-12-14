from rest_framework import serializers
from .models import IterativeArtwork, IterativeArtworkIteration


class IterativeArtworkIterationSerializer(serializers.ModelSerializer):
    """Serializer for IterativeArtworkIteration model"""
    
    class Meta:
        model = IterativeArtworkIteration
        fields = [
            'id',
            'artwork_id',
            'user_id',
            'user_prompt',
            'assistant_response',
            'reference_image_path',
            'generated_image_url',
            'generated_image_path',
            'image_prompt',
            'iteration_number',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class IterativeArtworkSerializer(serializers.ModelSerializer):
    """Serializer for IterativeArtwork model"""
    
    iterations = IterativeArtworkIterationSerializer(many=True, read_only=True)
    iteration_count = serializers.SerializerMethodField()
    
    class Meta:
        model = IterativeArtwork
        fields = [
            'id',
            'user_id',
            'title',
            'final_image_url',
            'final_image_path',
            'final_prompt',
            'conversation_history',
            'created_at',
            'updated_at',
            'iterations',
            'iteration_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_iteration_count(self, obj):
        return obj.iterations.count()


class IterativeArtworkCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating artwork"""
    
    class Meta:
        model = IterativeArtwork
        fields = [
            'id',
            'user_id',
            'title',
            'final_image_url',
            'final_image_path',
            'final_prompt',
            'conversation_history',
        ]
        read_only_fields = ['id']


class IterativeArtworkUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating artwork"""
    
    class Meta:
        model = IterativeArtwork
        fields = [
            'title',
            'final_image_url',
            'final_image_path',
            'final_prompt',
            'conversation_history',
        ]
