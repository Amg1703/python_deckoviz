from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import Sculpture, SculptureImage
from .serializers import (
    SculptureSerializer,
    CreateSculptureSerializer,
    UpdateSculptureSerializer,
    SculptureImageSerializer,
    SaveGeneratedImageSerializer,
)
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class InternalCreateView(APIView):
    """POST /api/sculptures/internal/create/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CreateSculptureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sculpture = serializer.save()
        
        return Response(
            {
                "success": True,
                "data": SculptureSerializer(sculpture).data
            },
            status=status.HTTP_201_CREATED
        )


class InternalGetView(APIView):
    """GET /api/sculptures/internal/?job_id=<job_id>"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        job_id = request.query_params.get("job_id")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {"success": True, "data": SculptureSerializer(sculpture).data},
            status=status.HTTP_200_OK
        )


class InternalUpdateView(APIView):
    """PATCH /api/sculptures/internal/update/"""
    permission_classes = [permissions.AllowAny]

    def patch(self, request):
        job_id = request.data.get("job_id")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UpdateSculptureSerializer(sculpture, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"success": True, "data": SculptureSerializer(sculpture).data},
            status=status.HTTP_200_OK
        )


class InternalDeleteView(APIView):
    """DELETE /api/sculptures/internal/delete/?job_id=<job_id>"""
    permission_classes = [permissions.AllowAny]

    def delete(self, request):
        job_id = request.query_params.get("job_id")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sculpture_id = sculpture.id
        sculpture.delete()
        
        return Response(
            {"success": True, "data": {"id": sculpture_id, "job_id": job_id}},
            status=status.HTTP_200_OK
        )


class SaveGeneratedImageView(APIView):
    """POST /api/sculptures/internal/images/save/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SaveGeneratedImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image = serializer.save()
        
        return Response(
            {
                "success": True,
                "data": SculptureImageSerializer(image).data
            },
            status=status.HTTP_201_CREATED
        )


class LinkAnglesToSculptureView(APIView):
    """PATCH /api/sculptures/internal/link-angles/"""
    permission_classes = [permissions.AllowAny]

    def patch(self, request):
        job_id = request.data.get("job_id")
        angles = request.data.get("angles", [])
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_images = []
        
        for angle_data in angles:
            image, _ = SculptureImage.objects.update_or_create(
                job_id=job_id,
                angle_number=angle_data.get("angle_number"),
                defaults={
                    "sculpture": sculpture,
                    "filename": angle_data.get("filename"),
                    "file_path": angle_data.get("path") or angle_data.get("file_path"),
                    "url": angle_data.get("s3_url") or angle_data.get("url"),
                    "s3_key": angle_data.get("s3_key"),
                }
            )
            created_images.append(SculptureImageSerializer(image).data)
        
        sculpture.status = "completed"
        sculpture.save()
        
        return Response(
            {"success": True, "data": created_images},
            status=status.HTTP_200_OK
        )


class ListUserSculpturesView(APIView):
    """GET /api/sculptures/list/?user_id=<user_id>&skip=<skip>&limit=<limit>"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user_id = request.query_params.get("user_id")
        
        try:
            skip = int(request.query_params.get("skip", 0))
        except (ValueError, TypeError):
            skip = 0
        
        try:
            limit = int(request.query_params.get("limit", 20))
        except (ValueError, TypeError):
            limit = 20
        
        if not user_id:
            return Response(
                {"success": False, "message": "user_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        qs = Sculpture.objects.filter(
            Q(user__id=user_id) | Q(user__username=user_id)
        ).order_by("-created_at")
        
        total = qs.count()
        items = qs[skip : skip + limit]
        
        data = SculptureSerializer(items, many=True).data
        
        return Response(
            {
                "success": True,
                "data": {
                    "sculptures": data,
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "count": len(data)
                }
            },
            status=status.HTTP_200_OK
        )


class SaveSculptureMetadataView(APIView):
    """POST /api/sculptures/internal/metadata/save/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        job_id = request.data.get("job_id")
        metadata = request.data.get("metadata", {})
        s3_url = request.data.get("s3_url")
        s3_key = request.data.get("s3_key")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sculpture.metadata = metadata
        if s3_url:
            sculpture.s3_url = s3_url
        if s3_key:
            sculpture.s3_key = s3_key
        sculpture.save()
        
        return Response(
            {"success": True, "data": SculptureSerializer(sculpture).data},
            status=status.HTTP_200_OK
        )


class GetSculptureMetadataView(APIView):
    """GET /api/sculptures/internal/metadata/?job_id=<job_id>"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        job_id = request.query_params.get("job_id")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "success": True,
                "data": {
                    "job_id": job_id,
                    "metadata": sculpture.metadata
                }
            },
            status=status.HTTP_200_OK
        )


class SubmitFeedbackView(APIView):
    """POST /api/sculptures/internal/feedback/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        job_id = request.data.get("job_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if rating and (rating < 1 or rating > 5):
            return Response(
                {"success": False, "message": "Rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sculpture.rating = rating
        sculpture.feedback_comment = comment
        sculpture.feedback_submitted_at = timezone.now()
        sculpture.save()
        
        return Response(
            {"success": True, "data": SculptureSerializer(sculpture).data},
            status=status.HTTP_200_OK
        )


class ShareSculptureView(APIView):
    """PATCH /api/sculptures/internal/share/"""
    permission_classes = [permissions.AllowAny]

    def patch(self, request):
        job_id = request.data.get("job_id")
        share = request.data.get("share", True)
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sculpture.share = share
        sculpture.is_shared = share
        sculpture.save()
        
        return Response(
            {"success": True, "data": SculptureSerializer(sculpture).data},
            status=status.HTTP_200_OK
        )


class GetPublicSculptureView(APIView):
    """GET /api/sculptures/public/?job_id=<job_id>"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        job_id = request.query_params.get("job_id")
        
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sculpture = Sculpture.objects.filter(job_id=job_id).first()
        
        if not sculpture:
            return Response(
                {"success": False, "message": "Sculpture not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not sculpture.share and not sculpture.is_shared:
            return Response(
                {"success": False, "message": "This sculpture is not shared"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(
            {"success": True, "data": SculptureSerializer(sculpture).data},
            status=status.HTTP_200_OK
        )