from rest_framework import serializers
from .models import Audio, Image, Collection, CollectionImage, DailyCuration, Ritual, DailyImageCuration
from apps.authentication.serializers import UserSerializer
from apps.marketplace.serializers import PriceSerializer
from apps.marketplace.models import Price
from django.db import transaction
import requests
import logging
from django.core.files.base import ContentFile
import os

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
    file_url = serializers.URLField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Image
        fields = [
            'id',
            'title',
            'description',
            'file',
            'file_url',
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
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['uploaded_by'] = user
        buy_price = validated_data.pop('buy_price')
        file_url = validated_data.pop('file_url', None)
        # Download image from URL if file_url is provided
        if file_url and not validated_data.get('file'):
            try:
                response = requests.get(file_url)
                response.raise_for_status()
                file_name = os.path.basename(file_url.split('?')[0]) or 'downloaded_image.jpg'
                validated_data['file'] = ContentFile(response.content, name=file_name)
            except Exception as e:
                raise serializers.ValidationError({'file_url': f'Failed to download image: {str(e)}'})
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
    music_url = serializers.CharField(write_only=True, required=False, allow_blank=True)

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
            'music_url',
            'view',
            'description',
            'tags',
        ]

    def create(self, validated_data):
        music_url = validated_data.pop('music_url', None)
        music_file = validated_data.get('music', None)
        if not music_file and music_url:
            # Set the music field to the S3 URL
            validated_data['music'] = music_url
        return super().create(validated_data)

    def update(self, instance, validated_data):
        music_url = validated_data.pop('music_url', None)
        music_file = validated_data.get('music', None)
        if not music_file and music_url:
            validated_data['music'] = music_url
        return super().update(instance, validated_data)

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

class DailyImageCurationSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = DailyImageCuration
        fields = ['date', 'images']

class AdminRitualSerializer(serializers.ModelSerializer):
    collections = CollectionSerializer(many=True, read_only=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), write_only=True, many=True, source='collections'
    )

    class Meta:
        model = Ritual
        fields = [
            'id', 'name', 'time_of_day', 'collections', 'collection_ids', 'is_active', 'is_global', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'collections']

    def validate_collection_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate collections are not allowed in a ritual.")
        return value

    def create(self, validated_data):
        collections = validated_data.pop('collections', [])
        ritual = Ritual.objects.create(is_global=True, created_by=None, **validated_data)
        ritual.collections.set(collections)
        return ritual

    def update(self, instance, validated_data):
        collections = validated_data.pop('collections', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if collections is not None:
            instance.collections.set(collections)
        return instance

class UserRitualSerializer(serializers.ModelSerializer):
    collections = CollectionSerializer(many=True, read_only=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), write_only=True, many=True, source='collections'
    )

    class Meta:
        model = Ritual
        fields = [
            'id', 'name', 'time_of_day', 'collections', 'collection_ids', 'is_active', 'is_global', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'collections', 'is_global']

    def validate_collection_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate collections are not allowed in a ritual.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        time_of_day = data.get('time_of_day')
        # For update, exclude self
        instance = getattr(self, 'instance', None)
        qs = Ritual.objects.filter(is_global=False, created_by=user, time_of_day=time_of_day)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'time_of_day': 'You already have a ritual at this time.'
            })
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        collections = validated_data.pop('collections', [])
        ritual = Ritual.objects.create(is_global=False, created_by=user, **validated_data)
        ritual.collections.set(collections)
        return ritual

    def update(self, instance, validated_data):
        collections = validated_data.pop('collections', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if collections is not None:
            instance.collections.set(collections)
        return instance
