import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer

def test_direct_upload():
    """Test direct image upload functionality"""
    
    try:
        # Get a test part
        part = Part.objects.first()
        if not part:
            print("No parts found in database")
            return
        
        print(f"Testing upload for part: {part.name} (ID: {part.id})")
        
        # Create a test image file
        test_image_content = b'fake image content for testing'
        test_file = SimpleUploadedFile(
            "test_real_upload.jpg",
            test_image_content,
            content_type="image/jpeg"
        )
        
        # Test serializer directly
        data = {
            'image': test_file,
            'is_primary': True
        }
        
        serializer = PartImageUploadSerializer(data=data)
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            image = serializer.save(part=part)
            print(f"✅ Image saved: {image.image.name}")
            print(f"   Primary: {image.is_primary}")
            print(f"   URL: {image.image.url}")
            
            # Verify it's in database
            images = PartImage.objects.filter(part=part)
            print(f"   Total images for part: {images.count()}")
        else:
            print("❌ Serializer validation failed:")
            print(serializer.errors)
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_direct_upload()
