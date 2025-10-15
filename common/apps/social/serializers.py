from rest_framework import serializers
from .models import SocialConnection, ImageInteraction, CollectionInteraction, Post
from apps.gallery.serializers import ImageSerializer
from apps.authentication.serializers import UserSerializer

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


# --- Post Serializer ---
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'images',
            'moods',
            'theme',
            'view',
            'is_active',
            'created_at',
            'updated_at',
        ]
