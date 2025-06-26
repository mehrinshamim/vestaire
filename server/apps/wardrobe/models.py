import uuid
from django.db import models
from django.contrib.auth.models import User

class ClothingCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ClothingItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Analysis Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clothing_items')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ClothingCategory, on_delete=models.SET_NULL, null=True)
    brand = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    material = models.CharField(max_length=100, blank=True)
    pattern = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    ai_analysis_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    wear_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ClothingImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('main', 'Main Image'),
        ('tag', 'Price Tag'),
        ('detail', 'Detail Shot'),
        ('back', 'Back View'),
        ('side', 'Side View'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='clothing_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='main')
    upload_order = models.PositiveSmallIntegerField()
    alt_text = models.CharField(max_length=200, blank=True)
    file_size = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} for {self.clothing_item.name}"

class AIAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clothing_item = models.OneToOneField(ClothingItem, on_delete=models.CASCADE, related_name='ai_analysis')
    gemini_raw_response = models.JSONField()
    extracted_data = models.JSONField()
    confidence_scores = models.JSONField()
    processing_time = models.DurationField(null=True, blank=True)
    api_cost = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Analysis for {self.clothing_item.name}" 