from rest_framework import serializers
from .models import StyleOption, StyledImage, AIGeneratedImage
from apps.gallery.serializers import ImageSerializer

class StyleOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StyleOption
        fields = ['id', 'name', 'description', 'thumbnail']

class StyledImageSerializer(serializers.ModelSerializer):
    original_image = ImageSerializer(read_only=True)
    style = StyleOptionSerializer(read_only=True)
    
    class Meta:
        model = StyledImage
        fields = ['id', 'original_image', 'style', 'result_image', 'created_at']
        read_only_fields = ['created_at']

class StyledImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StyledImage
        fields = ['original_image', 'style']

class AIGeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGeneratedImage
        fields = ['id', 'prompt', 'result_image', 'created_at']
        read_only_fields = ['result_image', 'created_at']
