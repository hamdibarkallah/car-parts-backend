# Part Model Relations Diagram

## Complete Entity Relationship Diagram

```
                                    ┌─────────────────────────────┐
                                    │         SUPPLIER            │
                                    ├─────────────────────────────┤
                                    │ PK: id                      │
                                    │ user_id (OneToOne)          │
                                    │ business_name               │
                                    │ address                     │
                                    │ governorate                 │
                                    │ postal_code                 │
                                    │ rating                      │
                                    │ created_at, updated_at      │
                                    └────────────────┬────────────┘
                                                     │
                                                     │ (1)
                                                     │
                                                CASCADE DELETE
                                                     │
                                                     │ (many)
                            ┌────────────────────────▼────────────────────────┐
                            │                  PART                           │
                            ├──────────────────────────────────────────────────┤
                            │ PK: id                                           │
                            │                                                  │
                            │ SUPPLIER RELATION:                               │
                            │   FK: supplier_id ────────────────── PROTECT    │
                            │                                                  │
                            │ VEHICLE TARGETING:                               │
                            │   FK: brand_id ─────────────────── PROTECT      │
                            │   FK: model_id ─────────────────── PROTECT      │
                            │   FK: model_year_id ────────────── PROTECT      │
                            │   FK: engine_id ────────────────── SET_NULL     │
                            │                          [OPTIONAL]              │
                            │ CATEGORIZATION:                                  │
                            │   FK: category_id ──────────────── PROTECT      │
                            │                                                  │
                            │ BASIC INFORMATION:                               │
                            │   name (CharField, 255)                          │
                            │   reference (CharField, 100, UNIQUE)             │
                            │   description (TextField, nullable)              │
                            │                                                  │
                            │ COMMERCIAL:                                      │
                            │   price (Decimal, 10.2)                          │
                            │   quantity (Integer, default=0)                  │
                            │   condition (NEW/USED)                           │
                            │                                                  │
                            │ TIMESTAMPS:                                      │
                            │   created_at (auto_now_add)                      │
                            │   updated_at (auto_now)                          │
                            │                                                  │
                            │ INDEXES:                                         │
                            │   - (supplier_id, created_at)                    │
                            │   - (brand_id, model_id, model_year_id)          │
                            │   - (category_id)                                │
                            └─┬──────────────────────┬──────────────────────┬──┘
                              │                      │                      │
                              │ (many)               │ (many)               │ (many)
                              │ PROTECT              │ PROTECT              │ PROTECT
                              │                      │                      │
                    ┌─────────▼──────────┐   ┌─────▼────────────┐    ┌───▼──────────┐
                    │      BRAND         │   │     MODEL        │    │ MODEL YEAR   │
                    ├────────────────────┤   ├──────────────────┤    ├──────────────┤
                    │ PK: id             │   │ PK: id           │    │ PK: id       │
                    │ name (UNIQUE)      │   │ name             │    │ year         │
                    │ created_at         │   │ FK: brand_id     │    │ FK: model_id │
                    │ updated_at         │   │ created_at       │    │ created_at   │
                    └────────────────────┘   │ updated_at       │    │ updated_at   │
                                             └──────────────────┘    └─────┬────────┘
                                                                            │
                                                                            │ (1)
                                                                            │
                                                                       PROTECT
                                                                            │
                                                                            │ (many)
                                                                            │
                                                                      ┌──────▼────────┐
                                                                      │     ENGINE     │
                                                                      ├────────────────┤
                                                                      │ PK: id         │
                                                                      │ name           │
                                                                      │ type           │
                                                                      │ horsepower     │
                                                                      │ FK: model_year │
                                                                      │ created_at     │
                                                                      │ updated_at     │
                                                                      └────────────────┘


                    ┌──────────────────────────┐
                    │      CATEGORY            │
                    ├──────────────────────────┤
                    │ PK: id                   │
                    │ name                     │
                    │ FK: parent_id (self-ref)│
                    │ created_at               │
                    │ updated_at               │
                    │                          │
                    │ (Hierarchical)           │
                    │ Example:                 │
                    │ - Electronics            │
                    │   - Electrical           │
                    │     - Batteries          │
                    │     - Alternators        │
                    │   - Engine               │
                    │     - Oil Filters        │
                    └────────────┬─────────────┘
                                 │
                                 │ (1)
                                 │
                            PROTECT
                                 │
                                 │ (many)
                                 │
                                 │
                    ┌────────────────────────────────┐
                    │ (Referenced by PART models)    │
                    └────────────────────────────────┘
```

## Foreign Key Constraints Summary

| Field | References | On Delete | Description |
|-------|-----------|-----------|-------------|
| `supplier` | Supplier | **CASCADE** | Delete part when supplier deleted |
| `brand` | Brand | **PROTECT** | Cannot delete brand if parts reference it |
| `model` | Model | **PROTECT** | Cannot delete model if parts reference it |
| `model_year` | ModelYear | **PROTECT** | Cannot delete year if parts reference it |
| `engine` | Engine | **SET_NULL** | Can delete engine; parts get NULL engine |
| `category` | Category | **PROTECT** | Cannot delete category if parts reference it |

## Query Performance

### Index Usage

```
INDEX 1: (supplier_id, created_at DESC)
├─ Optimizes: Supplier inventory queries
├─ Query: Part.objects.filter(supplier_id=X).order_by('-created_at')
└─ Use case: List supplier's parts chronologically

INDEX 2: (brand_id, model_id, model_year_id)
├─ Optimizes: Vehicle compatibility search
├─ Query: Part.objects.filter(brand=X, model=Y, model_year=Z)
└─ Use case: Find parts for specific vehicle

INDEX 3: (category_id)
├─ Optimizes: Category filtering
├─ Query: Part.objects.filter(category_id=X)
└─ Use case: Browse parts by category
```

## Relationship Patterns

### 1. One-to-Many: Supplier → Part

```python
# Access supplier's parts
supplier = Supplier.objects.get(id=1)
parts = supplier.parts.all()

# Filter and manipulate
new_parts = supplier.parts.filter(condition='NEW')
total_inventory = supplier.parts.aggregate(Sum('quantity'))

# Delete supplier (cascades to parts)
supplier.delete()  # All related parts deleted
```

### 2. One-to-Many: Brand → Part

```python
# Access all parts for a brand
brand = Brand.objects.get(id=1)
brand_parts = brand.parts.all()

# Cannot delete brand if parts reference it
brand.delete()  # Raises: django.db.IntegrityError
```

### 3. One-to-Many: Model → Part

```python
# Access all parts for a model
model = Model.objects.get(id=5)
model_parts = model.parts.all()

# Filter by vehicle configuration
specific_parts = model.parts.filter(model_year_id=10)
```

### 4. Many-to-One: Engine → Part (Optional)

```python
# Access all parts compatible with an engine
engine = Engine.objects.get(id=3)
engine_parts = engine.parts.all()

# Parts without engine (multi-engine compatible)
universal_parts = Part.objects.filter(engine__isnull=True)

# Can safely delete engine
engine.delete()  # Parts get engine_id=NULL
```

### 5. One-to-Many: Category → Part (Hierarchical)

```python
# Access all parts in a category
category = Category.objects.get(id=1)
parts = category.parts.all()

# Access subcategory parts
electronics = Category.objects.get(name='Electronics')
subcategories = electronics.children.all()
all_parts = Part.objects.filter(category__in=subcategories)

# Full category hierarchy
def get_all_parts_in_category(category):
    """Get parts from category and all subcategories"""
    categories = [category]
    for child in category.children.all():
        categories.extend(get_all_parts_in_category(child))
    return Part.objects.filter(category__in=categories)
```

## Complete Query Examples

### Vehicle-Based Search

```python
# Find all parts for a specific vehicle
vehicle_config = {
    'brand_id': 1,      # BMW
    'model_id': 5,      # 325i
    'model_year_id': 10 # 2020
}

parts = Part.objects.filter(**vehicle_config).select_related(
    'supplier', 'brand', 'model', 'model_year', 'engine', 'category'
)

# With optimization for frontend
parts_data = parts.values(
    'id', 'name', 'reference', 'price', 'quantity',
    'supplier__business_name', 'category__name', 'condition'
)
```

### Supplier Inventory Management

```python
# Get supplier's inventory summary
supplier = Supplier.objects.get(id=1)
inventory = supplier.parts.aggregate(
    total_items=Count('id'),
    total_quantity=Sum('quantity'),
    avg_price=Avg('price'),
    min_price=Min('price'),
    max_price=Max('price'),
    new_items=Count('id', filter=Q(condition='NEW')),
    used_items=Count('id', filter=Q(condition='USED'))
)

# Low stock alert
low_stock = supplier.parts.filter(quantity__lt=10)
```

### Category Browse

```python
# Browse category with pagination
category = Category.objects.get(id=1)
parts_page_1 = category.parts.all()[0:20]

# Filter within category
filtered = category.parts.filter(
    price__range=(10, 100),
    condition='NEW'
).order_by('price')

# Category tree navigation
def get_category_breadcrumb(category):
    """Get full path: Electronics > Electrical > Batteries"""
    path = []
    current = category
    while current:
        path.insert(0, current.name)
        current = current.parent
    return ' > '.join(path)
```

## Data Integrity

### Cascade Delete Example

```
Scenario: Delete Supplier with 5 parts

Before:
├── Supplier #1
│   ├── Part A (reference: P-001)
│   ├── Part B (reference: P-002)
│   ├── Part C (reference: P-003)
│   ├── Part D (reference: P-004)
│   └── Part E (reference: P-005)

Action:
>>> supplier = Supplier.objects.get(id=1)
>>> supplier.delete()

After:
├── Supplier #1  [DELETED]
└── All 5 Parts   [DELETED CASCADE]
```

### Protected Delete Example

```
Scenario: Try to delete Brand referenced by parts

Before:
├── Brand: BMW
│   ├── Parts using this brand: 50
│   └── Total references: 50

Action:
>>> brand = Brand.objects.get(name='BMW')
>>> brand.delete()

Result:
!!! IntegrityError: update or delete on table "brands"
    violates foreign key constraint "parts_brand_id_fk"
    DETAIL: Key (id)=(1) is still referenced from table "parts".

Solution:
1. Delete all parts referencing this brand first
2. Or use CASCADE on part deletion
```

### Set Null Example

```
Scenario: Delete Engine variant

Before:
├── Engine: 3.0L Twin-turbo
│   ├── Parts using this engine: 12
│   └── Total references: 12

Action:
>>> engine = Engine.objects.get(name='3.0L Twin-turbo')
>>> engine.delete()

After:
├── Engine: 3.0L Twin-turbo [DELETED]
├── All 12 Parts [PRESERVED]
└── Parts.engine_id [SET TO NULL]

Result:
Parts are preserved, but engine_id becomes NULL
```

## Related Models for Future Implementation

### PartImage Model (Planned)

```
PART (1) ──────► (many) PART_IMAGE
                 CASCADE DELETE

Attributes:
- id (PK)
- part_id (FK, CASCADE)
- image_url (URLField)
- created_at
- updated_at
```

### Cart Models (Planned)

```
CLIENT (1) ─────► (1) CART
                  OneToOne

CART (1) ────────► (many) CART_ITEM
                  CASCADE DELETE

CART_ITEM ──────► PART
                  CASCADE DELETE on cart
```

### Order Models (Planned)

```
CLIENT (1) ──────► (many) ORDER
                  CASCADE DELETE

ORDER (1) ────────► (many) ORDER_ITEM
                   CASCADE DELETE

ORDER_ITEM ──────► PART (PROTECT)
            ──────► SUPPLIER (PROTECT)
```

---

## Summary

The Part model establishes a complex but well-optimized network of relationships:

- **Supplier**: One supplier owns many parts (CASCADE)
- **Vehicle**: Four vehicle-related FKs (Brand, Model, Year, Engine)
- **Category**: Hierarchical categorization system
- **Commercial**: Price and inventory tracking
- **Performance**: 3 strategic indexes for common queries

This design enables:
✅ Complete vehicle compatibility targeting
✅ Efficient supplier inventory management
✅ Fast category browsing
✅ Scalable data organization
✅ Data integrity through proper constraints
