from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import IterativeArtwork, IterativeArtworkIteration
from .serializers import (
    IterativeArtworkSerializer,
    IterativeArtworkCreateSerializer,
    IterativeArtworkUpdateSerializer,
    IterativeArtworkIterationSerializer
)


class IterativeArtworkInternalViewSet(viewsets.ModelViewSet):
    """
    Internal API for iterative_artwork operations.
    Used by the AI container to manage artwork and iteration data.
    """
    queryset = IterativeArtwork.objects.all()
    serializer_class = IterativeArtworkSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return IterativeArtworkCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IterativeArtworkUpdateSerializer
        return IterativeArtworkSerializer
    
    def list(self, request, *args, **kwargs):
        """List artworks with optional filtering by user_id"""
        user_id = request.query_params.get('user_id')
        queryset = self.get_queryset()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # Changed: url_path='link-iterations' → url_path='link_iterations'
    @action(detail=False, methods=['post'], url_path='link_iterations')
    def link_iterations(self, request):
        """Link unsaved iterations to an artwork"""
        artwork_id = request.data.get('artwork_id')
        user_id = request.data.get('user_id')
        
        if not artwork_id or not user_id:
            return Response(
                {"error": "artwork_id and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artwork = get_object_or_404(IterativeArtwork, id=artwork_id, user_id=user_id)
        
        # Update all unsaved iterations
        updated_count = IterativeArtworkIteration.objects.filter(
            user_id=user_id,
            artwork_id__isnull=True
        ).update(artwork_id=artwork_id)
        
        return Response({
            "message": f"Linked {updated_count} iterations to artwork",
            "artwork_id": artwork_id,
            "iteration_count": updated_count
        })


class IterativeArtworkIterationInternalViewSet(viewsets.ModelViewSet):
    """
    Internal API for iteration operations.
    """
    queryset = IterativeArtworkIteration.objects.all()
    serializer_class = IterativeArtworkIterationSerializer
    
    def list(self, request, *args, **kwargs):
        """List iterations with optional filtering"""
        user_id = request.query_params.get('user_id')
        artwork_id = request.query_params.get('artwork_id')
        unsaved_only = request.query_params.get('unsaved_only')
        
        queryset = self.get_queryset()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if artwork_id:
            queryset = queryset.filter(artwork_id=artwork_id)
        
        if unsaved_only:
            queryset = queryset.filter(artwork_id__isnull=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # Changed: url_path='clear-unsaved' → url_path='clear_unsaved'
    @action(detail=False, methods=['delete'], url_path='clear_unsaved')
    def clear_unsaved(self, request):
        """Delete all unsaved iterations for a user"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = IterativeArtworkIteration.objects.filter(
            user_id=user_id,
            artwork_id__isnull=True
        ).delete()
        
        return Response({
            "message": f"Deleted {deleted_count} unsaved iterations",
            "deleted_count": deleted_count
        })
    
    # Changed: url_path='count-unsaved' → url_path='count_unsaved'
    @action(detail=False, methods=['get'], url_path='count_unsaved')
    def count_unsaved(self, request):
        """Count unsaved iterations for a user"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = IterativeArtworkIteration.objects.filter(
            user_id=user_id,
            artwork_id__isnull=True
        ).count()
        
        return Response({"count": count})