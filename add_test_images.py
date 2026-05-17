import os
import django
import urllib.request
from django.core.files.base import ContentFile
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage

def download_and_add_images():
    """Download sample car part images and add them to existing parts"""
    
    # Sample car part image URLs (using placeholder images)
    sample_images = [
        {
            'url': 'https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=Engine+Part',
            'name': 'engine_part.jpg'
        },
        {
            'url': 'https://via.placeholder.com/400x300/4ECDC4/FFFFFF?text=Brake+Pad',
            'name': 'brake_pad.jpg'
        },
        {
            'url': 'https://via.placeholder.com/400x300/45B7D1/FFFFFF?text=Oil+Filter',
            'name': 'oil_filter.jpg'
        },
        {
            'url': 'https://via.placeholder.com/400x300/96CEB4/FFFFFF?text=Headlight',
            'name': 'headlight.jpg'
        },
        {
            'url': 'https://via.placeholder.com/400x300/FFEAA7/000000?text=Battery',
            'name': 'battery.jpg'
        }
    ]
    
    parts = Part.objects.all()[:5]  # Get first 5 parts
    
    if not parts.exists():
        print("No parts found in database. Please create some parts first.")
        return
    
    print(f"Found {parts.count()} parts. Adding images...")
    
    for i, part in enumerate(parts):
        if i >= len(sample_images):
            break
            
        image_data = sample_images[i]
        
        try:
            # Download image
            with urllib.request.urlopen(image_data['url']) as response:
                if response.status == 200:
                    # Save image to part
                    part_image = PartImage(
                        part=part,
                        is_primary=True  # Make this the primary image
                    )
                    
                    # Save the downloaded image
                    part_image.image.save(
                        image_data['name'],
                        ContentFile(response.read()),
                        save=True
                    )
                    
                    print(f"Added image '{image_data['name']}' to part '{part.name}'")
                else:
                    print(f"Failed to download image from {image_data['url']}")
                    
        except Exception as e:
            print(f"Error adding image to part '{part.name}': {str(e)}")
    
    print("Image addition completed!")

if __name__ == '__main__':
    download_and_add_images()
