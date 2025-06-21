from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MetaCollection
from .serializers import MetaCollectionSerializer, AddToFavouriteSerializer
from apps.gallery.models import Collection

class MetaCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
        serializer = MetaCollectionSerializer(meta_collection)
        return Response(serializer.data)

class AddToFavouritesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToFavouriteSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            collection = Collection.objects.get(id=collection_id)
            meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
            
            # Check if collection is public or owned by user
            if collection.view == 'public' or collection.user == request.user:
                meta_collection.favourite_collections.add(collection)
                return Response({'status': 'collection added to favourites'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to add this collection to favourites'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromFavouritesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToFavouriteSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            collection = Collection.objects.get(id=collection_id)
            meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
            meta_collection.favourite_collections.remove(collection)
            return Response({'status': 'collection removed from favourites'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 