from django.db import models
from django.conf import settings
from apps.authentication.models import BaseModel

INTERACTION_TYPES = [
    ("like", "Like"),
    ("share", "Share"),
]

class SocialConnection(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_connections")
    connection = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="connected_to")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "connection")

class ImageInteraction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ForeignKey('gallery.Image', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

class CollectionInteraction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    collection = models.ForeignKey('gallery.Collection', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)


# --- Post Model ---
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class Post(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    images = models.ManyToManyField('gallery.Image', related_name="posts")
    moods = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    theme = models.CharField(max_length=100, blank=True, null=True)
    view = models.CharField(max_length=50, blank=True, null=True, default='public')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} ({self.id})"


class PostLike(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [models.Index(fields=['post']), models.Index(fields=['user'])]

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class PostComment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['post']), models.Index(fields=['user']), models.Index(fields=['created_at'])]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


class Follow(BaseModel):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [models.Index(fields=['follower']), models.Index(fields=['following'])]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
