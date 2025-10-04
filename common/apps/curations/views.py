from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import CuratedImages, CuratedCollections
from .serializers import CuratedImagesSerializer, CuratedCollectionsSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_curated_images(request):
    """
    Get the single curated images list
    """
    try:
        curation = CuratedImages.objects.filter(is_active=True).first()
        if curation:
            data = CuratedImagesSerializer(curation, context={'request': request}).data
            return Response(data)
        else:
            return Response({'images': [], 'message': 'No curated images available'})
    except CuratedImages.DoesNotExist:
        return Response({'images': [], 'message': 'No curated images available'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_curated_collections(request):
    """
    Get the single curated collections list
    """
    try:
        curation = CuratedCollections.objects.filter(is_active=True).first()
        if curation:
            data = CuratedCollectionsSerializer(curation, context={'request': request}).data
            return Response(data)
        else:
            return Response({'collections': [], 'message': 'No curated collections available'})
    except CuratedCollections.DoesNotExist:
        return Response({'collections': [], 'message': 'No curated collections available'})


@api_view(['GET'])
@permission_classes([AllowAny])
def all_curations(request):
    """
    Get all active curations (both images and collections) in one response
    """
    curated_images = CuratedImages.objects.filter(is_active=True).first()
    curated_collections = CuratedCollections.objects.filter(is_active=True).first()
    
    images_data = CuratedImagesSerializer(curated_images, context={'request': request}).data if curated_images else {'images': []}
    collections_data = CuratedCollectionsSerializer(curated_collections, context={'request': request}).data if curated_collections else {'collections': []}
    
    return Response({
        'curated_images': images_data,
        'curated_collections': collections_data
    })
