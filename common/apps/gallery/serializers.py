from rest_framework import serializers
from .models import Audio, Image, Collection, CollectionImage
from apps.authentication.serializers import UserSerializer
from apps.marketplace.serializers import PriceSerializer
from apps.marketplace.models import Price
from django.db import transaction

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
        
    def create(self,validated_data):
        user = self.context['request'].user
        validated_data['uploaded_by'] = user
        buy_price = validated_data.pop('buy_price')
        image = super().create(validated_data)
        
        # Create image and price in a transaction
        with transaction.atomic():
            Price.objects.create(image=image, final_price=buy_price, is_active=True)
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
    class Meta:
        model = Image
        fields = [
            'id',
            'file',
            'metadata',
        ]

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
        return [
            {
                'id': ci.image.id,
                'file': self.context['request'].build_absolute_uri(ci.image.file.url) if ci.image.file else None,
                'order': ci.order,
                'uploaded_by': UserSerializer(ci.image.uploaded_by).data if ci.image.uploaded_by else None,
                'created_at': ci.image.created_at,
                'updated_at': ci.image.updated_at,
            }
            for ci in collection_images
        ]
