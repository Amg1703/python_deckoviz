from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.gallery.models import Image, Collection
from .models import SocialConnection, ImageInteraction, CollectionInteraction, Post, Follow
from .serializers import PostSerializer, FollowSerializer
from apps.authentication.serializers import UserSerializer
from django.contrib.auth import get_user_model
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
from rest_framework.pagination import PageNumberPagination


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


@extend_schema(
    responses={200: 'UserProfileResponseSerializer'},
    description='Retrieve a public user profile including posts, followers, and following previews.',
    tags=['Social']
)
class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        User = get_user_model()
        try:
            profile_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

        # Privacy check
        if not getattr(profile_user, 'profile_visible', True) and (not request.user or not request.user.is_authenticated or request.user != profile_user):
            return Response({'detail': 'Profile is private.'}, status=403)

        # Posts (paginated using DRF pagination)
        posts_qs = Post.objects.filter(user=profile_user).order_by('-created_at')
        paginator = PageNumberPagination()
        # allow client to pass page_size, with default 10 and upper bound 100
        try:
            paginator.page_size = min(int(request.query_params.get('page_size', 10)), 100)
        except Exception:
            paginator.page_size = 10
        page = paginator.paginate_queryset(posts_qs, request, view=self)
        posts_data = PostSerializer(page, many=True).data if page is not None else []

        # Followers/following previews and counts
        followers_qs = Follow.objects.filter(following=profile_user).select_related('follower')[:5]
        following_qs = Follow.objects.filter(follower=profile_user).select_related('following')[:5]
        followers_preview = [f.follower for f in followers_qs]
        following_preview = [f.following for f in following_qs]

        followers_count = Follow.objects.filter(following=profile_user).count()
        following_count = Follow.objects.filter(follower=profile_user).count()

        is_following = False
        if request.user and getattr(request.user, 'is_authenticated', False) and request.user != profile_user:
            is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

        user_info = UserSerializer(profile_user).data

        base = {
            'user': user_info,
            'followers_count': followers_count,
            'following_count': following_count,
            'followers_preview': UserSerializer(followers_preview, many=True).data,
            'following_preview': UserSerializer(following_preview, many=True).data,
            'is_following': is_following,
        }

        # If we used pagination, include pagination metadata and results
        if page is not None:
            paginated = paginator.get_paginated_response(posts_data).data
            # paginated contains: count, next, previous, results
            base.update({
                'posts': paginated.get('results', []),
                'posts_count': paginated.get('count', 0),
                'posts_next': paginated.get('next'),
                'posts_previous': paginated.get('previous'),
            })
            return Response(base)

        base['posts'] = posts_data
        return Response(base)

# --- Follow/Unfollow and Followers/Following Endpoints ---
User = get_user_model()

@extend_schema(
    request={"application/json": OpenApiResponse(description="{ 'user_id': '<uuid>' }")},
    responses={200: OpenApiResponse(description="Unfollowed."), 201: OpenApiResponse(description="Followed."), 400: OpenApiResponse(description="Invalid user_id."), 404: OpenApiResponse(description="User not found.")},
    description="Toggle follow/unfollow for a user. Auth required.",
    tags=["Social"]
)
class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        target_user_id = request.data.get("user_id")
        if not target_user_id or str(request.user.id) == str(target_user_id):
            return Response({"detail": "Invalid user_id."}, status=400)
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if not created:
            follow.delete()
            return Response({"detail": "Unfollowed."}, status=200)
        return Response({"detail": "Followed."}, status=201)

@extend_schema(
    responses={200: UserSerializer(many=True)},
    description="List users who follow the given user.",
    tags=["Social"]
)
class FollowersListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        followers = Follow.objects.filter(following__id=user_id).select_related("follower")
        data = UserSerializer([f.follower for f in followers], many=True).data
        return Response(data)

@extend_schema(
    responses={200: UserSerializer(many=True)},
    description="List users the given user is following.",
    tags=["Social"]
)
class FollowingListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        following = Follow.objects.filter(follower__id=user_id).select_related("following")
        data = UserSerializer([f.following for f in following], many=True).data
        return Response(data)
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
