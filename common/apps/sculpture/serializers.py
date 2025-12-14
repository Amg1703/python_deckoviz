from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sculpture, SculptureImage

User = get_user_model()


class SculptureImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SculptureImage
        fields = [
            "id",
            "sculpture",
            "job_id",
            "filename",
            "file_path",
            "url",
            "s3_key",
            "mime_type",
            "width",
            "height",
            "angle_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SculptureSerializer(serializers.ModelSerializer):
    images = SculptureImageSerializer(many=True, read_only=True)

    class Meta:
        model = Sculpture
        fields = [
            "id",
            "user",
            "job_id",
            "title",
            "description",
            "input_filename",
            "output_filename",
            "prompt",
            "style",
            "status",
            "is_shared",
            "s3_url",
            "s3_key",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class CreateSculptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sculpture
        fields = [
            "job_id",
            "title",
            "description",
            "input_filename",
            "output_filename",
            "prompt",
            "style",
            "status",
            "is_shared",
            "s3_url",
            "s3_key",
        ]


class SaveGeneratedImageSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    job_id = serializers.CharField()
    filename = serializers.CharField()
    file_path = serializers.CharField(allow_blank=True, required=False)
    url = serializers.CharField(allow_blank=True, required=False)
    s3_key = serializers.CharField(allow_blank=True, required=False)
    file_size = serializers.IntegerField(required=False)
    mime_type = serializers.CharField(default="image/png")
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)
    angle_number = serializers.IntegerField(required=False)