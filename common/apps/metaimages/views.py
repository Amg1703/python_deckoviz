from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MetaImage
from .serializers import MetaImageSerializer, AddToLikedSerializer, AddToStarredSerializer
from apps.gallery.models import Image
from django.contrib.auth import get_user_model

class MetaImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meta_image, created = MetaImage.objects.get_or_create(user=request.user)
        serializer = MetaImageSerializer(meta_image)
        return Response(serializer.data)

class AddToLikedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToLikedSerializer(data=request.data)
        if serializer.is_valid():
            image_id = serializer.validated_data['image_id']
            image = Image.objects.get(id=image_id)
            meta_image, created = MetaImage.objects.get_or_create(user=request.user)
            if image.view == 'public' or image.uploaded_by == request.user:
                meta_image.liked_images.add(image)
                return Response({'status': 'image added to liked'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to like this image'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromLikedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToLikedSerializer(data=request.data)
        if serializer.is_valid():
            image_id = serializer.validated_data['image_id']
            image = Image.objects.get(id=image_id)
            meta_image, created = MetaImage.objects.get_or_create(user=request.user)
            meta_image.liked_images.remove(image)
            return Response({'status': 'image removed from liked'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddToStarredView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToStarredSerializer(data=request.data)
        if serializer.is_valid():
            image_id = serializer.validated_data['image_id']
            image = Image.objects.get(id=image_id)
            meta_image, created = MetaImage.objects.get_or_create(user=request.user)
            if image.view == 'public' or image.uploaded_by == request.user:
                meta_image.starred_images.add(image)
                return Response({'status': 'image added to starred'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to star this image'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromStarredView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToStarredSerializer(data=request.data)
        if serializer.is_valid():
            image_id = serializer.validated_data['image_id']
            image = Image.objects.get(id=image_id)
            meta_image, created = MetaImage.objects.get_or_create(user=request.user)
            meta_image.starred_images.remove(image)
            return Response({'status': 'image removed from starred'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 