from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sculpture, SculptureImage

User = get_user_model()


class SculptureImageSerializer(serializers.ModelSerializer):
    """Serializer for individual sculpture images/angles"""
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
            "file_size",
            "width",
            "height",
            "angle_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SculptureSerializer(serializers.ModelSerializer):
    """Serializer for sculpture with nested images"""
    images = SculptureImageSerializer(many=True, read_only=True)
    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = Sculpture
        fields = [
            "id",
            "user",
            "user_id",
            "username",
            "job_id",
            "title",
            "description",
            "input_filename",
            "output_filename",
            "prompt",
            "style",
            "status",
            "service",
            "model",
            "s3_url",
            "s3_key",
            "is_shared",
            "share",
            "rating",
            "feedback_comment",
            "feedback_submitted_at",
            "metadata",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def get_user_id(self, obj):
        return obj.user.id if obj.user else None

    def get_username(self, obj):
        return obj.user.username if obj.user else None


class CreateSculptureSerializer(serializers.Serializer):
    """Serializer for creating sculpture from backend client"""
    user_id = serializers.CharField(required=False)
    job_id = serializers.CharField()
    input_filename = serializers.CharField()
    output_filename = serializers.CharField()
    prompt = serializers.CharField(required=False, allow_blank=True)
    style = serializers.CharField(required=False, allow_blank=True)
    s3_url = serializers.CharField(required=False, allow_blank=True)
    s3_key = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(default="completed")
    service = serializers.CharField(default="runware")
    model = serializers.CharField(default="google:4@1")

    def create(self, validated_data):
        user_id = validated_data.pop("user_id", None)
        user = None
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        sculpture = Sculpture.objects.create(user=user, **validated_data)
        return sculpture


class UpdateSculptureSerializer(serializers.ModelSerializer):
    """Serializer for updating sculpture status/metadata"""
    class Meta:
        model = Sculpture
        fields = [
            "status",
            "s3_url",
            "s3_key",
            "is_shared",
            "share",
            "rating",
            "feedback_comment",
            "metadata",
        ]


class SaveGeneratedImageSerializer(serializers.Serializer):
    """Serializer for saving generated image metadata"""
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

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        job_id = validated_data.pop("job_id")
        
        # Get or create sculpture
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        if not sculpture:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None
            
            sculpture = Sculpture.objects.create(
                user=user,
                job_id=job_id,
                status="processing"
            )
        
        image = SculptureImage.objects.create(
            sculpture=sculpture,
            job_id=job_id,
            **validated_data
        )
        return image