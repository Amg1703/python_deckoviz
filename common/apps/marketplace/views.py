from rest_framework import viewsets,mixins,generics
from .models import Price
from .serializers import PriceSerializer



class PriceViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    def get_queryset(self):
        return self.get_queryset().for_user(self.request.user)

# --- ProductViewSet ---
from .models import Product, Cart, Order, Coupon
from .serializers import ProductSerializer, CartSerializer, OrderSerializer, CouponSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    