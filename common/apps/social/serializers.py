# --- Create Post Request Serializer ---
from rest_framework import serializers

class CreatePostRequestSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of image UUIDs to include in the post."
    )
    collections = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of collection UUIDs to include in the post."
    )
    moods = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of moods for the post."
    )
    theme = serializers.CharField(required=False, help_text="Theme of the post.")
    view = serializers.CharField(required=False, help_text="View type (e.g., public, private).")
from rest_framework import serializers
from .models import SocialConnection, ImageInteraction, CollectionInteraction, Post
from apps.gallery.serializers import ImageSerializer
from apps.authentication.serializers import UserSerializer
from .models import PostLike, PostComment, Follow

class SocialConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialConnection
        fields = '__all__'

class ImageInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageInteraction
        fields = '__all__'

class CollectionInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionInteraction
        fields = '__all__'


# --- Post Serializer ---
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    recent_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'images',
            'like_count',
            'comment_count',
            'recent_comments',
            'moods',
            'theme',
            'view',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def get_recent_comments(self, obj):
        comments = obj.comments.filter(is_active=True).order_by('-created_at')[:3]
        return [
            {
                'id': c.id,
                'user': UserSerializer(c.user).data,
                'content': c.content,
                'created_at': c.created_at,
            }
            for c in comments
        ]


class PostLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'post', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
