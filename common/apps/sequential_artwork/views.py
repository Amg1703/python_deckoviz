from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model  
from .models import SequentialArtwork, SequentialArtworkIteration
from .serializers import (
    SequentialArtworkListSerializer,
    SequentialArtworkDetailSerializer,
    CreateSequentialArtworkSerializer,
    SequentialArtworkIterationSerializer,
    UpdateSequenceImageSerializer
)
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class SequentialArtworkViewSet(viewsets.ModelViewSet):
    """ViewSet for Sequential Artwork"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return artworks only for the current user"""
        return SequentialArtwork.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SequentialArtworkDetailSerializer
        elif self.action == 'list':
            return SequentialArtworkListSerializer
        elif self.action == 'create':
            return CreateSequentialArtworkSerializer
        return SequentialArtworkDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new sequential artwork"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        artwork = SequentialArtwork.objects.create(
            user=request.user,
            **serializer.validated_data
        )
        
        return Response(
            SequentialArtworkDetailSerializer(artwork).data,
            status=status.HTTP_201_CREATED
        )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def link_iterations(self, request, pk=None):
        """Link all unsaved iterations to this artwork"""
        artwork = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update all unsaved iterations for this user
        updated_count = SequentialArtworkIteration.objects.filter(
            user_id=user_id,
            is_saved=False
        ).update(
            artwork=artwork,
            is_saved=True
        )
        
        return Response({
            'message': f'Linked {updated_count} iterations to artwork',
            'artwork_id': artwork.id,
            'linked_count': updated_count
        })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def images(self, request, pk=None):
        """Get all sequential images from artwork"""
        artwork = self.get_object()
        
        sequence_images = artwork.sequence_images or []
        
        return Response({
            'artwork_id': artwork.id,
            'title': artwork.title,
            'total_images': len(sequence_images),
            'sequential_images': [
                {
                    'index': idx + 1,
                    'url': img_url
                }
                for idx, img_url in enumerate(sequence_images)
            ]
        })
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def image(self, request, pk=None):
        """Get specific image from sequence by index"""
        artwork = self.get_object()
        image_index = request.query_params.get('index', 1)
        
        try:
            image_index = int(image_index)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid image index'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sequence_images = artwork.sequence_images or []
        idx = image_index - 1
        
        if idx < 0 or idx >= len(sequence_images):
            return Response(
                {'error': f'Image {image_index} not found in sequence'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'index': image_index,
            'url': sequence_images[idx]
        })
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def delete_image(self, request, pk=None):
        """Delete specific image from sequence"""
        artwork = self.get_object()
        image_index = request.data.get('index')
        
        if not image_index:
            return Response(
                {'error': 'Image index required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            image_index = int(image_index)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid image index'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sequence_images = artwork.sequence_images or []
        s3_keys = artwork.s3_image_keys or []
        
        # Don't allow deleting if only one image left
        if len(sequence_images) <= 1:
            return Response(
                {'error': 'Cannot delete the last image in sequence'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        idx = image_index - 1
        if idx < 0 or idx >= len(sequence_images):
            return Response(
                {'error': f'Image {image_index} not found in sequence'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove image and S3 key
        sequence_images.pop(idx)
        if idx < len(s3_keys):
            s3_keys.pop(idx)
        
        # Update artwork
        artwork.sequence_images = sequence_images
        artwork.s3_image_keys = s3_keys
        artwork.total_iterations = len(sequence_images)
        artwork.first_image_url = sequence_images[0] if sequence_images else None
        artwork.last_image_url = sequence_images[-1] if sequence_images else None
        artwork.save()
        
        logger.info(f"Deleted image {image_index} from artwork {artwork.id}")
        
        return Response({
            'message': f'Image {image_index} deleted successfully',
            'artwork_id': artwork.id,
            'remaining_images': len(sequence_images),
            'sequence_images': sequence_images
        })
    
    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_sequence(self, request, pk=None):
        """Update sequence images"""
        artwork = self.get_object()
        serializer = UpdateSequenceImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        artwork.sequence_images = serializer.validated_data['sequence_images']
        artwork.s3_image_keys = serializer.validated_data.get('s3_image_keys', [])
        artwork.total_iterations = serializer.validated_data['total_iterations']
        artwork.first_image_url = serializer.validated_data.get('first_image_url')
        artwork.last_image_url = serializer.validated_data.get('last_image_url')
        artwork.save()
        
        return Response(SequentialArtworkDetailSerializer(artwork).data)
    
    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def clear_unsaved(self, request):
        """Clear unsaved iterations"""
        count, _ = SequentialArtworkIteration.objects.filter(
            user=request.user,
            is_saved=False
        ).delete()
        
        return Response({
            'message': 'Unsaved iterations cleared',
            'deleted_count': count
        })

class SequentialArtworkIterationViewSet(viewsets.ModelViewSet):
    """ViewSet for Sequential Artwork Iterations"""
    permission_classes = [permissions.AllowAny]  # ✅ Changed to allow internal FastAPI calls
    serializer_class = SequentialArtworkIterationSerializer
    
    def get_queryset(self):
        """Return iterations for the user"""
        # If authenticated, filter by current user
        if self.request.user.is_authenticated:
            return SequentialArtworkIteration.objects.filter(user=self.request.user)
        # If not authenticated (internal API calls), return all
        return SequentialArtworkIteration.objects.all()
    
    def create(self, request, *args, **kwargs):
        """Create a new iteration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user from request data or current user
        user_id = request.data.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                iteration = serializer.save(user=user)
            except User.DoesNotExist:
                return Response(
                    {'error': f'User {user_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif request.user.is_authenticated:
            iteration = serializer.save(user=request.user)
        else:
            return Response(
                {'error': 'user_id required or must be authenticated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            self.get_serializer(iteration).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def count_unsaved(self, request):
        """Count unsaved iterations"""
        user_id = request.query_params.get('user_id')
        sequence_mode = request.query_params.get('sequence_mode') == 'true'
        
        if not user_id:
            return Response(
                {'error': 'user_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = SequentialArtworkIteration.objects.filter(
            user_id=user_id,
            is_saved=False
        ).count()
        
        return Response({'count': count})
    
    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def clear_unsaved(self, request):
        """Clear unsaved iterations"""
        user_id = request.query_params.get('user_id')
        sequence_mode = request.query_params.get('sequence_mode') == 'true'
        
        if not user_id:
            return Response(
                {'error': 'user_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count, _ = SequentialArtworkIteration.objects.filter(
            user_id=user_id,
            is_saved=False
        ).delete()
        
        return Response({
            'message': 'Unsaved iterations cleared',
            'deleted_count': count
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_artwork(self, request):
        """Get iterations for specific artwork"""
        artwork_id = request.query_params.get('artwork_id')
        
        if not artwork_id:
            return Response(
                {'error': 'artwork_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        artwork = get_object_or_404(SequentialArtwork, id=artwork_id, user=request.user)
        iterations = SequentialArtworkIteration.objects.filter(artwork=artwork)
        
        serializer = self.get_serializer(iterations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unsaved(self, request):
        """Get unsaved iterations"""
        iterations = SequentialArtworkIteration.objects.filter(
            user=request.user,
            is_saved=False
        )
        
        serializer = self.get_serializer(iterations, many=True)
        return Response(serializer.data)