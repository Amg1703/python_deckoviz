from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MetaAudio
from .serializers import MetaAudioSerializer, AddToLikedAudioSerializer, AddToStarredAudioSerializer
from apps.gallery.models import Audio
from django.contrib.auth import get_user_model

class MetaAudioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meta_audio, created = MetaAudio.objects.get_or_create(user=request.user)
        serializer = MetaAudioSerializer(meta_audio)
        return Response(serializer.data)

class AddToLikedAudioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToLikedAudioSerializer(data=request.data)
        if serializer.is_valid():
            audio_id = serializer.validated_data['audio_id']
            audio = Audio.objects.get(id=audio_id)
            meta_audio, created = MetaAudio.objects.get_or_create(user=request.user)
            if audio.view == 'public' or audio.uploaded_by == request.user:
                meta_audio.liked_audios.add(audio)
                return Response({'status': 'audio added to liked'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to like this audio'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromLikedAudioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToLikedAudioSerializer(data=request.data)
        if serializer.is_valid():
            audio_id = serializer.validated_data['audio_id']
            audio = Audio.objects.get(id=audio_id)
            meta_audio, created = MetaAudio.objects.get_or_create(user=request.user)
            meta_audio.liked_audios.remove(audio)
            return Response({'status': 'audio removed from liked'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddToStarredAudioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToStarredAudioSerializer(data=request.data)
        if serializer.is_valid():
            audio_id = serializer.validated_data['audio_id']
            audio = Audio.objects.get(id=audio_id)
            meta_audio, created = MetaAudio.objects.get_or_create(user=request.user)
            if audio.view == 'public' or audio.uploaded_by == request.user:
                meta_audio.starred_audios.add(audio)
                return Response({'status': 'audio added to starred'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'You do not have permission to star this audio'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoveFromStarredAudioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToStarredAudioSerializer(data=request.data)
        if serializer.is_valid():
            audio_id = serializer.validated_data['audio_id']
            audio = Audio.objects.get(id=audio_id)
            meta_audio, created = MetaAudio.objects.get_or_create(user=request.user)
            meta_audio.starred_audios.remove(audio)
            return Response({'status': 'audio removed from starred'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 