from rest_framework import viewsets,mixins,generics
from .models import Order
from .serializers import OrderSerializer,OrderCreateSerializer


class OrderView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
): 
    
    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return OrderCreateSerializer
        return OrderSerializer   
    
    def get_queryset(self):
        return Order.objects.for_user(user=self.request.user)
