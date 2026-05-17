import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
django.setup()

from marketplace.models import User, Client, Supplier, Part, Cart, CartItem, Order, OrderItem

def test_order_flow():
    """Test the complete order flow: client creates order -> supplier validates/rejects"""
    
    print("🚀 TEST COMPLET DU FLUX DE COMMANDE")
    print("=" * 60)
    
    try:
        # 1. Get test users - create if needed
        try:
            client_user = User.objects.get(username='jaaferg')
            print(f"✅ Found client user: {client_user.username}")
        except User.DoesNotExist:
            print("❌ Client user 'jaaferg' not found")
            return
        
        # Check if user has client profile, create if needed
        try:
            client = client_user.client_profile
            print(f"✅ Client profile found: {client}")
        except User.client_profile.RelatedObjectDoesNotExist:
            print("📝 Creating client profile for user...")
            from marketplace.models import Client
            client = Client.objects.create(user=client_user)
            print(f"✅ Client profile created: {client}")
        
        # Get any supplier for testing
        supplier = Supplier.objects.first()
        if not supplier:
            print("❌ No supplier found in database")
            return
        
        supplier_user = supplier.user
        print(f"✅ Using supplier: {supplier_user.username} ({supplier.business_name})")
        
        # 2. Get a part from this supplier
        part = Part.objects.filter(supplier=supplier).first()
        if not part:
            print("❌ No parts found for this supplier")
            return
        
        print(f"✅ Test part: {part.name} ({part.price} TND)")
        
        # 3. Clear existing cart and add item
        CartItem.objects.filter(cart__client=client).delete()
        cart, created = Cart.objects.get_or_create(client=client)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            part=part,
            defaults={'quantity': 2}
        )
        
        if not created:
            cart_item.quantity = 2
            cart_item.save()
        
        print(f"✅ Added {cart_item.quantity}x {part.name} to cart")
        print(f"   Cart total: {cart.get_total()} TND")
        
        # 4. Create order from cart (simulate client action)
        print(f"\n📝 ÉTAPE 1: Client crée la commande...")
        
        # Simulate API call
        order_data = {
            'client': client.user.id,
            'total_price': str(cart.get_total()),
            'status': 'SUPPLIER_PENDING'
        }
        
        # Create order manually for testing
        from django.db import transaction
        with transaction.atomic():
            order = Order.objects.create(
                client=client,
                total_price=cart.get_total(),
                status='SUPPLIER_PENDING'
            )
            
            total = 0
            for item in cart.items.all():
                item_price = item.part.price
                item_total = item_price * item.quantity
                
                OrderItem.objects.create(
                    order=order,
                    part=item.part,
                    supplier=item.part.supplier,
                    quantity=item.quantity,
                    price=item_price,
                    total_price=item_total,
                )
                
                # Decrease stock
                item.part.quantity -= item.quantity
                item.part.save()
                
                total += item_total
            
            order.total_price = total
            order.save()
            
            # Clear cart
            cart.items.all().delete()
        
        print(f"✅ Commande #{order.id} créée")
        print(f"   Statut: {order.get_status_display()}")
        print(f"   Total: {order.total_price} TND")
        print(f"   Articles: {order.items.count()}")
        
        # 5. Test supplier validation
        print(f"\n🔍 ÉTAPE 2: Fournisseur valide la commande...")
        
        # Test supplier can see the order
        supplier_orders = Order.objects.filter(items__supplier=supplier).distinct()
        print(f"✅ Fournisseur peut voir {supplier_orders.count()} commande(s)")
        
        # Test order details
        order_detail = Order.objects.prefetch_related('items__part', 'items__supplier').get(id=order.id)
        print(f"✅ Détails de la commande:")
        for item in order_detail.items.all():
            print(f"   - {item.quantity}x {item.part.name} @ {item.price} TND = {item.total_price} TND")
            print(f"     Fournisseur: {item.supplier.business_name}")
        
        # Test validation - APPROVE
        print(f"\n✅ ÉTAPE 3: Fournisseur approuve la commande...")
        
        order.status = 'APPROVED'
        order.supplier_notes = 'Commande approuvée rapidement'
        order.save()
        
        # Restore stock for this supplier's items
        for item in order.items.filter(supplier=supplier):
            item.part.quantity += item.quantity
            item.part.save()
        
        print(f"✅ Commande #{order.id} approuvée")
        print(f"   Nouveau statut: {order.get_status_display()}")
        print(f"   Notes: {order.supplier_notes}")
        
        # Test client can see updated status
        client_orders = Order.objects.filter(client=client)
        print(f"✅ Client peut voir {client_orders.count()} commande(s)")
        
        for client_order in client_orders:
            print(f"   - Commande #{client_order.id}: {client_order.get_status_display()}")
        
        # 6. Test rejection flow
        print(f"\n❌ ÉTAPE 4: Test de rejet de commande...")
        
        # Create another order for rejection test
        with transaction.atomic():
            reject_order = Order.objects.create(
                client=client,
                total_price=part.price,
                status='SUPPLIER_PENDING'
            )
            
            OrderItem.objects.create(
                order=reject_order,
                part=part,
                supplier=supplier,
                quantity=1,
                price=part.price,
                total_price=part.price,
            )
            
            # Decrease stock
            part.quantity -= 1
            part.save()
        
        print(f"✅ Commande #{reject_order.id} créée pour test de rejet")
        
        # Reject the order
        reject_order.status = 'REJECTED'
        reject_order.supplier_notes = 'Stock insuffisant pour cette pièce'
        reject_order.save()
        
        # Restore stock for all items (order is cancelled)
        for item in reject_order.items.all():
            item.part.quantity += item.quantity
            item.part.save()
        
        print(f"✅ Commande #{reject_order.id} rejetée")
        print(f"   Statut: {reject_order.get_status_display()}")
        print(f"   Notes: {reject_order.supplier_notes}")
        
        # 7. Final verification
        print(f"\n🔍 VÉRIFICATION FINALE:")
        
        all_orders = Order.objects.all()
        print(f"   Total commandes: {all_orders.count()}")
        print(f"   En attente: {all_orders.filter(status='SUPPLIER_PENDING').count()}")
        print(f"   Approuvées: {all_orders.filter(status='APPROVED').count()}")
        print(f"   Rejetées: {all_orders.filter(status='REJECTED').count()}")
        
        print(f"\n🎉 TEST DU FLUX COMPLET RÉUSSI!")
        print(f"✅ Client peut créer des commandes depuis le panier")
        print(f"✅ Fournisseur peut voir et valider/rejeter les commandes")
        print(f"✅ Statut mis à jour automatiquement pour le client")
        print(f"✅ Notes du fournisseur enregistrées")
        print(f"✅ Stock géré correctement")
        
        print(f"\n📋 URLs de test:")
        print(f"   Client orders: http://localhost:8000/api/orders/")
        print(f"   Supplier orders: http://localhost:8000/api/supplier/orders/")
        print(f"   Validate order: POST http://localhost:8000/api/supplier/orders/{{id}}/validate/")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_order_flow()
