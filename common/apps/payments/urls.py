from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CreateCouponView, CreatePromotionCodeView, CreateCheckoutSessionView,
    DeletePromotionCodeView, ListCouponsView, ListPromotionCodesView,
    TransactionView
)

router = DefaultRouter()

router.register('transactions', TransactionView,basename='transactions')
 
urlpatterns = [
    path('', include(router.urls)),
    path('create-coupon/', CreateCouponView.as_view(), name='create_coupon'),
    path('create-promotion-code/', CreatePromotionCodeView.as_view(), name='create_promotion_code'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('delete-promotion-code/<str:code>/', DeletePromotionCodeView.as_view(), name='delete_promotion_code'),
    path('list-coupons/', ListCouponsView.as_view(), name='list_coupons'),
    path('list-promotion-codes/', ListPromotionCodesView.as_view(), name='list_promotion_codes'),

]
