from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count


class Category(models.Model):
    """Product categories for organized browsing."""
    CATEGORY_CHOICES = [
        ('ROSES', 'Roses'),
        ('SUNFLOWER', 'Sunflower Bouquet'),
        ('MIXED', 'Mixed Bouquet'),
        ('ANNIVERSARY', 'Anniversary Flowers'),
        ('BIRTHDAY', 'Birthday Flowers'),
        ('GRADUATION', 'Graduation Flowers'),
        ('FUNERAL', 'Funeral Flowers'),
        ('ROMANTIC', 'Romantic Flowers'),
        ('CUSTOM', 'Custom Bouquet'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Flower(models.Model):
    """Individual flower types with stock management."""
    FLOWER_TYPES = [
        ('ROSE', 'Rose'),
        ('GERBERA', 'Gerbera'),
        ('MUM', 'Malaysian Mum'),
        ('JIMBA', 'Jimba'),
        ('STARGAZER', 'Stargazer'),
        ('ASTROMERIA', 'Astromeria'),
        ('BANGKOK', 'Bangkok Yellow'),
        ('JAGUAR', 'Jaguar Purple'),
        ('GLADIOLA', 'Gladiola'),
        ('SUNFLOWER', 'Sunflower'),
        ('CARNATION', 'Carnation'),
        ('GYPSOPHYLLA', 'Gypsophylla'),
        ('STATICE', 'Statice'),
        ('MISTY', 'Misty Blue'),
    ]
    
    AVAILABILITY_STATUS = [
        ('IN_STOCK', 'In Stock'),
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]
    
    name = models.CharField(max_length=100, choices=FLOWER_TYPES, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='flowers/')
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='IN_STOCK')
    is_featured = models.BooleanField(default=False)
    color = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flower'
        verbose_name = 'Flower'
        verbose_name_plural = 'Flowers'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()
    
    def update_availability(self):
        """Update availability status based on stock quantity."""
        if self.stock_quantity == 0:
            self.availability_status = 'OUT_OF_STOCK'
        elif self.stock_quantity < 5:
            self.availability_status = 'LOW_STOCK'
        else:
            self.availability_status = 'IN_STOCK'
        self.save()
    
    def is_available(self):
        return self.availability_status != 'OUT_OF_STOCK'


class Product(models.Model):
    """Pre-designed flower arrangements and bouquets."""
    PRODUCT_TYPE = [
        ('BOUQUET', 'Pre-designed Bouquet'),
        ('ARRANGEMENT', 'Flower Arrangement'),
        ('SPECIAL', 'Special Occasion'),
    ]
    
    SIZE_CHOICES = [
        ('SMALL', 'Small'),
        ('MEDIUM', 'Medium'),
        ('LARGE', 'Large'),
        ('PREMIUM', 'Premium'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    composition = models.JSONField(default=dict, blank=True, null=True)  # Stores bouquet composition details
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE, default='BOUQUET')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/')
    gallery_images = models.JSONField(default=list, blank=True)  # List of image paths
    stock_quantity = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='MEDIUM')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_review_stats(self):
        """Refresh cached rating data from approved reviews."""
        stats = self.reviews.filter(is_approved=True).aggregate(
            average=Avg('rating'),
            total=Count('id'),
        )
        self.rating = round(float(stats['average'] or 0), 1)
        self.review_count = stats['total'] or 0
        self.save(update_fields=['rating', 'review_count', 'updated_at'])

    @property
    def rating_percentage(self):
        return max(0, min(100, (float(self.rating or 0) / 5) * 100))


class ProductImage(models.Model):
    """Additional images for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_image'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image"


class ProductReview(models.Model):
    """Customer reviews for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews', null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    photo = models.ImageField(upload_to='review_photos/', blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_review'
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.customer_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_review_stats()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        product.update_review_stats()
