import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage
from marketplace.views import PartImageListCreateView

def test_image_upload():
    """Test image upload functionality"""
    
    try:
        # Get a test part
        part = Part.objects.first()
        if not part:
            print("No parts found in database")
            return
        
        print(f"Testing upload for part: {part.name} (ID: {part.id})")
        
        # Get a supplier user (the owner of the part)
        User = get_user_model()
        supplier_user = part.supplier.user
        print(f"Part owner: {supplier_user.username}")
        
        # Create a test image file
        test_image_content = b'fake image content for testing'
        test_file = SimpleUploadedFile(
            "test_upload.jpg",
            test_image_content,
            content_type="image/jpeg"
        )
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post(f'/api/parts/{part.id}/images/', {
            'image': test_file,
            'is_primary': True
        }, format='multipart')
        
        # Authenticate the request
        request.user = supplier_user
        
        # Test the view
        view = PartImageListCreateView()
        response = view.post(request, part_id=part.id)
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        if response.status_code == 201:
            print("✅ Upload successful!")
            # Check if image was actually saved
            images = PartImage.objects.filter(part=part)
            print(f"Total images for part: {images.count()}")
            for img in images:
                print(f"  - {img.image.name} (Primary: {img.is_primary})")
        else:
            print("❌ Upload failed!")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_image_upload()
