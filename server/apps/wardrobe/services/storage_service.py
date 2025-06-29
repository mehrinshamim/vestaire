import os
import tempfile
import requests
from urllib.parse import urlparse
from django.conf import settings
from django.core.exceptions import ValidationError
import cloudinary
import cloudinary.uploader
import cloudinary.api

class StorageService:
    def __init__(self):
        """Initialize Cloudinary configuration."""
        # Cloudinary is already configured in settings
        pass
    
    def upload_image(self, image_file, folder_path, public_id=None, overwrite=False):
        """
        Upload image to Cloudinary.
        
        Args:
            image_file: Image file object, bytes, or file path.
            folder_path (str): Path/folder in cloud storage.
            public_id (str): Custom public ID for the image.
            overwrite (bool): Whether to overwrite existing image.
            
        Returns:
            str: Public URL of uploaded image.
        """
        try:
            # Prepare upload parameters
            upload_params = {
                'folder': folder_path,
                'resource_type': 'image',
                'overwrite': overwrite,
                'transformation': [
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            }
            
            if public_id:
                upload_params['public_id'] = public_id
            
            # Handle different input types
            if hasattr(image_file, 'read'):
                # File object
                result = cloudinary.uploader.upload(
                    image_file,
                    **upload_params
                )
            elif isinstance(image_file, bytes):
                # Bytes data
                result = cloudinary.uploader.upload(
                    image_file,
                    **upload_params
                )
            elif isinstance(image_file, str):
                # File path
                if os.path.exists(image_file):
                    result = cloudinary.uploader.upload(
                        image_file,
                        **upload_params
                    )
                else:
                    raise ValidationError(f"File not found: {image_file}")
            else:
                raise ValidationError("Invalid image file type")
            
            return result['secure_url']
            
        except Exception as e:
            raise ValidationError(f"Failed to upload image: {str(e)}")
    
    def upload_image_from_url(self, image_url, folder_path, public_id=None):
        """
        Upload image from URL to Cloudinary.
        
        Args:
            image_url (str): URL of the image to upload.
            folder_path (str): Path/folder in cloud storage.
            public_id (str): Custom public ID for the image.
            
        Returns:
            str: Public URL of uploaded image.
        """
        try:
            upload_params = {
                'folder': folder_path,
                'resource_type': 'image',
                'transformation': [
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            }
            
            if public_id:
                upload_params['public_id'] = public_id
            
            result = cloudinary.uploader.upload(
                image_url,
                **upload_params
            )
            
            return result['secure_url']
            
        except Exception as e:
            raise ValidationError(f"Failed to upload image from URL: {str(e)}")
    
    def delete_image(self, image_url):
        """
        Delete image from Cloudinary using its public_id.
        
        Args:
            image_url (str): Public URL of the image to delete.
            
        Returns:
            bool: True if deleted, False otherwise.
        """
        try:
            public_id = self._extract_public_id(image_url)
            if not public_id:
                return False
            
            result = cloudinary.uploader.destroy(public_id, resource_type="image")
            return result.get('result') == 'ok'
            
        except Exception as e:
            print(f"Failed to delete image: {str(e)}")
            return False
    
    def download_temp(self, image_url, filename=None):
        """
        Download image from URL to temporary file.
        
        Args:
            image_url (str): URL of the image to download.
            filename (str): Optional filename for the temp file.
            
        Returns:
            str: Path to temporary file.
        """
        try:
            # Create temporary file
            if filename:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
            else:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            
            temp_path = temp_file.name
            temp_file.close()
            
            # Download image
            response = requests.get(image_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
            
        except Exception as e:
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise ValidationError(f"Failed to download image: {str(e)}")
    
    def get_image_info(self, image_url):
        """
        Get information about an image from Cloudinary.
        
        Args:
            image_url (str): Public URL of the image.
            
        Returns:
            dict: Image information.
        """
        try:
            public_id = self._extract_public_id(image_url)
            if not public_id:
                return None
            
            result = cloudinary.api.resource(public_id, resource_type="image")
            return result
            
        except Exception as e:
            print(f"Failed to get image info: {str(e)}")
            return None
    
    def generate_thumbnail_url(self, image_url, width=300, height=300, crop='fill'):
        """
        Generate thumbnail URL for an image.
        
        Args:
            image_url (str): Original image URL.
            width (int): Thumbnail width.
            height (int): Thumbnail height.
            crop (str): Crop mode.
            
        Returns:
            str: Thumbnail URL.
        """
        try:
            public_id = self._extract_public_id(image_url)
            if not public_id:
                return image_url
            
            # Generate transformation URL
            transformation = f"w_{width},h_{height},c_{crop}"
            thumbnail_url = cloudinary.CloudinaryImage(public_id).build_url(
                transformation=transformation
            )
            
            return thumbnail_url
            
        except Exception as e:
            print(f"Failed to generate thumbnail URL: {str(e)}")
            return image_url
    
    def optimize_image_url(self, image_url, quality='auto:good', format='auto'):
        """
        Generate optimized image URL.
        
        Args:
            image_url (str): Original image URL.
            quality (str): Image quality.
            format (str): Image format.
            
        Returns:
            str: Optimized image URL.
        """
        try:
            public_id = self._extract_public_id(image_url)
            if not public_id:
                return image_url
            
            # Generate optimization URL
            transformation = f"q_{quality},f_{format}"
            optimized_url = cloudinary.CloudinaryImage(public_id).build_url(
                transformation=transformation
            )
            
            return optimized_url
            
        except Exception as e:
            print(f"Failed to generate optimized URL: {str(e)}")
            return image_url

    def _extract_public_id(self, image_url):
        """
        Extract public_id from Cloudinary URL.
        
        Args:
            image_url (str): Cloudinary image URL.
            
        Returns:
            str: Public ID or None if not a Cloudinary URL.
        """
        try:
            parsed_url = urlparse(image_url)
            
            # Check if it's a Cloudinary URL
            if 'cloudinary.com' not in parsed_url.netloc:
                return None
            
            # Extract path components
            path_parts = parsed_url.path.split('/')
            
            # Find the upload part
            try:
                upload_index = path_parts.index('upload')
                # Everything after 'upload' and before the version (if present)
                public_id_parts = path_parts[upload_index + 1:]
                
                # Remove version if present
                if public_id_parts and public_id_parts[0].startswith('v'):
                    public_id_parts = public_id_parts[1:]
                
                # Remove file extension
                if public_id_parts:
                    filename = public_id_parts[-1]
                    if '.' in filename:
                        public_id_parts[-1] = filename.rsplit('.', 1)[0]
                
                public_id = '/'.join(public_id_parts)
                return public_id
                
            except ValueError:
                return None
                
        except Exception as e:
            print(f"Failed to extract public_id: {str(e)}")
            return None
    
    def list_images(self, folder_path=None, max_results=100):
        """
        List images in a folder.
        
        Args:
            folder_path (str): Folder path to list.
            max_results (int): Maximum number of results.
            
        Returns:
            list: List of image information.
        """
        try:
            params = {
                'max_results': max_results,
                'resource_type': 'image'
            }
            
            if folder_path:
                params['prefix'] = folder_path
            
            result = cloudinary.api.resources(**params)
            return result.get('resources', [])
            
        except Exception as e:
            print(f"Failed to list images: {str(e)}")
            return []
    
    def create_folder(self, folder_path):
        """
        Create a folder in Cloudinary (folders are created automatically on upload).
        
        Args:
            folder_path (str): Folder path to create.
            
        Returns:
            bool: True if successful.
        """
        try:
            # Upload a placeholder image to create the folder
            placeholder_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
            
            self.upload_image(
                placeholder_data,
                folder_path,
                public_id=f"{folder_path}/.placeholder",
                overwrite=True
            )
            
            return True
            
        except Exception as e:
            print(f"Failed to create folder: {str(e)}")
            return False 