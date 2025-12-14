from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SculptureViewSet, SculptureImageViewSet, SaveGeneratedImageAPIView

router = DefaultRouter()
router.register(r"sculptures", SculptureViewSet, basename="sculpture")
router.register(r"images", SculptureImageViewSet, basename="sculpture-image")

urlpatterns = [
    path("", include(router.urls)),
    # internal endpoint used by AI service
    path("internal/images/save/", SaveGeneratedImageAPIView.as_view(), name="sculpture-internal-save-image"),
]