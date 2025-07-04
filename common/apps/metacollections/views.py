from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MetaCollection, SharedCollection
from .serializers import MetaCollectionSerializer, AddToFavouriteSerializer, AddToStarredSerializer, ShareCollectionSerializer, AddToLikedCollectionSerializer
from apps.gallery.models import Collection
from django.contrib.auth import get_user_model

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

class AddToStarredView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToStarredSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            collection = Collection.objects.get(id=collection_id)
            meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
            # Check if collection is public or owned by user
            if collection.view == 'public' or collection.user == request.user:
                meta_collection.starred_collections.add(collection)
                return Response({'status': 'collection added to starred'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to add this collection to starred'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromStarredView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToStarredSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            collection = Collection.objects.get(id=collection_id)
            meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
            meta_collection.starred_collections.remove(collection)
            return Response({'status': 'collection removed from starred'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShareCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShareCollectionSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            email = serializer.validated_data['email']
            User = get_user_model()
            collection = Collection.objects.get(id=collection_id)
            user_to_share = User.objects.get(email=email)
            # Only owner can share
            if collection.user != request.user:
                return Response({'error': 'Only the owner can share this collection.'}, status=status.HTTP_403_FORBIDDEN)
            SharedCollection.objects.get_or_create(collection=collection, owner=request.user, shared_with=user_to_share)
            return Response({'status': f'Collection shared with {email}'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveSharedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShareCollectionSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            email = serializer.validated_data['email']
            User = get_user_model()
            collection = Collection.objects.get(id=collection_id)
            user_to_remove = User.objects.get(email=email)
            # Only owner can remove
            if collection.user != request.user:
                return Response({'error': 'Only the owner can remove shared users.'}, status=status.HTTP_403_FORBIDDEN)
            SharedCollection.objects.filter(collection=collection, owner=request.user, shared_with=user_to_remove).delete()
            return Response({'status': f'User {email} removed from shared collection'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddToLikedCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToLikedCollectionSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            collection = Collection.objects.get(id=collection_id)
            meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
            # Check if collection is public or owned by user
            if collection.view == 'public' or collection.user == request.user:
                meta_collection.liked_collections.add(collection)
                return Response({'status': 'collection added to liked'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to like this collection'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromLikedCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToLikedCollectionSerializer(data=request.data)
        if serializer.is_valid():
            collection_id = serializer.validated_data['collection_id']
            collection = Collection.objects.get(id=collection_id)
            meta_collection, created = MetaCollection.objects.get_or_create(user=request.user)
            meta_collection.liked_collections.remove(collection)
            return Response({'status': 'collection removed from liked'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 