from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import BeforeAfter
from .serializers import BeforeAfterSerializer, BeforeAfterCreateSerializer


class InternalCreateView(APIView):
    """POST /api/before-after/internal/create/"""
    def post(self, request):
        serializer = BeforeAfterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data}, status=status.HTTP_201_CREATED)


class InternalDetailView(APIView):
    """GET/PATCH/DELETE /api/before-after/internal/{id}/"""
    def get_object(self, pk):
        return get_object_or_404(BeforeAfter, pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data})

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = BeforeAfterSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data})

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response({"success": True, "data": {"id": pk}}, status=status.HTTP_200_OK)


class GetByJobIdView(APIView):
    """GET /api/before-after/internal/by-job/?job_id=<job_id>"""
    def get(self, request):
        job_id = request.query_params.get("job_id")
        if not job_id:
            return Response({"success": False, "message": "job_id required"}, status=status.HTTP_400_BAD_REQUEST)
        obj = BeforeAfter.objects.filter(job_id=job_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        return Response({"success": True, "data": BeforeAfterSerializer(obj).data})


class ListView(APIView):
    """GET /api/before-after/list/?user_id=&transformation_type=&skip=&limit="""
    def get(self, request):
        user_id = request.query_params.get("user_id")
        transformation_type = request.query_params.get("transformation_type")
        try:
            skip = int(request.query_params.get("skip", 0))
        except Exception:
            skip = 0
        try:
            limit = int(request.query_params.get("limit", 20))
        except Exception:
            limit = 20

        qs = BeforeAfter.objects.all().order_by("-created_at")
        
        if user_id:
            # Query by both user_id (FK) and user_id as string
            qs = qs.filter(Q(user__id=user_id) | Q(user__username=user_id))
        
        if transformation_type:
            qs = qs.filter(transformation_type=transformation_type)

        total = qs.count()
        items = qs[skip: skip + limit]
        data = BeforeAfterSerializer(items, many=True).data
        return Response({"success": True, "data": {"before_afters": data, "total": total, "skip": skip, "limit": limit}})


class ChangeLogSaveView(APIView):
    """POST /api/before-after/internal/change-log/save/"""
    def post(self, request):
        job_id = request.data.get("job_id")
        change_log = request.data.get("change_log")
        s3_url = request.data.get("s3_url")
        s3_key = request.data.get("s3_key")

        if not job_id or change_log is None:
            return Response({"success": False, "message": "job_id and change_log required"}, status=status.HTTP_400_BAD_REQUEST)

        obj = BeforeAfter.objects.filter(job_id=job_id).first()
        if not obj:
            user_id = request.data.get("user_id")
            obj = BeforeAfter.objects.create(
                job_id=job_id,
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
            meta = obj.metadata or {}
            meta["change_log"] = change_log
            if s3_url:
                meta["change_log_s3_url"] = s3_url
                meta["change_log_s3_key"] = s3_key
            obj.metadata = meta
            obj.save()

        return Response({"success": True, "data": {"job_id": job_id}})


class ChangeLogGetView(APIView):
    """GET /api/before-after/internal/change-log/?job_id=<job_id>"""
    def get(self, request):
        job_id = request.query_params.get("job_id")
        if not job_id:
            return Response({"success": False, "message": "job_id required"}, status=status.HTTP_400_BAD_REQUEST)
        obj = BeforeAfter.objects.filter(job_id=job_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        data = {
            "job_id": job_id,
            "change_log": obj.metadata.get("change_log"),
            "change_log_s3_url": obj.metadata.get("change_log_s3_url"),
            "change_log_s3_key": obj.metadata.get("change_log_s3_key"),
        }
        return Response({"success": True, "data": data})