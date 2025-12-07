from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import CollectionNarration
from .serializers import (
    CollectionNarrationSerializer,
    CollectionNarrationCreateSerializer,
    CollectionNarrationUpdateSerializer
)


class CollectionNarrationInternalViewSet(viewsets.ModelViewSet):
    """
    Internal API for collection_narration operations.
    Used by the AI container to manage narration data.
    """
    queryset = CollectionNarration.objects.all()
    serializer_class = CollectionNarrationSerializer
    lookup_field = 'narration_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionNarrationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CollectionNarrationUpdateSerializer
        return CollectionNarrationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new narration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full narration data
        narration = CollectionNarration.objects.get(narration_id=serializer.data['narration_id'])
        output_serializer = CollectionNarrationSerializer(narration)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """List narrations with optional filtering by user_id"""
        user_id = request.query_params.get('user_id')
        queryset = self.get_queryset()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific narration by narration_id"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update a narration"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full narration data
        output_serializer = CollectionNarrationSerializer(instance)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a narration"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, narration_id=None):
        """Update narration status"""
        narration = self.get_object()
        new_status = request.data.get('status')
        error_message = request.data.get('error_message')
        
        if new_status:
            narration.status = new_status
        if error_message:
            narration.error_message = error_message
        
        narration.save()
        serializer = self.get_serializer(narration)
        return Response(serializer.data)
