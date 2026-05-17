import os
import django
import logging
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer

def create_ultimate_image_solution():
    """Create ultimate solution for image upload and display"""
    
    logger.info("=== SOLUTION ULTIME POUR IMAGES ===")
    
    try:
        # Get all parts
        all_parts = Part.objects.all()
        logger.info(f"Traitement de {all_parts.count()} pièces...")
        
        for i, part in enumerate(all_parts):
            logger.info(f"\n--- Pièce {i+1}/{all_parts.count()}: {part.name} ---")
            
            # Check existing images
            existing_images = part.images.all()
            if existing_images.exists():
                primary_image = existing_images.filter(is_primary=True).first()
                if primary_image:
                    logger.info(f"✅ Déjà une image primaire: {primary_image.image.name}")
                    logger.info(f"   URL: http://localhost:8000{primary_image.image.url}")
                    continue
            
            # Create unique image for each part with different colors
            colors = [
                (255, 99, 71),    # Red
                (75, 192, 192),   # Teal
                (69, 183, 209),   # Blue
                (150, 206, 180),  # Green
                (255, 234, 167),  # Yellow
                (199, 125, 255),  # Purple
                (255, 154, 0),    # Orange
                (231, 76, 60),    # Deep Orange
                (0, 123, 255),    # Bright Blue
                (255, 193, 7),    # Amber
            ]
            
            color = colors[i % len(colors)]
            
            # Create high-quality image
            img = Image.new('RGB', (600, 450), color)
            
            # Add text overlay with part name
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Add part name text
            text = part.name[:15]  # Truncate if too long
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Center text
            x = (600 - text_width) // 2
            y = (450 - text_height) // 2
            
            # Add text with shadow for better visibility
            draw.text((x-2, y-2), text, fill=(0, 0, 0), font=font)  # Shadow
            draw.text((x, y), text, fill=(255, 255, 255), font=font)  # White text
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            
            # Create uploaded file
            filename = f"{part.name.lower().replace(' ', '_').replace('-', '_')}_ultimate.jpg"
            uploaded_file = SimpleUploadedFile(
                filename,
                img_bytes.read(),
                content_type="image/jpeg"
            )
            
            # Upload via serializer
            data = {
                'image': uploaded_file,
                'is_primary': True
            }
            
            serializer = PartImageUploadSerializer(data=data)
            if serializer.is_valid():
                image = serializer.save(part=part)
                logger.info(f"✅ Image créée: {image.image.name}")
                logger.info(f"   Taille: {uploaded_file.size} bytes")
                logger.info(f"   URL: http://localhost:8000{image.image.url}")
                logger.info(f"   Primaire: {image.is_primary}")
                
                # Verify file exists
                if hasattr(image.image, 'path'):
                    import os
                    if os.path.exists(image.image.path):
                        file_size = os.path.getsize(image.image.path)
                        logger.info(f"   Fichier sur disque: {file_size} bytes ✅")
                    else:
                        logger.error(f"   Fichier MANQUANT sur disque: {image.image.path} ❌")
                        
            else:
                logger.error(f"❌ Erreur serializer: {serializer.errors}")
        
        # Final verification
        logger.info(f"\n=== VÉRIFICATION FINALE ===")
        
        total_parts = Part.objects.count()
        parts_with_images = 0
        parts_with_primary = 0
        
        for part in Part.objects.all():
            images = part.images.all()
            if images.exists():
                parts_with_images += 1
                primary_image = images.filter(is_primary=True).first()
                if primary_image:
                    parts_with_primary += 1
                    logger.info(f"✅ {part.name}: http://localhost:8000{primary_image.image.url}")
                else:
                    logger.warning(f"⚠️  {part.name}: Images mais PAS de primaire")
            else:
                logger.error(f"❌ {part.name}: PAS d'images")
        
        logger.info(f"\n📊 RÉSULTATS FINAUX:")
        logger.info(f"   Total pièces: {total_parts}")
        logger.info(f"   Pièces avec images: {parts_with_images}")
        logger.info(f"   Pièces avec image primaire: {parts_with_primary}")
        logger.info(f"   Pièces sans images: {total_parts - parts_with_images}")
        
        if parts_with_primary == total_parts:
            logger.info("🎉 SUCCÈS TOTAL: Toutes les pièces ont des images primaires!")
            logger.info("📝 Les images devraient maintenant s'afficher dans 'My Parts'!")
        else:
            logger.warning(f"⚠️  {total_parts - parts_with_primary} pièces n'ont pas d'images primaires")
            
        logger.info("=== SOLUTION TERMINÉE ===")
        
    except Exception as e:
        logger.error(f"Erreur lors de la solution: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    create_ultimate_image_solution()
