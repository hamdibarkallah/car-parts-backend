import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw, ImageFont
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer

def ultimate_image_fix():
    """Solution ultime pour garantir l'upload et l'affichage des images"""
    
    print("🚀 SOLUTION ULTIME POUR LES IMAGES")
    print("=" * 60)
    
    try:
        # Get all parts
        all_parts = Part.objects.all()
        print(f"Traitement de {all_parts.count()} pièces...")
        
        for i, part in enumerate(all_parts):
            print(f"\n📝 Pièce {i+1}/{all_parts.count()}: {part.name}")
            
            # Check existing images
            existing_images = part.images.all()
            if existing_images.exists():
                primary_image = existing_images.filter(is_primary=True).first()
                if primary_image:
                    print(f"✅ Déjà une image primaire: {primary_image.image.name}")
                    print(f"   URL: http://localhost:8000{primary_image.image.url}")
                    continue
                else:
                    print("⚠️  Images existantes mais PAS de primaire")
                    # Set first image as primary
                    first_image = existing_images.first()
                    first_image.is_primary = True
                    first_image.save()
                    print(f"✅ Première image définie comme primaire: {first_image.image.name}")
                    continue
            else:
                print("❌ Aucune image existante")
            
            # Create a professional image with part name
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
            img = Image.new('RGB', (800, 600), color)
            
            # Add professional text
            try:
                # Try to use a nice font
                draw = ImageDraw.Draw(img)
                
                # Add part name
                font_size = 48
                text = part.name.upper()
                
                # Calculate text position (centered)
                bbox = draw.textbbox((0, 0), text, font=ImageFont.load_default())
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (800 - text_width) // 2
                y = (600 - text_height) // 2 - 50
                
                # Draw text with shadow for better visibility
                draw.text((x-3, y-3), text, fill=(0, 0, 0))  # Shadow
                draw.text((x, y), text, fill=(255, 255, 255))  # White text
                
                # Add part reference
                ref_text = f"REF: {part.reference}"
                ref_font_size = 24
                ref_bbox = draw.textbbox((0, 0), ref_text, font=ImageFont.load_default())
                ref_width = ref_bbox[2] - ref_bbox[0]
                ref_x = (800 - ref_width) // 2
                ref_y = y + 80
                
                draw.text((ref_x-2, ref_y-2), ref_text, fill=(0, 0, 0))  # Shadow
                draw.text((ref_x, ref_y), ref_text, fill=(255, 255, 255))  # White text
                
                # Add price
                price_text = f"{part.price} TND"
                price_y = ref_y + 60
                draw.text((x-2, price_y-2), price_text, fill=(0, 0, 0))  # Shadow
                draw.text((x, price_y), price_text, fill=(255, 255, 0))  # White text
                
            except Exception as e:
                print(f"   Erreur lors de l'ajout du texte: {e}")
            
            # Save to high-quality JPEG
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95, optimize=True)
            img_bytes.seek(0)
            
            # Create uploaded file
            filename = f"{part.name.lower().replace(' ', '_').replace('-', '_')}_professional.jpg"
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
                print(f"✅ Image créée et uploadée: {image.image.name}")
                print(f"   Taille: {uploaded_file.size} bytes")
                print(f"   URL: http://localhost:8000{image.image.url}")
                print(f"   Primaire: {image.is_primary}")
                
                # Verify file was saved
                if hasattr(image.image, 'path'):
                    import os
                    if os.path.exists(image.image.path):
                        file_size = os.path.getsize(image.image.path)
                        print(f"   Fichier sur disque: {file_size} bytes ✅")
                    else:
                        print(f"   Fichier MANQUANT sur disque: {image.image.path} ❌")
                        
            else:
                print(f"❌ Erreur lors de l'upload: {serializer.errors}")
        
        # Final verification
        print(f"\n" + "=" * 60)
        print("🔍 VÉRIFICATION FINALE")
        
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
                    print(f"✅ {part.name}: http://localhost:8000{primary_image.image.url}")
                else:
                    print(f"⚠️  {part.name}: Images mais PAS de primaire")
            else:
                print(f"❌ {part.name}: Aucune image")
        
        print(f"\n📊 RÉSULTATS FINAUX:")
        print(f"   Total pièces: {total_parts}")
        print(f"   Pièces avec images: {parts_with_images}")
        print(f"   Pièces avec image primaire: {parts_with_primary}")
        print(f"   Pièces sans images: {total_parts - parts_with_images}")
        
        if parts_with_primary == total_parts:
            print("\n🎉 SUCCÈS TOTAL!")
            print("✅ Toutes les pièces ont maintenant des images primaires!")
            print("📝 Les images devraient s'afficher correctement dans 'My Parts'!")
            print("🌐 Testez l'upload dans l'interface: http://localhost:4200/supplier/parts/new")
        else:
            print(f"\n⚠️  ATTENTION: {total_parts - parts_with_primary} pièces n'ont pas d'images primaires")
            
        print("=" * 60)
        
    except Exception as e:
        print(f"Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    ultimate_image_fix()
