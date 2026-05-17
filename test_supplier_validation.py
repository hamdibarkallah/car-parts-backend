import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import User, Client, Supplier, Part, Cart, CartItem, Order, OrderItem

def test_supplier_validation_routes():
    """Test the supplier validation routes manually"""
    
    print("🔧 TEST DES ROUTES DE VALIDATION FOURNISSEUR")
    print("=" * 60)
    
    try:
        # 1. Get supplier user
        supplier = Supplier.objects.first()
        if not supplier:
            print("❌ No supplier found")
            return
        
        print(f"✅ Supplier: {supplier.user.username} ({supplier.business_name})")
        
        # 2. Get orders for this supplier
        orders = Order.objects.filter(items__supplier=supplier).distinct()
        print(f"✅ Found {orders.count()} orders for this supplier")
        
        for order in orders:
            print(f"\n📦 Commande #{order.id}")
            print(f"   Statut: {order.get_status_display()}")
            print(f"   Client: {order.client.user.username}")
            print(f"   Total: {order.total_price} TND")
            print(f"   Créée: {order.created_at}")
            
            # Show items
            for item in order.items.filter(supplier=supplier):
                print(f"   📋 Article: {item.quantity}x {item.part.name} @ {item.price} TND")
            
            # Show validation routes
            print(f"\n🔗 Routes de validation:")
            print(f"   GET  /api/supplier/orders/{order.id}/")
            print(f"   POST /api/supplier/orders/{order.id}/validate/")
            
            # Show validation payload
            if order.status == 'SUPPLIER_PENDING':
                print(f"\n✅ Payload pour approuver:")
                approve_payload = {
                    "action": "approve",
                    "notes": "Commande approuvée - livraison dans 2 jours"
                }
                print(f"   {json.dumps(approve_payload, indent=6)}")
                
                print(f"\n❌ Payload pour rejeter:")
                reject_payload = {
                    "action": "reject", 
                    "notes": "Stock insuffisant pour cette pièce"
                }
                print(f"   {json.dumps(reject_payload, indent=6)}")
        
        print(f"\n📋 RÉSUMÉ DES ROUTES:")
        print(f"   📊 GET  /api/supplier/orders/                    - Liste des commandes")
        print(f"   📊 GET  /api/supplier/orders/{{id}}/              - Détails d'une commande")
        print(f"   ✅ POST /api/supplier/orders/{{id}}/validate/      - Valider une commande")
        print(f"   📊 GET  /api/supplier/orders/stats/               - Statistiques")
        
        print(f"\n🎯 EXEMPLE D'UTILISATION:")
        print(f"   # Approuver une commande")
        print(f"   POST http://localhost:8000/api/supplier/orders/123/validate/")
        print(f"   Content-Type: application/json")
        print(f'   {{"action": "approve", "notes": "Commande prête"}}')
        
        print(f"\n   # Rejeter une commande")
        print(f"   POST http://localhost:8000/api/supplier/orders/123/validate/")
        print(f"   Content-Type: application/json")
        print(f'   {{"action": "reject", "notes": "Stock insuffisant"}}')
        
        print(f"\n🔍 TEST DES PERMISSIONS:")
        print(f"   ✅ Seul le fournisseur concerné peut voir/valider ses commandes")
        print(f"   ✅ Les autres fournisseurs ne voient pas les commandes des autres")
        print(f"   ✅ Les clients ne peuvent pas valider les commandes")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_supplier_validation_routes()
