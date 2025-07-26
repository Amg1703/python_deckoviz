from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Image, Collection, Audio
from .serializers import ImageSearchSerializer, CollectionSearchSerializer, CollectionSearchInputSerializer, AudioSerializer, AudioSearchInputSerializer
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
from collections import Counter
from drf_spectacular.utils import extend_schema

class ImageSearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# Utility for extracting keywords from text
STOPWORDS = set([
    'a', 'an', 'the', 'in', 'on', 'at', 'is', 'it', 'and', 'or', 'of', 'to', 'for', 'with', 'by', 'as', 'from', 'that', 'this', 'these', 'those', 'be', 'are', 'was', 'were', 'has', 'have', 'had', 'but', 'not', 'so', 'if', 'then', 'than', 'which', 'who', 'whom', 'whose', 'can', 'will', 'would', 'should', 'could', 'may', 'might', 'do', 'does', 'did', 'into', 'out', 'about', 'over', 'under', 'again', 'further', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'too', 'very', 's', 't', 'just', 'don', 'now'
])
def extract_keywords(text):
    # Lowercase, remove non-alphanumeric, split, remove stopwords
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

class ImageSearchView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ImageSearchPagination

    def post(self, request):
        data = request.data
        search_text = data.get('search_text', '')
        moods = set([m.lower() for m in data.get('moods', [])])
        tags = set([t.lower() for t in data.get('tags', [])])
        search_type = data.get('search_type', 'global')
        user = request.user

        keywords = extract_keywords(search_text)

        # Build base queryset
        if search_type == 'private':
            queryset = Image.objects.filter(
                uploaded_by=user, metadata__isnull=False, is_active=True
            ).select_related('uploaded_by')
        else:  # global
            queryset = Image.objects.filter(
                view='public', metadata__isnull=False, is_active=True
            ).select_related('uploaded_by')

        results = []
        for img in queryset:
            meta = img.metadata or {}
            score = 0
            # Score moods
            img_moods = set([m.lower() for m in meta.get('mood_tags', [])])
            mood_matches = moods & img_moods
            score += 15 * len(mood_matches)
            # Score tags
            img_tags = set([t.lower() for t in meta.get('tags', [])])
            tag_matches = tags & img_tags
            score += 10 * len(tag_matches)
            # Score title
            title = meta.get('title', '').lower()
            for kw in keywords:
                if kw in title:
                    score += 5
            # Score description
            desc = meta.get('description', '').lower()
            for kw in keywords:
                if kw in desc:
                    score += 2
            # Also check tags and moods for keywords
            for kw in keywords:
                if kw in img_tags:
                    score += 5
                if kw in img_moods:
                    score += 5
            if score > 0 or (not keywords and not moods and not tags):
                results.append((score, img))
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        images = [img for score, img in results]
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(images, request)
        serializer = ImageSearchSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class CollectionSearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CollectionSearchView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CollectionSearchPagination

    @extend_schema(
        request=CollectionSearchInputSerializer,
        responses=CollectionSearchSerializer(many=True),
        description="Search collections by metadata, tags, moods, and keywords. "
                    "Use 'search_type' to specify user/private or public/global search. "
                    "All fields except 'search_type' are optional. 'search_type' defaults to 'global' if not provided."
    )
    def post(self, request):
        data = request.data
        search_text = data.get('search_text', '')
        moods = set([m.lower() for m in data.get('moods', [])])
        tags = set([t.lower() for t in data.get('tags', [])])
        search_type = data.get('search_type', 'global')
        user = request.user

        keywords = extract_keywords(search_text)

        # Build base queryset
        if search_type == 'private':
            queryset = Collection.objects.filter(
                user=user, metadata__isnull=False, is_active=True
            ).prefetch_related('collection_images__image__uploaded_by')
        else:  # global
            queryset = Collection.objects.filter(
                view='public', metadata__isnull=False, is_active=True
            ).prefetch_related('collection_images__image__uploaded_by')

        results = []
        for col in queryset:
            meta = col.metadata or {}
            score = 0
            # Score moods
            col_moods = set([m.lower() for m in (meta.get('mood_tags') or [])])
            mood_matches = moods & col_moods
            score += 15 * len(mood_matches)
            # Score tags
            col_tags = set([t.lower() for t in (meta.get('tags') or [])])
            tag_matches = tags & col_tags
            score += 10 * len(tag_matches)
            # Score name
            name = (col.name or '').lower()
            for kw in keywords:
                if kw in name:
                    score += 5
            # Score description
            desc = (col.description or '').lower()
            for kw in keywords:
                if kw in desc:
                    score += 2
            # Also check tags and moods for keywords
            for kw in keywords:
                if kw in col_tags:
                    score += 5
                if kw in col_moods:
                    score += 5
            if score > 0 or (not keywords and not moods and not tags):
                results.append((score, col))
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        collections = [col for score, col in results]
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(collections, request)
        serializer = CollectionSearchSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AudioSearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AudioSearchView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = AudioSearchPagination

    @extend_schema(
        request=AudioSearchInputSerializer,
        responses=AudioSerializer(many=True),
        description="Search audios by track title, description, genre, and transcript content. "
                    "Returns paginated results ranked by relevance score.",
        summary="Search Audio Files",
        tags=["Audio Search"],
        examples=[
            {
                "name": "Search Public Audios",
                "description": "Search for jazz music in public audios",
                "value": {
                    "search_text": "jazz music",
                    "search_type": "global"
                }
            },
            {
                "name": "Search Private Audios",
                "description": "Search user's own uploaded audios",
                "value": {
                    "search_text": "my recording",
                    "search_type": "private"
                }
            }
        ]
    )
    def post(self, request):
        serializer = AudioSearchInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        search_text = serializer.validated_data['search_text']
        search_type = serializer.validated_data.get('search_type', 'global')
        user = request.user

        keywords = extract_keywords(search_text)

        # Build base queryset
        if search_type == 'private':
            queryset = Audio.objects.filter(
                uploaded_by=user, is_active=True
            ).select_related('uploaded_by')
        else:  # global (public)
            queryset = Audio.objects.filter(
                view='public', is_active=True
            ).select_related('uploaded_by')

        results = []
        for audio in queryset:
            score = 0
            
            # Score track title (highest priority)
            track_title = (audio.track_title or '').lower()
            for keyword in keywords:
                if keyword in track_title:
                    score += 10
            
            # Score genre
            genre = (audio.genre or '').lower()
            for keyword in keywords:
                if keyword in genre:
                    score += 8
            
            # Score description
            description = (audio.description or '').lower()
            for keyword in keywords:
                if keyword in description:
                    score += 5
            
            # Score transcript content
            transcript = (audio.transcript or '').lower()
            for keyword in keywords:
                if keyword in transcript:
                    score += 3
            
            # Score transcript summary
            transcript_summary = (audio.transcript_summary or '').lower()
            for keyword in keywords:
                if keyword in transcript_summary:
                    score += 4
            
            # Include all results if no specific keywords or if there's a match
            if score > 0 or not keywords:
                results.append((score, audio))

        # Sort by score descending, then by creation date
        results.sort(key=lambda x: (x[0], x[1].created_at), reverse=True)
        audios = [audio for score, audio in results]

        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(audios, request)
        serializer = AudioSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data) 