from django.urls import path
from .views import get_curated_images, get_curated_collections, all_curations

urlpatterns = [
    path('all/', all_curations, name='all-curations'),
    path('images/', get_curated_images, name='curated-images'),
    path('collections/', get_curated_collections, name='curated-collections'),
]
