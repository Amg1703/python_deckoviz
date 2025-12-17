from rest_framework import serializers
from .models import BeforeAfter


class BeforeAfterSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = BeforeAfter
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "id")

    def get_user_id(self, obj):
        """Get user_id from ForeignKey"""
        return obj.user.id if obj.user else None
    
    def get_username(self, obj):
        """Get username from ForeignKey"""
        return obj.user.username if obj.user else None


class BeforeAfterCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = BeforeAfter
        fields = (
            "user_id",
            "session_id",
            "job_id",
            "original_filename",
            "original_image_uuid",
            "edited_filename",
            "transformation_type",
            "edit_instructions",
            "style_hint",
            "placement_instructions",
            "deckoviz_variant",
            "size_variant",
            "halo_color",
            "frame_material",
            "preserve_room",
            "s3_original_url",
            "s3_original_key",
            "s3_output_url",
            "s3_output_key",
            "status",
            "service",
            "model",
            "parsed_changes",
            "deckoviz_specs",
            "metadata",
            "share",
        )

    def create(self, validated_data):
        """Handle user_id assignment"""
        user_id = validated_data.pop("user_id", None)
        instance = super().create(validated_data)
        
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                instance.user = user
                instance.save()
            except User.DoesNotExist:
                pass
        
        return instance


class BeforeAfterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeforeAfter
        fields = (
            "edited_filename",
            "s3_output_url",
            "s3_output_key",
            "change_log_path",
            "change_log_s3_url",
            "change_log_s3_key",
            "metadata_path",
            "metadata_s3_url",
            "metadata_s3_key",
            "status",
            "parsed_changes",
            "deckoviz_specs",
            "metadata",
            "share",
        )