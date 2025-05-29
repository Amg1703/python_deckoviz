from rest_framework import viewsets,mixins,generics
from .models import Order,OrderDetail
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer,OrderCreateSerializer,OrderDetailSerializer


class OrderView(
    mixins.CreateModelMixin, 
    viewsets.GenericViewSet,
): 
    permission_classes = [IsAuthenticated]
    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return OrderCreateSerializer
        return OrderSerializer   
    
    def get_queryset(self):
        return Order.objects.for_user(user=self.request.user)


class OrderDetailView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
): 
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OrderDetail.objects.filter(order__user=self.request.user)
