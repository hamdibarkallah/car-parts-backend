import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer, PartImageSerializer

def fix_image_display_issue():
    """Fix image display issue by ensuring all parts have proper images"""
    
    try:
        # Get all parts that don't have images or have broken images
        parts_without_images = []
        all_parts = Part.objects.all()
        
        print(f"Checking {all_parts.count()} parts for image issues...")
        
        for part in all_parts:
            images = part.images.all()
            if not images.exists():
                parts_without_images.append(part)
                print(f"❌ Part '{part.name}' (ID: {part.id}) has NO images")
            else:
                primary_image = images.filter(is_primary=True).first()
                if not primary_image:
                    # Set first image as primary
                    first_image = images.first()
                    first_image.is_primary = True
                    first_image.save()
                    print(f"🔧 Part '{part.name}' - Set first image as primary")
                else:
                    print(f"✅ Part '{part.name}' - Has primary image: {primary_image.image.name}")
        
        # Create images for parts that don't have any
        if parts_without_images:
            print(f"\n📝 Creating images for {len(parts_without_images)} parts without images...")
            
            for i, part in enumerate(parts_without_images):
                # Create a unique colored image for each part
                colors = [
                    (255, 99, 71),   # Red
                    (75, 192, 192),  # Teal  
                    (69, 183, 209),  # Blue
                    (150, 206, 180), # Green
                    (255, 234, 167), # Yellow
                    (199, 125, 255), # Purple
                    (255, 154, 0),   # Orange
                    (231, 76, 60),   # Deep Orange
                    (0, 123, 255),   # Blue
                    (255, 193, 7),   # Amber
                ]
                color = colors[i % len(colors)]
                
                # Create image with part name
                img = Image.new('RGB', (400, 300), color)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)
                
                # Create and save image
                test_file = SimpleUploadedFile(
                    f"{part.name.lower().replace(' ', '_')}_image.jpg",
                    img_bytes.read(),
                    content_type="image/jpeg"
                )
                
                data = {
                    'image': test_file,
                    'is_primary': True
                }
                
                serializer = PartImageUploadSerializer(data=data)
                if serializer.is_valid():
                    image = serializer.save(part=part)
                    print(f"✅ Created image for '{part.name}': {image.image.name}")
                else:
                    print(f"❌ Failed to create image for '{part.name}': {serializer.errors}")
        
        # Final verification
        print(f"\n🔍 Final verification:")
        all_parts_after = Part.objects.all()
        parts_with_images = 0
        parts_with_primary = 0
        
        for part in all_parts_after:
            images = part.images.all()
            if images.exists():
                parts_with_images += 1
                primary_image = images.filter(is_primary=True).first()
                if primary_image:
                    parts_with_primary += 1
                    print(f"✅ {part.name}: {primary_image.image.url}")
                else:
                    print(f"⚠️  {part.name}: Has images but NO primary")
            else:
                print(f"❌ {part.name}: NO images")
        
        print(f"\n📊 Summary:")
        print(f"   Total parts: {all_parts_after.count()}")
        print(f"   Parts with images: {parts_with_images}")
        print(f"   Parts with primary image: {parts_with_primary}")
        print(f"   Parts missing images: {all_parts_after.count() - parts_with_images}")
        
        if parts_with_primary == all_parts_after.count():
            print("🎉 SUCCESS: All parts now have primary images!")
        else:
            print("⚠️  WARNING: Some parts still missing primary images")
            
    except Exception as e:
        print(f"Error during fix: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_image_display_issue()
