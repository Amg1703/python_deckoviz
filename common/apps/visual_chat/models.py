from django.db import models
from django.utils import timezone
import uuid


class PDF(models.Model):
    """Uploaded PDF files for visual chat"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    size_bytes = models.BigIntegerField()
    pages_count = models.IntegerField()
    file_data = models.BinaryField()
    extracted_text = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'visual_chat_pdfs'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['-uploaded_at']),
        ]
    
    def __str__(self):
        return f"PDF: {self.filename}"


class Job(models.Model):
    """Image generation jobs for PDFs"""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE, related_name='jobs')
    prompt = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    chapter_number = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    error = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['pdf', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Job {self.id} - {self.status}"


class Image(models.Model):
    """Generated images from jobs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='images')
    provider = models.CharField(max_length=50)
    provider_job_id = models.CharField(max_length=255, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    mime = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'visual_chat_images'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', '-created_at']),
        ]
    
    def __str__(self):
        return f"Image {self.id} - {self.provider}"
