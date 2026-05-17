import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer

def test_valid_image_upload():
    """Test upload with a valid image"""
    
    try:
        # Get a test part
        part = Part.objects.first()
        if not part:
            print("No parts found in database")
            return
        
        print(f"Testing upload for part: {part.name} (ID: {part.id})")
        
        # Create a real image using PIL
        img = Image.new('RGB', (400, 300), (255, 0, 0))  # Red image
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Create a valid image file
        test_file = SimpleUploadedFile(
            "valid_test_image.jpg",
            img_bytes.read(),
            content_type="image/jpeg"
        )
        
        # Test serializer
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
            print(f"   Full URL: http://localhost:8000{image.image.url}")
            
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
    test_valid_image_upload()
