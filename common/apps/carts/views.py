from rest_framework.viewsets import ModelViewSet
from .models import Cart
from .serializers import CartSerializer,CartCreateSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.db.models import F, Sum

class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['POST','PUT','PATCH']:
            print("Using CartCreateSerializer")
            return CartCreateSerializer
        return CartSerializer

    def get_queryset(self):
        user = self.request.user
        cart_items = self.queryset.filter(user=user)
        # Return just the queryset, let DRF handle the serialization
        return cart_items

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        total_price = queryset.aggregate(
            total=Sum(F('quantity') * F('price__final_price'))
        )['total'] or 0

        return JsonResponse({
            'items': serializer.data,
            'total_price': str(total_price)
        })
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


        