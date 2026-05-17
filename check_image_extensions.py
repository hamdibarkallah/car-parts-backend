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

def test_all_image_extensions():
    """Test upload with all common image extensions"""
    
    # All common image formats and their PIL support
    image_formats = {
        'JPEG': {'ext': 'jpg', 'format': 'JPEG', 'mode': 'RGB'},
        'JPEG2000': {'ext': 'jp2', 'format': 'JPEG2000', 'mode': 'RGB'},
        'PNG': {'ext': 'png', 'format': 'PNG', 'mode': 'RGBA'},
        'WEBP': {'ext': 'webp', 'format': 'WEBP', 'mode': 'RGB'},
        'GIF': {'ext': 'gif', 'format': 'GIF', 'mode': 'RGB'},
        'BMP': {'ext': 'bmp', 'format': 'BMP', 'mode': 'RGB'},
        'TIFF': {'ext': 'tiff', 'format': 'TIFF', 'mode': 'RGB'},
        'ICO': {'ext': 'ico', 'format': 'ICO', 'mode': 'RGB'},
        'PPM': {'ext': 'ppm', 'format': 'PPM', 'mode': 'RGB'},
        'PGM': {'ext': 'pgm', 'format': 'PGM', 'mode': 'L'},
        'PBm': {'ext': 'pbm', 'format': 'PBM', 'mode': '1'},
    }
    
    # Get a test part
    part = Part.objects.first()
    if not part:
        print("No parts found in database")
        return
    
    print(f"Testing all image formats for part: {part.name} (ID: {part.id})")
    print("=" * 60)
    
    successful_uploads = []
    failed_uploads = []
    
    for format_name, config in image_formats.items():
        try:
            # Create image based on format
            if config['mode'] == 'RGBA':
                img = Image.new('RGBA', (200, 150), (255, 0, 0, 128))  # Red with alpha
            elif config['mode'] == 'L':
                img = Image.new('L', (200, 150), 128)  # Grayscale
            elif config['mode'] == '1':
                img = Image.new('1', (200, 150), 0)  # Black and white
            else:
                img = Image.new('RGB', (200, 150), (255, 0, 0))  # Red
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=config['format'])
            img_bytes.seek(0)
            
            # Create uploaded file
            filename = f"test_image.{config['ext']}"
            test_file = SimpleUploadedFile(
                filename,
                img_bytes.read(),
                content_type=f"image/{config['ext']}"
            )
            
            # Test serializer
            data = {
                'image': test_file,
                'is_primary': False
            }
            
            serializer = PartImageUploadSerializer(data=data)
            if serializer.is_valid():
                image = serializer.save(part=part)
                successful_uploads.append({
                    'format': format_name,
                    'ext': config['ext'],
                    'filename': image.image.name,
                    'url': f"http://localhost:8000{image.image.url}"
                })
                print(f"✅ {format_name} ({config['ext']}) - SUCCESS")
            else:
                failed_uploads.append({
                    'format': format_name,
                    'ext': config['ext'],
                    'error': serializer.errors
                })
                print(f"❌ {format_name} ({config['ext']}) - FAILED: {serializer.errors}")
                
        except Exception as e:
            failed_uploads.append({
                'format': format_name,
                'ext': config['ext'],
                'error': str(e)
            })
            print(f"❌ {format_name} ({config['ext']}) - ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"✅ Successful uploads: {len(successful_uploads)}")
    print(f"❌ Failed uploads: {len(failed_uploads)}")
    
    if successful_uploads:
        print(f"\n✅ SUPPORTED FORMATS:")
        for upload in successful_uploads:
            print(f"   • {upload['format']} (.{upload['ext']}) - {upload['url']}")
    
    if failed_uploads:
        print(f"\n❌ UNSUPPORTED FORMATS:")
        for upload in failed_uploads:
            print(f"   • {upload['format']} (.{upload['ext']}) - {upload['error']}")

if __name__ == '__main__':
    test_all_image_extensions()
