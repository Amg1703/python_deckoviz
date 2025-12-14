from django.urls import path

from .views import (
    InternalCreateView,
    InternalDetailView,
    GetByJobIdView,
    ListView,
)

urlpatterns = [
    path("internal/create/", InternalCreateView.as_view(), name="before_after_deckoviz_internal_create"),
    path("internal/<int:pk>/", InternalDetailView.as_view(), name="before_after_deckoviz_internal_detail"),
    path("internal/by-job/", GetByJobIdView.as_view(), name="before_after_deckoviz_internal_by_job"),
    path("list/", ListView.as_view(), name="before_after_deckoviz_list"),
]