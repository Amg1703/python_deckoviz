from rest_framework import serializers
from .models import MetaImage
from apps.gallery.serializers import ImageSerializer

class MetaImageSerializer(serializers.ModelSerializer):
    liked_images = ImageSerializer(many=True, read_only=True)
    starred_images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = MetaImage
        fields = ['id', 'user', 'liked_images', 'starred_images']

class AddToLikedSerializer(serializers.Serializer):
    image_id = serializers.UUIDField()

    def validate_image_id(self, value):
        from apps.gallery.models import Image
        if not Image.objects.filter(id=value).exists():
            raise serializers.ValidationError("Image does not exist.")
        return value

class AddToStarredSerializer(serializers.Serializer):
    image_id = serializers.UUIDField()

    def validate_image_id(self, value):
        from apps.gallery.models import Image
        if not Image.objects.filter(id=value).exists():
            raise serializers.ValidationError("Image does not exist.")
        return value 