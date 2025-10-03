from rest_framework import serializers
from .models import AIModel, AIOperation, AICallback

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'model_type', 'provider', 'model_id', 'version', 
                  'description', 'is_active', 'config', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AIOperationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = AIOperation
        fields = ['id', 'user', 'username', 'operation_type', 'model', 'model_name', 
                  'status', 'input_data', 'result_data', 'error_message', 'credits_used',
                  'processing_time', 'external_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'username', 'model_name', 'credits_used',
                           'processing_time', 'created_at', 'updated_at']

class AICallbackSerializer(serializers.ModelSerializer):
    operation_type = serializers.CharField(source='operation.operation_type', read_only=True)
    
    class Meta:
        model = AICallback
        fields = ['id', 'operation', 'operation_type', 'callback_data', 'processed', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'operation_type', 'created_at', 'updated_at']

class TranscriptionRequestSerializer(serializers.Serializer):
    audio_url = serializers.URLField()
    analyze = serializers.BooleanField(default=False)

class AnalysisRequestSerializer(serializers.Serializer):
    transcript = serializers.CharField()

class SummarizationRequestSerializer(serializers.Serializer):
    text = serializers.CharField()
    max_length = serializers.IntegerField(default=150)
    min_length = serializers.IntegerField(default=40)

class ImageGenerationRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    num_images = serializers.IntegerField(default=1, min_value=1, max_value=10)
    size = serializers.ChoiceField(choices=["256x256", "512x512", "1024x1024"], default="1024x1024")

class ImageEditingRequestSerializer(serializers.Serializer):
    image_url = serializers.URLField()
    prompt = serializers.CharField()

class AICallbackRequestSerializer(serializers.Serializer):
    operation_id = serializers.UUIDField(required=False)
    id = serializers.CharField(required=False)  # External ID
    status = serializers.ChoiceField(choices=["pending", "processing", "completed", "failed"])
    result = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)
