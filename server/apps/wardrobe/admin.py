from django.contrib import admin
from .models import ClothingCategory, ClothingItem, ClothingImage, AIAnalysis

@admin.register(ClothingCategory)
class ClothingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('parent',)

@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'brand', 'color', 'size', 'ai_analysis_status', 'is_active', 'created_at')
    search_fields = ('name', 'brand', 'color', 'size')
    list_filter = ('category', 'ai_analysis_status', 'is_active')

@admin.register(ClothingImage)
class ClothingImageAdmin(admin.ModelAdmin):
    list_display = ('clothing_item', 'image_type', 'upload_order', 'file_size', 'created_at')
    list_filter = ('image_type',)

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('clothing_item', 'processing_time', 'api_cost', 'created_at') 