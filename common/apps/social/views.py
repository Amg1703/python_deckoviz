from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, F
from apps.gallery.models import Image, Collection
from .models import SocialConnection, ImageInteraction, CollectionInteraction
from apps.authentication.models import User
from apps.gallery.serializers import ImageSerializer, CollectionSerializer

class SocialFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mode = request.query_params.get('mode', 'friends')
        limit = min(int(request.query_params.get('limit', 100)), 100)
        user = request.user
        now = timezone.now()
        since = now - timedelta(hours=24)

        if mode == 'friends':
            connections = SocialConnection.objects.filter(user=user).values_list('connection', flat=True)
            images = Image.objects.filter(
                Q(uploaded_by__in=connections) |
                Q(imageinteraction__user__in=connections, imageinteraction__interaction_type='share')
            ).filter(created_at__gte=since).annotate(
                like_count=Count('imageinteraction', filter=Q(imageinteraction__interaction_type='like', imageinteraction__created_at__gte=since))
            ).order_by('-like_count', '-created_at').distinct()[:limit]
            # Similar for collections
            collections = Collection.objects.filter(
                Q(created_by__in=connections) |
                Q(collectioninteraction__user__in=connections, collectioninteraction__interaction_type='share')
            ).filter(created_at__gte=since).annotate(
                like_count=Count('collectioninteraction', filter=Q(collectioninteraction__interaction_type='like', collectioninteraction__created_at__gte=since))
            ).order_by('-like_count', '-created_at').distinct()[:limit]
        else:
            images = Image.objects.annotate(
                like_count=Count('imageinteraction', filter=Q(imageinteraction__interaction_type='like', imageinteraction__created_at__gte=since)),
                share_count=Count('imageinteraction', filter=Q(imageinteraction__interaction_type='share', imageinteraction__created_at__gte=since)),
            ).filter(
                Q(like_count__gt=0) | Q(share_count__gt=0),
                created_at__gte=since
            ).exclude(uploaded_by=user).order_by(
                F('like_count') + F('share_count')
            ).distinct()[:limit]
            collections = Collection.objects.annotate(
                like_count=Count('collectioninteraction', filter=Q(collectioninteraction__interaction_type='like', collectioninteraction__created_at__gte=since)),
                share_count=Count('collectioninteraction', filter=Q(collectioninteraction__interaction_type='share', collectioninteraction__created_at__gte=since)),
            ).filter(
                Q(like_count__gt=0) | Q(share_count__gt=0),
                created_at__gte=since
            ).exclude(created_by=user).order_by(
                F('like_count') + F('share_count')
            ).distinct()[:limit]

        image_data = ImageSerializer(images, many=True).data
        collection_data = CollectionSerializer(collections, many=True).data
        return Response({'images': image_data, 'collections': collection_data})

class UserPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        images = Image.objects.filter(uploaded_by=user).order_by('-created_at')
        collections = Collection.objects.filter(created_by=user).order_by('-created_at')
        image_data = ImageSerializer(images, many=True).data
        collection_data = CollectionSerializer(collections, many=True).data
        return Response({
            'images': image_data,
            'collections': collection_data
        })
