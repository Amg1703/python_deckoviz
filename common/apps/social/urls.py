

from django.urls import path
from .views import (
    FriendsFeedView, SerendipityFeedView, CreatePostView, UserPostsView, CreatePostOptionsView
)

urlpatterns = [
    path('feed/friends/', FriendsFeedView.as_view(), name='social-feed-friends'),
    path('feed/serendipity/', SerendipityFeedView.as_view(), name='social-feed-serendipity'),
    path('feed/', FriendsFeedView.as_view(), name='social-feed'),  # Backwards compatible: default to friends
    path('create-post/', CreatePostView.as_view(), name='social-create-post'),
    path('my-posts/', UserPostsView.as_view(), name='user-posts'),
    path('create-posts-options/', CreatePostOptionsView.as_view(), name='social-create-posts-options'),
]
