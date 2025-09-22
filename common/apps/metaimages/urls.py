from django.urls import path
from .views import (
    MetaImageView, AddToLikedView, RemoveFromLikedView, 
    AddToStarredView, RemoveFromStarredView, ShareImageView, RemoveSharedUserView,
<<<<<<< HEAD
    MySharedImagesView, SharedImagesByUserView, UsersWhoSharedImagesView
=======
    MySharedImagesView
>>>>>>> 6e0cfd7 (Adding and committing code that was altered in production back to the github repo)
)

urlpatterns = [
    path('', MetaImageView.as_view(), name='meta-image'),
    path('liked/add/', AddToLikedView.as_view(), name='add-to-liked'),
    path('liked/remove/', RemoveFromLikedView.as_view(), name='remove-from-liked'),
    path('starred/add/', AddToStarredView.as_view(), name='add-to-starred-image'),
    path('starred/remove/', RemoveFromStarredView.as_view(), name='remove-from-starred-image'),
    path('share/', ShareImageView.as_view(), name='share-image'),
    path('share/remove/', RemoveSharedUserView.as_view(), name='remove-shared-user'),
    path('my-shared/', MySharedImagesView.as_view(), name='my-shared-images'),
<<<<<<< HEAD
    path('shared-by-user/<int:user_id>/', SharedImagesByUserView.as_view(), name='shared-images-by-user'),
    path('shared-users/', UsersWhoSharedImagesView.as_view(), name='users-who-shared-images'),
=======
>>>>>>> 6e0cfd7 (Adding and committing code that was altered in production back to the github repo)
] 