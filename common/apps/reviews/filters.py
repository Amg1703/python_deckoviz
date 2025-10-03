import django_filters as filters
from .models import Review

class ReviewFilter(filters.FilterSet):
    order_dtl = filters.CharFilter(field_name="order_dtl",lookup_expr="exact")
    booking_dtl = filters.CharFilter(field_name="booking_dtl",lookup_expr="exact")
    product = filters.CharFilter(field_name="order_dtl__sku__product",lookup_expr="exact")
    service = filters.CharFilter(field_name="booking_dtl__service",lookup_expr="exact")

    class Meta:
        model = Review
        fields = [
            "order_dtl",
            "booking_dtl",
            "product",
            "service",
        ]
