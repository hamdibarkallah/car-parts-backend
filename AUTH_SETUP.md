# Authentication System - Quick Setup Guide

## ✅ What's Been Implemented

### 1. Custom User Model
- **Location:** `marketplace/models.py`
- **Features:**
  - Extended Django's AbstractUser
  - Role field (ADMIN, CLIENT, SUPPLIER)
  - Phone number validation
  - Helper methods: `is_admin()`, `is_client()`, `is_supplier()`

### 2. Client & Supplier Models
- **Client Model:** Basic profile for customers
- **Supplier Model:** Extended profile with business information
  - business_name
  - address
  - governorate
  - postal_code
  - rating (0.0 default)

### 3. JWT Authentication
- **Package:** djangorestframework-simplejwt
- **Access Token:** 1 hour lifetime
- **Refresh Token:** 7 days lifetime
- **Features:** Token rotation and blacklisting enabled

### 4. API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/register/` | POST | No | Register new user (Client/Supplier) |
| `/api/auth/login/` | POST | No | Login and get JWT tokens |
| `/api/auth/logout/` | POST | Yes | Logout (blacklist refresh token) |
| `/api/auth/profile/` | GET | Yes | Get current user profile |
| `/api/auth/token/refresh/` | POST | No | Refresh access token |

## 🚀 Next Steps to Complete Setup

### Step 1: Start Docker Containers (if not running)
```bash
docker-compose up -d
```

### Step 2: Install New Dependencies
```bash
# Build the container with updated requirements
docker-compose build web
docker-compose up -d
```

### Step 3: Create and Run Migrations
```bash
# Create migrations for the new User model
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

### Step 4: Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
# Follow prompts to create admin user
```

### Step 5: Test Authentication APIs

#### Test Registration (Client)
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testclient",
    "email": "client@test.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "Client",
    "phone": "+21612345678",
    "role": "CLIENT"
  }'
```

#### Test Registration (Supplier)
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testsupplier",
    "email": "supplier@test.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "Supplier",
    "phone": "+21698765432",
    "role": "SUPPLIER",
    "business_name": "Test Auto Parts",
    "address": "Avenue Bourguiba, Tunis",
    "governorate": "Tunis",
    "postal_code": "1000"
  }'
```

#### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testclient",
    "password": "testpass123"
  }'
```

#### Test Profile (use access token from login)
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 📁 Files Created/Modified

### New Files:
- ✅ `marketplace/serializers.py` - Authentication serializers
- ✅ `API_DOCUMENTATION.md` - Complete API documentation
- ✅ `AUTH_SETUP.md` - This file

### Modified Files:
- ✅ `marketplace/models.py` - User, Client, Supplier models
- ✅ `marketplace/views.py` - Authentication views
- ✅ `marketplace/urls.py` - Authentication endpoints
- ✅ `marketplace/admin.py` - Admin configuration
- ✅ `carparts/settings.py` - JWT & custom user config
- ✅ `requirements.txt` - Added djangorestframework-simplejwt

## 🔐 Security Features

1. **Password Validation:** Django's built-in password validators
2. **Token Blacklisting:** Refresh tokens blacklisted on logout
3. **Token Rotation:** New refresh token issued on each refresh
4. **Phone Validation:** Regex validator for phone numbers
5. **Role-Based Access:** User roles for permission management

## 🎯 User Registration Flow

### Client Registration:
1. User provides: username, email, password, name, phone
2. System creates User with CLIENT role
3. System creates Client profile (linked to User)
4. Returns: user data + JWT tokens

### Supplier Registration:
1. User provides: all client fields + business details
2. System validates business information
3. System creates User with SUPPLIER role
4. System creates Supplier profile with business info
5. Returns: user data + JWT tokens

## 🔑 Authentication Flow

1. **Login:**
   - Send username + password to `/api/auth/login/`
   - Receive access token (1 hour) + refresh token (7 days)

2. **Access Protected Routes:**
   - Add header: `Authorization: Bearer <access_token>`

3. **Token Expired:**
   - Send refresh token to `/api/auth/token/refresh/`
   - Receive new access token + new refresh token

4. **Logout:**
   - Send refresh token to `/api/auth/logout/`
   - Token blacklisted (cannot be used again)

## 🛠 Troubleshooting

### Issue: "AUTH_USER_MODEL is not set"
**Solution:** Ensure `AUTH_USER_MODEL = 'marketplace.User'` is in settings.py

### Issue: "No such table: users"
**Solution:** Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

### Issue: "Unable to log in with provided credentials"
**Solution:** 
- Check username/password are correct
- Ensure user exists and is active
- Try creating a new user via registration

### Issue: Token not working
**Solution:**
- Check token hasn't expired
- Verify Authorization header: `Bearer <token>`
- Ensure token isn't blacklisted (after logout)

## 📊 Database Schema

### Users Table:
- id, username, email, password
- first_name, last_name, phone
- role (ADMIN/CLIENT/SUPPLIER)
- is_staff, is_active, is_superuser
- date_joined, last_login

### Clients Table:
- user_id (PK, FK → users)
- created_at, updated_at

### Suppliers Table:
- user_id (PK, FK → users)
- business_name, address
- governorate, postal_code
- rating
- created_at, updated_at

## 🎨 Admin Panel

Access at: http://localhost:8000/admin/

**Features:**
- User management with role filtering
- Client profile management
- Supplier profile management
- Search by username, email, business name
- Filter by role, governorate, date

## ✅ Ready for Development

Authentication system is complete! You can now:
1. Register clients and suppliers
2. Login with JWT tokens
3. Access protected routes
4. Build additional features (vehicles, parts, cart, orders)

See `API_DOCUMENTATION.md` for complete API reference.
