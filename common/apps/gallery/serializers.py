from rest_framework import serializers
from .models import Image, Collection, CollectionImage
from apps.authentication.serializers import UserSerializer
from apps.marketplace.serializers import PriceSerializer

class ImageSerializer(serializers.ModelSerializer):
    price = PriceSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Image
        fields = [
            'id', 
            'file', 
            'music',
            'external_url', 
            'uploaded_by', 
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
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['price'] = PriceSerializer(instance.prices.first()).data
        return data 

class CollectionImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer(read_only=True)
    # image_id = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all(), source='image', write_only=True)

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
            'display_time', 
            'music_preference', 
            'meta_notes', 
            'is_active', 
            'collection_images', 
            'created_at', 
            'updated_at',
            'music',
            'view'
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
