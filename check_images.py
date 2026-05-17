import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part

def check_images():
    """Check if parts have images and their URLs"""
    
    parts = Part.objects.all()[:3]
    
    for part in parts:
        print(f'Part: {part.name}')
        primary_image = part.images.filter(is_primary=True).first()
        if primary_image:
            print(f'Primary image: {primary_image.image.name}')
            print(f'Image URL: {primary_image.image.url}')
        else:
            print('No primary image found')
        print('---')

if __name__ == '__main__':
    check_images()
