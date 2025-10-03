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
    
    