from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Client, Supplier


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
