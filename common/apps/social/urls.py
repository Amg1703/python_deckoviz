

from django.urls import path
from .views import (
    FriendsFeedView, SerendipityFeedView, CreatePostView, UserPostsView, CreatePostOptionsView,
    UserGalleriesView, UserCollectionsView,
    PostLikeToggleView, PostCommentCreateView, PostCommentsListView, PostLikesListView,
    FollowToggleView, FollowersListView, FollowingListView
)

urlpatterns = [
    path('feed/friends/', FriendsFeedView.as_view(), name='social-feed-friends'),
    path('feed/serendipity/', SerendipityFeedView.as_view(), name='social-feed-serendipity'),
    path('feed/', FriendsFeedView.as_view(), name='social-feed'),  # Backwards compatible: default to friends
    path('create-post/', CreatePostView.as_view(), name='social-create-post'),
    path('my-posts/', UserPostsView.as_view(), name='user-posts'),
    path('create-posts-options/', CreatePostOptionsView.as_view(), name='social-create-posts-options'),
    path('user-galleries/', UserGalleriesView.as_view(), name='user-galleries'),
    path('user-collections/', UserCollectionsView.as_view(), name='user-collections'),
    # Post interactions
    path('posts/<uuid:post_id>/like/', PostLikeToggleView.as_view(), name='post-like-toggle'),
    path('posts/<uuid:post_id>/comment/', PostCommentCreateView.as_view(), name='post-comment-create'),
    path('posts/<uuid:post_id>/comments/', PostCommentsListView.as_view(), name='post-comments-list'),
    path('posts/<uuid:post_id>/likes/', PostLikesListView.as_view(), name='post-likes-list'),
    # Follow
    path('follow/<uuid:user_id>/', FollowToggleView.as_view(), name='follow-toggle'),
    path('followers/<uuid:user_id>/', FollowersListView.as_view(), name='followers-list'),
    path('following/<uuid:user_id>/', FollowingListView.as_view(), name='following-list'),
]
