import os
import time
import json
from typing import List, Dict, Any
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
import google.generativeai as genai
from apps.wardrobe.models import ClothingCategory, ClothingItem, ClothingImage, AIAnalysis
from .image_service import ImageProcessingService
from .storage_service import StorageService

class GeminiAnalysisService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValidationError("GEMINI_API_KEY is not configured")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
    def analyze_clothing_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple clothing images and extract details using Gemini Vision API.
        
        Args:
            image_paths (list): List of image file paths.
            
        Returns:
            dict: Extracted details and raw API response.
        """
        if not image_paths:
            raise ValidationError("No images provided for analysis")
        
        start_time = time.time()
        
        try:
            # Prepare the prompt for clothing analysis
            prompt = """
            Analyze these clothing images and extract the following information in JSON format:
            {
                "category": "clothing category (e.g., shirt, pants, dress, shoes)",
                "brand": "brand name if visible",
                "color": "primary color",
                "size": "size if visible on tag or label",
                "material": "fabric/material type",
                "pattern": "pattern type (solid, striped, floral, etc.)",
                "style": "style description",
                "condition": "item condition (new, good, fair, poor)",
                "estimated_price": "estimated price range",
                "confidence": "confidence score (0-1)"
            }
            
            Focus on:
            1. Main clothing item details
            2. Any visible tags or labels
            3. Color and pattern analysis
            4. Material identification
            5. Brand recognition if possible
            
            Return only valid JSON without any additional text.
            """
            
            # Load images
            image_parts = []
            for image_path in image_paths:
                if os.path.exists(image_path):
                    image_part = {
                        "mime_type": "image/jpeg",
                        "data": open(image_path, "rb").read()
                    }
                    image_parts.append(image_part)
            
            if not image_parts:
                raise ValidationError("No valid images found")
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt] + image_parts)
            
            # Parse the response
            try:
                extracted_data = json.loads(response.text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract structured data
                extracted_data = self._parse_unstructured_response(response.text)
            
            processing_time = time.time() - start_time
            
            return {
                'gemini_raw_response': {
                    'text': response.text,
                    'candidates': response.candidates[0].text if response.candidates else None
                },
                'extracted_data': extracted_data,
                'confidence_scores': {
                    'overall': extracted_data.get('confidence', 0.7),
                    'category': 0.8,
                    'color': 0.9,
                    'brand': 0.6
                },
                'processing_time': processing_time,
                'api_cost': self._calculate_cost(processing_time)
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'gemini_raw_response': {'error': str(e)},
                'extracted_data': {},
                'confidence_scores': {},
                'processing_time': processing_time,
                'api_cost': 0
            }
    
    def extract_tag_information(self, tag_image_path: str) -> Dict[str, Any]:
        """
        Extract price, brand, size from clothing tag image using Gemini Vision API.
        
        Args:
            tag_image_path (str): Path to the tag image file.
            
        Returns:
            dict: Extracted tag information.
        """
        if not os.path.exists(tag_image_path):
            raise ValidationError(f"Tag image not found: {tag_image_path}")
        
        try:
            prompt = """
            Extract the following information from this clothing tag/label in JSON format:
            {
                "brand": "brand name",
                "size": "size information",
                "price": "price if visible",
                "material": "material composition",
                "care_instructions": "care instructions if visible",
                "model_number": "model/sku number if visible"
            }
            
            Focus on:
            1. Brand name and logo
            2. Size information (S, M, L, XL, or numerical sizes)
            3. Price tags or labels
            4. Material composition
            5. Any care instructions
            
            Return only valid JSON without additional text.
            """
            
            image_part = {
                "mime_type": "image/jpeg",
                "data": open(tag_image_path, "rb").read()
            }
            
            response = self.model.generate_content([prompt, image_part])
            
            try:
                tag_data = json.loads(response.text)
            except json.JSONDecodeError:
                tag_data = self._parse_tag_response(response.text)
            
            return tag_data
            
        except Exception as e:
            return {
                'brand': None,
                'size': None,
                'price': None,
                'material': None,
                'care_instructions': None,
                'model_number': None,
                'error': str(e)
            }
    
    def generate_item_description(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate a natural language description for a clothing item based on analysis data.
        
        Args:
            analysis_data (dict): Data extracted from AI analysis.
            
        Returns:
            str: Generated description.
        """
        try:
            prompt = f"""
            Generate a natural, engaging description for this clothing item based on the following data:
            {json.dumps(analysis_data, indent=2)}
            
            The description should be:
            - 2-3 sentences long
            - Include key details like color, style, material
            - Mention brand if available
            - Be suitable for a digital wardrobe app
            - Natural and conversational tone
            
            Return only the description without any additional formatting.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            # Fallback description
            category = analysis_data.get('category', 'clothing item')
            color = analysis_data.get('color', '')
            brand = analysis_data.get('brand', '')
            
            description_parts = []
            if brand:
                description_parts.append(f"{brand}")
            if color:
                description_parts.append(f"{color}")
            description_parts.append(f"{category}")
            
            return f"A {' '.join(description_parts)}" if description_parts else f"A {category}"
    
    def _parse_unstructured_response(self, response_text: str) -> Dict[str, Any]:
        """Parse unstructured Gemini response into structured data."""
        extracted_data = {
            'category': 'unknown',
            'brand': '',
            'color': '',
            'size': '',
            'material': '',
            'pattern': 'solid',
            'style': '',
            'condition': 'good',
            'estimated_price': '',
            'confidence': 0.5
        }
        
        # Simple keyword extraction
        text_lower = response_text.lower()
        
        # Extract category
        categories = ['shirt', 'pants', 'dress', 'skirt', 'jacket', 'coat', 'sweater', 'hoodie', 'jeans', 'shorts']
        for cat in categories:
            if cat in text_lower:
                extracted_data['category'] = cat
                break
        
        # Extract color
        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'grey', 'brown', 'pink', 'purple', 'orange']
        for color in colors:
            if color in text_lower:
                extracted_data['color'] = color
                break
        
        # Extract pattern
        patterns = ['striped', 'floral', 'plaid', 'checkered', 'polka dot', 'solid']
        for pattern in patterns:
            if pattern in text_lower:
                extracted_data['pattern'] = pattern
                break
        
        return extracted_data
    
    def _parse_tag_response(self, response_text: str) -> Dict[str, Any]:
        """Parse tag response into structured data."""
        tag_data = {
            'brand': '',
            'size': '',
            'price': '',
            'material': '',
            'care_instructions': '',
            'model_number': ''
        }
        
        text_lower = response_text.lower()
        
        # Extract size
        sizes = ['xs', 's', 'm', 'l', 'xl', 'xxl', 'xxxl']
        for size in sizes:
            if size in text_lower:
                tag_data['size'] = size.upper()
                break
        
        # Extract price patterns
        import re
        price_pattern = r'\$?\d+\.?\d*'
        prices = re.findall(price_pattern, response_text)
        if prices:
            tag_data['price'] = prices[0]
        
        return tag_data
    
    def _calculate_cost(self, processing_time: float) -> float:
        """Calculate estimated API cost based on processing time."""
        # Rough estimation: $0.0025 per 1K characters input + $0.0125 per 1K characters output
        # This is a simplified calculation
        base_cost = 0.01  # Base cost per request
        time_cost = processing_time * 0.001  # Additional cost based on time
        return round(base_cost + time_cost, 4)

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
            category, _ = ClothingCategory.objects.get_or_create(
                name=category_name, 
                defaults={'slug': category_name.lower().replace(' ', '-')}
            )
            item_data['category'] = category
        item_data.pop('category_name', None)

        # 2. Create ClothingItem
        clothing_item = ClothingItem.objects.create(user=user, **item_data)

        # 3. Process and upload images
        uploaded_images = []
        for idx, image_file in enumerate(images[:5]):
            # Validate image
            self.image_service.validate_image(image_file)
            
            # Upload to cloud storage
            url = self.storage_service.upload_image(image_file, f"clothing_items/{clothing_item.id}")
            
            # Create ClothingImage record
            clothing_image = ClothingImage.objects.create(
                clothing_item=clothing_item,
                image=url,
                image_type='main' if idx == 0 else 'detail',
                upload_order=idx + 1,
                alt_text=item_data.get('name', ''),
                file_size=getattr(image_file, 'size', 0)
            )
            uploaded_images.append(clothing_image)

        # 4. AI analysis if requested
        if use_ai and uploaded_images:
            try:
                # Get local file paths for AI analysis
                image_paths = []
                for img in uploaded_images:
                    if hasattr(img.image, 'path'):
                        image_paths.append(img.image.path)
                    else:
                        # If using cloud storage, download temporarily
                        temp_path = self.storage_service.download_temp(img.image.url)
                        image_paths.append(temp_path)
                
                # Perform AI analysis
                ai_result = self.ai_service.analyze_clothing_images(image_paths)
                
                # Update clothing item fields from AI analysis
                extracted_data = ai_result.get('extracted_data', {})
                for field, value in extracted_data.items():
                    if hasattr(clothing_item, field) and value:
                        setattr(clothing_item, field, value)
                
                # Generate description if not provided
                if not clothing_item.description:
                    clothing_item.description = self.ai_service.generate_item_description(extracted_data)
                
                clothing_item.ai_analysis_status = 'completed'
                clothing_item.save()
                
                # Create AI analysis record
                AIAnalysis.objects.create(
                    clothing_item=clothing_item,
                    gemini_raw_response=ai_result.get('gemini_raw_response', {}),
                    extracted_data=extracted_data,
                    confidence_scores=ai_result.get('confidence_scores', {}),
                    processing_time=ai_result.get('processing_time'),
                    api_cost=ai_result.get('api_cost')
                )
                
            except Exception as e:
                clothing_item.ai_analysis_status = 'failed'
                clothing_item.save()
                # Log the error for debugging
                print(f"AI analysis failed for item {clothing_item.id}: {str(e)}")
        
        return clothing_item 