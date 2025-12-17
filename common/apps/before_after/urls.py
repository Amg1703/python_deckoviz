from django.urls import path

from .views import (
    InternalCreateView,
    InternalDetailView,
    GetBySessionIdView,
    GetByJobIdView,
    ListByUserView,
    ChangeLogSaveView,
    ChangeLogGetView,
    PlacementMetadataSaveView,
    PlacementMetadataGetView,
)

urlpatterns = [
    # Create
    path("internal/create/", InternalCreateView.as_view(), name="before_after_internal_create"),
    
    # Retrieve/Update/Delete
    path("internal/<int:pk>/", InternalDetailView.as_view(), name="before_after_internal_detail"),
    
    # Query by session_id or job_id
    path("internal/by-session/", GetBySessionIdView.as_view(), name="before_after_internal_by_session"),
    path("internal/by-job/", GetByJobIdView.as_view(), name="before_after_internal_by_job"),
    
    # List
    path("list/", ListByUserView.as_view(), name="before_after_list"),
    
    # Change Log
    path("internal/change-log/save/", ChangeLogSaveView.as_view(), name="before_after_change_log_save"),
    path("internal/change-log/", ChangeLogGetView.as_view(), name="before_after_change_log_get"),
    
    # Placement Metadata
    path("internal/placement-metadata/save/", PlacementMetadataSaveView.as_view(), name="before_after_placement_metadata_save"),
    path("internal/placement-metadata/", PlacementMetadataGetView.as_view(), name="before_after_placement_metadata_get"),
]