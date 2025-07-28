from rest_framework import serializers
from .models import MetaImage
from apps.gallery.serializers import ImageSerializer

class MetaImageSerializer(serializers.ModelSerializer):
    liked_images = ImageSerializer(many=True, read_only=True)
    starred_images = ImageSerializer(many=True, read_only=True)
    shared_images = serializers.SerializerMethodField()

    class Meta:
        model = MetaImage
        fields = ['id', 'user', 'liked_images', 'starred_images', 'shared_images']

    def get_shared_images(self, obj):
        from .models import SharedImage
        shared = SharedImage.objects.filter(shared_with=obj.user)
        return ImageSerializer([s.image for s in shared], many=True).data

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

class ShareImageSerializer(serializers.Serializer):
    image_id = serializers.UUIDField()
    email = serializers.EmailField()

    def validate(self, data):
        from apps.gallery.models import Image
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not Image.objects.filter(id=data['image_id']).exists():
            raise serializers.ValidationError("Image does not exist.")
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return data 