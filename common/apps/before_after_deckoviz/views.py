from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import DeckovizComparison
from .serializers import DeckovizComparisonSerializer, DeckovizCreateSerializer


class InternalCreateView(APIView):
    """POST /api/before-after-deckoviz/internal/create/"""
    def post(self, request):
        serializer = DeckovizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response({"success": True, "data": DeckovizComparisonSerializer(obj).data}, status=status.HTTP_201_CREATED)


class InternalDetailView(APIView):
    """GET/PATCH/DELETE /api/before-after-deckoviz/internal/{id}/"""
    def get_object(self, pk):
        return get_object_or_404(DeckovizComparison, pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        return Response({"success": True, "data": DeckovizComparisonSerializer(obj).data})

    def patch(self, request, pk):
        obj = self.get_object(pk)
        serializer = DeckovizComparisonSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data})

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response({"success": True, "data": {"id": pk}}, status=status.HTTP_200_OK)


class GetByJobIdView(APIView):
    """GET /api/before-after-deckoviz/internal/by-job/?job_id=<job_id>"""
    def get(self, request):
        job_id = request.query_params.get("job_id")
        if not job_id:
            return Response({"success": False, "message": "job_id required"}, status=status.HTTP_400_BAD_REQUEST)
        obj = DeckovizComparison.objects.filter(job_id=job_id).first()
        if not obj:
            return Response({"success": True, "data": None})
        return Response({"success": True, "data": DeckovizComparisonSerializer(obj).data})


class ListView(APIView):
    """GET /api/before-after-deckoviz/list/?user_id=&skip=&limit="""
    def get(self, request):
        user_id = request.query_params.get("user_id")
        try:
            skip = int(request.query_params.get("skip", 0))
        except Exception:
            skip = 0
        try:
            limit = int(request.query_params.get("limit", 20))
        except Exception:
            limit = 20

        qs = DeckovizComparison.objects.all().order_by("-created_at")
        
        if user_id:
            # Query by both user_id (FK) and user_id as string
            qs = qs.filter(Q(user__id=user_id) | Q(user__username=user_id))

        total = qs.count()
        items = qs[skip: skip + limit]
        data = DeckovizComparisonSerializer(items, many=True).data
        return Response({"success": True, "data": {"comparisons": data, "total": total, "skip": skip, "limit": limit}})