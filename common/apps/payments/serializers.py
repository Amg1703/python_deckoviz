from rest_framework import serializers
from .models import Transaction
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
 
class TransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Transaction
        fields =  [
            'id',
            'user',
            'order',
            'amount',
            'payment_method',
            'ref_id',
            'signature',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
            'status'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
class CreateCouponSerializer(serializers.Serializer):
    percent_off = serializers.FloatField(required=False)
    amount_off = serializers.IntegerField(required=False)
    currency = serializers.CharField(max_length=3, default='usd')
    duration = serializers.CharField(default='once')
    duration_in_months = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('percent_off') and not data.get('amount_off'):
            raise serializers.ValidationError("Provide percent_off or amount_off")
        return data

class CreatePromotionCodeSerializer(serializers.Serializer):
    coupon_id = serializers.CharField()
    code = serializers.CharField()
    active = serializers.BooleanField(default=True)

class CreateCheckoutSerializer(serializers.Serializer):
    price_id = serializers.CharField()
    mode = serializers.CharField(default='payment')
    quantity = serializers.IntegerField(default=1)
    promotion_code_id = serializers.CharField(required=False)
    allow_promotion_codes = serializers.BooleanField(required=False)
    success_url = serializers.URLField(default='https://example.com/success?session_id={CHECKOUT_SESSION_ID}')
    cancel_url = serializers.URLField(default='https://example.com/cancel')