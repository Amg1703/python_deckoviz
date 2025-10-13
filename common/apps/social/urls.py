from django.urls import path
from .views import SocialFeedView, UserPostsView

urlpatterns = [
    path('feed/', SocialFeedView.as_view(), name='social-feed'),
    path('my-posts/', UserPostsView.as_view(), name='user-posts'),
]
