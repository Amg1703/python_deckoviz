from django.urls import path
from .views import (
    MetaImageView, AddToLikedView, RemoveFromLikedView, 
    AddToStarredView, RemoveFromStarredView, ShareImageView, RemoveSharedUserView
)

urlpatterns = [
    path('', MetaImageView.as_view(), name='meta-image'),
    path('liked/add/', AddToLikedView.as_view(), name='add-to-liked'),
    path('liked/remove/', RemoveFromLikedView.as_view(), name='remove-from-liked'),
    path('starred/add/', AddToStarredView.as_view(), name='add-to-starred-image'),
    path('starred/remove/', RemoveFromStarredView.as_view(), name='remove-from-starred-image'),
    path('share/', ShareImageView.as_view(), name='share-image'),
    path('share/remove/', RemoveSharedUserView.as_view(), name='remove-shared-user'),
] 