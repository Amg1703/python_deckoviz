from rest_framework import serializers
from .models import DeckovizComparison


class DeckovizComparisonSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = DeckovizComparison
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "id")

    def get_user_id(self, obj):
        """Get user_id from ForeignKey"""
        return obj.user.id if obj.user else None


class DeckovizCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = DeckovizComparison
        fields = (
            "user_id",
            "job_id",
            "before_filename",
            "after_filename",
            "deckoviz_variant",
            "size",
            "halo_color",
            "content_type",
            "placement_instructions",
            "prompt",
            "s3_before_url",
            "s3_before_key",
            "s3_after_url",
            "s3_after_key",
            "status",
            "metadata",
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