from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
        ('SUPPLIER', 'Supplier'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def is_client(self):
        return self.role == 'CLIENT'
    
    def is_supplier(self):
        return self.role == 'SUPPLIER'


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='client_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return f"Client: {self.user.username}"


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='supplier_profile')
    business_name = models.CharField(max_length=255)
    address = models.TextField()
    governorate = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
    
    def __str__(self):
        return f"Supplier: {self.business_name}"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'models'
        verbose_name = 'Model'
        verbose_name_plural = 'Models'
        ordering = ['name']
        unique_together = [['name', 'brand']]
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"


class ModelYear(models.Model):
    year = models.IntegerField()
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='model_years')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'model_years'
        verbose_name = 'Model Year'
        verbose_name_plural = 'Model Years'
        ordering = ['-year']
        unique_together = [['year', 'model']]
    
    def __str__(self):
        return f"{self.model.brand.name} {self.model.name} ({self.year})"


class Engine(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    horsepower = models.IntegerField()
    model_year = models.ForeignKey(ModelYear, on_delete=models.CASCADE, related_name='engines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'engines'
        verbose_name = 'Engine'
        verbose_name_plural = 'Engines'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.type} ({self.horsepower}hp)"


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Get the full hierarchical path of the category"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)


class Part(models.Model):
    CONDITION_CHOICES = (
        ('NEW', 'New'),
        ('USED', 'Used'),
    )
    
    # Basic Information
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Vehicle Targeting
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='parts')
    model = models.ForeignKey(Model, on_delete=models.PROTECT, related_name='parts')
    model_year = models.ForeignKey(ModelYear, on_delete=models.PROTECT, related_name='parts')
    engine = models.ForeignKey(Engine, on_delete=models.SET_NULL, null=True, blank=True, related_name='parts')
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='parts')
    
    # Commercial Details
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='NEW')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'parts'
        verbose_name = 'Part'
        verbose_name_plural = 'Parts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['supplier', 'created_at']),
            models.Index(fields=['brand', 'model', 'model_year']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.reference}) - {self.supplier.business_name}"
    
    def is_in_stock(self):
        """Check if part is in stock"""
        return self.quantity > 0
    
    def get_vehicle_compatibility(self):
        """Get vehicle compatibility details"""
        return f"{self.brand.name} {self.model.name} ({self.model_year.year})"


class PartImage(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='parts/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'part_images'
        verbose_name = 'Part Image'
        verbose_name_plural = 'Part Images'
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"Image for {self.part.name} - {'Primary' if self.is_primary else 'Additional'}"
    
    def save(self, *args, **kwargs):
        # If this image is set as primary, unset other primary images for this part
        if self.is_primary:
            PartImage.objects.filter(part=self.part, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the image file from storage
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
