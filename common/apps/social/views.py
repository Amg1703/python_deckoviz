from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.gallery.models import Image, Collection
# --- User Collections Endpoint ---
class UserCollectionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        collections = Collection.objects.filter(user=user)
        # Only return id, title, and cover image (if available)
        data = []
        for col in collections:
            # Get the first image in the collection as cover
            cover_url = None
            first_image = None
            if hasattr(col, 'collection_images'):
                col_images = col.collection_images.select_related('image').all()
                if col_images:
                    first_image = col_images[0].image if hasattr(col_images[0], 'image') else None
            if first_image and hasattr(first_image, 'file') and first_image.file:
                cover_url = first_image.file.url
            data.append({
                'id': col.id,
                'title': getattr(col, 'title', ''),
                'cover_image': cover_url
            })
        return Response({'collections': data})

# --- User Galleries (Images) Endpoint ---
class UserGalleriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        images = Image.objects.filter(uploaded_by=user)
        # Only return id, title, and file (image URL)
        data = [
            {
                'id': img.id,
                'title': getattr(img, 'title', ''),
                'file': img.file.url if hasattr(img, 'file') and img.file else None
            }
            for img in images
        ]
        return Response({'galleries': data})

# --- Create Post Options Endpoint ---
class CreatePostOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Images: only id, title, file
        images = Image.objects.filter(uploaded_by=user).order_by('-created_at')
        images_data = [
            {
                'id': img.id,
                'title': img.title,
                'file': img.file.url if img.file else None
            }
            for img in images
        ]

        # Collections: id, name, and images (id, title, file)
        collections = Collection.objects.filter(user=user).order_by('-created_at')
        collections_data = []
        for col in collections:
            col_images = col.collection_images.select_related('image').all()
            col_images_data = [
                {
                    'id': ci.image.id,
                    'title': ci.image.title,
                    'file': ci.image.file.url if ci.image.file else None
                }
                for ci in col_images if ci.image
            ]
            collections_data.append({
                'id': col.id,
                'name': col.name,
                'images': col_images_data
            })

        return Response({
            'images': images_data,
            'collections': collections_data
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, F
from apps.gallery.models import Image, Collection
from .models import SocialConnection, ImageInteraction, CollectionInteraction
from apps.authentication.models import User
from apps.gallery.serializers import ImageSerializer, CollectionSerializer
from rest_framework.decorators import api_view, permission_classes


# --- Friends Feed ---
class FriendsFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 100)), 100)
        user = request.user
        now = timezone.now()
        since = now - timedelta(hours=24)
        connections = SocialConnection.objects.filter(user=user).values_list('connection', flat=True)
        images = Image.objects.filter(
            Q(uploaded_by__in=connections) |
            Q(imageinteraction__user__in=connections, imageinteraction__interaction_type='share')
        ).filter(created_at__gte=since).annotate(
            like_count=Count('imageinteraction', filter=Q(imageinteraction__interaction_type='like', imageinteraction__created_at__gte=since))
        ).order_by('-like_count', '-created_at').distinct()[:limit]
        collections = Collection.objects.filter(
            Q(user__in=connections) |
            Q(collectioninteraction__user__in=connections, collectioninteraction__interaction_type='share')
        ).filter(created_at__gte=since).annotate(
            like_count=Count('collectioninteraction', filter=Q(collectioninteraction__interaction_type='like', collectioninteraction__created_at__gte=since))
        ).order_by('-like_count', '-created_at').distinct()[:limit]
        image_data = ImageSerializer(images, many=True).data
        collection_data = CollectionSerializer(collections, many=True).data
        return Response({'images': image_data, 'collections': collection_data})

# --- Serendipity Feed ---
class SerendipityFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 100)), 100)
        user = request.user
        now = timezone.now()
        since = now - timedelta(hours=24)
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
        ).exclude(user=user).order_by(
            F('like_count') + F('share_count')
        ).distinct()[:limit]
        image_data = ImageSerializer(images, many=True).data
        collection_data = CollectionSerializer(collections, many=True).data
        return Response({'images': image_data, 'collections': collection_data})

# --- Create Post Endpoint ---
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Accepts creation of a new Post with images, moods, theme, view
        from .models import Post
        from .serializers import PostSerializer
        user = request.user
        images = request.data.get('images', [])
        moods = request.data.get('moods', [])
        theme = request.data.get('theme', None)
        view = request.data.get('view', 'public')

        # images can be a list of image IDs
        if not isinstance(images, list):
            return Response({'error': 'images must be a list of image IDs.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate images exist and belong to user (or are accessible)
        from apps.gallery.models import Image
        image_objs = Image.objects.filter(id__in=images)
        if image_objs.count() != len(images):
            return Response({'error': 'One or more images not found.'}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.create(user=user, theme=theme, view=view, moods=moods)
        post.images.set(image_objs)
        post.save()
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from .models import Post
from .serializers import PostSerializer

class UserPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        images = data.pop('images', [])
        post = Post.objects.create(user=user, **data)
        if images:
            post.images.set(images)
        serializer = PostSerializer(post)

        # Fetch user's galleries (images)
        user_images = Image.objects.filter(uploaded_by=user)
        galleries = [
            {
                'id': img.id,
                'title': getattr(img, 'title', ''),
                'file': img.file.url if hasattr(img, 'file') and img.file else None
            }
            for img in user_images
        ]

        # Fetch user's collections
        user_collections = Collection.objects.filter(user=user)
        collections = []
        for col in user_collections:
            cover_url = None
            first_image = None
            if hasattr(col, 'collection_images'):
                col_images = col.collection_images.select_related('image').all()
                if col_images:
                    first_image = col_images[0].image if hasattr(col_images[0], 'image') else None
            if first_image and hasattr(first_image, 'file') and first_image.file:
                cover_url = first_image.file.url
            collections.append({
                'id': col.id,
                'title': getattr(col, 'title', ''),
                'cover_image': cover_url
            })

        return Response({
            'post': serializer.data,
            'galleries': galleries,
            'collections': collections
        }, status=201)
