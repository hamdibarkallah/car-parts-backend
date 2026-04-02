# Swagger API Documentation Guide

## 🎯 What is Swagger?

Swagger provides an interactive API documentation interface where you can:
- View all available endpoints
- See request/response schemas
- Test APIs directly from the browser
- Authenticate and test protected endpoints
- Export OpenAPI specifications

Just like Symfony's API Platform with annotations!

## 🚀 Accessing Swagger Documentation

### Available Documentation URLs:

| URL | Description |
|-----|-------------|
| **http://localhost:8000/** | Swagger UI (Interactive) - **Main Interface** |
| **http://localhost:8000/swagger/** | Swagger UI Alternative URL |
| **http://localhost:8000/redoc/** | ReDoc UI (Alternative beautiful docs) |
| **http://localhost:8000/swagger.json** | OpenAPI JSON Schema |
| **http://localhost:8000/swagger.yaml** | OpenAPI YAML Schema |

### Primary Access:
```
http://localhost:8000/
```
or
```
http://localhost:8000/swagger/
```

## 🔐 How to Test Authenticated Endpoints

### Step 1: Register or Login
1. In Swagger UI, find the **Authentication** section
2. Expand `POST /api/auth/login/` or `POST /api/auth/register/`
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. Copy the `access` token from the response

### Step 2: Authorize
1. Click the **"Authorize"** button at the top right (🔒 icon)
2. In the popup, enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"
4. Click "Close"

### Step 3: Test Protected Endpoints
Now all authenticated endpoints will work! Try:
- `GET /api/auth/profile/` - Get your profile
- `POST /api/auth/logout/` - Logout

## 📋 Example: Complete Authentication Flow in Swagger

### 1. Register a New Client
```
POST /api/auth/register/

Request Body:
{
  "username": "testclient",
  "email": "client@test.com",
  "password": "testpass123",
  "password2": "testpass123",
  "first_name": "Test",
  "last_name": "Client",
  "phone": "+21612345678",
  "role": "CLIENT"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "testclient",
    "email": "client@test.com",
    "first_name": "Test",
    "last_name": "Client",
    "phone": "+21612345678",
    "role": "CLIENT"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

### 2. Copy Access Token
Copy the `access` token value (the long JWT string)

### 3. Click Authorize Button
Enter: `Bearer eyJ0eXAiOiJKV1QiLCJhbGc...`

### 4. Test Protected Endpoint
```
GET /api/auth/profile/
```

## 🎨 Swagger Features

### Interactive Testing
- **Try it out**: Test any endpoint directly
- **Execute**: Send real requests to your API
- **Response**: See actual responses with status codes
- **Schema**: View request/response models

### Documentation Details
- **Operation Summary**: Brief description
- **Operation Description**: Detailed explanation
- **Parameters**: All request parameters
- **Request Body**: Schema with examples
- **Responses**: All possible responses with examples
- **Tags**: Organized by category (Authentication, Parts, etc.)

### Authentication Support
- **Bearer Token**: JWT authentication
- **Authorize**: Global authentication for all endpoints
- **Lock Icons**: Shows which endpoints require auth

## 📊 API Organization

### Tags (Categories):
- **Authentication** - Register, Login, Logout, Profile
- (Future: Vehicles, Parts, Cart, Orders, etc.)

Each tag groups related endpoints together for easy navigation.

## 🔧 Adding Swagger Annotations

To document your APIs (similar to Symfony's OA annotations):

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MyView(APIView):
    @swagger_auto_schema(
        operation_description="Detailed description here",
        operation_summary="Brief summary",
        tags=['Category Name'],
        request_body=MySerializer,
        responses={
            200: openapi.Response(
                description="Success response",
                schema=ResponseSerializer,
                examples={
                    "application/json": {
                        "key": "value"
                    }
                }
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        # Your view logic
        pass
```

## 🎯 Current Available Endpoints

### Authentication Section:
1. **POST /api/auth/register/** - Register new user
2. **POST /api/auth/login/** - Login and get tokens
3. **POST /api/auth/logout/** - Logout (blacklist token)
4. **GET /api/auth/profile/** - Get current user profile
5. **POST /api/auth/token/refresh/** - Refresh access token

## 🌐 ReDoc Alternative

For a different documentation style, visit:
```
http://localhost:8000/redoc/
```

ReDoc provides:
- Beautiful three-column layout
- Better for reading long documentation
- Print-friendly format
- Same API information

## 📥 Export API Schema

### JSON Format:
```
http://localhost:8000/swagger.json
```

### YAML Format:
```
http://localhost:8000/swagger.yaml
```

Use these for:
- Frontend code generation
- API client libraries
- Postman/Insomnia import
- Third-party integrations

## ✅ Next Steps

1. **Rebuild Docker containers** to install drf-yasg:
   ```bash
   docker-compose build web
   docker-compose up -d
   ```

2. **Access Swagger UI**:
   ```
   http://localhost:8000/
   ```

3. **Test Authentication Flow**:
   - Register a user
   - Login to get tokens
   - Authorize with Bearer token
   - Test protected endpoints

4. **Add More APIs** and they'll automatically appear in Swagger!

## 🆚 Symfony Comparison

| Symfony (API Platform) | Django (drf-yasg) |
|------------------------|-------------------|
| `@OA\Post()` annotation | `@swagger_auto_schema()` decorator |
| Auto-generates from entities | Auto-generates from serializers |
| `/api/docs` endpoint | `/swagger/` endpoint |
| Interactive Swagger UI | Interactive Swagger UI |
| OpenAPI 3.0 | OpenAPI 2.0/3.0 |

Same concept, different syntax! Both give you full Swagger documentation.

## 🎉 Benefits

✅ **No manual documentation** - Auto-generated from code  
✅ **Interactive testing** - Test APIs without Postman  
✅ **Always up-to-date** - Updates when code changes  
✅ **Team collaboration** - Share API docs easily  
✅ **Client generation** - Generate API clients automatically  
✅ **Local testing** - Works perfectly on localhost  

Enjoy your interactive API documentation! 🚀
