import os
import django
import logging
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from marketplace.models import Part

def test_real_http_upload():
    """Test real HTTP upload like frontend does"""
    
    logger.info("=== TEST D'UPLOAD HTTP RÉEL ===")
    
    try:
        # Get a test part and user
        part = Part.objects.first()
        if not part:
            logger.error("Aucune pièce trouvée")
            return
            
        User = get_user_model()
        user = User.objects.get(username='jaaferg')  # The supplier user
        
        logger.info(f"Test pour la pièce: {part.name} (ID: {part.id})")
        logger.info(f"Utilisateur: {user.username}")
        
        # Create test image
        img = Image.new('RGB', (400, 300), (0, 255, 0))  # Green image
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Create uploaded file like frontend
        test_file = SimpleUploadedFile(
            "test_upload_real.jpg",
            img_bytes.read(),
            content_type="image/jpeg"
        )
        
        # Create Django test client
        client = Client()
        
        # Login the user with correct credentials
        client.login(username='jaaferg', password='Jk95803281')
        
        # Make POST request to upload endpoint
        upload_url = f'/api/parts/{part.id}/images/'
        
        logger.info(f"URL d'upload: {upload_url}")
        logger.info(f"Fichier: {test_file.name} ({test_file.size} bytes)")
        
        response = client.post(upload_url, {
            'image': test_file,
            'is_primary': 'true'
        }, format='multipart')
        
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response content: {response.content.decode()}")
        
        if response.status_code == 201:
            logger.info("✅ UPLOAD HTTP RÉUSSIE!")
            
            # Parse response
            import json
            response_data = response.json()
            logger.info(f"Image URL: {response_data.get('image_url', 'N/A')}")
            
            # Verify in database
            from marketplace.models import PartImage
            images = PartImage.objects.filter(part=part)
            logger.info(f"Total d'images en BDD: {images.count()}")
            
            for img in images:
                logger.info(f"  - {img.image.name} (Primaire: {img.is_primary})")
                logger.info(f"    URL: http://localhost:8000{img.image.url}")
                
        else:
            logger.error("❌ UPLOAD HTTP ÉCHOUÉ!")
            logger.error(f"Erreurs: {response.content.decode()}")
            
    except Exception as e:
        logger.error(f"Erreur lors du test: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("=== FIN DU TEST ===")

if __name__ == '__main__':
    test_real_http_upload()
