from rest_framework.views import APIView
from rest_framework.response import Response 
from .serializers import RegisterSerializer, UserSerializer,AddressSerializer,NewsLetterSubscriberSerializer
from rest_framework import mixins,viewsets,status,generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import get_user_model
from .models import Address,NewsLetterSubscriber
from apps.utils.google_sheet import GoogleSheet

User = get_user_model()
google_sheet = GoogleSheet(sheet_name="Deckoviz-User-Waiting-List")

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


class NewsLetterSubscriberView(generics.CreateAPIView):
    queryset = NewsLetterSubscriber.objects.all()
    serializer_class = NewsLetterSubscriberSerializer
    permission_classes = [AllowAny]
 
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
        
    def perform_create(self,serializer):
        instance = serializer.save()
        google_sheet.append_to_google_sheet(instance.name,instance.email)
    