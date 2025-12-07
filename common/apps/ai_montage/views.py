from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Montage, UploadedImage, MontageStatus
from .serializers import (
    MontageSerializer,
    UploadedImageSerializer,
    MontageCreateRequestSerializer,
    MontageStatusResponseSerializer,
    MontageUpdateSerializer,
    ImageUploadRequestSerializer
)
import logging
import uuid

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls from FastAPI
def create_montage(request):
    """Create a new montage record (called from FastAPI)"""
    try:
        serializer = MontageCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get user
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create montage
        montage = Montage.objects.create(
            user=user,
            prompt=data['prompt'],
            mood=data.get('mood'),
            total_images_uploaded=data['total_images_uploaded'],
            status=MontageStatus.PENDING
        )
        
        montage_serializer = MontageSerializer(montage)
        
        return Response({
            'success': True,
            'message': 'Montage created successfully',
            'data': montage_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.exception("Error creating montage")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def get_montage(request, montage_id):
    """Get montage by ID (called from FastAPI)"""
    try:
        montage = get_object_or_404(Montage, id=montage_id)
        serializer = MontageSerializer(montage)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error fetching montage {montage_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([])  # No auth required for internal API calls
def update_montage(request, montage_id):
    """Update montage fields (called from FastAPI during processing)"""
    try:
        montage = get_object_or_404(Montage, id=montage_id)
        
        serializer = MontageUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update fields
        for field, value in serializer.validated_data.items():
            setattr(montage, field, value)
        
        montage.save()
        
        montage_serializer = MontageSerializer(montage)
        
        return Response({
            'success': True,
            'message': 'Montage updated successfully',
            'data': montage_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error updating montage {montage_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def get_montage_status(request, montage_id):
    """Get montage status (called from FastAPI)"""
    try:
        montage = get_object_or_404(Montage, id=montage_id)
        
        # Calculate progress percentage
        status_map = {
            MontageStatus.PENDING: (5, "Montage request received"),
            MontageStatus.PROCESSING: (15, "Analyzing prompt and mood"),
            MontageStatus.SELECTING_IMAGES: (30, "Selecting optimal images"),
            MontageStatus.SEARCHING_MUSIC: (50, "Finding perfect background music"),
            MontageStatus.DOWNLOADING_MUSIC: (65, "Downloading music track"),
            MontageStatus.CREATING_VIDEO: (80, "Creating your montage video"),
            MontageStatus.COMPLETED: (100, "Montage completed successfully"),
            MontageStatus.FAILED: (0, "Montage creation failed")
        }
        
        progress, current_step = status_map.get(montage.status, (0, "Unknown status"))
        
        response_data = {
            'id': str(montage.id),
            'status': montage.status,
            'progress_percentage': progress,
            'current_step': current_step,
            'error_message': montage.error_message
        }
        
        return Response({
            'success': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error fetching montage status {montage_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Requires authentication for user-facing endpoint
def list_user_montages(request):
    """List all montages for a user (user-facing endpoint)"""
    try:
        user = request.user
        skip = int(request.GET.get('skip', 0))
        limit = int(request.GET.get('limit', 20))
        
        montages = Montage.objects.filter(user=user)[skip:skip+limit]
        total = Montage.objects.filter(user=user).count()
        
        serializer = MontageSerializer(montages, many=True)
        
        return Response({
            'success': True,
            'data': {
                'total': total,
                'montages': serializer.data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Error listing user montages")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls
def save_uploaded_image(request):
    """Save uploaded image record (called from FastAPI)"""
    try:
        serializer = ImageUploadRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get user
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get montage if provided
        montage = None
        if data.get('montage_id'):
            try:
                montage = Montage.objects.get(id=data['montage_id'])
            except Montage.DoesNotExist:
                pass
        
        # Create uploaded image
        uploaded_image = UploadedImage.objects.create(
            user=user,
            montage=montage,
            filename=data['filename'],
            original_filename=data['original_filename'],
            file_path=data['file_path'],
            file_size=data.get('file_size'),
            mime_type=data.get('mime_type'),
            width=data.get('width'),
            height=data.get('height'),
            url=data['url'],
            thumbnail_url=data.get('thumbnail_url')
        )
        
        image_serializer = UploadedImageSerializer(uploaded_image)
        
        return Response({
            'success': True,
            'message': 'Image record saved successfully',
            'data': image_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.exception("Error saving uploaded image")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([])  # No auth required for internal API calls
def link_images_to_montage(request, montage_id):
    """Link uploaded images to a montage (called from FastAPI)"""
    try:
        montage = get_object_or_404(Montage, id=montage_id)
        
        image_ids = request.data.get('image_ids', [])
        
        if not image_ids:
            return Response({
                'success': False,
                'message': 'No image IDs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update images
        UploadedImage.objects.filter(
            id__in=image_ids,
            user=montage.user
        ).update(montage=montage)
        
        return Response({
            'success': True,
            'message': f'Linked {len(image_ids)} images to montage'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error linking images to montage {montage_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
