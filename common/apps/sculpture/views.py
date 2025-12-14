from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Sculpture, SculptureImage
from .serializers import (
    SculptureSerializer,
    CreateSculptureSerializer,
    SculptureImageSerializer,
    SaveGeneratedImageSerializer,
)
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class SculptureViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sculpture.objects.all()
    serializer_class = SculptureSerializer

    def get_queryset(self):
        return Sculpture.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated], url_path="link-angles")
    def link_angles(self, request, pk=None):
        sculpture = self.get_object()
        angles = request.data.get("angles", [])
        created = []
        for a in angles:
            s = SculptureImage.objects.create(
                sculpture=sculpture,
                job_id=sculpture.job_id,
                filename=a.get("filename"),
                file_path=a.get("path"),
                url=a.get("s3_url") or a.get("url"),
                s3_key=a.get("s3_key"),
                angle_number=a.get("angle_number"),
            )
            created.append(SculptureImageSerializer(s).data)
        sculpture.status = "completed"
        sculpture.total_iterations = sculpture.images.count() if hasattr(sculpture, "total_iterations") else sculpture.images.count()
        sculpture.save()
        return Response({"success": True, "data": created})

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="list")
    def list_user(self, request):
        qs = self.get_queryset().order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = SculptureSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SculptureSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class SculptureImageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SculptureImage.objects.all()
    serializer_class = SculptureImageSerializer

    def get_queryset(self):
        return SculptureImage.objects.filter(job_id__in=Sculpture.objects.filter(user=self.request.user).values_list("job_id", flat=True))


class SaveGeneratedImageAPIView(APIView):
    """
    Internal endpoint used by the AI service to save generated image metadata.
    Expects JSON with fields defined in SaveGeneratedImageSerializer.
    """
    permission_classes = [permissions.AllowAny]  # internal calls may not have auth token

    def post(self, request):
        serializer = SaveGeneratedImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # try to attach to existing sculpture
        sculpture = Sculpture.objects.filter(job_id=data["job_id"]).first()
        if not sculpture:
            # create a minimal sculpture record for linkage
            sculpture = Sculpture.objects.create(
                user=User.objects.filter(id=data["user_id"]).first(),
                job_id=data["job_id"],
                input_filename=data.get("file_path"),
                output_filename=data.get("filename"),
                status="created",
            )

        img = SculptureImage.objects.create(
            sculpture=sculpture,
            job_id=data["job_id"],
            filename=data["filename"],
            file_path=data.get("file_path"),
            url=data.get("url"),
            s3_key=data.get("s3_key"),
            mime_type=data.get("mime_type", "image/png"),
            width=data.get("width"),
            height=data.get("height"),
            angle_number=data.get("angle_number"),
        )

        return Response({"success": True, "data": SculptureImageSerializer(img).data}, status=status.HTTP_201_CREATED)