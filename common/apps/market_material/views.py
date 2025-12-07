from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import MarketingMaterial, BrandAsset
from .serializers import (
    MarketingMaterialSerializer,
    MarketingMaterialCreateSerializer,
    MarketingMaterialUpdateSerializer,
    BrandAssetSerializer,
    BrandAssetCreateSerializer
)


class MarketingMaterialInternalViewSet(viewsets.ModelViewSet):
    """
    Internal API for marketing_material operations.
    Used by the AI container to manage marketing material data.
    """
    queryset = MarketingMaterial.objects.all()
    serializer_class = MarketingMaterialSerializer
    lookup_field = 'request_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MarketingMaterialCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MarketingMaterialUpdateSerializer
        return MarketingMaterialSerializer
    
    def list(self, request, *args, **kwargs):
        """List marketing materials with optional filtering by user_id"""
        user_id = request.query_params.get('user_id')
        queryset = self.get_queryset()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new marketing material"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full material data
        material = MarketingMaterial.objects.get(request_id=serializer.data['request_id'])
        output_serializer = MarketingMaterialSerializer(material)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific marketing material by request_id"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update a marketing material"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full material data
        output_serializer = MarketingMaterialSerializer(instance)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a marketing material"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BrandAssetInternalViewSet(viewsets.ModelViewSet):
    """
    Internal API for brand asset operations.
    """
    queryset = BrandAsset.objects.all()
    serializer_class = BrandAssetSerializer
    lookup_field = 'asset_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BrandAssetCreateSerializer
        return BrandAssetSerializer
    
    def list(self, request, *args, **kwargs):
        """List brand assets with optional filtering by user_id"""
        user_id = request.query_params.get('user_id')
        queryset = self.get_queryset()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new brand asset"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full asset data
        asset = BrandAsset.objects.get(asset_id=serializer.data['asset_id'])
        output_serializer = BrandAssetSerializer(asset)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific brand asset by asset_id"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a brand asset"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
