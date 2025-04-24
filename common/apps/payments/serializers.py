from rest_framework import serializers
from .models import Transaction

 
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
            'status',
            'created_at',
            'updated_at'
        ]
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)