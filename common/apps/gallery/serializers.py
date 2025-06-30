from rest_framework import serializers
from .models import Audio, Image, Collection, CollectionImage, DailyCuration
from apps.authentication.serializers import UserSerializer
from apps.marketplace.serializers import PriceSerializer
from apps.marketplace.models import Price
from django.db import transaction
import requests
import logging

logger = logging.getLogger(__name__)

class AudioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Audio
        fields = [
            'id', 
            'transcript', 
            'transcript_url', 
            'transcript_status', 
            'audio', 
            'uploaded_by', 
            'view', 
            'is_active', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'uploaded_by', 
            'created_at', 
            'updated_at'
        ]
    
    def create(self,validated_data):
        user = self.context['request'].user 
        validated_data['uploaded_by'] = user
        return super().create(validated_data)

class ImageSerializer(serializers.ModelSerializer):
    price = PriceSerializer(read_only=True)
    buy_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    uploaded_by = UserSerializer(read_only=True)
    
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Image
        fields = [
            'id',
            'title',
            'description',
            'file',
            'music',
            'external_url',
            'uploaded_by',
            'buy_price',
            'view',
            'price',
            'is_active',
            'created_at',
            'updated_at'
        ]
        
        read_only_fields = [
            'id', 
            'uploaded_by', 
            'view', 
            'price',
            'is_active', 
            'created_at', 
            'updated_at'
        ]
        
    def _generate_metadata(self, image):
        # TODO: Move URL and token to environment variables
        url = "https://ai.deckoviz.com/image-meta-gen/generate-from-url"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwNDk3MjU3LCJpYXQiOjE3NDg5NjEyNTcsImp0aSI6IjhiZDc5YmMzMjMzZTQwNGJhZDQwOWMxMWIwNDIzZGEyIiwidXNlcl9pZCI6ImNiODYxYjVjLWYwYjEtNGQxNy1hOWM2LTE0MTI0YzhhOTdiYiJ9.t9EuZW5nFwTxTAgFT9LoM8BhPgu377FRrHXus8igA7c"
        }
        payload = {
            "url": image.file.url
        }
        try:
            print(f"Generating metadata for: {image.file.url}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                metadata = response.json().get('metadata', {})
                image.metadata = metadata
                image.save(update_fields=['metadata'])
                image_identifier = image.title if image.title else image.id
                metadata_title = metadata.get('title', 'N/A')
                logger.info(f"Successfully generated metadata for: {image_identifier} - Title: {metadata_title}")
            else:
                logger.error(f"Error generating metadata for {image.file.url}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error processing image {image.id}: {str(e)}")
        
    def create(self,validated_data):
        user = self.context['request'].user
        validated_data['uploaded_by'] = user
        buy_price = validated_data.pop('buy_price')
        # title and description will be set by super().create(validated_data)
        with transaction.atomic():
            image = super().create(validated_data)
            Price.objects.create(image=image, final_price=buy_price, is_active=True)
        self._generate_metadata(image)
        return image
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            price = Price.objects.get(image=instance)
            data['price'] = PriceSerializer(price).data
        except Price.DoesNotExist:
            data['price'] = None
        return data

class ImageSearchSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    class Meta:
        model = Image
        fields = [
            'id',
            'file',
            'metadata',
            'title',
            'description',
        ]
    def get_title(self, obj):
        if obj.title:
            return obj.title
        if obj.metadata and isinstance(obj.metadata, dict):
            return obj.metadata.get('title', '') or ''
        return ''
    def get_description(self, obj):
        if obj.description:
            return obj.description
        if obj.metadata and isinstance(obj.metadata, dict):
            return obj.metadata.get('description', '') or ''
        return ''

class CollectionImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer(read_only=True)

    class Meta:
        model = CollectionImage
        fields = ['id', 'collection', 'image',   'order']


class CollectionImageCreateSerializer(serializers.ModelSerializer):
    
    class Meta: 
        model = CollectionImage
        fields = [
            'collection',
            'image',
        ]

class CollectionSerializer(serializers.ModelSerializer):
    collection_images = CollectionImageSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Collection
        fields = [
            'id', 
            'user', 
            'name', 
            'type',
            'display_time', 
            'music_preference', 
            'meta_notes', 
            'is_active', 
            'collection_images', 
            'created_at', 
            'updated_at',
            'music',
            'view',
            'description',
            'tags',
        ]


class CollectionDetailSerializer(CollectionSerializer):
    """Extended serializer with more details for single collection view"""
    images = serializers.SerializerMethodField()
    
    class Meta(CollectionSerializer.Meta):
        fields = CollectionSerializer.Meta.fields + ['images']
    
    def get_images(self, obj):
        """Return images in the correct order with complete details"""
        collection_images = obj.collection_images.all().select_related('image')
        def get_title(image):
            if image.title:
                return image.title
            if image.metadata and isinstance(image.metadata, dict):
                return image.metadata.get('title', '') or ''
            return ''
        def get_description(image):
            if image.description:
                return image.description
            if image.metadata and isinstance(image.metadata, dict):
                return image.metadata.get('description', '') or ''
            return ''
        return [
            {
                'id': ci.image.id,
                'file': self.context['request'].build_absolute_uri(ci.image.file.url) if ci.image.file else None,
                'order': ci.order,
                'uploaded_by': UserSerializer(ci.image.uploaded_by).data if ci.image.uploaded_by else None,
                'created_at': ci.image.created_at,
                'updated_at': ci.image.updated_at,
                'title': get_title(ci.image),
                'description': get_description(ci.image),
            }
            for ci in collection_images
        ]

class DailyCurationSerializer(serializers.ModelSerializer):
    collections = CollectionSerializer(many=True, read_only=True)

    class Meta:
        model = DailyCuration
        fields = ['date', 'collections']
