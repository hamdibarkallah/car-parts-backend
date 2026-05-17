import os
import django
from django.core.files.base import ContentFile
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage

def add_image_to_jfdfs():
    """Add an image to the JFDFS part"""
    
    try:
        # Find the JFDFS part
        jfdfs_part = Part.objects.get(name='JFDFS')
        print(f"Found part: {jfdfs_part.name} (ID: {jfdfs_part.id})")
        
        # Create a simple image for JFDFS part
        img = Image.new('RGB', (400, 300), (255, 165, 0))  # Orange color
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Create and save the image
        part_image = PartImage(
            part=jfdfs_part,
            is_primary=True
        )
        
        part_image.image.save(
            'jfdfs_part.jpg',
            ContentFile(img_bytes.read()),
            save=True
        )
        
        print(f"Successfully added image to part '{jfdfs_part.name}'")
        print(f"Image URL: {part_image.image.url}")
        
    except Part.DoesNotExist:
        print("Part 'JFDFS' not found in database")
    except Exception as e:
        print(f"Error adding image: {str(e)}")

if __name__ == '__main__':
    add_image_to_jfdfs()
