from django.urls import path

from .views import (
    InternalCreateView,
    InternalDetailView,
    GetByJobIdView,
    ListView,
    ChangeLogSaveView,
    ChangeLogGetView,
)

urlpatterns = [
    path("internal/create/", InternalCreateView.as_view(), name="before_after_internal_create"),
    path("internal/<int:pk>/", InternalDetailView.as_view(), name="before_after_internal_detail"),
    path("internal/by-job/", GetByJobIdView.as_view(), name="before_after_internal_by_job"),
    path("list/", ListView.as_view(), name="before_after_list"),
    path("internal/change-log/save/", ChangeLogSaveView.as_view(), name="before_after_change_log_save"),
    path("internal/change-log/", ChangeLogGetView.as_view(), name="before_after_change_log_get"),
]