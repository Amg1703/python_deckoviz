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
    file_data = serializers.FileField(write_only=True)
    
    class Meta:
        model = PDF
        fields = ['filename', 'file_data']  # Only these 2 fields required

    def create(self, validated_data):
        import PyPDF2
        from io import BytesIO
        
        file = validated_data.pop('file_data')
        file_bytes = file.read()
        
        # Calculate size_bytes
        validated_data['size_bytes'] = len(file_bytes)
        
        # Calculate pages_count
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            validated_data['pages_count'] = len(pdf_reader.pages)
        except Exception:
            validated_data['pages_count'] = 0
        
        # Store file data
        validated_data['file_data'] = file_bytes
        
        return super().create(validated_data)

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
    file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Image
        fields = ['job', 'provider', 'provider_job_id', 'width', 'height', 'mime', 'file']
    
    def create(self, validated_data):
        file = validated_data.pop('file', None)
        if file:
            validated_data['image_data'] = file.read()
        return super().create(validated_data)
