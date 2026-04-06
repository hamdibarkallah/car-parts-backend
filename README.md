# Car Parts Marketplace Platform

## Project Overview

A marketplace platform for car spare parts in Tunisia that connects suppliers, car part sellers, and end users.

## Features

The platform allows suppliers to list car parts with detailed specifications including compatibility with vehicles (brand, model, year, engine), price, quantity, and condition (new or used).

Users (clients) can search for parts by selecting their vehicle characteristics or browsing categories. They can add parts to a shopping cart and place orders.

### Core Capabilities

- **User roles**: Admin, Supplier, Client
- **Vehicle-based filtering**: Brand → Model → Year → Engine
- **Product categorization**: Hierarchical categories
- **Supplier-managed inventory**: Each supplier owns their parts
- **Shopping cart**: Cart and CartItems
- **Order system**: Order and OrderItems with price snapshot at purchase time
- **Image management**: Multiple images per part

### Architecture

The architecture follows a listing-based marketplace model where each supplier independently creates and manages their own part listings.

- **Backend**: Django REST API
- **Frontend**: Angular (to be implemented)
- **Market**: Tailored for Tunisia

## Data Model

### Users

#### User
- `id`: int (PK)
- `firstName`: string
- `lastName`: string
- `username`: string
- `email`: string
- `password`: string
- `phone`: string
- `role`: enum (ADMIN, SUPPLIER, CLIENT)

#### Supplier (inherits User)
- `id`: int (FK → User)
- `businessName`: string
- `address`: string
- `governorate`: string
- `postalCode`: string
- `rating`: float

#### Client (inherits User)
- `id`: int (FK → User)

### Vehicles

#### Brand
- `id`: int (PK)
- `name`: string

#### Model
- `id`: int (PK)
- `name`: string
- `brandId`: int (FK → Brand)

#### ModelYear
- `id`: int (PK)
- `year`: int
- `modelId`: int (FK → Model)

#### Engine
- `id`: int (PK)
- `name`: string
- `type`: string
- `horsepower`: int
- `modelYearId`: int (FK → ModelYear)

#### Vehicle
- `id`: int (PK)
- `clientId`: int (FK → Client)
- `brandId`: int (FK → Brand)
- `modelId`: int (FK → Model)
- `modelYearId`: int (FK → ModelYear)
- `engineId`: int (FK → Engine)

### Category

#### Category
- `id`: int (PK)
- `name`: string
- `parentId`: int (FK → Category, nullable) - for hierarchical categories

### Part

#### Part (✅ Implemented)
Car spare parts with complete vehicle compatibility targeting and inventory management.

**Basic Information:**
- `id`: int (PK)
- `name`: string (max 255 chars) - Part name
- `reference`: string (max 100 chars, unique) - Part reference/SKU
- `description`: string (nullable) - Detailed part description

**Supplier Relation:**
- `supplier`: ForeignKey → Supplier (CASCADE) - Supplier who owns this part

**Vehicle Targeting:**
- `brand`: ForeignKey → Brand (PROTECT) - Vehicle brand
- `model`: ForeignKey → Model (PROTECT) - Vehicle model
- `model_year`: ForeignKey → ModelYear (PROTECT) - Vehicle year
- `engine`: ForeignKey → Engine (SET_NULL, nullable) - Specific engine variant (optional)

**Categorization:**
- `category`: ForeignKey → Category (PROTECT) - Part category

**Commercial Details:**
- `price`: decimal (max_digits=10, decimal_places=2) - Part price
- `quantity`: int (default=0) - Available stock quantity
- `condition`: enum (NEW, USED) - Part condition

**Timestamps:**
- `created_at`: datetime - Auto-set on creation
- `updated_at`: datetime - Auto-updated on modification

**Database Indexes:**
- `(supplier, created_at)` - For supplier inventory queries
- `(brand, model, model_year)` - For vehicle compatibility search
- `(category)` - For category-based search

**Methods:**
- `is_in_stock()` - Check if part is available
- `get_vehicle_compatibility()` - Get formatted vehicle details
- `__str__()` - Returns: "Part Name (Reference) - Supplier Name"

### Images

#### PartImage
- `id`: int (PK)
- `partId`: int (FK → Part)
- `imageUrl`: string

### Shopping Cart

#### Cart
- `id`: int (PK)
- `clientId`: int (FK → Client)
- `createdAt`: datetime
- `updatedAt`: datetime

#### CartItem
- `id`: int (PK)
- `cartId`: int (FK → Cart)
- `partId`: int (FK → Part)
- `quantity`: int

### Orders

#### Order
- `id`: int (PK)
- `clientId`: int (FK → Client)
- `totalPrice`: decimal
- `status`: enum (PENDING, PAID, SHIPPED, DELIVERED, CANCELLED)
- `createdAt`: datetime
- `updatedAt`: datetime

#### OrderItem
- `id`: int (PK)
- `orderId`: int (FK → Order)
- `partId`: int (FK → Part)
- `supplierId`: int (FK → Supplier)
- `quantity`: int
- `price`: decimal (price snapshot at purchase time)
- `totalPrice`: decimal

## Relationships

### User Inheritance
- User ← Supplier
- User ← Client

### Vehicle Hierarchy
- Brand (1) → (many) Model
- Model (1) → (many) ModelYear
- ModelYear (1) → (many) Engine

### Part Associations
- Supplier (1) → (many) Part
- Part → Brand
- Part → Model
- Part → ModelYear
- Part → Engine
- Part → Category
- Part (1) → (many) PartImage

### Client Associations
- Client (1) → (many) Vehicle
- Client (1) → (1) Cart
- Client (1) → (many) Order

### Cart System
- Cart (1) → (many) CartItem
- CartItem → Part

### Order System
- Order (1) → (many) OrderItem
- OrderItem → Part
- OrderItem → Supplier

## Development Roadmap

1. ✅ Project setup and documentation
2. ✅ Django project and app creation
3. ✅ PostgreSQL configuration
4. ✅ Docker containerization
5. ✅ Models implementation (User, Supplier, Client, Brand, Model, ModelYear, Engine, Category, Part)
6. ⏳ PartImage model & REST API endpoints
7. ⏳ Cart, CartItem models & endpoints
8. ⏳ Order, OrderItem models & endpoints
9. ⏳ Authentication and authorization
10. ⏳ Frontend (Angular)
11. ⏳ Testing and deployment

## Technology Stack

- **Backend Framework**: Django 5.2.12 + Django REST Framework
- **Database**: PostgreSQL 15
- **Caching**: Redis 7 (optional)
- **Containerization**: Docker + Docker Compose
- **Frontend**: Angular (to be implemented)

## Part Model Implementation

The **Part** model is the core product entity of the marketplace. It represents a car spare part with complete vehicle compatibility targeting and inventory management.

### Part Model Structure

```python
class Part(models.Model):
    # Basic Information
    name = CharField(max_length=255)              # Part name
    reference = CharField(max_length=100, unique) # Part SKU/Reference
    description = TextField(nullable)             # Detailed description
    
    # Relations
    supplier = ForeignKey(Supplier, CASCADE)      # Part owner
    brand = ForeignKey(Brand, PROTECT)            # Vehicle brand
    model = ForeignKey(Model, PROTECT)            # Vehicle model
    model_year = ForeignKey(ModelYear, PROTECT)   # Vehicle year
    engine = ForeignKey(Engine, SET_NULL, nullable) # Engine variant (optional)
    category = ForeignKey(Category, PROTECT)      # Part category
    
    # Commercial
    price = DecimalField(max_digits=10, decimal_places=2) # Price
    quantity = IntegerField(default=0)            # Stock quantity
    condition = CharField(choices=['NEW', 'USED']) # Part condition
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Key Features

**1. Vehicle Compatibility**
- Parts are linked to specific vehicle configurations (Brand → Model → Year → Engine)
- Engine field is optional (nullable) to support parts compatible with multiple engines
- Database indexes for fast vehicle-based searches

**2. Supplier Management**
- Each part belongs to exactly one supplier
- Cascade deletion: If supplier is deleted, all their parts are deleted
- Supplier can manage multiple parts

**3. Stock Management**
- `quantity` field tracks available inventory
- `is_in_stock()` method returns True if quantity > 0
- Easy to implement low-stock alerts

**4. Product Information**
- `reference` is unique (SKU/Part Number)
- Supports both NEW and USED parts
- Detailed description field for specifications

**5. Categorization**
- Linked to hierarchical Category model
- Supports parent-child category relationships
- Example: Electronics > Electrical > Batteries

### Relations

```
Supplier (1) ──→ (many) Part
    │
    └── CASCADE deletion

Brand ──→ Part
Model ──→ Part
ModelYear ──→ Part
Engine ──→ Part (optional)
Category ──→ Part
```

### Database Optimization

**Indexes:**
- `(supplier, created_at)` - Supplier inventory queries
- `(brand, model, model_year)` - Vehicle search
- `(category)` - Category filtering

**Foreign Key Constraints:**
- `supplier`: CASCADE (delete parts when supplier is deleted)
- `brand`, `model`, `model_year`, `category`: PROTECT (prevent accidental deletion of referenced data)
- `engine`: SET_NULL (allow deletion of engine type)

### Usage Examples

```python
# Get part details
part = Part.objects.get(reference="BMW-325i-OIL-FILTER")
print(part.get_vehicle_compatibility())  # "BMW 325i (2020)"

# Check stock availability
if part.is_in_stock():
    print(f"In stock: {part.quantity} units available")

# Get supplier's parts
supplier_parts = Part.objects.filter(supplier=supplier_id)

# Find parts by vehicle
parts = Part.objects.filter(
    brand=brand_id,
    model=model_id,
    model_year=year_id
)

# Find parts by category
parts = Part.objects.filter(category__parent=category_id)
```

### Next Steps

1. Create serializers for Part model (PartSerializer, PartDetailSerializer)
2. Implement REST API endpoints (CRUD operations)
3. Add filtering and searching capabilities
4. Create PartImage model for multiple images per part
5. Implement Cart and Order systems that reference Part

---

## Getting Started

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker Desktop installed
- Docker Compose installed

**Steps:**

1. **Create environment file:**
```bash
cp .env.example .env
```

2. **Build and start containers:**
```bash
docker-compose build
docker-compose up -d
```

3. **Run migrations:**
```bash
docker-compose exec web python manage.py migrate
```

4. **Create superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Access the application:**
- Django Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/
- pgAdmin: http://localhost:5050 (Email: admin@carparts.com, Password: admin)

📖 See **[DOCKER.md](DOCKER.md)** for complete Docker documentation.
📖 See **[PGADMIN_GUIDE.md](PGADMIN_GUIDE.md)** for database management guide.

### Option 2: Local Development

**Prerequisites:**
- Python 3.11+
- PostgreSQL 15+
- pip
- virtualenv

**Steps:**

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env and set DB_HOST=localhost
```

5. **Create PostgreSQL database:**
```sql
CREATE DATABASE carparts_db;
```

6. **Run migrations:**
```bash
python manage.py migrate
```

7. **Create superuser:**
```bash
python manage.py createsuperuser
```

8. **Run development server:**
```bash
python manage.py runserver
```

## Project Structure

```
backend/
├── carparts/              # Django project settings
│   ├── settings.py        # Configured for PostgreSQL, REST framework, CORS
│   ├── urls.py            # Main URL routing
│   └── wsgi.py
├── marketplace/           # Main application
│   ├── models.py          # Database models (to be implemented)
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers (to be created)
│   ├── urls.py            # App-specific URLs
│   └── admin.py           # Admin configurations
├── media/                 # User uploaded files (images)
├── staticfiles/           # Collected static files
├── venv/                  # Virtual environment
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Django container definition
├── entrypoint.sh          # Docker startup script
├── .env.example           # Environment variables template
├── .dockerignore          # Docker build exclusions
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
├── README.md              # This file
├── DOCKER.md              # Docker deployment guide
└── QUICKSTART.md          # Development quick reference

```

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference for common tasks
- **[DOCKER.md](DOCKER.md)** - Complete Docker deployment guide
- **[PGADMIN_GUIDE.md](PGADMIN_GUIDE.md)** - Database management UI guide

## Docker Containers

The project uses the following containers:

1. **PostgreSQL** (`db`) - Database server (Port 5432)
2. **Django** (`web`) - Backend API (Port 8000)
3. **pgAdmin** (`pgadmin`) - Database management UI (Port 5050)
4. **Redis** (`redis`) - Caching & task queue (Port 6379)
5. **Nginx** (optional) - Reverse proxy for production

## License

TBD
