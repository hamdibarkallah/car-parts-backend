# Quick Start Guide

## Project Setup Complete! ✅

Your Django Car Parts Marketplace project has been successfully initialized.

## What's Been Set Up

### 1. Virtual Environment
- Location: `venv/`
- Python packages installed:
  - Django 5.2.12
  - Django REST Framework 3.17.1
  - django-cors-headers 4.9.0
  - Pillow 12.2.0

### 2. Django Project Structure
```
backend/
├── carparts/           # Main project directory
│   ├── settings.py     # Configured with REST framework, CORS, media files
│   ├── urls.py         # Main URL configuration
│   └── ...
├── marketplace/        # Main app for marketplace functionality
│   ├── models.py       # Ready for model definitions
│   ├── views.py        # Ready for API views
│   ├── urls.py         # App-specific URLs
│   └── ...
├── venv/               # Virtual environment
├── manage.py           # Django management script
├── db.sqlite3          # Database (created after migrations)
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
└── README.md           # Project documentation
```

### 3. Configuration Highlights

**Settings (`carparts/settings.py`):**
- ✅ REST Framework configured with pagination (20 items/page)
- ✅ CORS enabled for Angular frontend (localhost:4200)
- ✅ Media files configured for part images
- ✅ Timezone set to Africa/Tunis
- ✅ Marketplace app registered

**URLs:**
- Admin panel: `/admin/`
- API endpoints: `/api/` (routed to marketplace app)

## Next Steps

### 1. Activate Virtual Environment
```bash
# Windows
.\venv\Scripts\activate
```

### 2. Create Django Models
Edit `marketplace/models.py` to implement the data model:
- User, Supplier, Client
- Brand, Model, ModelYear, Engine, Vehicle
- Category
- Part, PartImage
- Cart, CartItem
- Order, OrderItem

### 3. Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/admin/`

### 6. Implement API Endpoints
- Create serializers in `marketplace/serializers.py`
- Create viewsets in `marketplace/views.py`
- Register routes in `marketplace/urls.py`

## Development Workflow

### Creating Models
1. Define models in `marketplace/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Register models in `marketplace/admin.py` for admin interface

### Creating API Endpoints
1. Create serializers for models
2. Create ViewSets or APIViews
3. Register ViewSets with router or add paths to urls.py
4. Test with tools like Postman or httpie

### Testing API
```bash
# Install httpie (optional)
pip install httpie

# Test API endpoint
http GET http://127.0.0.1:8000/api/
```

## Useful Commands

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install new package
pip install package-name
pip freeze > requirements.txt

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Django shell
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic
```

## Project Architecture

### User Flow
1. **Suppliers** register and create part listings
2. **Clients** browse parts by vehicle or category
3. **Clients** add parts to cart
4. **Clients** place orders
5. **Admins** manage the platform

### Data Hierarchy
- Brand → Model → ModelYear → Engine
- Category (hierarchical with parent/child)
- Part (links to vehicle specs and category)

### Key Features to Implement
- [ ] Custom User model with roles (Admin, Supplier, Client)
- [ ] Vehicle-based part filtering
- [ ] Supplier inventory management
- [ ] Shopping cart system
- [ ] Order processing with price snapshots
- [ ] Image upload for parts
- [ ] Search and filtering
- [ ] Rating system for suppliers

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)

## Troubleshooting

### Virtual Environment Not Activating
Make sure you're in the `backend` directory and run:
```bash
.\venv\Scripts\activate
```

### Module Not Found Error
Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Issues
Delete `db.sqlite3` and run migrations again:
```bash
python manage.py migrate
```

## Happy Coding! 🚀
