from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Client, Supplier, Part, Brand, Model, ModelYear, Engine, Category, Cart, CartItem, Order, OrderItem, PartImage, UserVehicle


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role']
        read_only_fields = ['id']


class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Client
        fields = ['user', 'created_at', 'updated_at']


class SupplierProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Supplier
        fields = ['user', 'business_name', 'address', 'governorate', 'postal_code', 'rating', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')
    
    # Supplier-specific fields (optional)
    business_name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    governorate = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'role',
                  'business_name', 'address', 'governorate', 'postal_code']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate supplier fields if role is SUPPLIER
        if attrs.get('role') == 'SUPPLIER':
            if not attrs.get('business_name'):
                raise serializers.ValidationError({"business_name": "Business name is required for suppliers."})
            if not attrs.get('address'):
                raise serializers.ValidationError({"address": "Address is required for suppliers."})
            if not attrs.get('governorate'):
                raise serializers.ValidationError({"governorate": "Governorate is required for suppliers."})
            if not attrs.get('postal_code'):
                raise serializers.ValidationError({"postal_code": "Postal code is required for suppliers."})
        
        return attrs
    
    def create(self, validated_data):
        # Remove password2 and supplier fields from validated_data
        validated_data.pop('password2')
        business_name = validated_data.pop('business_name', None)
        address = validated_data.pop('address', None)
        governorate = validated_data.pop('governorate', None)
        postal_code = validated_data.pop('postal_code', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create role-specific profile
        if user.role == 'CLIENT':
            Client.objects.create(user=user)
        elif user.role == 'SUPPLIER':
            Supplier.objects.create(
                user=user,
                business_name=business_name,
                address=address,
                governorate=governorate,
                postal_code=postal_code
            )
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        attrs['user'] = user
        return attrs


# Part Serializers

class PartSerializer(serializers.ModelSerializer):
    """
    Serializer for Part model with related data
    """
    supplier = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    model_year = serializers.SerializerMethodField()
    engine = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    vehicle_compatibility = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    model_year_value = serializers.SerializerMethodField()
    engine_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Part
        fields = [
            'id', 'supplier', 'supplier_name', 'name', 'reference', 'description',
            'brand', 'brand_name', 'model', 'model_name', 'model_year', 'model_year_value',
            'engine', 'engine_name', 'category', 'category_name',
            'price', 'quantity', 'available_quantity', 'condition',
            'is_in_stock', 'primary_image', 'images', 'vehicle_compatibility',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_supplier(self, obj):
        return {
            'id': obj.supplier.pk,
            'business_name': obj.supplier.business_name,
            'user': {
                'id': obj.supplier.user.id,
                'username': obj.supplier.user.username
            }
        }
    
    def get_brand(self, obj):
        return {
            'id': obj.brand.id,
            'name': obj.brand.name
        }
    
    def get_model(self, obj):
        return {
            'id': obj.model.id,
            'name': obj.model.name
        }
    
    def get_model_year(self, obj):
        return {
            'id': obj.model_year.id,
            'year': obj.model_year.year
        }
    
    def get_engine(self, obj):
        if obj.engine:
            return {
                'id': obj.engine.id,
                'name': obj.engine.name,
                'type': obj.engine.type,
                'horsepower': obj.engine.horsepower
            }
        return None
    
    def get_category(self, obj):
        return {
            'id': obj.category.id,
            'name': obj.category.name
        }
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock()
    
    def get_vehicle_compatibility(self, obj):
        return obj.get_vehicle_compatibility()

    def get_supplier_name(self, obj):
        return obj.supplier.business_name

    def get_brand_name(self, obj):
        return obj.brand.name

    def get_model_name(self, obj):
        return obj.model.name

    def get_model_year_value(self, obj):
        return obj.model_year.year

    def get_engine_name(self, obj):
        return obj.engine.name if obj.engine else None

    def get_category_name(self, obj):
        return obj.category.name

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        first = obj.images.first()
        if first:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first.image.url)
            return first.image.url
        return None

    def get_available_quantity(self, obj):
        return obj.quantity

    def get_images(self, obj):
        images = obj.images.all()
        request = self.context.get('request')
        result = []
        for img in images:
            image_url = img.image.url
            if request:
                image_url = request.build_absolute_uri(image_url)
            result.append({
                'id': img.id,
                'part': img.part_id,
                'image': img.image.url,
                'image_url': image_url,
                'is_primary': img.is_primary,
                'created_at': img.created_at.isoformat() if hasattr(img, 'created_at') else None
            })
        return result


class PartCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new parts (Supplier only)
    """
    class Meta:
        model = Part
        fields = [
            'name', 'reference', 'description',
            'brand', 'model', 'model_year', 'engine',
            'category', 'price', 'quantity', 'condition'
        ]
    
    def validate_reference(self, value):
        """Ensure reference is unique"""
        if Part.objects.filter(reference=value).exists():
            raise serializers.ValidationError("A part with this reference already exists.")
        return value
    
    def validate_price(self, value):
        """Ensure price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_quantity(self, value):
        """Ensure quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
    
    def create(self, validated_data):
        # Set supplier from request user
        request = self.context.get('request')
        if request and hasattr(request.user, 'supplier_profile'):
            validated_data['supplier'] = request.user.supplier_profile
        return super().create(validated_data)


class PartUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating parts (Supplier only, own parts)
    """
    class Meta:
        model = Part
        fields = [
            'name', 'description', 'price', 'quantity', 'condition'
        ]
    
    def validate_price(self, value):
        """Ensure price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_quantity(self, value):
        """Ensure quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value


# Cart Serializers

class CartItemSerializer(serializers.ModelSerializer):
    """Read serializer for cart items with part details"""
    part_detail = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'part', 'part_detail', 'quantity', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_part_detail(self, obj):
        return {
            'id': obj.part.id,
            'name': obj.part.name,
            'reference': obj.part.reference,
            'price': str(obj.part.price),
            'condition': obj.part.condition,
            'supplier': obj.part.supplier.business_name,
            'in_stock': obj.part.is_in_stock(),
            'available_quantity': obj.part.quantity,
        }
    
    def get_subtotal(self, obj):
        return str(obj.get_subtotal())


class CartSerializer(serializers.ModelSerializer):
    """Read serializer for cart with all items"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        return str(obj.get_total())
    
    def get_item_count(self, obj):
        return obj.get_item_count()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding an item to cart"""
    part_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_part_id(self, value):
        try:
            part = Part.objects.get(id=value)
        except Part.DoesNotExist:
            raise serializers.ValidationError("Part not found.")
        if not part.is_in_stock():
            raise serializers.ValidationError("Part is out of stock.")
        return value
    
    def validate(self, attrs):
        part = Part.objects.get(id=attrs['part_id'])
        if attrs['quantity'] > part.quantity:
            raise serializers.ValidationError({
                "quantity": f"Requested quantity ({attrs['quantity']}) exceeds available stock ({part.quantity})."
            })
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        if hasattr(self, 'instance') and self.instance:
            part = self.instance.part
            if value > part.quantity:
                raise serializers.ValidationError(
                    f"Requested quantity ({value}) exceeds available stock ({part.quantity})."
                )
        return value


# Order Serializers

class OrderItemSerializer(serializers.ModelSerializer):
    """Read serializer for order items"""
    part_detail = serializers.SerializerMethodField()
    supplier_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'part', 'part_detail', 'supplier', 'supplier_detail', 'quantity', 'price', 'total_price']
        read_only_fields = ['id']
    
    def get_part_detail(self, obj):
        return {
            'id': obj.part.id,
            'name': obj.part.name,
            'reference': obj.part.reference,
        }
    
    def get_supplier_detail(self, obj):
        return {
            'id': obj.supplier.user.id,
            'business_name': obj.supplier.business_name,
        }


class OrderSerializer(serializers.ModelSerializer):
    """Read serializer for orders with all items"""
    items = OrderItemSerializer(many=True, read_only=True)
    client_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'client_username', 'total_price', 'status', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'client', 'total_price', 'created_at', 'updated_at']
    
    def get_client_username(self, obj):
        return obj.client.user.username


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order list (no items)"""
    client_username = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'client_username', 'total_price', 'status', 'item_count', 'created_at']
        read_only_fields = ['id', 'total_price', 'created_at']
    
    def get_client_username(self, obj):
        return obj.client.user.username
    
    def get_item_count(self, obj):
        return obj.items.count()


# Vehicle Hierarchy Serializers

class BrandSerializer(serializers.ModelSerializer):
    model_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'model_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_model_count(self, obj):
        return obj.models.count()


class ModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = Model
        fields = ['id', 'name', 'brand', 'brand_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class ModelYearSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    brand_name = serializers.CharField(source='model.brand.name', read_only=True)
    
    class Meta:
        model = ModelYear
        fields = ['id', 'year', 'model', 'model_name', 'brand_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class EngineSerializer(serializers.ModelSerializer):
    model_year_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Engine
        fields = ['id', 'name', 'type', 'horsepower', 'model_year', 'model_year_display', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_model_year_display(self, obj):
        return str(obj.model_year)


# Category Serializers

class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)
    full_path = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'parent_name', 'full_path', 'children', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_full_path(self, obj):
        return obj.get_full_path()
    
    def get_children(self, obj):
        children = obj.children.all()
        if children.exists():
            return [{'id': c.id, 'name': c.name} for c in children]
        return []


# PartImage Serializers

class PartImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PartImage
        fields = ['id', 'part', 'image', 'image_url', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class PartImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartImage
        fields = ['image', 'is_primary']


# UserVehicle (My Garage) Serializers

class UserVehicleSerializer(serializers.ModelSerializer):
    brand_detail = serializers.SerializerMethodField()
    model_detail = serializers.SerializerMethodField()
    model_year_detail = serializers.SerializerMethodField()
    engine_detail = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = UserVehicle
        fields = [
            'id', 'nickname', 'brand', 'model', 'model_year', 'engine',
            'is_default', 'brand_detail', 'model_detail', 'model_year_detail',
            'engine_detail', 'display_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_brand_detail(self, obj):
        return {'id': obj.brand.id, 'name': obj.brand.name}

    def get_model_detail(self, obj):
        return {'id': obj.model.id, 'name': obj.model.name}

    def get_model_year_detail(self, obj):
        return {'id': obj.model_year.id, 'year': obj.model_year.year}

    def get_engine_detail(self, obj):
        if obj.engine:
            return {'id': obj.engine.id, 'name': obj.engine.name, 'type': obj.engine.type, 'horsepower': obj.engine.horsepower}
        return None

    def get_display_name(self, obj):
        if obj.nickname:
            return obj.nickname
        name = f"{obj.brand.name} {obj.model.name} {obj.model_year.year}"
        if obj.engine:
            name += f" - {obj.engine.name}"
        return name
