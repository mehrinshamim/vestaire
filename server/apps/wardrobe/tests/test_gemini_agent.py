import os
import tempfile
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from apps.wardrobe.models import ClothingItem, ClothingCategory
from apps.wardrobe.services.ai_service import GeminiAnalysisService, GeminiAgent

class GeminiAnalysisServiceTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = ClothingCategory.objects.create(
            name='Shirts',
            slug='shirts'
        )
        
        # Create a test image file
        self.test_image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        
        # Create temporary image file
        self.temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.temp_image.write(self.test_image_data)
        self.temp_image.close()
    
    def tearDown(self):
        """Clean up test data."""
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)
    
    @patch('apps.wardrobe.services.ai_service.genai')
    def test_analyze_clothing_images_success(self, mock_genai):
        """Test successful clothing image analysis."""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "category": "shirt",
            "brand": "Nike",
            "color": "blue",
            "size": "M",
            "material": "cotton",
            "pattern": "solid",
            "style": "casual",
            "condition": "good",
            "estimated_price": "25-35",
            "confidence": 0.85
        }
        '''
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        # Test the service
        service = GeminiAnalysisService()
        result = service.analyze_clothing_images([self.temp_image.name])
        
        # Verify results
        self.assertIn('extracted_data', result)
        self.assertIn('gemini_raw_response', result)
        self.assertIn('confidence_scores', result)
        
        extracted_data = result['extracted_data']
        self.assertEqual(extracted_data['category'], 'shirt')
        self.assertEqual(extracted_data['brand'], 'Nike')
        self.assertEqual(extracted_data['color'], 'blue')
    
    @patch('apps.wardrobe.services.ai_service.genai')
    def test_analyze_clothing_images_invalid_json(self, mock_genai):
        """Test handling of invalid JSON response from Gemini."""
        # Mock Gemini response with invalid JSON
        mock_response = MagicMock()
        mock_response.text = "This is a blue Nike shirt made of cotton."
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        # Test the service
        service = GeminiAnalysisService()
        result = service.analyze_clothing_images([self.temp_image.name])
        
        # Verify fallback parsing worked
        self.assertIn('extracted_data', result)
        extracted_data = result['extracted_data']
        self.assertIn('category', extracted_data)
        self.assertIn('color', extracted_data)
    
    @patch('apps.wardrobe.services.ai_service.genai')
    def test_extract_tag_information(self, mock_genai):
        """Test tag information extraction."""
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "brand": "Adidas",
            "size": "L",
            "price": "$29.99",
            "material": "100% cotton",
            "care_instructions": "Machine wash cold",
            "model_number": "AD123"
        }
        '''
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
        
        # Test the service
        service = GeminiAnalysisService()
        result = service.extract_tag_information(self.temp_image.name)
        
        # Verify results
        self.assertEqual(result['brand'], 'Adidas')
        self.assertEqual(result['size'], 'L')
        self.assertEqual(result['price'], '$29.99')
    
    def test_generate_item_description(self):
        """Test item description generation."""
        analysis_data = {
            'category': 'shirt',
            'brand': 'Nike',
            'color': 'blue',
            'material': 'cotton',
            'pattern': 'solid'
        }
        
        with patch('apps.wardrobe.services.ai_service.genai') as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "A stylish blue Nike cotton shirt perfect for casual wear."
            mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
            
            service = GeminiAnalysisService()
            description = service.generate_item_description(analysis_data)
            
            self.assertIsInstance(description, str)
            self.assertIn('blue', description.lower())
    
    def test_generate_item_description_fallback(self):
        """Test fallback description generation when AI fails."""
        analysis_data = {
            'category': 'shirt',
            'brand': 'Nike',
            'color': 'blue'
        }
        
        with patch('apps.wardrobe.services.ai_service.genai') as mock_genai:
            mock_genai.GenerativeModel.return_value.generate_content.side_effect = Exception("API Error")
            
            service = GeminiAnalysisService()
            description = service.generate_item_description(analysis_data)
            
            self.assertIsInstance(description, str)
            self.assertIn('shirt', description.lower())

class GeminiAgentTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test image file
        self.test_image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        self.test_image = SimpleUploadedFile(
            "test_image.jpg",
            self.test_image_data,
            content_type="image/jpeg"
        )

    @patch('apps.wardrobe.services.ai_service.GeminiAnalysisService')
    @patch('apps.wardrobe.services.ai_service.StorageService')
    @patch('apps.wardrobe.services.ai_service.ImageProcessingService')
    def test_process_clothing_item_with_ai(self, mock_image_service, mock_storage_service, mock_ai_service):
        """Test processing clothing item with AI analysis."""
        # Mock services
        mock_storage_service.return_value.upload_image.return_value = "https://example.com/image.jpg"
        mock_ai_service.return_value.analyze_clothing_images.return_value = {
            'extracted_data': {
                'category': 'shirt',
                'brand': 'Nike',
                'color': 'blue'
            },
        'gemini_raw_response': {},
            'confidence_scores': {}
        }
        mock_ai_service.return_value.generate_item_description.return_value = "A blue Nike shirt"
        
        # Test data
        item_data = {
            'name': 'Test Shirt',
            'category_name': 'Shirts'
        }
        images = [self.test_image]
        
        # Process item
        agent = GeminiAgent()
        clothing_item = agent.process_clothing_item(self.user, images, item_data, use_ai=True)
        
        # Verify results
        self.assertIsInstance(clothing_item, ClothingItem)
        self.assertEqual(clothing_item.user, self.user)
        self.assertEqual(clothing_item.name, 'Test Shirt')
        self.assertEqual(clothing_item.ai_analysis_status, 'completed')
        self.assertEqual(clothing_item.brand, 'Nike')
        self.assertEqual(clothing_item.color, 'blue')
        self.assertEqual(clothing_item.description, 'A blue Nike shirt')
        
        # Verify images were created
        self.assertEqual(clothing_item.images.count(), 1)
        
        # Verify AI analysis was created
        self.assertTrue(hasattr(clothing_item, 'ai_analysis'))
    
    @patch('apps.wardrobe.services.ai_service.StorageService')
    @patch('apps.wardrobe.services.ai_service.ImageProcessingService')
    def test_process_clothing_item_without_ai(self, mock_image_service, mock_storage_service):
        """Test processing clothing item without AI analysis."""
        # Mock services
        mock_storage_service.return_value.upload_image.return_value = "https://example.com/image.jpg"
        
        # Test data
        item_data = {
            'name': 'Test Shirt',
            'category_name': 'Shirts'
        }
        images = [self.test_image]
        
        # Process item
        agent = GeminiAgent()
        clothing_item = agent.process_clothing_item(self.user, images, item_data, use_ai=False)
        
        # Verify results
        self.assertIsInstance(clothing_item, ClothingItem)
        self.assertEqual(clothing_item.user, self.user)
        self.assertEqual(clothing_item.name, 'Test Shirt')
        self.assertEqual(clothing_item.ai_analysis_status, 'pending')
        
        # Verify images were created
        self.assertEqual(clothing_item.images.count(), 1)
        
        # Verify no AI analysis was created
        self.assertFalse(hasattr(clothing_item, 'ai_analysis')) 