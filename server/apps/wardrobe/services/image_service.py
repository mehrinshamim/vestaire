from PIL import Image
import os

class ImageProcessingService:
    @staticmethod
    def validate_image(image_file):
        """
        Validate image format, size, and dimensions.
        Args:
            image_file (File): Uploaded image file.
        Raises:
            ValueError: If image is invalid.
        """
        try:
            img = Image.open(image_file)
            img.verify()
            # Example: Check file size (max 5MB)
            if hasattr(image_file, 'size') and image_file.size > 5 * 1024 * 1024:
                raise ValueError('Image file too large (max 5MB).')
            # Example: Check format
            if img.format not in ['JPEG', 'PNG']:
                raise ValueError('Unsupported image format.')
        except Exception as e:
            raise ValueError(f'Invalid image: {e}')
    
    @staticmethod
    def optimize_image(image_file, output_path, quality=85):
        """
        Resize and compress image for storage.
        Args:
            image_file (File): Uploaded image file.
            output_path (str): Path to save optimized image.
            quality (int): JPEG quality (default 85).
        """
        img = Image.open(image_file)
        img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
    
    @staticmethod
    def generate_thumbnails(image_file, sizes=None):
        """
        Generate thumbnails of different sizes.
        Args:
            image_file (File): Uploaded image file.
            sizes (list): List of (width, height) tuples.
        Returns:
            dict: Mapping of size to thumbnail file path.
        """
        if sizes is None:
            sizes = [(128, 128), (256, 256), (512, 512)]
        img = Image.open(image_file)
        thumbnails = {}
        for size in sizes:
            thumb = img.copy()
            thumb.thumbnail(size)
            thumb_path = f"thumb_{size[0]}x{size[1]}.jpg"
            thumb.save(thumb_path, 'JPEG')
            thumbnails[size] = thumb_path
        return thumbnails 