# from django.db import models


# class MarketingMaterial(models.Model):
#     """Marketing Material model for AI-generated marketing content"""
    
#     request_id = models.CharField(max_length=255, unique=True, db_index=True)
#     user_id = models.CharField(max_length=255, db_index=True)
#     prompt = models.TextField()
#     campaign_goal = models.TextField()
#     tone = models.CharField(max_length=100)
#     material_type = models.CharField(max_length=100)
#     aspect_ratio = models.CharField(max_length=20, default="1:1")
#     num_outputs = models.IntegerField(default=1)
#     status = models.CharField(max_length=50)  # processing, completed, failed
#     materials = models.JSONField(null=True, blank=True)  # Store generated material metadata
#     text_suggestions = models.JSONField(null=True, blank=True)
#     error = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = "marketing_materials"
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["user_id"]),
#             models.Index(fields=["request_id"]),
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#         ]
    
#     def __str__(self):
#         return f"{self.material_type} - {self.request_id}"


# class BrandAsset(models.Model):
#     """Brand Asset model for user-uploaded brand materials"""
    
#     asset_id = models.CharField(max_length=255, unique=True, db_index=True)
#     user_id = models.CharField(max_length=255, db_index=True)
#     filename = models.CharField(max_length=500)
#     file_type = models.CharField(max_length=50)  # image, document
#     file_path = models.CharField(max_length=500)
#     extracted_colors = models.JSONField(null=True, blank=True)
#     extracted_text = models.TextField(null=True, blank=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         db_table = "brand_assets"
#         ordering = ["-uploaded_at"]
#         indexes = [
#             models.Index(fields=["user_id"]),
#             models.Index(fields=["asset_id"]),
#             models.Index(fields=["uploaded_at"]),
#         ]
    
#     def __str__(self):
#         return f"{self.filename} ({self.asset_id})"
