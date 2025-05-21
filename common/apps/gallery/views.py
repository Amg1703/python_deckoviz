# views.py
from rest_framework import viewsets, filters,mixins
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Image, Collection, CollectionImage,Audio
from .serializers import (CollectionImageCreateSerializer,AudioSerializer, ImageSerializer, CollectionSerializer, CollectionImageSerializer,CollectionDetailSerializer)
from django.db.models import Q

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
from apps.utils.decoviz_ai import AIClient
from .models import Audio
from apps.utils.storage import Storage
from apps.utils.unsplash_client import UnsplashClient
from apps.utils.unsplash_client import scrape_flickr

search_queries=['nature', 'people', 'food', 'travel', 'architecture', 'animals', 'technology', 'cities', 'sports', 'abstract']
client = UnsplashClient(search_queries = search_queries)

class TestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            scrape_flickr(search_query=search_queries)
            return Response({"message": "Hello World"})
        except Exception as e:
            return Response({"message": str(e)})
