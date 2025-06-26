from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.wardrobe.models import ClothingCategory, ClothingItem, ClothingImage, AIAnalysis
from apps.wardrobe.services.ai_service import GeminiAgent
from unittest.mock import patch, MagicMock
from io import BytesIO

class GeminiAgentTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.agent = GeminiAgent()

    @patch('apps.wardrobe.services.storage_service.StorageService.upload_image', return_value='https://cloud.example.com/test.jpg')
    @patch('apps.wardrobe.services.image_service.ImageProcessingService.validate_image', return_value=None)
    @patch('apps.wardrobe.services.ai_service.GeminiAnalysisService.analyze_clothing_images', return_value={
        'gemini_raw_response': {},
        'extracted_data': {'brand': 'Nike', 'color': 'Red'},
        'confidence_scores': {'brand': 0.95, 'color': 0.9},
    })
    def test_process_clothing_item(self, mock_ai, mock_validate, mock_upload):
        image_file = BytesIO(b"fake image data")
        image_file.name = 'test.jpg'
        image_file.size = 1024
        item_data = {'name': 'Test Shirt', 'category_name': 'Shirts'}
        clothing_item = self.agent.process_clothing_item(self.user, [image_file], item_data, use_ai=True)
        self.assertEqual(clothing_item.name, 'Test Shirt')
        self.assertEqual(clothing_item.category.name, 'Shirts')
        self.assertEqual(clothing_item.brand, 'Nike')
        self.assertEqual(clothing_item.color, 'Red')
        self.assertEqual(clothing_item.images.count(), 1)
        self.assertTrue(AIAnalysis.objects.filter(clothing_item=clothing_item).exists()) 