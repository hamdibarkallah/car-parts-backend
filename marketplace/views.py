from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import models
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, PartSerializer, PartCreateSerializer, PartUpdateSerializer
from .models import User, Part


class RegisterView(generics.CreateAPIView):
    """
    Register a new user (Client or Supplier)
    
    Create a new user account with role-based access.
    Clients need basic information, while Suppliers must provide business details.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new user account (CLIENT or SUPPLIER)",
        operation_summary="User Registration",
        tags=['Authentication'],
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
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
                }
            ),
            400: "Bad Request - Invalid input data"
        }
    )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User login endpoint
    
    Authenticate user and receive JWT access and refresh tokens.
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login with username and password to receive JWT tokens",
        operation_summary="User Login",
        tags=['Authentication'],
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
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
                }
            ),
            400: "Bad Request - Invalid credentials"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    User logout endpoint
    
    Blacklist the refresh token to logout the user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout user by blacklisting the refresh token",
        operation_summary="User Logout",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist')
            }
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Logout successful"
                    }
                }
            ),
            400: "Bad Request - Invalid token"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Get current authenticated user profile
    
    Returns the profile information of the currently logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get the current authenticated user's profile information",
        operation_summary="Get User Profile",
        tags=['Authentication'],
        responses={
            200: openapi.Response(
                description="User profile retrieved successfully",
                schema=UserSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "johndoe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone": "+21612345678",
                        "role": "CLIENT"
                    }
                }
            ),
            401: "Unauthorized - Authentication required"
        }
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Part CRUD Views

class PartListCreateView(generics.ListCreateAPIView):
    """
    List all parts or create a new part (Supplier only)
    
    GET: List all parts with complete information
    POST: Create a new part (Suppliers only)
    """
    queryset = Part.objects.all().select_related(
        'supplier__user', 'brand', 'model', 'model_year', 'engine', 'category'
    ).order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PartCreateSerializer
        return PartSerializer
    
    def get_queryset(self):
        """Filter parts based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by supplier
        supplier_id = self.request.query_params.get('supplier')
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        # Filter by brand
        brand_id = self.request.query_params.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by condition
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Filter by in stock
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(quantity__gt=0)
        
        # Search by name or reference
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(reference__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="List all parts with filtering and search capabilities",
        operation_summary="List Parts",
        tags=['Parts'],
        manual_parameters=[
            openapi.Parameter('supplier', openapi.IN_QUERY, description="Filter by supplier ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('brand', openapi.IN_QUERY, description="Filter by brand ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('condition', openapi.IN_QUERY, description="Filter by condition (NEW/USED)", type=openapi.TYPE_STRING),
            openapi.Parameter('in_stock', openapi.IN_QUERY, description="Filter by in stock status (true/false)", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in name, reference, description", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Parts retrieved successfully",
                schema=PartSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "supplier": {
                                "id": 1,
                                "business_name": "Auto Parts Tunisia",
                                "user": {"id": 1, "username": "supplier1"}
                            },
                            "name": "Oil Filter",
                            "reference": "BMW-325i-OIL-FILTER",
                            "description": "Original BMW oil filter",
                            "brand": {"id": 1, "name": "BMW"},
                            "model": {"id": 5, "name": "325i"},
                            "model_year": {"id": 10, "year": 2020},
                            "engine": {"id": 3, "name": "2.0L Turbo", "type": "Petrol", "horsepower": 245},
                            "category": {"id": 2, "name": "Engine Parts"},
                            "price": 15.99,
                            "quantity": 100,
                            "condition": "NEW",
                            "is_in_stock": True,
                            "vehicle_compatibility": "BMW 325i (2020)",
                            "created_at": "2024-01-01T10:00:00Z",
                            "updated_at": "2024-01-01T10:00:00Z"
                        }
                    ]
                }
            ),
            401: "Unauthorized - Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new part (Suppliers only)",
        operation_summary="Create Part",
        tags=['Parts'],
        request_body=PartCreateSerializer,
        responses={
            201: openapi.Response(
                description="Part created successfully",
                schema=PartSerializer
            ),
            400: "Bad Request - Invalid input data",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Supplier access required"
        }
    )
    def post(self, request, *args, **kwargs):
        # Check if user is a supplier
        if not hasattr(request.user, 'supplier_profile'):
            return Response(
                {'error': 'Only suppliers can create parts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class PartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a part
    
    GET: Get part details by ID
    PUT/PATCH: Update part (Supplier only, own parts)
    DELETE: Delete part (Supplier only, own parts)
    """
    queryset = Part.objects.all().select_related(
        'supplier__user', 'brand', 'model', 'model_year', 'engine', 'category'
    )
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PartUpdateSerializer
        return PartSerializer
    
    @swagger_auto_schema(
        operation_description="Get detailed information about a specific part",
        operation_summary="Get Part Details",
        tags=['Parts'],
        responses={
            200: openapi.Response(
                description="Part details retrieved successfully",
                schema=PartSerializer
            ),
            404: "Not Found - Part does not exist",
            401: "Unauthorized - Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update part information (Suppliers only, own parts)",
        operation_summary="Update Part",
        tags=['Parts'],
        request_body=PartUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Part updated successfully",
                schema=PartSerializer
            ),
            400: "Bad Request - Invalid input data",
            403: "Forbidden - Can only update own parts",
            404: "Not Found - Part does not exist",
            401: "Unauthorized - Authentication required"
        }
    )
    def put(self, request, *args, **kwargs):
        part = self.get_object()
        if not hasattr(request.user, 'supplier_profile') or part.supplier != request.user.supplier_profile:
            return Response(
                {'error': 'You can only update your own parts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update part information partially (Suppliers only, own parts)",
        operation_summary="Partial Update Part",
        tags=['Parts'],
        request_body=PartUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Part updated successfully",
                schema=PartSerializer
            ),
            400: "Bad Request - Invalid input data",
            403: "Forbidden - Can only update own parts",
            404: "Not Found - Part does not exist",
            401: "Unauthorized - Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        part = self.get_object()
        if not hasattr(request.user, 'supplier_profile') or part.supplier != request.user.supplier_profile:
            return Response(
                {'error': 'You can only update your own parts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a part (Suppliers only, own parts)",
        operation_summary="Delete Part",
        tags=['Parts'],
        responses={
            204: openapi.Response(
                description="Part deleted successfully"
            ),
            403: "Forbidden - Can only delete own parts",
            404: "Not Found - Part does not exist",
            401: "Unauthorized - Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        part = self.get_object()
        if not hasattr(request.user, 'supplier_profile') or part.supplier != request.user.supplier_profile:
            return Response(
                {'error': 'You can only delete your own parts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)
