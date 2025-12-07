from rest_framework import serializers
from .models import PDF, Job, Image


class PDFSerializer(serializers.ModelSerializer):
    """Full serializer for PDF"""
    
    class Meta:
        model = PDF
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_at')


class PDFCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PDF"""
    
    class Meta:
        model = PDF
        fields = ['filename', 'size_bytes', 'pages_count', 'file_data', 'extracted_text']


class PDFListSerializer(serializers.ModelSerializer):
    """Serializer for listing PDFs (without file_data)"""
    
    class Meta:
        model = PDF
        fields = ['id', 'filename', 'size_bytes', 'pages_count', 'uploaded_at']


class JobSerializer(serializers.ModelSerializer):
    """Full serializer for Job"""
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class JobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Job"""
    
    class Meta:
        model = Job
        fields = ['pdf', 'prompt', 'page_number', 'chapter_number', 'status']


class JobUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Job"""
    
    class Meta:
        model = Job
        fields = ['status', 'error', 'updated_at']
        read_only_fields = ('updated_at',)


class ImageSerializer(serializers.ModelSerializer):
    """Full serializer for Image"""
    
    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class ImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Image"""
    
    class Meta:
        model = Image
        fields = ['job', 'provider', 'provider_job_id', 'width', 'height', 'mime']
