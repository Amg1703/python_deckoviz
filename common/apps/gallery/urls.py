from django.urls import path,include 
from rest_framework.routers import DefaultRouter 
from .views import (ImageViewSet,CollectionViewSet,CollectionImageViewSet,AudioViewSet,TestView, today_curation, AdminRitualViewSet, UserRitualViewSet)
from .search_views import ImageSearchView


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
    path('',include(router.urls)),  
    # path('images/backfill-metadata/', BackfillImageMetadataView.as_view(), name='backfill-image-metadata'),
    path('test/', TestView.as_view(), name='test'),
]
