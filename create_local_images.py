import os
import django
from django.core.files.base import ContentFile
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage

def create_simple_images():
    """Create simple colored images for parts"""
    
    # Define colors and names for different part types
    part_configs = [
        {'color': (255, 107, 107), 'name': 'engine_part.jpg', 'text': 'Engine'},
        {'color': (78, 205, 196), 'name': 'brake_part.jpg', 'text': 'Brake'},
        {'color': (69, 183, 209), 'name': 'filter_part.jpg', 'text': 'Filter'},
        {'color': (150, 206, 180), 'name': 'light_part.jpg', 'text': 'Light'},
        {'color': (255, 234, 167), 'name': 'electric_part.jpg', 'text': 'Electric'},
    ]
    
    parts = Part.objects.all()[:5]  # Get first 5 parts
    
    if not parts.exists():
        print("No parts found in database. Please create some parts first.")
        return
    
    print(f"Found {parts.count()} parts. Creating images...")
    
    for i, part in enumerate(parts):
        if i >= len(part_configs):
            break
            
        config = part_configs[i]
        
        try:
            # Create a simple image
            img = Image.new('RGB', (400, 300), config['color'])
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Save image to part
            part_image = PartImage(
                part=part,
                is_primary=True  # Make this the primary image
            )
            
            # Save the created image
            part_image.image.save(
                config['name'],
                ContentFile(img_bytes.read()),
                save=True
            )
            
            print(f"Created image '{config['name']}' for part '{part.name}'")
                
        except Exception as e:
            print(f"Error creating image for part '{part.name}': {str(e)}")
    
    print("Image creation completed!")

if __name__ == '__main__':
    create_simple_images()
