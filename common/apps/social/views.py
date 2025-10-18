from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.gallery.models import Image, Collection
from .models import SocialConnection, ImageInteraction, CollectionInteraction, Post
from .serializers import PostSerializer
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

from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, F
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
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import CreatePostRequestSerializer
from .serializers import PostLikeSerializer, PostCommentSerializer, FollowSerializer
from .models import PostLike, PostComment, Follow
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

@extend_schema(
    request=CreatePostRequestSerializer,
    responses={201: PostSerializer, 400: OpenApiResponse(description="Invalid input.")},
    description="Create a new post with images, collections, moods, theme, and view.",
    tags=["Social"]
)
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new post. Accepts:
        - images: list of image UUIDs
        - collections: list of collection UUIDs
        - moods: list of strings
        - theme: string
        - view: 'public' or 'private' (public = Serendipity feed, private = Friends feed)
        Now: All images from selected collections are auto-attached to the post (deduplicated with images).
        """
        from .models import Post
        from .serializers import PostSerializer
        from apps.gallery.models import Image, Collection
        user = request.user
        images = request.data.get('images', [])
        collections = request.data.get('collections', [])
        moods = request.data.get('moods', [])
        theme = request.data.get('theme', None)
        view = request.data.get('view', 'public')

        # Validate images
        if not isinstance(images, list):
            return Response({'error': 'images must be a list of image IDs.'}, status=status.HTTP_400_BAD_REQUEST)
        image_objs = list(Image.objects.filter(id__in=images, uploaded_by=user))
        if len(image_objs) != len(images):
            return Response({'error': 'One or more images not found or do not belong to user.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate collections
        if collections and not isinstance(collections, list):
            return Response({'error': 'collections must be a list of collection IDs.'}, status=status.HTTP_400_BAD_REQUEST)
        collection_objs = list(Collection.objects.filter(id__in=collections, user=user)) if collections else []
        if collections and len(collection_objs) != len(collections):
            return Response({'error': 'One or more collections not found or do not belong to user.'}, status=status.HTTP_400_BAD_REQUEST)

        # Gather all images from selected collections (deduplicate with images)
        collection_image_ids = set()
        for col in collection_objs:
            # Get all images in the collection (CollectionImage relation)
            for ci in col.collection_images.select_related('image').all():
                if ci.image and ci.image.uploaded_by == user:
                    collection_image_ids.add(ci.image.id)

        # Merge with explicitly listed images (deduplicate)
        all_image_ids = set([img.id for img in image_objs]) | collection_image_ids
        all_image_objs = list(Image.objects.filter(id__in=all_image_ids, uploaded_by=user))

        post = Post.objects.create(user=user, theme=theme, view=view, moods=moods)
        post.images.set(all_image_objs)
        post.save()
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    request=None,
    responses={200: OpenApiResponse(description='Toggled like status')},
    description="Toggle like/unlike for a post.",
    tags=["Social"]
)
class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        like, created = PostLike.objects.get_or_create(user=user, post=post)
        if not created:
            # already liked -> unlike
            like.delete()
            return Response({'liked': False}, status=status.HTTP_200_OK)
        return Response({'liked': True}, status=status.HTTP_201_CREATED)


@extend_schema(
    request=PostCommentSerializer,
    responses={201: PostCommentSerializer, 400: OpenApiResponse(description='Invalid input')},
    description="Add a comment to a post.",
    tags=["Social"]
)
class PostCommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = PostComment.objects.create(
                user=user,
                post=post,
                content=serializer.validated_data.get('content')
            )
            return Response(PostCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostCommentsListView(ListAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return PostComment.objects.filter(post_id=post_id, is_active=True).order_by('-created_at')


class PostLikesListView(ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return PostLike.objects.filter(post_id=post_id).select_related('user')


@extend_schema(
    request=None,
    responses={200: OpenApiResponse(description='Toggled follow status')},
    description="Toggle follow/unfollow a user.",
    tags=["Social"]
)
class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        follower = request.user
        if str(follower.id) == str(user_id):
            return Response({'error': 'Cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            to_follow = follower.__class__.objects.get(id=user_id)
        except Exception:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        rel, created = Follow.objects.get_or_create(follower=follower, following=to_follow)
        if not created:
            rel.delete()
            return Response({'following': False}, status=status.HTTP_200_OK)
        return Response({'following': True}, status=status.HTTP_201_CREATED)


class FollowersListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Follow.objects.filter(following_id=user_id).select_related('follower')


class FollowingListView(ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Follow.objects.filter(follower_id=user_id).select_related('following')

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
