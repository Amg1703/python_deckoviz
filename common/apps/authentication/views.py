from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import status 
from .serializers import RegisterSerializer, UserSerializer,AddressSerializer
from rest_framework import mixins,viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
class UserView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(id=self.request.user.id)
    
class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # use manager directly since QuerySet lacks for_user
        return Address.objects.for_user(self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)