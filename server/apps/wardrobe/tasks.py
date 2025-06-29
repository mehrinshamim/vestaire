import os
import time
from celery import shared_task
from django.conf import settings
from .models import ClothingItem, ClothingImage
from .services.ai_service import GeminiAnalysisService
from .services.image_service import ImageProcessingService
from .services.storage_service import StorageService

@shared_task
def analyze_clothing_item(clothing_item_id):
    """
    Celery task to analyze clothing item with AI using Gemini Vision API.
    
    Args:
        clothing_item_id (str): UUID of the clothing item to analyze
    """
    try:
        clothing_item = ClothingItem.objects.get(id=clothing_item_id)
        clothing_item.ai_analysis_status = 'processing'
        clothing_item.save()
        
        # Initialize services
        ai_service = GeminiAnalysisService()
        image_service = ImageProcessingService()
        storage_service = StorageService()
        
        # Get images for analysis
        images = clothing_item.images.all().order_by('upload_order')
        if not images.exists():
            raise Exception("No images found for analysis")
        
        # Prepare image paths for AI analysis
        image_paths = []
        for image in images:
            if hasattr(image.image, 'path') and os.path.exists(image.image.path):
                # Local file
                image_paths.append(image.image.path)
            else:
                # Cloud storage file - download temporarily
                try:
                    temp_path = storage_service.download_temp(image.image.url)
                    image_paths.append(temp_path)
                except Exception as e:
                    print(f"Failed to download image {image.id}: {str(e)}")
                    continue
        
        if not image_paths:
            raise Exception("No valid images could be processed")
        
        # Perform AI analysis
        start_time = time.time()
        ai_result = ai_service.analyze_clothing_images(image_paths)
        processing_time = time.time() - start_time
        
        # Update clothing item with extracted data
        extracted_data = ai_result.get('extracted_data', {})
        for field, value in extracted_data.items():
            if hasattr(clothing_item, field) and value:
                setattr(clothing_item, field, value)
        
        # Generate description if not provided
        if not clothing_item.description:
            clothing_item.description = ai_service.generate_item_description(extracted_data)
        
        clothing_item.ai_analysis_status = 'completed'
        clothing_item.save()
        
        # Create or update AI analysis record
        from .models import AIAnalysis
        AIAnalysis.objects.update_or_create(
            clothing_item=clothing_item,
            defaults={
                'gemini_raw_response': ai_result.get('gemini_raw_response', {}),
                'extracted_data': extracted_data,
                'confidence_scores': ai_result.get('confidence_scores', {}),
                'processing_time': processing_time,
                'api_cost': ai_result.get('api_cost', 0)
            }
        )
        
        # Clean up temporary files
        for temp_path in image_paths:
            if temp_path.startswith('/tmp/') and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
        
        return f"Analysis completed for item {clothing_item_id}"
        
    except ClothingItem.DoesNotExist:
        return f"Clothing item {clothing_item_id} not found"
    except Exception as e:
        # Update status to failed
        try:
            clothing_item = ClothingItem.objects.get(id=clothing_item_id)
            clothing_item.ai_analysis_status = 'failed'
            clothing_item.save()
        except:
            pass
        
        return f"Analysis failed for item {clothing_item_id}: {str(e)}"

@shared_task
def process_uploaded_images(clothing_item_id, image_ids):
    """
    Process and optimize uploaded images.
    
    Args:
        clothing_item_id (str): UUID of the clothing item
        image_ids (list): List of image UUIDs to process
    """
    try:
        clothing_item = ClothingItem.objects.get(id=clothing_item_id)
        images = ClothingImage.objects.filter(
            id__in=image_ids,
            clothing_item=clothing_item
        )
        
        image_service = ImageProcessingService()
        storage_service = StorageService()
        
        processed_images = []
        
        for image in images:
            try:
                # Validate image
                image_service.validate_image(image.image)
                
                # Generate thumbnails
                thumbnails = image_service.generate_thumbnails(image.image)
                
                # Upload thumbnails to cloud storage
                thumbnail_urls = {}
                for size, thumbnail in thumbnails.items():
                    thumbnail_url = storage_service.upload_image(
                        thumbnail, 
                        f"thumbnails/{clothing_item.id}/{image.id}_{size}"
                    )
                    thumbnail_urls[size] = thumbnail_url
                
                # Update image record with thumbnail URLs
                if not hasattr(image, 'thumbnail_urls'):
                    # Add thumbnail_urls field if it doesn't exist
                    # This would require a migration
                    pass
                
                processed_images.append(image.id)
                
            except Exception as e:
                print(f"Failed to process image {image.id}: {str(e)}")
                continue
        
        return f"Image processing completed for item {clothing_item_id}. Processed {len(processed_images)} images."
        
    except ClothingItem.DoesNotExist:
        return f"Clothing item {clothing_item_id} not found"
    except Exception as e:
        return f"Image processing failed for item {clothing_item_id}: {str(e)}"

@shared_task
def extract_tag_information(image_id):
    """
    Extract information from clothing tag images.
    
    Args:
        image_id (str): UUID of the tag image
    """
    try:
        image = ClothingImage.objects.get(id=image_id, image_type='tag')
        ai_service = GeminiAnalysisService()
        storage_service = StorageService()
        
        # Get image path
        if hasattr(image.image, 'path') and os.path.exists(image.image.path):
            image_path = image.image.path
        else:
            # Download from cloud storage
            image_path = storage_service.download_temp(image.image.url)
        
        # Extract tag information
        tag_data = ai_service.extract_tag_information(image_path)
        
        # Update clothing item with extracted data
        clothing_item = image.clothing_item
        
        if tag_data.get('brand'):
            clothing_item.brand = tag_data['brand']
        if tag_data.get('size'):
            clothing_item.size = tag_data['size']
        if tag_data.get('price'):
            try:
                price = float(tag_data['price'].replace('$', ''))
                clothing_item.price = price
            except:
                pass
        
        clothing_item.save()
        
        # Clean up temporary file
        if image_path.startswith('/tmp/') and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        return f"Tag information extracted for image {image_id}"
        
    except ClothingImage.DoesNotExist:
        return f"Image {image_id} not found"
    except Exception as e:
        return f"Tag extraction failed for image {image_id}: {str(e)}"

@shared_task
def cleanup_failed_analyses():
    """
    Clean up failed AI analyses and reset status for retry.
    """
    try:
        failed_items = ClothingItem.objects.filter(ai_analysis_status='failed')
        count = failed_items.count()
        
        # Reset status to pending for retry
        failed_items.update(ai_analysis_status='pending')
        
        return f"Reset {count} failed analyses to pending status"
        
    except Exception as e:
        return f"Cleanup failed: {str(e)}" 