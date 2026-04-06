# Part Model Documentation

## Overview

The `Part` model is the core product entity in the car parts marketplace. It represents a specific car spare part with complete vehicle compatibility information, inventory management, and supplier tracking.

## Model Fields

### Basic Information

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK, Auto | Auto-generated primary key |
| `name` | CharField | max_length=255, required | Part name/description |
| `reference` | CharField | max_length=100, unique, required | Part SKU or reference number |
| `description` | TextField | nullable, blank | Detailed specifications and features |

### Relations

| Field | Type | On Delete | Description |
|-------|------|-----------|-------------|
| `supplier` | ForeignKey | CASCADE | Supplier who owns/sells this part |
| `brand` | ForeignKey | PROTECT | Vehicle brand (BMW, Mercedes, etc.) |
| `model` | ForeignKey | PROTECT | Vehicle model (325i, C-Class, etc.) |
| `model_year` | ForeignKey | PROTECT | Specific year of the vehicle |
| `engine` | ForeignKey | SET_NULL | Engine variant (optional, nullable) |
| `category` | ForeignKey | PROTECT | Part category (hierarchical) |

### Commercial Details

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `price` | DecimalField | required | Price per unit (10 digits, 2 decimals) |
| `quantity` | IntegerField | 0 | Current stock quantity |
| `condition` | CharField | NEW | Part condition: NEW or USED |

### Timestamps

| Field | Type | Auto | Description |
|-------|------|------|-------------|
| `created_at` | DateTimeField | add_now | Creation timestamp |
| `updated_at` | DateTimeField | auto_now | Last modification timestamp |

## Database Configuration

### Table Name
- **Database Table**: `parts`
- **Ordering**: By `created_at` descending (newest first)

### Indexes

Three composite indexes are created for optimal query performance:

```sql
-- Supplier inventory queries
CREATE INDEX parts_supplier_created_at ON parts(supplier_id, created_at DESC);

-- Vehicle compatibility search
CREATE INDEX parts_brand_model_year ON parts(brand_id, model_id, model_year_id);

-- Category-based filtering
CREATE INDEX parts_category ON parts(category_id);
```

### Constraints

**Unique Constraints:**
- `reference`: Must be globally unique (no two parts can have the same reference)

**Foreign Key Constraints:**
- `supplier`: CASCADE - When supplier is deleted, all their parts are deleted
- `brand`, `model`, `model_year`, `category`: PROTECT - Cannot delete if parts reference them
- `engine`: SET_NULL - Can delete engine type; parts will have NULL engine

## Methods

### Instance Methods

#### `is_in_stock()`
```python
def is_in_stock(self) -> bool:
    """Check if part is currently in stock"""
    return self.quantity > 0
```

**Returns:** `True` if quantity > 0, `False` otherwise

**Usage:**
```python
part = Part.objects.get(id=1)
if part.is_in_stock():
    print(f"Available: {part.quantity} units")
```

#### `get_vehicle_compatibility()`
```python
def get_vehicle_compatibility() -> str:
    """Get formatted vehicle compatibility string"""
    return f"{self.brand.name} {self.model.name} ({self.model_year.year})"
```

**Returns:** Formatted string like "BMW 325i (2020)"

**Usage:**
```python
part = Part.objects.get(id=1)
print(part.get_vehicle_compatibility())  # "BMW 325i (2020)"
```

#### `__str__()`
```python
def __str__(self) -> str:
    """String representation of part"""
    return f"{self.name} ({self.reference}) - {self.supplier.business_name}"
```

**Returns:** "Part Name (Reference) - Supplier Name"

## Model Choices

### Condition
```python
CONDITION_CHOICES = (
    ('NEW', 'New'),      # Brand new part
    ('USED', 'Used'),    # Used/reconditioned part
)
```

## Relationships

### One-to-Many
```
Supplier (1) ──→ (many) Part
    ├── Cascade: Deleting supplier deletes all their parts
    └── Related name: supplier.parts.all()

Brand (1) ──→ (many) Part
    ├── Protect: Cannot delete brand if parts reference it
    └── Related name: brand.parts.all()

Model (1) ──→ (many) Part
    ├── Protect: Cannot delete model if parts reference it
    └── Related name: model.parts.all()

ModelYear (1) ──→ (many) Part
    ├── Protect: Cannot delete year if parts reference it
    └── Related name: modelyear.parts.all()

Engine (1) ──→ (many) Part
    ├── Set Null: Engine can be deleted; parts remain with NULL engine
    └── Related name: engine.parts.all()

Category (1) ──→ (many) Part
    ├── Protect: Cannot delete category if parts reference it
    └── Related name: category.parts.all()
```

## Query Examples

### Basic Queries

```python
# Get a specific part
part = Part.objects.get(id=1)
part = Part.objects.get(reference="BMW-325i-OIL-FILTER")

# Get all parts from a supplier
supplier_parts = Part.objects.filter(supplier_id=1)

# Get all parts in a category
category_parts = Part.objects.filter(category_id=5)

# Get all parts in stock
in_stock = Part.objects.filter(quantity__gt=0)

# Get all NEW parts
new_parts = Part.objects.filter(condition='NEW')

# Get all USED parts
used_parts = Part.objects.filter(condition='USED')
```

### Vehicle-Based Queries

```python
# Find parts for a specific vehicle
parts = Part.objects.filter(
    brand_id=1,
    model_id=5,
    model_year_id=10
)

# Find parts for a specific vehicle with a specific engine
parts = Part.objects.filter(
    brand_id=1,
    model_id=5,
    model_year_id=10,
    engine_id=3
)

# Find parts compatible with multiple engine types (parts with NULL engine)
universal_parts = Part.objects.filter(
    brand_id=1,
    model_id=5,
    model_year_id=10,
    engine__isnull=True
)
```

### Advanced Queries

```python
# Parts with low stock (less than 5 units)
low_stock = Part.objects.filter(quantity__lt=5)

# Parts added in the last 7 days
from datetime import timedelta
from django.utils import timezone

recent = Part.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=7)
)

# Parts by price range
expensive = Part.objects.filter(price__gte=100)
affordable = Part.objects.filter(price__lt=50)

# Parts from a specific supplier in a category
supplier_category = Part.objects.filter(
    supplier_id=1,
    category_id=5
)

# Search by name or reference
from django.db.models import Q
search_results = Part.objects.filter(
    Q(name__icontains='oil') | Q(reference__icontains='OIL')
)

# Aggregation examples
from django.db.models import Sum, Count, Avg

# Total quantity in stock
total_stock = Part.objects.aggregate(
    total=Sum('quantity')
)

# Average price
avg_price = Part.objects.aggregate(
    average=Avg('price')
)

# Parts per supplier
from django.db.models import Count
supplier_counts = Part.objects.values('supplier').annotate(
    count=Count('id')
)
```

## Admin Interface

The Part model is registered in Django Admin with:

- **List Display**: name, reference, supplier, price, quantity, condition, created_at
- **List Filters**: condition, supplier, category, brand, created_at
- **Search Fields**: name, reference, description
- **Read-only Fields**: created_at, updated_at, vehicle compatibility

### Admin Fieldsets

1. **Basic Information**: name, reference, description, supplier, category
2. **Vehicle Compatibility**: brand, model, model_year, engine, compatibility display
3. **Commercial Details**: price, quantity, condition
4. **Timestamps** (collapsed): created_at, updated_at

## Validation Rules

- `name`: Required, max 255 characters
- `reference`: Required, max 100 characters, **must be unique**
- `price`: Required, positive decimal with max 10 digits and 2 decimal places
- `quantity`: Must be >= 0 (non-negative integer)
- `supplier`: Required (cannot be NULL)
- `brand`, `model`, `model_year`, `category`: Required (cannot be NULL)
- `engine`: Optional (can be NULL)
- `condition`: Must be either 'NEW' or 'USED'

## Migration

The Part model is created in migration `0002_brand_category_model_modelyear_engine_part.py`

**To apply migration:**
```bash
python manage.py migrate marketplace
```

**To create new migrations after model changes:**
```bash
python manage.py makemigrations marketplace
python manage.py migrate marketplace
```

## Related Models

### Supplier
- One supplier can have many parts
- Deleting a supplier cascades deletion to all their parts

### Brand, Model, ModelYear, Engine, Category
- These models define the vehicle hierarchy
- Parts reference these to define compatibility

### Future Related Models
- **PartImage**: Multiple images per part
- **CartItem**: References Part in shopping cart
- **OrderItem**: References Part in orders

## Performance Considerations

1. **Indexes**: Three composite indexes are configured for common query patterns
2. **Select Related**: When fetching parts, use `select_related()` to optimize queries:
   ```python
   parts = Part.objects.select_related(
       'supplier', 'brand', 'model', 'model_year', 'engine', 'category'
   )
   ```
3. **Pagination**: Use pagination for large result sets
4. **Caching**: Consider caching popular queries or parts

## Best Practices

1. **Always use unique reference numbers** - Use meaningful SKU format
2. **Set correct condition** - Mark used parts clearly
3. **Maintain accurate inventory** - Update quantity correctly
4. **Use descriptive names and descriptions** - Help users find parts
5. **Categorize properly** - Use hierarchical categories effectively
6. **Keep supplier data updated** - Maintain supplier information

## Common Operations

### Create a Part
```python
from marketplace.models import Part, Supplier, Brand, Model, ModelYear, Category

supplier = Supplier.objects.get(id=1)
brand = Brand.objects.get(id=1)
model = Model.objects.get(id=1)
model_year = ModelYear.objects.get(id=1)
category = Category.objects.get(id=1)

part = Part.objects.create(
    supplier=supplier,
    name="Oil Filter",
    reference="BMW-325i-OIL-FILTER",
    description="Original BMW oil filter for 325i",
    brand=brand,
    model=model,
    model_year=model_year,
    category=category,
    price=15.99,
    quantity=100,
    condition='NEW'
)
```

### Update Part Stock
```python
part = Part.objects.get(id=1)
part.quantity = 50
part.save()
```

### Delete a Part
```python
part = Part.objects.get(id=1)
part.delete()
```

### Bulk Operations
```python
# Update multiple parts
Part.objects.filter(
    condition='NEW',
    price__lt=20
).update(quantity=0)

# Delete parts from a supplier
Part.objects.filter(supplier_id=1).delete()
```
