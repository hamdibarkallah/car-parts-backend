from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import models
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PartSerializer, PartCreateSerializer, PartUpdateSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    OrderSerializer, OrderListSerializer,
    BrandSerializer, ModelSerializer, ModelYearSerializer, EngineSerializer,
    CategorySerializer,
    PartImageSerializer, PartImageUploadSerializer,
    UserVehicleSerializer,
)
from .models import (
    User, Part, Cart, CartItem, Order, OrderItem,
    Brand, Model, ModelYear, Engine, Category, PartImage,
    UserVehicle,
)


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
        
        # Filter by model
        model_id = self.request.query_params.get('model')
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        # Filter by year (model_year)
        year_id = self.request.query_params.get('year')
        if year_id:
            queryset = queryset.filter(model_year_id=year_id)
        
        # Filter by engine
        engine_id = self.request.query_params.get('engine')
        if engine_id:
            queryset = queryset.filter(engine_id=engine_id)
        
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
        
        # Filter by price range
        price_min = self.request.query_params.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        price_max = self.request.query_params.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
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
            openapi.Parameter('model', openapi.IN_QUERY, description="Filter by model ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('year', openapi.IN_QUERY, description="Filter by model year ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('engine', openapi.IN_QUERY, description="Filter by engine ID", type=openapi.TYPE_INTEGER),
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
        # Admin has full access, otherwise must be a supplier
        if not request.user.is_admin() and not hasattr(request.user, 'supplier_profile'):
            return Response(
                {'error': 'Only suppliers and admins can create parts'},
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
        # Admin has full access, suppliers can only update their own parts
        if not request.user.is_admin():
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
        # Admin has full access, suppliers can only update their own parts
        if not request.user.is_admin():
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
        # Admin has full access, suppliers can only delete their own parts
        if not request.user.is_admin():
            if not hasattr(request.user, 'supplier_profile') or part.supplier != request.user.supplier_profile:
                return Response(
                    {'error': 'You can only delete your own parts'},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().delete(request, *args, **kwargs)


# Cart Views

class CartView(APIView):
    """
    Get the current client's cart
    
    GET: Retrieve cart with all items, totals
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def _get_client(self, user):
        if not hasattr(user, 'client_profile'):
            return None
        return user.client_profile
    
    @swagger_auto_schema(
        operation_description="Get the current client's cart with all items and totals",
        operation_summary="Get Cart",
        tags=['Cart'],
        responses={
            200: CartSerializer,
            403: "Forbidden - Client access required",
        }
    )
    def get(self, request):
        client = self._get_client(request.user)
        if not client:
            return Response({'error': 'Only clients can access the cart'}, status=status.HTTP_403_FORBIDDEN)
        
        cart, _ = Cart.objects.get_or_create(client=client)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddItemView(APIView):
    """
    Add an item to the cart
    
    POST: Add a part to the client's cart. If part already in cart, quantity is increased.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Add a part to the client's cart. If the part already exists in the cart, the quantity is increased.",
        operation_summary="Add Item to Cart",
        tags=['Cart'],
        request_body=AddToCartSerializer,
        responses={
            200: CartSerializer,
            400: "Bad Request - Invalid data or stock issue",
            403: "Forbidden - Client access required",
        }
    )
    def post(self, request):
        if not hasattr(request.user, 'client_profile'):
            return Response({'error': 'Only clients can add to cart'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        client = request.user.client_profile
        cart, _ = Cart.objects.get_or_create(client=client)
        part = Part.objects.get(id=serializer.validated_data['part_id'])
        quantity = serializer.validated_data['quantity']
        
        # If part already in cart, increase quantity
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, part=part,
            defaults={'quantity': quantity}
        )
        if not created:
            new_qty = cart_item.quantity + quantity
            if new_qty > part.quantity:
                return Response(
                    {'error': f'Total quantity ({new_qty}) exceeds available stock ({part.quantity}).'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_qty
            cart_item.save()
        
        return Response(CartSerializer(cart).data)


class CartItemUpdateView(APIView):
    """
    Update or remove a cart item
    
    PUT: Update cart item quantity
    DELETE: Remove item from cart
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def _get_cart_item(self, request, item_id):
        if not hasattr(request.user, 'client_profile'):
            return None, Response({'error': 'Only clients can modify cart'}, status=status.HTTP_403_FORBIDDEN)
        try:
            cart_item = CartItem.objects.select_related('cart__client', 'part').get(
                id=item_id, cart__client=request.user.client_profile
            )
            return cart_item, None
        except CartItem.DoesNotExist:
            return None, Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Update the quantity of a specific cart item",
        operation_summary="Update Cart Item Quantity",
        tags=['Cart'],
        request_body=UpdateCartItemSerializer,
        responses={
            200: CartSerializer,
            400: "Bad Request - Invalid quantity or stock issue",
            403: "Forbidden - Client access required",
            404: "Not Found - Cart item not found",
        }
    )
    def put(self, request, item_id):
        cart_item, error = self._get_cart_item(request, item_id)
        if error:
            return error
        
        serializer = UpdateCartItemSerializer(data=request.data, instance=cart_item)
        serializer.is_valid(raise_exception=True)
        
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        
        return Response(CartSerializer(cart_item.cart).data)
    
    @swagger_auto_schema(
        operation_description="Remove an item from the cart",
        operation_summary="Remove Cart Item",
        tags=['Cart'],
        responses={
            200: CartSerializer,
            403: "Forbidden - Client access required",
            404: "Not Found - Cart item not found",
        }
    )
    def delete(self, request, item_id):
        cart_item, error = self._get_cart_item(request, item_id)
        if error:
            return error
        
        cart = cart_item.cart
        cart_item.delete()
        
        return Response(CartSerializer(cart).data)


# Order Views

class OrderListCreateView(APIView):
    """
    List orders or create order from cart
    
    GET: List all orders for the current client
    POST: Create a new order from the client's cart (copies price at order time)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="List all orders for the current client",
        operation_summary="List Orders",
        tags=['Orders'],
        responses={
            200: OrderListSerializer(many=True),
            403: "Forbidden - Client access required",
        }
    )
    def get(self, request):
        if hasattr(request.user, 'client_profile'):
            orders = Order.objects.filter(client=request.user.client_profile).order_by('-created_at')
        elif hasattr(request.user, 'supplier_profile'):
            orders = Order.objects.filter(
                items__supplier=request.user.supplier_profile
            ).distinct().order_by('-created_at')
        else:
            return Response({'error': 'No profile found'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Create a new order from the client's cart. Copies the current price of each part at order time. Clears the cart after order creation.",
        operation_summary="Create Order from Cart",
        tags=['Orders'],
        responses={
            201: OrderSerializer,
            400: "Bad Request - Cart is empty or stock issues",
            403: "Forbidden - Client access required",
        }
    )
    def post(self, request):
        if not hasattr(request.user, 'client_profile'):
            return Response({'error': 'Only clients can create orders'}, status=status.HTTP_403_FORBIDDEN)
        
        client = request.user.client_profile
        
        try:
            cart = Cart.objects.prefetch_related('items__part__supplier').get(client=client)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate stock availability before creating order
        stock_errors = []
        for item in cart_items:
            if item.quantity > item.part.quantity:
                stock_errors.append(
                    f"{item.part.name}: requested {item.quantity}, available {item.part.quantity}"
                )
        if stock_errors:
            return Response({'error': 'Insufficient stock', 'details': stock_errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order in a transaction
        with transaction.atomic():
            order = Order.objects.create(client=client, total_price=0)
            
            total = 0
            for item in cart_items:
                # Copy price at order time
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
            cart_items.delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """
    Get details of a specific order
    
    GET: Retrieve order with all items and price details
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get detailed information about a specific order including all items",
        operation_summary="Get Order Details",
        tags=['Orders'],
        responses={
            200: OrderSerializer,
            403: "Forbidden - Client access required",
            404: "Not Found - Order not found",
        }
    )
    def get(self, request, pk):
        if not hasattr(request.user, 'client_profile'):
            return Response({'error': 'Only clients can view orders'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = Order.objects.prefetch_related('items__part', 'items__supplier').get(
                id=pk, client=request.user.client_profile
            )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# Vehicle Hierarchy Views

class BrandListCreateView(generics.ListCreateAPIView):
    """
    List all brands or create a new one
    
    GET: List all brands (public)
    POST: Create a brand (Admin only)
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="List all vehicle brands",
        operation_summary="List Brands",
        tags=['Vehicle Hierarchy'],
        responses={200: BrandSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new brand (Admin only)",
        operation_summary="Create Brand",
        tags=['Vehicle Hierarchy'],
        request_body=BrandSerializer,
        responses={201: BrandSerializer, 403: "Forbidden - Admin access required"}
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can create brands'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class ModelListCreateView(generics.ListCreateAPIView):
    """
    List models (filterable by brand) or create a new one
    
    GET: List models, optionally filtered by brand_id
    POST: Create a model (Admin only)
    """
    serializer_class = ModelSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Model.objects.select_related('brand').all()
        brand_id = self.request.query_params.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        return queryset
    
    @swagger_auto_schema(
        operation_description="List vehicle models. Filter by brand using ?brand=ID",
        operation_summary="List Models",
        tags=['Vehicle Hierarchy'],
        manual_parameters=[
            openapi.Parameter('brand', openapi.IN_QUERY, description="Filter by brand ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ModelSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new model (Admin only)",
        operation_summary="Create Model",
        tags=['Vehicle Hierarchy'],
        request_body=ModelSerializer,
        responses={201: ModelSerializer, 403: "Forbidden - Admin access required"}
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can create models'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class ModelYearListCreateView(generics.ListCreateAPIView):
    """
    List model years (filterable by model) or create a new one
    
    GET: List model years, optionally filtered by model_id
    POST: Create a model year (Admin only)
    """
    serializer_class = ModelYearSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = ModelYear.objects.select_related('model__brand').all()
        model_id = self.request.query_params.get('model')
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        return queryset
    
    @swagger_auto_schema(
        operation_description="List model years. Filter by model using ?model=ID",
        operation_summary="List Model Years",
        tags=['Vehicle Hierarchy'],
        manual_parameters=[
            openapi.Parameter('model', openapi.IN_QUERY, description="Filter by model ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ModelYearSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new model year (Admin only)",
        operation_summary="Create Model Year",
        tags=['Vehicle Hierarchy'],
        request_body=ModelYearSerializer,
        responses={201: ModelYearSerializer, 403: "Forbidden - Admin access required"}
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can create model years'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class EngineListCreateView(generics.ListCreateAPIView):
    """
    List engines (filterable by model_year) or create a new one
    
    GET: List engines, optionally filtered by model_year_id
    POST: Create an engine (Admin only)
    """
    serializer_class = EngineSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Engine.objects.select_related('model_year__model__brand').all()
        model_year_id = self.request.query_params.get('model_year')
        if model_year_id:
            queryset = queryset.filter(model_year_id=model_year_id)
        return queryset
    
    @swagger_auto_schema(
        operation_description="List engines. Filter by model year using ?model_year=ID",
        operation_summary="List Engines",
        tags=['Vehicle Hierarchy'],
        manual_parameters=[
            openapi.Parameter('model_year', openapi.IN_QUERY, description="Filter by model year ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: EngineSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new engine (Admin only)",
        operation_summary="Create Engine",
        tags=['Vehicle Hierarchy'],
        request_body=EngineSerializer,
        responses={201: EngineSerializer, 403: "Forbidden - Admin access required"}
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can create engines'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


# Category Views

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    List categories or create a new one
    
    GET: List all categories. Use ?root=true to get only root categories.
    POST: Create a category (Admin only)
    """
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Category.objects.select_related('parent').prefetch_related('children').all()
        root_only = self.request.query_params.get('root')
        if root_only == 'true':
            queryset = queryset.filter(parent__isnull=True)
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset
    
    @swagger_auto_schema(
        operation_description="List categories. Use ?root=true for root categories only, or ?parent=ID for children of a specific category.",
        operation_summary="List Categories",
        tags=['Categories'],
        manual_parameters=[
            openapi.Parameter('root', openapi.IN_QUERY, description="Set to 'true' to get only root categories", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('parent', openapi.IN_QUERY, description="Filter by parent category ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new category (Admin only)",
        operation_summary="Create Category",
        tags=['Categories'],
        request_body=CategorySerializer,
        responses={201: CategorySerializer, 403: "Forbidden - Admin access required"}
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can create categories'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category
    """
    queryset = Category.objects.select_related('parent').prefetch_related('children').all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get category details",
        operation_summary="Get Category",
        tags=['Categories'],
        responses={200: CategorySerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a category (Admin only)",
        operation_summary="Update Category",
        tags=['Categories'],
        request_body=CategorySerializer,
        responses={200: CategorySerializer, 403: "Forbidden - Admin access required"}
    )
    def put(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can update categories'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a category (Admin only)",
        operation_summary="Delete Category",
        tags=['Categories'],
        responses={204: "Deleted", 403: "Forbidden - Admin access required"}
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.is_admin():
            return Response({'error': 'Only admins can delete categories'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


# PartImage Views

class PartImageListCreateView(APIView):
    """
    List images for a part or upload a new image
    
    GET: List all images for a specific part
    POST: Upload an image for a part (Supplier who owns the part, or Admin)
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    def _get_part(self, part_id):
        try:
            return Part.objects.get(id=part_id)
        except Part.DoesNotExist:
            return None
    
    @swagger_auto_schema(
        operation_description="List all images for a specific part",
        operation_summary="List Part Images",
        tags=['Part Images'],
        responses={200: PartImageSerializer(many=True), 404: "Part not found"}
    )
    def get(self, request, part_id):
        part = self._get_part(part_id)
        if not part:
            return Response({'error': 'Part not found'}, status=status.HTTP_404_NOT_FOUND)
        
        images = PartImage.objects.filter(part=part)
        serializer = PartImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Upload an image for a part (owner Supplier or Admin)",
        operation_summary="Upload Part Image",
        tags=['Part Images'],
        request_body=PartImageUploadSerializer,
        responses={
            201: PartImageSerializer,
            403: "Forbidden - Must be part owner or admin",
            404: "Part not found",
        }
    )
    def post(self, request, part_id):
        part = self._get_part(part_id)
        if not part:
            return Response({'error': 'Part not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check ownership: admin or supplier who owns the part
        if not request.user.is_admin():
            if not hasattr(request.user, 'supplier_profile') or part.supplier != request.user.supplier_profile:
                return Response({'error': 'You can only upload images for your own parts'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PartImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(part=part)
        
        return Response(
            PartImageSerializer(image, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class PartImageDeleteView(APIView):
    """
    Delete a specific part image
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Delete a part image (owner Supplier or Admin)",
        operation_summary="Delete Part Image",
        tags=['Part Images'],
        responses={
            204: "Deleted",
            403: "Forbidden - Must be part owner or admin",
            404: "Image not found",
        }
    )
    def delete(self, request, pk):
        try:
            image = PartImage.objects.select_related('part__supplier').get(id=pk)
        except PartImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user.is_admin():
            if not hasattr(request.user, 'supplier_profile') or image.part.supplier != request.user.supplier_profile:
                return Response({'error': 'You can only delete images from your own parts'}, status=status.HTTP_403_FORBIDDEN)
        
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# My Garage Views

class UserVehicleListCreateView(APIView):
    """
    List user's saved vehicles or add a new one
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vehicles = UserVehicle.objects.filter(user=request.user).select_related(
            'brand', 'model', 'model_year', 'engine'
        )
        serializer = UserVehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserVehicleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserVehicleDetailView(APIView):
    """
    Get, update, or delete a saved vehicle
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_vehicle(self, request, pk):
        try:
            return UserVehicle.objects.select_related(
                'brand', 'model', 'model_year', 'engine'
            ).get(pk=pk, user=request.user)
        except UserVehicle.DoesNotExist:
            return None

    def get(self, request, pk):
        vehicle = self._get_vehicle(request, pk)
        if not vehicle:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserVehicleSerializer(vehicle).data)

    def patch(self, request, pk):
        vehicle = self._get_vehicle(request, pk)
        if not vehicle:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserVehicleSerializer(vehicle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        vehicle = self._get_vehicle(request, pk)
        if not vehicle:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserVehicleSetDefaultView(APIView):
    """
    Set a vehicle as the default
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            vehicle = UserVehicle.objects.get(pk=pk, user=request.user)
        except UserVehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)
        vehicle.is_default = True
        vehicle.save()
        return Response(UserVehicleSerializer(vehicle).data)
