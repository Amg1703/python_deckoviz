from rest_framework import viewsets,mixins,generics
from .models import Order
from .serializers import OrderSerializer,OrderCreateSerializer


class OrderView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return OrderCreateSerializer
        return OrderSerializer   
    
    def get_queryset(self):
        return self.get_queryset().for_user(self.request.user)
