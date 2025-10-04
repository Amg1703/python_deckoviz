from rest_framework import mixins,viewsets,generics 
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionView(
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
    ):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        return self.get_queryset().for_user(self.request.user)