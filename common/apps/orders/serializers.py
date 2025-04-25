from apps.payments.models import Transaction
from rest_framework import serializers
from .models import Order
from apps.marketplace.serializers import PriceSerializer
from apps.gallery.serializers import ImageSerializer
from django.db import transaction

 
     
class OrderSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'price',
            'image',
            'billing_address',
            'shipping_address',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
    
    def get_image(self, obj):
        return ImageSerializer(obj.price.image).data
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['price'] = PriceSerializer(instance.price).data
        return data
     
      
            

class OrderCreateSerializer(serializers.ModelSerializer):
    txn_id = serializers.CharField(write_only=True)
    ref_id = serializers.CharField(required=True, write_only=True)
    signature = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'price',
            'txn_id',
            'ref_id',
            'signature',
            'billing_address',
            'shipping_address',
            'status',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 
            'user', 
            'status', 
            'is_active', 
            'created_at', 
            'updated_at'
        ]
        extra_kwargs = {
            'txn_id': {'write_only': True},
            'ref_id': {'write_only': True},
            'signature': {'write_only': True},
        }
  
         
    def get_user(self, obj):
        return obj.user.username
    
    def validate(self,data):
        user = self.context['request'].user
        
        # Validate payment data together
        txn_id = data.get('txn_id')
        ref_id = data.get('ref_id')
        signature = data.get('signature')
        
        if not all([txn_id, ref_id, signature]):
            raise serializers.ValidationError(
                "Payment is required to place order. 'txn_id', 'ref_id' and 'signature' must be provided."
            )
            
        try:
            self.transaction_obj = Transaction.objects.get(id=txn_id) 
            if self.transaction_obj.user != user:
                raise serializers.ValidationError("Transaction ID does not match user.")
            if self.transaction_obj.status == 'completed':
                raise serializers.ValidationError("Transaction ID already used.")
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Transaction ID does not exist.")
            
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user

        price = validated_data.get('price',None)
        billing_address = validated_data.get('billing_address',None)
        shipping_address = validated_data.get('shipping_address',None)

        # Extract payment fields from validated data
        ref_id = validated_data.pop('ref_id')
        signature = validated_data.pop('signature')

        self.transaction_obj.ref_id = ref_id
        self.transaction_obj.signature = signature
        self.transaction_obj.status = 'completed'
        self.transaction_obj.save()

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                price=price,
                billing_address=billing_address,
                shipping_address=shipping_address,
                status='confirmed'
            )
            self.transaction_obj.order = order
            self.transaction_obj.save()
            return order

    def to_representation(self, instance):
        # Delegate to OrderSerializer to avoid payment fields
        return OrderSerializer(instance, context=self.context).data