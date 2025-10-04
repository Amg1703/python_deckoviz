from rest_framework import serializers
from .models import Price
 
class PriceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Price
        fields = [
            'id',
            'image',
            'final_price',
            'created_at',
            'updated_at'
        ] 
    
    
 