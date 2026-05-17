import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageDraw
import io

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import Part, PartImage
from marketplace.serializers import PartImageUploadSerializer

def complete_media_solution():
    """Solution complète pour l'upload et l'affichage des images"""
    
    print("🚀 SOLUTION COMPLÈTE POUR LE DOSSIER MEDIA")
    print("=" * 60)
    
    try:
        # 1. Vérifier toutes les pièces
        all_parts = Part.objects.all()
        print(f"Traitement de {all_parts.count()} pièces...")
        
        # 2. Couleurs uniques pour chaque pièce
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
            (128, 128, 128),  # Gray
            (255, 255, 255),  # White
        ]
        
        # 3. Traiter chaque pièce
        for i, part in enumerate(all_parts):
            print(f"\n📝 Pièce {i+1}/{all_parts.count()}: {part.name}")
            
            # Vérifier les images existantes
            existing_images = part.images.all()
            if existing_images.exists():
                primary_image = existing_images.filter(is_primary=True).first()
                if primary_image:
                    print(f"✅ Image primaire existante: {primary_image.image.name}")
                    print(f"   URL: http://localhost:8000{primary_image.image.url}")
                    
                    # Vérifier si le fichier existe
                    if hasattr(primary_image.image, 'path'):
                        import os
                        if os.path.exists(primary_image.image.path):
                            file_size = os.path.getsize(primary_image.image.path)
                            print(f"   Fichier: {file_size} bytes ✅")
                        else:
                            print(f"   Fichier: MANQUANT ❌")
                            # Recréer l'image si le fichier n'existe pas
                            create_image_for_part(part, colors[i % len(colors)])
                    continue
                else:
                    print("⚠️  Images existantes mais PAS de primaire")
                    # Définir la première image comme primaire
                    first_image = existing_images.first()
                    first_image.is_primary = True
                    first_image.save()
                    print(f"✅ Première image définie comme primaire: {first_image.image.name}")
                    continue
            else:
                print("❌ Aucune image existante")
                # Créer une nouvelle image
                create_image_for_part(part, colors[i % len(colors)])
        
        # 4. Vérification finale
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
                    print(f"✅ {part.name[:25]:25} | {primary_image.image.name} | http://localhost:8000{primary_image.image.url}")
                else:
                    print(f"⚠️  {part.name[:25]:25} | Images mais PAS de primaire")
            else:
                print(f"❌ {part.name[:25]:25} | Aucune image")
        
        # 5. Statistiques
        print(f"\n📊 STATISTIQUES FINALES:")
        print(f"   Total pièces: {total_parts}")
        print(f"   Pièces avec images: {parts_with_images}")
        print(f"   Pièces avec image primaire: {parts_with_primary}")
        print(f"   Pièces sans images: {total_parts - parts_with_images}")
        
        # 6. Vérification du dossier media
        print(f"\n📁 VÉRIFICATION DU DOSSIER MEDIA:")
        media_path = '/app/media'
        if os.path.exists(media_path):
            print(f"✅ Dossier media existe: {media_path}")
            
            # Compter les fichiers d'images
            image_count = 0
            for root, dirs, files in os.walk(media_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.ico')):
                        image_count += 1
            
            print(f"✅ {image_count} fichiers d'images trouvés dans /app/media/")
            
            # Afficher quelques exemples
            example_files = []
            for root, dirs, files in os.walk(media_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        example_files.append(os.path.join(root, file).replace('/app/', '/'))
                        if len(example_files) >= 5:
                            break
                if len(example_files) >= 5:
                    break
            
            print(f"📋 Exemples de fichiers:")
            for file in example_files:
                print(f"   📁 {file}")
        
        # 7. Instructions finales
        if parts_with_primary == total_parts:
            print(f"\n🎉 SUCCÈS TOTAL!")
            print(f"✅ Toutes les pièces ont maintenant des images primaires!")
            print(f"✅ Les images sont sauvegardées dans: /app/media/")
            print(f"✅ Les URLs sont accessibles via: http://localhost:8000/media/")
            print(f"✅ Le frontend Angular peut maintenant afficher les images!")
            print(f"\n📋 INSTRUCTIONS:")
            print(f"   1. Allez sur: http://localhost:4200/supplier/parts")
            print(f"   2. Vous devriez voir toutes les pièces avec leurs images")
            print(f"   3. Pour uploader: http://localhost:4200/supplier/parts/new")
            print(f"   4. Sélectionnez une image (JPG, PNG, WEBP, etc.)")
            print(f"   5. L'image devrait s'uploader et s'afficher immédiatement")
        else:
            print(f"\n⚠️  ATTENTION: {total_parts - parts_with_primary} pièces n'ont pas d'images primaires")
            
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()

def create_image_for_part(part, color):
    """Créer et sauvegarder une image pour une pièce"""
    try:
        # Créer une image de haute qualité
        img = Image.new('RGB', (600, 450), color)
        
        # Ajouter du texte
        draw = ImageDraw.Draw(img)
        
        # Nom de la pièce
        text = part.name.upper()
        try:
            # Centrer le texte
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (600 - text_width) // 2
            y = (450 - text_height) // 2 - 30
            
            # Ajouter le texte avec ombre
            draw.text((x-2, y-2), text, fill=(0, 0, 0))  # Ombre
            draw.text((x, y), text, fill=(255, 255, 255))  # Texte blanc
            
            # Référence
            ref_text = f"REF: {part.reference}"
            ref_y = y + 60
            draw.text((x-1, ref_y-1), ref_text, fill=(0, 0, 0))  # Ombre
            draw.text((x, ref_y), ref_text, fill=(255, 255, 255))  # Texte blanc
            
            # Prix
            price_text = f"{part.price} TND"
            price_y = ref_y + 40
            draw.text((x-1, price_y-1), price_text, fill=(0, 0, 0))  # Ombre
            draw.text((x, price_y), price_text, fill=(255, 255, 0))  # Texte jaune
            
        except Exception as e:
            print(f"   Erreur lors de l'ajout du texte: {e}")
        
        # Sauvegarder en mémoire
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        
        # Créer le fichier uploadé
        filename = f"{part.name.lower().replace(' ', '_').replace('-', '_')}_final.jpg"
        uploaded_file = SimpleUploadedFile(
            filename,
            img_bytes.read(),
            content_type="image/jpeg"
        )
        
        # Sauvegarder via serializer
        data = {
            'image': uploaded_file,
            'is_primary': True
        }
        
        serializer = PartImageUploadSerializer(data=data)
        if serializer.is_valid():
            image = serializer.save(part=part)
            print(f"✅ Image créée: {image.image.name}")
            print(f"   Taille: {uploaded_file.size} bytes")
            print(f"   URL: http://localhost:8000{image.image.url}")
            print(f"   Primaire: {image.is_primary}")
            
            # Vérifier si le fichier existe
            if hasattr(image.image, 'path'):
                import os
                if os.path.exists(image.image.path):
                    file_size = os.path.getsize(image.image.path)
                    print(f"   Fichier sur disque: {file_size} bytes ✅")
                else:
                    print(f"   Fichier MANQUANT sur disque: {image.image.path} ❌")
        else:
            print(f"❌ Erreur serializer: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'image: {str(e)}")

if __name__ == '__main__':
    complete_media_solution()
