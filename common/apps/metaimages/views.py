from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MetaImage, SharedImage
from .serializers import MetaImageSerializer, AddToLikedSerializer, AddToStarredSerializer, ShareImageSerializer
from apps.gallery.models import Image
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(
    responses={200: MetaImageSerializer},
    description="Retrieve the current user's MetaImage object, including liked, starred, and shared images. Creates one if it does not exist."
)
class MetaImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meta_image, created = MetaImage.objects.prefetch_related(
            'liked_images__uploaded_by',
            'starred_images__uploaded_by'
        ).get_or_create(user=request.user)
        serializer = MetaImageSerializer(meta_image)
        return Response(serializer.data)

@extend_schema(
    request=AddToLikedSerializer,
    responses={200: OpenApiResponse(description='Image added to liked.'), 403: OpenApiResponse(description='Permission denied.'), 400: OpenApiResponse(description='Invalid input.')},
    description="Add an image to the user's liked images. Only public or self-owned images can be liked."
)
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

@extend_schema(
    request=AddToLikedSerializer,
    responses={200: OpenApiResponse(description='Image removed from liked.'), 400: OpenApiResponse(description='Invalid input.')},
    description="Remove an image from the user's liked images."
)
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

@extend_schema(
    request=AddToStarredSerializer,
    responses={200: OpenApiResponse(description='Image added to starred.'), 403: OpenApiResponse(description='Permission denied.'), 400: OpenApiResponse(description='Invalid input.')},
    description="Add an image to the user's starred images. Only public or self-owned images can be starred."
)
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

@extend_schema(
    request=AddToStarredSerializer,
    responses={200: OpenApiResponse(description='Image removed from starred.'), 400: OpenApiResponse(description='Invalid input.')},
    description="Remove an image from the user's starred images."
)
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

@extend_schema(
    request=ShareImageSerializer,
    responses={200: OpenApiResponse(description='Image shared with user.'), 403: OpenApiResponse(description='Only the owner can share this image.'), 400: OpenApiResponse(description='Invalid input.')},
    description="Share an image with another user by email. Only the owner can share."
)
class ShareImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShareImageSerializer(data=request.data)
        if serializer.is_valid():
            image_id = serializer.validated_data['image_id']
            email = serializer.validated_data['email']
            User = get_user_model()
            image = Image.objects.get(id=image_id)
            user_to_share = User.objects.get(email=email)
            # Only owner can share
            if image.uploaded_by != request.user:
                return Response({'error': 'Only the owner can share this image.'}, status=status.HTTP_403_FORBIDDEN)
            SharedImage.objects.get_or_create(image=image, owner=request.user, shared_with=user_to_share)
            return Response({'status': f'Image shared with {email}'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=ShareImageSerializer,
    responses={200: OpenApiResponse(description='User removed from shared image.'), 403: OpenApiResponse(description='Only the owner can remove shared users.'), 400: OpenApiResponse(description='Invalid input.')},
    description="Remove a user from a shared image. Only the owner can remove."
)
class RemoveSharedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShareImageSerializer(data=request.data)
        if serializer.is_valid():
            image_id = serializer.validated_data['image_id']
            email = serializer.validated_data['email']
            User = get_user_model()
            image = Image.objects.get(id=image_id)
            user_to_remove = User.objects.get(email=email)
            # Only owner can remove
            if image.uploaded_by != request.user:
                return Response({'error': 'Only the owner can remove shared users.'}, status=status.HTTP_403_FORBIDDEN)
            SharedImage.objects.filter(image=image, owner=request.user, shared_with=user_to_remove).delete()
            return Response({'status': f'User {email} removed from shared image'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    responses={200: OpenApiResponse(description='List of images shared by the current user.')},
    description="Get all images that the current user has shared with others, including sharing details."
)
class MySharedImagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shared_by_me = SharedImage.objects.filter(owner=request.user).select_related('image', 'shared_with')
        
        # Group by image and include sharing details
        shared_data = []
        for share in shared_by_me:
            from apps.gallery.serializers import ImageSerializer
            image_data = ImageSerializer(share.image).data
            # Add sharing metadata
            image_data['shared_with_email'] = share.shared_with.email
            image_data['shared_with_username'] = share.shared_with.username
            image_data['shared_at'] = share.shared_at
            shared_data.append(image_data)
        
        return Response({
            'images_shared_by_me': shared_data,
            'total_count': len(shared_data)
        }) 