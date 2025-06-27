from rest_framework import serializers
from .models import MetaCollection
from apps.gallery.serializers import CollectionSerializer

class MetaCollectionSerializer(serializers.ModelSerializer):
    favourite_collections = CollectionSerializer(many=True, read_only=True)
    starred_collections = CollectionSerializer(many=True, read_only=True)
    shared_collections = serializers.SerializerMethodField()

    class Meta:
        model = MetaCollection
        fields = ['id', 'user', 'favourite_collections', 'starred_collections', 'shared_collections']

    def get_shared_collections(self, obj):
        from .models import SharedCollection
        shared = SharedCollection.objects.filter(shared_with=obj.user)
        return CollectionSerializer([s.collection for s in shared], many=True).data

class AddToFavouriteSerializer(serializers.Serializer):
    collection_id = serializers.UUIDField()

    def validate_collection_id(self, value):
        from apps.gallery.models import Collection
        if not Collection.objects.filter(id=value).exists():
            raise serializers.ValidationError("Collection does not exist.")
        return value

class AddToStarredSerializer(serializers.Serializer):
    collection_id = serializers.UUIDField()

    def validate_collection_id(self, value):
        from apps.gallery.models import Collection
        if not Collection.objects.filter(id=value).exists():
            raise serializers.ValidationError("Collection does not exist.")
        return value

class ShareCollectionSerializer(serializers.Serializer):
    collection_id = serializers.UUIDField()
    email = serializers.EmailField()

    def validate(self, data):
        from apps.gallery.models import Collection
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not Collection.objects.filter(id=data['collection_id']).exists():
            raise serializers.ValidationError("Collection does not exist.")
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return data 