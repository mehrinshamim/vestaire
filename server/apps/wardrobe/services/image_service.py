import os
import tempfile
from PIL import Image, ImageOps
from django.core.exceptions import ValidationError
from django.conf import settings

class ImageProcessingService:
    ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DIMENSIONS = (4000, 4000)  # Max width/height
    THUMBNAIL_SIZES = {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (600, 600)
    }
    
    @staticmethod
    def validate_image(image_file):
        """
        Validate image format, size, and dimensions.
        
        Args:
            image_file: Uploaded image file or file path.
            
        Raises:
            ValidationError: If image is invalid.
        """
        try:
            # Handle both file objects and file paths
            if hasattr(image_file, 'path'):
                img_path = image_file.path
            elif isinstance(image_file, str):
                img_path = image_file
            else:
                # File object - save to temp for validation
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    for chunk in image_file.chunks():
                        tmp.write(chunk)
                    img_path = tmp.name
                    image_file.seek(0)  # Reset file pointer
            
            # Open and validate image
            with Image.open(img_path) as img:
                # Check format
                if img.format not in ImageProcessingService.ALLOWED_FORMATS:
                    raise ValidationError(f'Unsupported image format: {img.format}. Allowed: {ImageProcessingService.ALLOWED_FORMATS}')
                
                # Check dimensions
                if img.size[0] > ImageProcessingService.MAX_DIMENSIONS[0] or img.size[1] > ImageProcessingService.MAX_DIMENSIONS[1]:
                    raise ValidationError(f'Image dimensions too large. Max: {ImageProcessingService.MAX_DIMENSIONS}')
                
                # Check file size
                if hasattr(image_file, 'size') and image_file.size > ImageProcessingService.MAX_FILE_SIZE:
                    raise ValidationError(f'Image file too large. Max: {ImageProcessingService.MAX_FILE_SIZE // (1024*1024)}MB')
                
                # Verify image is not corrupted
            img.verify()
            
            # Clean up temp file if created
            if img_path != getattr(image_file, 'path', None):
                try:
                    os.unlink(img_path)
                except:
                    pass
                    
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Invalid image: {str(e)}')
    
    @staticmethod
    def optimize_image(image_file, output_path=None, quality=85, max_size=None):
        """
        Resize and compress image for storage.
        
        Args:
            image_file: Uploaded image file or file path.
            output_path (str): Path to save optimized image. If None, returns bytes.
            quality (int): JPEG quality (default 85).
            max_size (tuple): Maximum dimensions (width, height).
            
        Returns:
            str or bytes: Path to optimized image or image bytes.
        """
        try:
            # Handle different input types
            if hasattr(image_file, 'path'):
                img_path = image_file.path
            elif isinstance(image_file, str):
                img_path = image_file
            else:
                # File object
                img_path = image_file
            
            with Image.open(img_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                # Resize if max_size is specified
                if max_size:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                # Auto-orient based on EXIF data
                img = ImageOps.exif_transpose(img)
                # Save optimized image
                if output_path:
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                    return output_path
                else:
                    # Return bytes
                    import io
                    buffer = io.BytesIO()
                    img.save(buffer, 'JPEG', quality=quality, optimize=True)
                    return buffer.getvalue()
                    
        except Exception as e:
            raise ValidationError(f'Failed to optimize image: {str(e)}')
    
    @staticmethod
    def generate_thumbnails(image_file, sizes=None, output_dir=None):
        """
        Generate thumbnails of different sizes.
        
        Args:
            image_file: Uploaded image file or file path.
            sizes (dict): Dictionary of size names to (width, height) tuples.
            output_dir (str): Directory to save thumbnails. If None, uses temp directory.
            
        Returns:
            dict: Mapping of size name to thumbnail file path.
        """
        if sizes is None:
            sizes = ImageProcessingService.THUMBNAIL_SIZES
        
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        try:
            # Handle different input types
            if hasattr(image_file, 'path'):
                img_path = image_file.path
            elif isinstance(image_file, str):
                img_path = image_file
            else:
                # File object
                img_path = image_file
            
            with Image.open(img_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Auto-orient based on EXIF data
                img = ImageOps.exif_transpose(img)
                thumbnails = {}
                for size_name, (width, height) in sizes.items():
                    # Create thumbnail
                    thumb = img.copy()
                    thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
                    # Save thumbnail
                    thumb_path = os.path.join(output_dir, f"thumb_{size_name}_{width}x{height}.jpg")
                    thumb.save(thumb_path, 'JPEG', quality=85, optimize=True)
                    thumbnails[size_name] = thumb_path
                return thumbnails
                
        except Exception as e:
            raise ValidationError(f'Failed to generate thumbnails: {str(e)}')
    
    @staticmethod
    def extract_exif_data(image_file):
        """
        Extract EXIF data from image.
        
        Args:
            image_file: Uploaded image file or file path.
            
        Returns:
            dict: EXIF data or empty dict if no EXIF data.
        """
        try:
            # Handle different input types
            if hasattr(image_file, 'path'):
                img_path = image_file.path
            elif isinstance(image_file, str):
                img_path = image_file
            else:
                # File object
                img_path = image_file
            
            with Image.open(img_path) as img:
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    # Common EXIF tags
                    exif_tags = {
                        36867: 'DateTimeOriginal',
                        306: 'DateTime',
                        271: 'Make',
                        272: 'Model',
                        37377: 'FNumber',
                        37378: 'ExposureTime',
                        37383: 'ExposureProgram',
                        37384: 'SpectralSensitivity',
                        37385: 'ISOSpeedRatings',
                        37386: 'OECF',
                        37396: 'SubjectDistance',
                        37397: 'MeteringMode',
                        37398: 'LightSource',
                        37399: 'Flash',
                        37400: 'FocalLength',
                        41986: 'ExposureMode',
                        41987: 'WhiteBalance',
                        41988: 'DigitalZoomRatio',
                        41989: 'FocalLengthIn35mmFilm',
                        41990: 'SceneCaptureType',
                        41991: 'GainControl',
                        41992: 'Contrast',
                        41993: 'Saturation',
                        41994: 'Sharpness',
                        41995: 'DeviceSettingDescription',
                        41996: 'SubjectDistanceRange',
                        42016: 'ImageUniqueID',
                        42032: 'CameraOwnerName',
                        42033: 'BodySerialNumber',
                        42034: 'LensSpecification',
                        42035: 'LensMake',
                        42036: 'LensModel',
                        42037: 'LensSerialNumber',
                    }
                    
                    for tag_id, tag_name in exif_tags.items():
                        if tag_id in exif:
                            exif_data[tag_name] = exif[tag_id]
                
                return exif_data
                
        except Exception as e:
            return {}
    
    @staticmethod
    def calculate_image_hash(image_file):
        """
        Calculate perceptual hash of image for duplicate detection.
        
        Args:
            image_file: Uploaded image file or file path.
            
        Returns:
            str: Perceptual hash of the image.
        """
        try:
            # Handle different input types
            if hasattr(image_file, 'path'):
                img_path = image_file.path
            elif isinstance(image_file, str):
                img_path = image_file
            else:
                # File object
                img_path = image_file
            
            with Image.open(img_path) as img:
                # Convert to grayscale and resize to 8x8
                img = img.convert('L').resize((8, 8), Image.Resampling.LANCZOS)
                
                # Calculate average pixel value
                pixels = list(img.getdata())
                avg = sum(pixels) / len(pixels)
                
                # Create hash based on pixels above/below average
                hash_bits = ''.join(['1' if pixel > avg else '0' for pixel in pixels])
                
                # Convert to hexadecimal
                hash_hex = hex(int(hash_bits, 2))[2:].zfill(16)
                
                return hash_hex
                
        except Exception as e:
            return None 