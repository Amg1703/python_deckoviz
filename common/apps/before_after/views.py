from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import BeforeAfter
from .serializers import BeforeAfterSerializer, BeforeAfterCreateSerializer, BeforeAfterUpdateSerializer


@method_decorator(csrf_exempt, name='dispatch')
class InternalCreateView(APIView):
    """POST /api/before-after/internal/create/"""
    def post(self, request):
        serializer = BeforeAfterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(
            {"success": True, "data": BeforeAfterSerializer(obj).data},
            status=status.HTTP_201_CREATED
        )


class InternalDetailView(APIView):
    """GET/PATCH/DELETE /api/before-after/internal/<int:pk>/"""
    def get_object(self, pk):
        return get_object_or_404(BeforeAfter, pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data})

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = BeforeAfterUpdateSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data})

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response({"success": True, "data": {"id": pk}}, status=status.HTTP_200_OK)


class GetBySessionIdView(APIView):
    """GET /api/before-after/internal/by-session/?session_id=<session_id>"""
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj = BeforeAfter.objects.filter(session_id=session_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data})


class GetByJobIdView(APIView):
    """GET /api/before-after/internal/by-job/?job_id=<job_id>"""
    def get(self, request):
        job_id = request.query_params.get("job_id")
        if not job_id:
            return Response(
                {"success": False, "message": "job_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj = BeforeAfter.objects.filter(job_id=job_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data})


class ListByUserView(APIView):
    """GET /api/before-after/list/?user_id=<user_id>&transformation_type=<type>&skip=<skip>&limit=<limit>"""
    def get(self, request):
        user_id = request.query_params.get("user_id")
        transformation_type = request.query_params.get("transformation_type")
        
        try:
            skip = int(request.query_params.get("skip", 0))
        except (ValueError, TypeError):
            skip = 0
        
        try:
            limit = int(request.query_params.get("limit", 20))
        except (ValueError, TypeError):
            limit = 20

        qs = BeforeAfter.objects.all().order_by("-created_at")
        
        if user_id:
            qs = qs.filter(Q(user__id=user_id) | Q(user__username=user_id))
        
        if transformation_type:
            qs = qs.filter(transformation_type=transformation_type)

        total = qs.count()
        items = qs[skip : skip + limit]
        data = BeforeAfterSerializer(items, many=True).data
        
        return Response({
            "success": True,
            "data": {
                "items": data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        })


class ChangeLogSaveView(APIView):
    """POST /api/before-after/internal/change-log/save/"""
    def post(self, request):
        session_id = request.data.get("session_id")
        change_log = request.data.get("change_log")
        s3_url = request.data.get("s3_url")
        s3_key = request.data.get("s3_key")

        if not session_id or change_log is None:
            return Response(
                {"success": False, "message": "session_id and change_log required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = BeforeAfter.objects.filter(session_id=session_id).first()
        if not obj:
            user_id = request.data.get("user_id")
            obj = BeforeAfter.objects.create(
                session_id=session_id,
                change_log_path=request.data.get("change_log_path"),
                status="completed",
                metadata={"change_log": change_log}
            )
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                    obj.user = user
                    obj.save()
                except User.DoesNotExist:
                    pass
        else:
            obj.change_log_path = request.data.get("change_log_path", obj.change_log_path)
            obj.change_log_s3_url = s3_url
            obj.change_log_s3_key = s3_key
            meta = obj.metadata or {}
            meta["change_log"] = change_log
            obj.metadata = meta
            obj.save()

        return Response({"success": True, "data": {"session_id": session_id}})


class ChangeLogGetView(APIView):
    """GET /api/before-after/internal/change-log/?session_id=<session_id>"""
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        obj = BeforeAfter.objects.filter(session_id=session_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        
        data = {
            "session_id": session_id,
            "change_log": obj.metadata.get("change_log") if obj.metadata else None,
            "change_log_path": obj.change_log_path,
            "change_log_s3_url": obj.change_log_s3_url,
            "change_log_s3_key": obj.change_log_s3_key,
        }
        return Response({"success": True, "data": data})


class PlacementMetadataSaveView(APIView):
    """POST /api/before-after/internal/placement-metadata/save/"""
    def post(self, request):
        session_id = request.data.get("session_id")
        placement_metadata = request.data.get("placement_metadata")
        s3_url = request.data.get("s3_url")
        s3_key = request.data.get("s3_key")

        if not session_id or placement_metadata is None:
            return Response(
                {"success": False, "message": "session_id and placement_metadata required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = BeforeAfter.objects.filter(session_id=session_id).first()
        if not obj:
            user_id = request.data.get("user_id")
            obj = BeforeAfter.objects.create(
                session_id=session_id,
                transformation_type="deckoviz_placement",
                metadata_path=request.data.get("metadata_path"),
                status="completed",
                metadata=placement_metadata
            )
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                    obj.user = user
                    obj.save()
                except User.DoesNotExist:
                    pass
        else:
            obj.metadata_path = request.data.get("metadata_path", obj.metadata_path)
            obj.metadata_s3_url = s3_url
            obj.metadata_s3_key = s3_key
            obj.metadata = placement_metadata
            obj.save()

        return Response({"success": True, "data": {"session_id": session_id}})


class PlacementMetadataGetView(APIView):
    """GET /api/before-after/internal/placement-metadata/?session_id=<session_id>"""
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        obj = BeforeAfter.objects.filter(session_id=session_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        
        data = {
            "session_id": session_id,
            "placement_metadata": obj.metadata,
            "metadata_path": obj.metadata_path,
            "metadata_s3_url": obj.metadata_s3_url,
            "metadata_s3_key": obj.metadata_s3_key,
        }
        return Response({"success": True, "data": data})