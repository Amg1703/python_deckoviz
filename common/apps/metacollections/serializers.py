from rest_framework import serializers
from .models import MetaCollection
from apps.gallery.serializers import CollectionSerializer

class MetaCollectionSerializer(serializers.ModelSerializer):
    favourite_collections = CollectionSerializer(many=True, read_only=True)

    class Meta:
        model = MetaCollection
        fields = ['id', 'user', 'favourite_collections']

class AddToFavouriteSerializer(serializers.Serializer):
    collection_id = serializers.UUIDField()

    def validate_collection_id(self, value):
        from apps.gallery.models import Collection
        if not Collection.objects.filter(id=value).exists():
            raise serializers.ValidationError("Collection does not exist.")
        return value 