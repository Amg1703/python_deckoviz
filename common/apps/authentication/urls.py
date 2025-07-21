from django.urls import path,include 
from rest_framework.routers import DefaultRouter 
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import  RegisterView,UserView,AddressView,NewsLetterSubscriberView,GoogleLoginView,GoogleCallbackView,UserProfileViewSet, ForgotPasswordView, ResetPasswordView, VerifyEmailView, ResendVerificationView, MyTokenObtainPairView

router = DefaultRouter()
router.register('user', UserView, basename='user_profile')
router.register('address', AddressView, basename='address')
router.register('user-profile', UserProfileViewSet, basename='user_profile_info')

urlpatterns = [
    path('',include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('newsletter/', NewsLetterSubscriberView.as_view(),name='newsletter'),
    
    # Google OAuth2 URLs
    path('login/google/', GoogleLoginView.as_view(), name='google_login'),
    path('login/google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
]
