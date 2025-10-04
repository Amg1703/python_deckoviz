from django.urls import path
from .views import (
    MetaAudioView, AddToLikedAudioView, RemoveFromLikedAudioView, AddToStarredAudioView, RemoveFromStarredAudioView
)

urlpatterns = [
    path('', MetaAudioView.as_view(), name='meta-audio'),
    path('liked/add/', AddToLikedAudioView.as_view(), name='add-to-liked-audio'),
    path('liked/remove/', RemoveFromLikedAudioView.as_view(), name='remove-from-liked-audio'),
    path('starred/add/', AddToStarredAudioView.as_view(), name='add-to-starred-audio'),
    path('starred/remove/', RemoveFromStarredAudioView.as_view(), name='remove-from-starred-audio'),
] 