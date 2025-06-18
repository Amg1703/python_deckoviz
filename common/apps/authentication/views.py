from rest_framework.views import APIView
from rest_framework.response import Response 
from .serializers import RegisterSerializer, UserSerializer,AddressSerializer,NewsLetterSubscriberSerializer
from rest_framework import mixins,viewsets,status,generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import get_user_model
from .models import Address,NewsLetterSubscriber
from apps.utils.google_sheet import GoogleSheet
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend
from django.shortcuts import redirect
from django.conf import settings

User = get_user_model()
_google_sheet = None

def get_google_sheet():
    global _google_sheet
    if _google_sheet is None:
        try:
            _google_sheet = GoogleSheet(sheet_name="Deckoviz-User-Waiting-List")
        except Exception as e:
            print(f"Warning: Failed to initialize Google Sheets client: {e}")
            _google_sheet = None
    return _google_sheet
    
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
        # Try to add to Google Sheet, but don't fail if it doesn't work
        google_sheet = get_google_sheet()
        if google_sheet:
            google_sheet.append_to_google_sheet(instance.name,instance.email)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Initiates the Google OAuth2 login process
        """
        strategy = load_strategy(request)
        try:
            # Specify the redirect URI explicitly
            redirect_uri = 'http://localhost:8000/auth/login/google/callback/'
            backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=redirect_uri)
        except MissingBackend:
            return Response({"error": "Google OAuth2 backend not configured"}, status=status.HTTP_400_BAD_REQUEST)
            
        auth_url = backend.auth_url()
        return Response({"auth_url": auth_url})

class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Handles the Google OAuth2 callback
        """
        code = request.GET.get('code')
        if not code:
            return Response({"error": "No authorization code provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        strategy = load_strategy(request)
        try:
            # Use the same redirect URI as in the login view
            redirect_uri = 'http://localhost:8000/auth/login/google/callback/'
            backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=redirect_uri)
        except MissingBackend:
            return Response({"error": "Google OAuth2 backend not configured"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Complete the authentication process
            user = backend.complete(request=request)
            
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Return tokens in response
            return Response({
                "access_token": access_token,
                "refresh_token": str(refresh),
                "user": UserSerializer(user).data
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    