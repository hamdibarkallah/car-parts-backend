"""Seed script - run with: .\venv\Scripts\python.exe manage.py shell < seed_data.py"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carparts.settings')
os.environ['DB_HOST'] = 'localhost'
django.setup()

from marketplace.models import User, Client, Supplier, Brand, Model, ModelYear, Engine, Category, Part
from django.contrib.auth import get_user_model

User = get_user_model()

# --- Client ---
client_user, created = User.objects.get_or_create(
    username='testclient',
    defaults={'email': 'client@test.com', 'first_name': 'Test', 'last_name': 'Client', 'role': 'CLIENT'}
)
if created:
    client_user.set_password('testpass123')
    client_user.save()
else:
    client_user.set_password('testpass123')
    client_user.save()
Client.objects.get_or_create(user=client_user)
print(f'Client: testclient / testpass123 (id={client_user.id})')

# --- Supplier ---
supplier_user, created = User.objects.get_or_create(
    username='testsupplier',
    defaults={'email': 'supplier@test.com', 'first_name': 'Test', 'last_name': 'Supplier', 'role': 'SUPPLIER'}
)
if created:
    supplier_user.set_password('testpass123')
    supplier_user.save()
else:
    supplier_user.set_password('testpass123')
    supplier_user.save()
sp, _ = Supplier.objects.get_or_create(
    user=supplier_user,
    defaults={'business_name': 'AutoParts Tunisia', 'address': '12 Rue de la Liberte', 'governorate': 'Tunis', 'postal_code': '1000', 'phone': '+216 71 123 456'}
)
print(f'Supplier: testsupplier / testpass123 (id={supplier_user.id})')

# --- Brands ---
brand_vw, _ = Brand.objects.get_or_create(name='Volkswagen')
brand_pg, _ = Brand.objects.get_or_create(name='Peugeot')
print(f'Brands: {brand_vw.name}, {brand_pg.name}')

# --- Models ---
model_golf, _ = Model.objects.get_or_create(brand=brand_vw, name='Golf')
model_208, _ = Model.objects.get_or_create(brand=brand_pg, name='208')
print(f'Models: {model_golf.name}, {model_208.name}')

# --- Years ---
year_golf, _ = ModelYear.objects.get_or_create(model=model_golf, year=2020)
year_208, _ = ModelYear.objects.get_or_create(model=model_208, year=2019)
print(f'Years: {year_golf.year}, {year_208.year}')

# --- Engines ---
engine_golf, _ = Engine.objects.get_or_create(model_year=year_golf, name='1.4 TSI', defaults={'type': 'GASOLINE', 'horsepower': 150})
engine_208, _ = Engine.objects.get_or_create(model_year=year_208, name='1.2 PureTech', defaults={'type': 'GASOLINE', 'horsepower': 110})
print(f'Engines: {engine_golf.name}, {engine_208.name}')

# --- Categories ---
cat_brakes, _ = Category.objects.get_or_create(name='Brakes')
cat_engine, _ = Category.objects.get_or_create(name='Engine Parts')
cat_susp, _ = Category.objects.get_or_create(name='Suspension')
print(f'Categories: {cat_brakes.name}, {cat_engine.name}, {cat_susp.name}')

# --- Parts (only create if supplier has < 5 parts) ---
existing = Part.objects.filter(supplier=sp).count()
if existing < 5:
    parts_data = [
        {'name': 'Front Brake Pads - Golf VII', 'reference': 'VW-BRK-001', 'description': 'High quality ceramic front brake pads for VW Golf VII.', 'price': 85.00, 'quantity': 25, 'condition': 'NEW', 'category': cat_brakes, 'brand': brand_vw, 'model': model_golf, 'model_year': year_golf, 'engine': engine_golf},
        {'name': 'Oil Filter - Golf VII 1.4 TSI', 'reference': 'VW-FLT-002', 'description': 'Premium oil filter for VW Golf VII 1.4 TSI engine.', 'price': 22.50, 'quantity': 40, 'condition': 'NEW', 'category': cat_engine, 'brand': brand_vw, 'model': model_golf, 'model_year': year_golf, 'engine': engine_golf},
        {'name': 'Front Shock Absorber - 208', 'reference': 'PG-SUS-001', 'description': 'Front shock absorber for Peugeot 208.', 'price': 120.00, 'quantity': 12, 'condition': 'NEW', 'category': cat_susp, 'brand': brand_pg, 'model': model_208, 'model_year': year_208, 'engine': engine_208},
        {'name': 'Used Alternator - Golf VI', 'reference': 'VW-ALT-003', 'description': 'Tested used alternator from VW Golf VI.', 'price': 150.00, 'quantity': 3, 'condition': 'USED', 'category': cat_engine, 'brand': brand_vw, 'model': model_golf, 'model_year': year_golf},
        {'name': 'Rear Brake Discs - 208', 'reference': 'PG-BRK-002', 'description': 'Rear brake discs for Peugeot 208. Sold as pair.', 'price': 95.00, 'quantity': 8, 'condition': 'NEW', 'category': cat_brakes, 'brand': brand_pg, 'model': model_208, 'model_year': year_208, 'engine': engine_208},
    ]
    for pd in parts_data:
        Part.objects.get_or_create(reference=pd['reference'], defaults={**pd, 'supplier': sp})
    print(f'Created {len(parts_data)} new parts')
else:
    print(f'Supplier already has {existing} parts, skipping')

print(f'\nTotal parts: {Part.objects.count()}')
print('SEED COMPLETE!')
