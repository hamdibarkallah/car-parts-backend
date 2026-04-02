# Car Parts Marketplace - API Documentation

## Authentication System

### Base URL
```
http://localhost:8000/api/
```

---

## Authentication Endpoints

### 1. Register User

**Endpoint:** `POST /api/auth/register/`

**Description:** Register a new user (Client, Supplier, or Admin)

**Authentication:** Not required

**Request Body (Client):**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securePassword123",
  "password2": "securePassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+21612345678",
  "role": "CLIENT"
}
```

**Request Body (Supplier):**
```json
{
  "username": "autoparts_supplier",
  "email": "supplier@example.com",
  "password": "securePassword123",
  "password2": "securePassword123",
  "first_name": "Ahmed",
  "last_name": "Ben Ali",
  "phone": "+21698765432",
  "role": "SUPPLIER",
  "business_name": "Auto Parts Tunisia",
  "address": "Avenue Habib Bourguiba, Tunis",
  "governorate": "Tunis",
  "postal_code": "1000"
}
```

**Success Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
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

**Error Response (400 Bad Request):**
```json
{
  "password": ["Password fields didn't match."],
  "email": ["User with this email already exists."]
}
```

---

### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Description:** Authenticate user and receive JWT tokens

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securePassword123"
}
```

**Success Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+21612345678",
    "role": "CLIENT"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Login successful"
}
```

**Error Response (400 Bad Request):**
```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

---

### 3. Refresh Token

**Endpoint:** `POST /api/auth/token/refresh/`

**Description:** Get a new access token using refresh token

**Authentication:** Not required (but needs valid refresh token)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Logout

**Endpoint:** `POST /api/auth/logout/`

**Description:** Blacklist the refresh token (logout user)

**Authentication:** Required (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

---

### 5. Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Description:** Get current authenticated user's profile

**Authentication:** Required (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+21612345678",
  "role": "CLIENT"
}
```

---

## User Roles

### Available Roles:
- **ADMIN** - System administrator with full access
- **CLIENT** - Regular customer who can browse and purchase parts
- **SUPPLIER** - Supplier who can list and manage car parts

### Role-Specific Features:

**CLIENT:**
- Browse and search parts
- Add parts to cart
- Place orders
- Manage vehicles

**SUPPLIER:**
- All client features
- Create and manage part listings
- View orders for their parts
- Update inventory
- Manage business profile

**ADMIN:**
- Full system access
- User management
- Content moderation
- System configuration

---

## Authentication Flow

### Using JWT Tokens

1. **Register or Login** to receive tokens:
   - `access` token (expires in 1 hour)
   - `refresh` token (expires in 7 days)

2. **Access Protected Routes:**
   ```
   Authorization: Bearer <access_token>
   ```

3. **Refresh Access Token** when it expires:
   ```
   POST /api/auth/token/refresh/
   Body: { "refresh": "<refresh_token>" }
   ```

4. **Logout** to blacklist refresh token:
   ```
   POST /api/auth/logout/
   Body: { "refresh": "<refresh_token>" }
   ```

---

## Testing with cURL

### Register Client
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

### Register Supplier
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

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testclient",
    "password": "testpass123"
  }'
```

### Get Profile (with token)
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer <your_access_token>"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

---

## Token Lifetimes

- **Access Token:** 1 hour
- **Refresh Token:** 7 days
- **Rotation:** Enabled (new refresh token on each refresh)
- **Blacklisting:** Enabled (tokens blacklisted on logout)

---

## Next Steps

Once authentication is working, you can:
1. Add vehicle models (Brand, Model, ModelYear, Engine)
2. Implement part listing functionality
3. Create shopping cart system
4. Build order management
5. Add search and filtering
