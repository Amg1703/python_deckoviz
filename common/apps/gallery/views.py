# views.py
from rest_framework import viewsets, filters,mixins
from rest_framework.permissions import IsAuthenticated
from .models import Image, Collection, CollectionImage
from .serializers import (CollectionImageCreateSerializer, ImageSerializer, CollectionSerializer, CollectionImageSerializer,CollectionDetailSerializer)
from django.db.models import Q


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

