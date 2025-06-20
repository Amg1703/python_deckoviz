# views.py
from rest_framework import viewsets, filters,mixins
from rest_framework.permissions import IsAuthenticated,AllowAny, IsAdminUser
from .models import Image, Collection, CollectionImage,Audio
from .serializers import (CollectionImageCreateSerializer,AudioSerializer, ImageSerializer, CollectionSerializer, CollectionImageSerializer,CollectionDetailSerializer)
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

class AudioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AudioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['audio']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter audio for current user or active shared audio"""
        return Audio.objects.filter(
            Q(uploaded_by=self.request.user) & Q(is_active=True)
        )
        
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['file']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter images for current user or active shared images"""
        return Image.objects.filter(
            Q(uploaded_by=self.request.user) & Q(is_active=True)
        )
        
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'meta_notes']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectionDetailSerializer
        return CollectionSerializer
    
    def get_queryset(self):
        """Filter collections for current user"""
        return Collection.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """
        Get all public collections that are active.
        This endpoint is accessible without authentication.
        """
        public_collections = Collection.objects.filter(
            view='public',
            is_active=True
        ).order_by('-created_at')
        
        page = self.paginate_queryset(public_collections)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(public_collections, many=True)
        return Response(serializer.data)


class CollectionImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return CollectionImageCreateSerializer
        return CollectionImageSerializer
    
    def get_queryset(self):
        return CollectionImage.objects.filter(collection__user=self.request.user)



from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json

# from apps.utils.decoviz_ai import AIClient
# from .models import Audio
# from apps.utils.storage import Storage
# from apps.utils.unsplash_client import UnsplashClient
# # from apps.utils.unsplash_client import scrape_flickr

# search_queries=['nature', 'people', 'food', 'travel', 'architecture', 'animals', 'technology', 'cities', 'sports', 'abstract']
# client = UnsplashClient(search_queries = search_queries)

class TestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            images = Image.objects.filter(is_active=True, metadata__isnull=True)
            for image in images:
                try:
                    url = "https://365b-49-36-171-13.ngrok-free.app/metadata/generate-from-url"
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwNDk3MjU3LCJpYXQiOjE3NDg5NjEyNTcsImp0aSI6IjhiZDc5YmMzMjMzZTQwNGJhZDQwOWMxMWIwNDIzZGEyIiwidXNlcl9pZCI6ImNiODYxYjVjLWYwYjEtNGQxNy1hOWM2LTE0MTI0YzhhOTdiYiJ9.t9EuZW5nFwTxTAgFT9LoM8BhPgu377FRrHXus8igA7c"
                    }
                    payload = {
                        "image": image.file.url
                    }
                    print(image.file.url)
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    if response.status_code == 200:
                        image.metadata = response.json().get('metadata', None)
                        image.save() 
                except Exception as e:
                    print(f"Error generating metadata: {str(e)}")
            return Response({"message": "Metadata generated successfully"})
        except Exception as e:
            return Response({"message": str(e)})
