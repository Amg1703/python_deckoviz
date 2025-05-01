from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CreditPackageViewSet, UserCreditViewSet, 
    CreditTransactionViewSet, 
    CreditPricingViewSet, CreditPlanViewSet,
    UserSubscriptionViewSet
)

router = DefaultRouter()
router.register(r'packages', CreditPackageViewSet, basename='credit-packages')
router.register(r'accounts', UserCreditViewSet, basename='credit-accounts')
router.register(r'transactions', CreditTransactionViewSet, basename='credit-transactions')
router.register(r'pricing', CreditPricingViewSet, basename='credit-pricing')
router.register(r'plans', CreditPlanViewSet, basename='credit-plans')
router.register(r'subscriptions', UserSubscriptionViewSet, basename='user-subscriptions')

urlpatterns = [
    path('', include(router.urls)),
]
