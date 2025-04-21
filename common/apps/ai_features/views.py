from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StyleOption, StyledImage, AIGeneratedImage
from .serializers import (
    StyleOptionSerializer, 
    StyledImageSerializer, 
    StyledImageCreateSerializer,
    AIGeneratedImageSerializer
)
from apps.gallery.models import Image

class StyleOptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving style options for AI style transfer"""
    queryset = StyleOption.objects.filter(is_active=True)
    serializer_class = StyleOptionSerializer
    permission_classes = [IsAuthenticated]


class StyledImageViewSet(viewsets.ModelViewSet):
    """ViewSet for handling AI style transfer"""
    serializer_class = StyledImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StyledImage.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StyledImageCreateSerializer
        return StyledImageSerializer
    
    def perform_create(self, serializer):
        # In a production system, this would trigger an async task to perform the style transfer
        # For now, we'll just create the record and assume the processing happens
        serializer.save(
            created_by=self.request.user,
            result_image=serializer.validated_data['original_image'].file  # Placeholder
        )


class AIGeneratedImageViewSet(viewsets.ModelViewSet):
    """ViewSet for handling AI image generation from text prompts"""
    serializer_class = AIGeneratedImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIGeneratedImage.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        # In a production system, this would trigger an async task to generate the image
        # For now, we'll just create a placeholder record
        instance = serializer.save(created_by=self.request.user)
        
        # Here we would connect to an AI service to generate the image
        # For now, we'll update with a placeholder note
        instance.result_image = None  # This would be set by the actual AI service
        instance.save()
        
        return instance
