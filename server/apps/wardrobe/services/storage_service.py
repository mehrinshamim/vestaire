import cloudinary.uploader

class StorageService:
    def __init__(self):
        # TODO: Initialize Supabase or Cloudinary client here
        pass
    
    def upload_image(self, image_file, folder_path):
        """
        Upload image to Cloudinary.
        Args:
            image_file (File): Image file to upload.
            folder_path (str): Path/folder in cloud storage.
        Returns:
            str: Public URL of uploaded image.
        """
        result = cloudinary.uploader.upload(
            image_file,
            folder=folder_path,
            resource_type="image"
        )
        return result['secure_url']
    
    def delete_image(self, image_url):
        """
        Delete image from Cloudinary using its public_id.
        Args:
            image_url (str): Public URL of the image to delete.
        Returns:
            bool: True if deleted, False otherwise.
        """
        # Extract public_id from the URL or store it when uploading
        public_id = self._extract_public_id(image_url)
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return result.get('result') == 'ok'

    def _extract_public_id(self, image_url):
        # Implement logic to extract public_id from the image_url
        # Example: https://res.cloudinary.com/<cloud_name>/image/upload/v1234567890/folder/filename.jpg
        # public_id = 'folder/filename'
        # You may want to store public_id in your DB for easy deletion
        pass 