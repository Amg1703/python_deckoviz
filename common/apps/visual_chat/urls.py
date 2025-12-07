from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PDFInternalViewSet, JobInternalViewSet, ImageInternalViewSet

router = DefaultRouter()
router.register(r'pdfs', PDFInternalViewSet, basename='pdf-internal')
router.register(r'jobs', JobInternalViewSet, basename='job-internal')
router.register(r'images', ImageInternalViewSet, basename='image-internal')

urlpatterns = [
    path('', include(router.urls)),
]
