import os
from django.conf import settings
from django.db import transaction
from apps.wardrobe.models import ClothingCategory, ClothingItem, ClothingImage, AIAnalysis
from .image_service import ImageProcessingService
from .storage_service import StorageService

class GeminiAnalysisService:
    def __init__(self):
        # Use GEMINI_API_KEY from Django settings
        self.api_key = settings.GEMINI_API_KEY
        # TODO: Initialize Gemini Vision API client here

    def analyze_clothing_images(self, image_paths):
        """
        Analyze multiple clothing images and extract details using Gemini Vision API.
        Args:
            image_paths (list): List of image file paths.
        Returns:
            dict: Extracted details and raw API response.
        """
        # TODO: Call Gemini Vision API with image_paths and process the response
        return {
            'gemini_raw_response': {},
            'extracted_data': {},
            'confidence_scores': {},
        }

    def extract_tag_information(self, tag_image_path):
        """
        Extract price, brand, size from clothing tag image using Gemini Vision API.
        Args:
            tag_image_path (str): Path to the tag image file.
        Returns:
            dict: Extracted tag information.
        """
        # TODO: Call Gemini Vision API for tag extraction
        return {
            'brand': None,
            'size': None,
            'price': None,
        }

    def generate_item_description(self, analysis_data):
        """
        Generate a natural language description for a clothing item based on analysis data.
        Args:
            analysis_data (dict): Data extracted from AI analysis.
        Returns:
            str: Generated description.
        """
        # TODO: Use Gemini Vision API or custom logic to generate description
        return "A stylish clothing item."

class GeminiAgent:
    def __init__(self):
        self.image_service = ImageProcessingService()
        self.storage_service = StorageService()
        self.ai_service = GeminiAnalysisService()

    @transaction.atomic
    def process_clothing_item(self, user, images, item_data, use_ai=False):
        """
        Orchestrates the upload, processing, and AI analysis for a ClothingItem.
        Args:
            user: User instance
            images: list of image files (max 5)
            item_data: dict with ClothingItem fields (name, category, etc.)
            use_ai: bool, whether to use Gemini AI analysis
        Returns:
            ClothingItem instance
        """
        # 1. Handle category (create if not exists)
        category_name = item_data.get('category_name')
        if category_name:
            category, _ = ClothingCategory.objects.get_or_create(name=category_name, defaults={'slug': category_name.lower().replace(' ', '-')})
            item_data['category'] = category
        item_data.pop('category_name', None)

        # 2. Create ClothingItem
        clothing_item = ClothingItem.objects.create(user=user, **item_data)

        # 3. Process and upload images
        for idx, image_file in enumerate(images[:5]):
            self.image_service.validate_image(image_file)
            # Optionally optimize image before upload (reduces transfer size)
            # optimized_path = f"/tmp/optimized_{image_file.name}"
            # self.image_service.optimize_image(image_file, optimized_path)
            # upload_file = open(optimized_path, 'rb')
            # url = self.storage_service.upload_image(upload_file, f"clothing_items/{clothing_item.id}")
            # upload_file.close()
            # os.remove(optimized_path)
            # For simplicity, upload original file:
            url = self.storage_service.upload_image(image_file, f"clothing_items/{clothing_item.id}")
            ClothingImage.objects.create(
                clothing_item=clothing_item,
                image=url,
                image_type='main' if idx == 0 else 'detail',
                upload_order=idx + 1,
                alt_text=item_data.get('name', ''),
                file_size=getattr(image_file, 'size', 0)
            )

        # 4. AI analysis if requested
        if use_ai:
            image_paths = [img.image for img in clothing_item.images.all()]
            ai_result = self.ai_service.analyze_clothing_images(image_paths)
            # Update clothing item fields from AI
            for field, value in ai_result.get('extracted_data', {}).items():
                setattr(clothing_item, field, value)
            clothing_item.ai_analysis_status = 'completed'
            clothing_item.save()
            AIAnalysis.objects.create(
                clothing_item=clothing_item,
                gemini_raw_response=ai_result.get('gemini_raw_response', {}),
                extracted_data=ai_result.get('extracted_data', {}),
                confidence_scores=ai_result.get('confidence_scores', {}),
                processing_time=None,  # Set if available
                api_cost=None  # Set if available
            )
        return clothing_item 