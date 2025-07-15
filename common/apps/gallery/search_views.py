from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Image, Collection
from .serializers import ImageSearchSerializer, CollectionSearchSerializer, CollectionSearchInputSerializer
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
            queryset = Image.objects.filter(uploaded_by=user, metadata__isnull=False, is_active=True)
        else:  # global
            queryset = Image.objects.filter(view='public', metadata__isnull=False, is_active=True)

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
            queryset = Collection.objects.filter(user=user, metadata__isnull=False, is_active=True)
        else:  # global
            queryset = Collection.objects.filter(view='public', metadata__isnull=False, is_active=True)

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