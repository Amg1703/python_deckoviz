from django.urls import path
from .views import MetaCollectionView, AddToFavouritesView, RemoveFromFavouritesView

urlpatterns = [
    path('', MetaCollectionView.as_view(), name='meta-collection'),
    path('favourites/add/', AddToFavouritesView.as_view(), name='add-to-favourites'),
    path('favourites/remove/', RemoveFromFavouritesView.as_view(), name='remove-from-favourites'),
] 