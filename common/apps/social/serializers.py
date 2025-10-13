from rest_framework import serializers
from .models import SocialConnection, ImageInteraction, CollectionInteraction

class SocialConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialConnection
        fields = '__all__'

class ImageInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageInteraction
        fields = '__all__'

class CollectionInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionInteraction
        fields = '__all__'
