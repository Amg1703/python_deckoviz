from rest_framework import mixins,viewsets,generics 
from .models import Transaction
from .serializers import TransactionSerializer, CreateCouponSerializer, CreatePromotionCodeSerializer, CreateCheckoutSerializer
import stripe
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, APIException
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class TransactionView(
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
    ):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        return self.get_queryset().for_user(self.request.user)

class CreateCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateCouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        params = {"duration": data['duration']}
        if data.get('percent_off'):
            params["percent_off"] = data['percent_off']
        elif data.get('amount_off'):
            params["amount_off"] = data['amount_off']
            params["currency"] = data['currency']
        if data.get('duration_in_months') and data['duration'] == 'repeating':
            params["duration_in_months"] = data['duration_in_months']
        if data.get('name'):
            params["name"] = data['name']

        try:
            coupon = stripe.Coupon.create(**params)
            return Response({"coupon": coupon}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            raise APIException(str(e))

class CreatePromotionCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePromotionCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        coupon_id = data['coupon_id']
        if coupon_id.startswith("coupon_"):
            coupon_id = coupon_id.replace("coupon_", "")

        params = {
            "promotion": {"type": "coupon", "coupon": coupon_id},
            "active": data['active']
        }
        if data.get('code'):
            params["code"] = data['code']

        try:
            promo = stripe.PromotionCode.create(**params)
            return Response({"promotion_code": promo}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            raise APIException(str(e))

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        line_item = {"price": data['price_id'], "quantity": data['quantity']}
        checkout_params = {
            "mode": data['mode'],
            "line_items": [line_item],
            "success_url": data['success_url'],
            "cancel_url": data['cancel_url'],
        }

        if data.get('promotion_code_id'):
            checkout_params["discounts"] = [{"promotion_code": data['promotion_code_id']}]
        elif data.get('allow_promotion_codes'):
            checkout_params["allow_promotion_codes"] = True

        try:
            session = stripe.checkout.Session.create(**checkout_params)
            return Response({"checkout_session_id": session.id, "checkout_url": session.url}, status=status.HTTP_201_CREATED)
        except stripe.error.StripeError as e:
            raise APIException(str(e))

class DeletePromotionCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, code):
        try:
            promotion_codes = stripe.PromotionCode.list(code=code, limit=1)
            if not promotion_codes.data:
                return Response({"detail": f"Promotion code '{code}' not found"}, status=status.HTTP_404_NOT_FOUND)
            promo_code = promotion_codes.data[0]
            updated_promo = stripe.PromotionCode.modify(promo_code.id, active=False)
            return Response({"message": f"Promotion code '{code}' deactivated", "promotion_code": updated_promo})
        except stripe.error.StripeError as e:
            raise APIException(str(e))

class ListCouponsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = request.query_params.get('limit', 10)
        try:
            coupons = stripe.Coupon.list(limit=int(limit))
            return Response({
                "coupons": coupons.data,
                "has_more": coupons.has_more,
                "count": len(coupons.data)
            })
        except stripe.error.StripeError as e:
            raise APIException(str(e))

class ListPromotionCodesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = request.query_params.get('limit', 10)
        active = request.query_params.get('active')
        params = {"limit": int(limit)}
        if active is not None:
            params["active"] = active.lower() == 'true'

        try:
            promotion_codes = stripe.PromotionCode.list(**params)
            return Response({
                "promotion_codes": promotion_codes.data,
                "has_more": promotion_codes.has_more,
                "count": len(promotion_codes.data)
            })
        except stripe.error.StripeError as e:
            raise APIException(str(e))