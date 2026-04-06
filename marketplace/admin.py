from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, Supplier, Brand, Model, ModelYear, Engine, Category, Part


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role')}),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'governorate', 'rating', 'created_at']
    list_filter = ['governorate']
    search_fields = ['business_name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'created_at']
    list_filter = ['brand']
    search_fields = ['name', 'brand__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ModelYear)
class ModelYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'model', 'created_at']
    list_filter = ['year', 'model__brand']
    search_fields = ['model__name', 'model__brand__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Engine)
class EngineAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'horsepower', 'model_year', 'created_at']
    list_filter = ['type', 'model_year__model__brand']
    search_fields = ['name', 'type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'reference', 'supplier', 'price', 'quantity', 'condition', 'created_at']
    list_filter = ['condition', 'supplier', 'category', 'brand', 'created_at']
    search_fields = ['name', 'reference', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_vehicle_compatibility']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'reference', 'description', 'supplier', 'category')
        }),
        ('Vehicle Compatibility', {
            'fields': ('brand', 'model', 'model_year', 'engine', 'get_vehicle_compatibility')
        }),
        ('Commercial Details', {
            'fields': ('price', 'quantity', 'condition')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_vehicle_compatibility(self, obj):
        """Display vehicle compatibility"""
        if obj.id:
            return obj.get_vehicle_compatibility()
        return "N/A"
    get_vehicle_compatibility.short_description = "Vehicle Compatibility"
