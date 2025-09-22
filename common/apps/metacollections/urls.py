from django.urls import path
<<<<<<< HEAD
from .views import MetaCollectionView, AddToFavouritesView, RemoveFromFavouritesView, AddToStarredView, RemoveFromStarredView, ShareCollectionView, RemoveSharedUserView, AddToLikedCollectionView, RemoveFromLikedCollectionView, MySharedCollectionsView, SharedCollectionsByUserView, UsersWhoSharedCollectionsView
=======
from .views import MetaCollectionView, AddToFavouritesView, RemoveFromFavouritesView, AddToStarredView, RemoveFromStarredView, ShareCollectionView, RemoveSharedUserView, AddToLikedCollectionView, RemoveFromLikedCollectionView, MySharedCollectionsView
>>>>>>> 6e0cfd7 (Adding and committing code that was altered in production back to the github repo)

urlpatterns = [
    path('', MetaCollectionView.as_view(), name='meta-collection'),
    path('favourites/add/', AddToFavouritesView.as_view(), name='add-to-favourites'),
    path('favourites/remove/', RemoveFromFavouritesView.as_view(), name='remove-from-favourites'),
    path('starred/add/', AddToStarredView.as_view(), name='add-to-starred'),
    path('starred/remove/', RemoveFromStarredView.as_view(), name='remove-from-starred'),
    path('share-collection/', ShareCollectionView.as_view(), name='share-collection'),
    path('remove-shared-user/', RemoveSharedUserView.as_view(), name='remove-shared-user'),
    path('liked/add/', AddToLikedCollectionView.as_view(), name='add-to-liked-collection'),
    path('liked/remove/', RemoveFromLikedCollectionView.as_view(), name='remove-from-liked-collection'),
    path('my-shared/', MySharedCollectionsView.as_view(), name='my-shared-collections'),
<<<<<<< HEAD
    path('shared-by-user/<int:user_id>/', SharedCollectionsByUserView.as_view(), name='shared-collections-by-user'),
    path('shared-users/', UsersWhoSharedCollectionsView.as_view(), name='users-who-shared-collections'),
=======
>>>>>>> 6e0cfd7 (Adding and committing code that was altered in production back to the github repo)
] 