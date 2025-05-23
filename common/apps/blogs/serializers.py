from rest_framework import serializers
from .models import Blog,Asset

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['file']

class BlogSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    
    def get_images(self, obj):
        # Get the file URLs directly from the related assets
        return [asset.file.url for asset in obj.images.all() if asset.file]
    
    def get_videos(self, obj):
        # Get the file URLs directly from the related assets
        return [asset.file.url for asset in obj.videos.all() if asset.file]
    
    class Meta:
        model = Blog
        fields = [
            'id', 
            'title', 
            'description', 
            'tags', 
            'images', 
            'videos',
            'created_at',
        ]
