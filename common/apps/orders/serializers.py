from  apps.payments.models import Transaction
from rest_framework import serializers
from .models import Order

 
     
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'price',
            'billing_address',
            'shipping_address',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
        
    def get_user(self, obj):
        return obj.user.username
        
    def get_price(self, obj):
        return obj.price.final_price
      
            
from django.db import transaction

class OrderCreateSerializer(serializers.Serializer):
    txn_id = serializers.CharField()
    payment_id = serializers.CharField(required=False, allow_null=True)
    payment_signature = serializers.CharField(required=False, allow_null=True)
    payment_order_id = serializers.CharField(required=False, allow_null=True) 

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'price',
            'billing_address',
            'shipping_address',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
         
    def get_user(self, obj):
        return obj.user.username
    
    def create(self,validated_data):
        user = self.context['request'].user
        
        price = validated_data['price']
        billing_address = validated_data['billing_address']
        shipping_address = validated_data['shipping_address']
        
        payment_ref_id = validated_data['payment_ref_id']
        txn_id = validated_data['txn_id']
        
        if txn_id and payment_ref_id:
            transaction = Transaction.objects.filter(id=txn_id).first()
            if not transaction:
                raise serializers.ValidationError("Invalid transaction ID")
            else:
                transaction.ref_id = payment_ref_id
                transaction.status = 'completed'
                transaction.save()
            
            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    price=price,
                    billing_address=billing_address,
                    shipping_address=shipping_address,
                    status='confirmed',
                    is_active=True
                )
                return order
        else:
            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    price=price,
                    billing_address=billing_address,
                    shipping_address=shipping_address,
                status='pending',
                is_active=True
            )
        
        