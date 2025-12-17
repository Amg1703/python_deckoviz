from django.urls import path
from .views import (
    InternalCreateView,
    InternalGetView,
    InternalUpdateView,
    InternalDeleteView,
    SaveGeneratedImageView,
    LinkAnglesToSculptureView,
    ListUserSculpturesView,
    SaveSculptureMetadataView,
    GetSculptureMetadataView,
    SubmitFeedbackView,
    ShareSculptureView,
    GetPublicSculptureView,
)

urlpatterns = [
    # Internal endpoints (used by FastAPI backend)
    path("internal/create/", InternalCreateView.as_view(), name="sculpture_internal_create"),
    path("internal/", InternalGetView.as_view(), name="sculpture_internal_get"),
    path("internal/update/", InternalUpdateView.as_view(), name="sculpture_internal_update"),
    path("internal/delete/", InternalDeleteView.as_view(), name="sculpture_internal_delete"),
    
    # Images
    path("internal/images/save/", SaveGeneratedImageView.as_view(), name="sculpture_save_image"),
    path("internal/link-angles/", LinkAnglesToSculptureView.as_view(), name="sculpture_link_angles"),
    
    # Metadata
    path("internal/metadata/save/", SaveSculptureMetadataView.as_view(), name="sculpture_save_metadata"),
    path("internal/metadata/", GetSculptureMetadataView.as_view(), name="sculpture_get_metadata"),
    
    # User operations
    path("list/", ListUserSculpturesView.as_view(), name="sculpture_list"),
    
    # Feedback & sharing
    path("internal/feedback/", SubmitFeedbackView.as_view(), name="sculpture_feedback"),
    path("internal/share/", ShareSculptureView.as_view(), name="sculpture_share"),
    path("public/", GetPublicSculptureView.as_view(), name="sculpture_public"),
]