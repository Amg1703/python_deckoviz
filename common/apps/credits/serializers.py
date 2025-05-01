from rest_framework import serializers
from .models import (CreditPackage, UserCredit, CreditTransaction, CreditAIOperation, 
                     CreditPricing, PlanFeature, CreditPlan, PlanFeatureAssociation, 
                     UserSubscription)

class CreditPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPackage
        fields = ['id', 'name', 'description', 'credits', 'price', 'is_active']
        read_only_fields = ['id']

class UserCreditSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserCredit
        fields = ['id', 'user', 'username', 'balance', 'lifetime_credits', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'username', 'lifetime_credits', 'created_at', 'updated_at']

class CreditTransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CreditTransaction   
        fields = ['id', 'user', 'username', 'amount', 'transaction_type', 'description', 
                  'reference_id', 'created_at']
        read_only_fields = ['id', 'user', 'username', 'created_at']

class CreditAIOperationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CreditAIOperation
        fields = ['id', 'user', 'username', 'operation_type', 'credits_used', 'status',
                  'input_data', 'result_data', 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at']

class CreditPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPricing
        fields = ['id', 'operation_type', 'base_credits', 'per_unit_credits', 'description']
        read_only_fields = ['id']

class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class PlanFeatureAssociationSerializer(serializers.ModelSerializer):
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    feature_description = serializers.CharField(source='feature.description', read_only=True)
    description = serializers.SerializerMethodField()
    
    class Meta:
        model = PlanFeatureAssociation
        fields = ['id', 'feature', 'feature_name', 'feature_description', 'custom_description', 'description']
        read_only_fields = ['id', 'feature_name', 'feature_description']
    
    def get_description(self, obj):
        # Return custom description if available, otherwise use feature description
        return obj.custom_description if obj.custom_description else obj.feature.description

class CreditPlanSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    
    class Meta:
        model = CreditPlan
        fields = ['id', 'name', 'plan_type', 'price', 'display_price', 'price_suffix', 
                  'credits', 'description', 'tagline', 'is_popular', 'is_custom', 
                  'features']
        read_only_fields = ['id']
    
    def get_features(self, obj):
        feature_associations = obj.feature_associations.all().select_related('feature')
        return PlanFeatureAssociationSerializer(feature_associations, many=True).data

class UserSubscriptionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'username', 'plan', 'plan_name', 'status', 
                  'start_date', 'end_date', 'auto_renew', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'username', 'plan_name', 'created_at', 'updated_at']

class CreditBalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField(read_only=True)
    lifetime_credits = serializers.IntegerField(read_only=True)

class CreditUsageSerializer(serializers.Serializer):
    operation_type = serializers.ChoiceField(choices=CreditAIOperation.OPERATION_TYPES)
    units = serializers.IntegerField(default=1, min_value=1)
    input_data = serializers.JSONField(required=False)

class CreditEstimateSerializer(serializers.Serializer):
    operation_type = serializers.ChoiceField(choices=CreditAIOperation.OPERATION_TYPES)
    units = serializers.IntegerField(default=1, min_value=1)
    estimated_cost = serializers.IntegerField(read_only=True)
