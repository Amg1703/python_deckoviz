from django.urls import path,include 
from rest_framework.routers import DefaultRouter 
from .views import (ImageViewSet,CollectionViewSet,CollectionImageViewSet,AudioViewSet,TestView, today_curation, AdminRitualViewSet, UserRitualViewSet, regenerate_empty_collection_metadata, today_image_curation)
from .search_views import ImageSearchView, CollectionSearchView


router = DefaultRouter()

router.register(r'audios',  AudioViewSet,basename='audios')
router.register(r'images', ImageViewSet,basename='images')
router.register(r'collections', CollectionViewSet,basename='collections')
router.register(r'collection-images', CollectionImageViewSet,basename='collection_images')
router.register(r'admin-rituals', AdminRitualViewSet, basename='admin_rituals')
router.register(r'user-rituals', UserRitualViewSet, basename='user_rituals')

urlpatterns = [
    path('images/search/', ImageSearchView.as_view(), name='image-search'),
    path('curations/today/', today_curation, name='today-curation'),
    path('image-curations/today/', today_image_curation, name='today-image-curation'),
    path('collections/search/', CollectionSearchView.as_view(), name='collection-search'),
    path('',include(router.urls)),  
    # path('images/backfill-metadata/', BackfillImageMetadataView.as_view(), name='backfill-image-metadata'),
    path('test/', TestView.as_view(), name='test'),
    path('admin/regenerate-empty-collection-metadata/', regenerate_empty_collection_metadata, name='regenerate-empty-collection-metadata'),
]
