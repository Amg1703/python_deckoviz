from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import VisualAudiobook
from .serializers import VisualAudiobookSerializer, CreateVisualAudiobookSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
ART_STYLES = [
    "watercolor painting", "oil painting", "digital art", "impressionist",
    "minimalist", "abstract", "photorealistic", "anime style",
    "comic book style", "vintage illustration"
]


class VisualAudiobookViewSet(viewsets.ModelViewSet):
    """ViewSet for user-facing Visual Audiobook operations"""
    
    serializer_class = VisualAudiobookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return audiobooks for current user"""
        return VisualAudiobook.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve specific audiobook"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """List all audiobooks for current user"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete audiobook"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Internal API endpoints (called by FastAPI) - no auth required
@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls from FastAPI
def create_audiobook(request):
    """Create audiobook record (called from FastAPI)"""
    try:
        serializer = CreateVisualAudiobookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Validate voice and art_style
        voice = data['voice']
        art_style = data['art_style']
        
        if voice not in AVAILABLE_VOICES:
            return Response({
                'success': False,
                'message': f'Invalid voice. Choose from: {AVAILABLE_VOICES}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if art_style not in ART_STYLES:
            return Response({
                'success': False,
                'message': f'Invalid art style. Choose from: {ART_STYLES}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        try:
            user = User.objects.get(id=data['user'])
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create audiobook in 'processing' status
        audiobook = VisualAudiobook.objects.create(
            user=user,
            book_title=data['book_title'],
            voice=voice,
            art_style=art_style,
            num_frames=data['num_frames'],
            status='processing'
        )
        
        logger.info(f"Audiobook {audiobook.id} created - waiting for FastAPI processing")
        
        audiobook_serializer = VisualAudiobookSerializer(audiobook)
        
        return Response({
            'success': True,
            'message': 'Audiobook created successfully',
            'data': audiobook_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.exception("Error creating audiobook")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def get_audiobook(request, audiobook_id):
    """Get audiobook by ID (called from FastAPI)"""
    try:
        audiobook = get_object_or_404(VisualAudiobook, id=audiobook_id)
        serializer = VisualAudiobookSerializer(audiobook)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error fetching audiobook {audiobook_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([])  # No auth required for internal API calls
def update_audiobook(request, audiobook_id):
    """Update audiobook status (called from FastAPI during processing)"""
    try:
        audiobook = get_object_or_404(VisualAudiobook, id=audiobook_id)
        
        data = request.data
        
        # Update fields
        if 'video_url' in data:
            audiobook.video_url = data['video_url']
        if 'video_duration' in data:
            audiobook.video_duration = data['video_duration']
        if 'video_size_mb' in data:
            audiobook.video_size_mb = data['video_size_mb']
        if 'status' in data:
            audiobook.status = data['status']
        if 'error_message' in data:
            audiobook.error_message = data['error_message']
        if 'num_pages' in data:
            audiobook.num_pages = data['num_pages']
        if 'text_extracted' in data:
            audiobook.text_extracted = data['text_extracted']
        
        if data.get('status') == 'completed':
            audiobook.completed_at = timezone.now()
        
        audiobook.save()
        
        logger.info(f"Audiobook {audiobook_id} updated with status: {audiobook.status}")
        
        audiobook_serializer = VisualAudiobookSerializer(audiobook)
        
        return Response({
            'success': True,
            'message': 'Audiobook updated successfully',
            'data': audiobook_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error updating audiobook {audiobook_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def get_audiobook_status(request, audiobook_id):
    """Get audiobook status (called from FastAPI or client polling)"""
    try:
        audiobook = get_object_or_404(VisualAudiobook, id=audiobook_id)
        
        status_map = {
            'processing': (20, "Processing audiobook"),
            'completed': (100, "Audiobook completed successfully"),
            'failed': (0, "Audiobook creation failed")
        }
        
        progress, current_step = status_map.get(audiobook.status, (0, "Unknown status"))
        
        response_data = {
            'id': str(audiobook.id),
            'status': audiobook.status,
            'progress_percentage': progress,
            'current_step': current_step,
            'video_url': audiobook.video_url,
            'error_message': audiobook.error_message
        }
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error fetching audiobook status {audiobook_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Requires authentication for user-facing endpoint
def list_user_audiobooks(request):
    """List all audiobooks for a user (user-facing endpoint)"""
    try:
        user = request.user
        skip = int(request.GET.get('skip', 0))
        limit = int(request.GET.get('limit', 20))
        
        audiobooks = VisualAudiobook.objects.filter(user=user)[skip:skip+limit]
        total = VisualAudiobook.objects.filter(user=user).count()
        
        serializer = VisualAudiobookSerializer(audiobooks, many=True)
        
        return Response({
            'success': True,
            'data': {
                'total': total,
                'audiobooks': serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Error listing user audiobooks")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)