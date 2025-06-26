from rest_framework import serializers
from .models import ClothingCategory, ClothingItem, ClothingImage, AIAnalysis

class ClothingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingCategory
        fields = '__all__'

class ClothingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingImage
        fields = ('id', 'image', 'image_type', 'upload_order', 'alt_text', 'file_size', 'created_at')
        read_only_fields = ('id', 'file_size', 'created_at')

class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = ('id', 'extracted_data', 'confidence_scores', 'processing_time', 'api_cost', 'created_at')
        read_only_fields = ('id', 'processing_time', 'api_cost', 'created_at')

class ClothingItemSerializer(serializers.ModelSerializer):
    images = ClothingImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    ai_analysis = AIAnalysisSerializer(read_only=True)
    
    class Meta:
        model = ClothingItem
        fields = ('id', 'name', 'category', 'category_name', 'brand', 'color', 'size', 
                 'material', 'pattern', 'price', 'purchase_date', 'purchase_location', 
                 'description', 'ai_analysis_status', 'wear_count', 'is_active', 
                 'created_at', 'updated_at', 'images', 'ai_analysis')
        read_only_fields = ('id', 'ai_analysis_status', 'wear_count', 'created_at', 'updated_at')

class ClothingItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingItem
        fields = ('name', 'category', 'brand', 'color', 'size', 'material', 'pattern', 
                 'price', 'purchase_date', 'purchase_location', 'description')

class ClothingItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ClothingItem
        fields = ('id', 'name', 'category_name', 'brand', 'color', 'size', 
                 'ai_analysis_status', 'is_active', 'created_at', 'main_image')
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(image_type='main').first()
        if main_image:
            return self.context['request'].build_absolute_uri(main_image.image.url)
        return None 