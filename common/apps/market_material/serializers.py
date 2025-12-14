# from rest_framework import serializers
# from .models import MarketingMaterial, BrandAsset


# class MarketingMaterialSerializer(serializers.ModelSerializer):
#     """Serializer for MarketingMaterial model"""
    
#     class Meta:
#         model = MarketingMaterial
#         fields = [
#             'id',
#             'request_id',
#             'user_id',
#             'prompt',
#             'campaign_goal',
#             'tone',
#             'material_type',
#             'aspect_ratio',
#             'num_outputs',
#             'status',
#             'materials',
#             'text_suggestions',
#             'error',
#             'created_at',
#             'updated_at',
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class MarketingMaterialCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating marketing material"""
    
#     class Meta:
#         model = MarketingMaterial
#         fields = [
#             'request_id',
#             'user_id',
#             'prompt',
#             'campaign_goal',
#             'tone',
#             'material_type',
#             'aspect_ratio',
#             'num_outputs',
#             'status',
#         ]


# class MarketingMaterialUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for updating marketing material"""
    
#     class Meta:
#         model = MarketingMaterial
#         fields = [
#             'status',
#             'materials',
#             'text_suggestions',
#             'error',
#         ]


# class BrandAssetSerializer(serializers.ModelSerializer):
#     """Serializer for BrandAsset model"""
    
#     class Meta:
#         model = BrandAsset
#         fields = [
#             'id',
#             'asset_id',
#             'user_id',
#             'filename',
#             'file_type',
#             'file_path',
#             'extracted_colors',
#             'extracted_text',
#             'uploaded_at',
#         ]
#         read_only_fields = ['id', 'uploaded_at']


# class BrandAssetCreateSerializer(serializers.ModelSerializer):
#     """Serializer for creating brand asset"""
    
#     class Meta:
#         model = BrandAsset
#         fields = [
#             'asset_id',
#             'user_id',
#             'filename',
#             'file_type',
#             'file_path',
#             'extracted_colors',
#             'extracted_text',
#         ]
