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
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer

def debug_upload_process():
    """Debug the complete upload process with detailed logging"""
    
    logger.info("=== DÉBUT DU DEBUG D'UPLOAD ===")
    
    try:
        # Get a test part
        part = Part.objects.first()
        if not part:
            logger.error("Aucune pièce trouvée dans la base de données")
            return
        
        logger.info(f"Pièce de test: {part.name} (ID: {part.id})")
        
        # Test different image scenarios
        test_scenarios = [
            {
                'name': 'JPEG Standard',
                'filename': 'test_standard.jpg',
                'format': 'JPEG',
                'size': (400, 300),
                'color': (255, 0, 0),  # Red
                'mime': 'image/jpeg'
            },
            {
                'name': 'PNG avec transparence',
                'filename': 'test_transparent.png',
                'format': 'PNG',
                'size': (400, 300),
                'color': (0, 255, 0, 128),  # Green with alpha
                'mime': 'image/png'
            },
            {
                'name': 'WEBP moderne',
                'filename': 'test_webp.webp',
                'format': 'WEBP',
                'size': (400, 300),
                'color': (0, 0, 255),  # Blue
                'mime': 'image/webp'
            }
        ]
        
        for scenario in test_scenarios:
            logger.info(f"\n--- Test: {scenario['name']} ---")
            
            try:
                # Create image
                if scenario['format'] == 'PNG':
                    img = Image.new('RGBA', scenario['size'], scenario['color'])
                else:
                    img = Image.new('RGB', scenario['size'], scenario['color'])
                
                logger.info(f"✅ Image créée: {scenario['format']} {scenario['size']}")
                
                # Save to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=scenario['format'])
                img_bytes.seek(0)
                
                logger.info(f"✅ Image sauvegardée en mémoire: {len(img_bytes.read())} bytes")
                img_bytes.seek(0)
                
                # Create SimpleUploadedFile
                uploaded_file = SimpleUploadedFile(
                    scenario['filename'],
                    img_bytes.read(),
                    content_type=scenario['mime']
                )
                
                logger.info(f"✅ SimpleUploadedFile créé: {uploaded_file.name}")
                logger.info(f"   Taille: {uploaded_file.size} bytes")
                logger.info(f"   Content-Type: {uploaded_file.content_type}")
                
                # Test serializer
                data = {
                    'image': uploaded_file,
                    'is_primary': False
                }
                
                logger.info(f"📝 Test du serializer avec données: {list(data.keys())}")
                
                serializer = PartImageUploadSerializer(data=data)
                
                if serializer.is_valid():
                    logger.info("✅ Serializer validation RÉUSSIE")
                    
                    # Save image
                    image = serializer.save(part=part)
                    logger.info(f"✅ Image sauvegardée en BDD: {image.image.name}")
                    logger.info(f"   URL: {image.image.url}")
                    logger.info(f"   Primaire: {image.is_primary}")
                    
                    # Verify file exists
                    if image.image and hasattr(image.image, 'path'):
                        import os
                        if os.path.exists(image.image.path):
                            file_size = os.path.getsize(image.image.path)
                            logger.info(f"✅ Fichier existe sur disque: {file_size} bytes")
                        else:
                            logger.error(f"❌ Fichier NON TROUVÉ sur disque: {image.image.path}")
                    
                else:
                    logger.error("❌ Serializer validation ÉCHOUÉE")
                    logger.error(f"   Erreurs: {serializer.errors}")
                    
                    # Analyser les erreurs spécifiques
                    if 'image' in serializer.errors:
                        for error in serializer.errors['image']:
                            logger.error(f"   Erreur image: {error}")
                            
            except Exception as e:
                logger.error(f"❌ Exception dans le test {scenario['name']}: {str(e)}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
        
        # Final check
        logger.info("\n=== VÉRIFICATION FINALE ===")
        all_images = PartImage.objects.filter(part=part)
        logger.info(f"Total d'images pour la pièce {part.name}: {all_images.count()}")
        
        for img in all_images:
            logger.info(f"  - {img.image.name} (Primaire: {img.is_primary})")
            logger.info(f"    URL: {img.image.url}")
            
            # Test URL access
            full_url = f"http://localhost:8000{img.image.url}"
            logger.info(f"    URL complète: {full_url}")
        
        logger.info("=== FIN DU DEBUG ===")
        
    except Exception as e:
        logger.error(f"Erreur générale dans le debug: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    debug_upload_process()
