import django_filters
from .models import ImageInteraction, CollectionInteraction

class ImageInteractionFilter(django_filters.FilterSet):
    interaction_type = django_filters.CharFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = ImageInteraction
        fields = ['interaction_type', 'created_at']

class CollectionInteractionFilter(django_filters.FilterSet):
    interaction_type = django_filters.CharFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = CollectionInteraction
        fields = ['interaction_type', 'created_at']
