from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from custom_bouquet.models import Bouquet
from delivery.models import Delivery
import uuid
from django.utils import timezone


class Order(models.Model):
    """Main order model."""
    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('PREPARING', 'Preparing Bouquet'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Order identification
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders'
    )
    
    # Customer information
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Delivery information
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_postal_code = models.CharField(max_length=20, blank=True)
    delivery_date = models.DateField()
    delivery_time_window = models.ForeignKey(
        'delivery.DeliveryTimeWindow',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Order details
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='PENDING',
        db_index=True
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='PENDING'
    )
    
    # Special requests
    gift_message = models.TextField(blank=True)
    anonymous_sender = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tracking
    delivery = models.OneToOneField(
        Delivery,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['customer_email']),
            models.Index(fields=['status']),
            models.Index(fields=['delivery_date']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            timestamp = timezone.now().strftime('%Y%m%d')
            unique_id = str(uuid.uuid4().hex[:8]).upper()
            self.order_number = f"ORD-{timestamp}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_status_badge_color(self):
        """Get color for status badge in templates."""
        color_map = {
            'PENDING': 'warning',
            'PROCESSING': 'info',
            'PREPARING': 'primary',
            'OUT_FOR_DELIVERY': 'warning',
            'DELIVERED': 'success',
            'CANCELLED': 'danger',
        }
        return color_map.get(self.status, 'secondary')
    
    def mark_as_delivered(self):
        """Mark order as delivered."""
        self.status = 'DELIVERED'
        self.delivery_completed_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    """Items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    bouquet = models.ForeignKey(Bouquet, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_item'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        item_name = self.product.name if self.product else self.bouquet.name
        return f"{item_name} x {self.quantity}"
    
    def get_item_name(self):
        return self.product.name if self.product else self.bouquet.name
    
    def get_item_image(self):
        return self.product.image if self.product else self.bouquet.image


class OrderTracking(models.Model):
    """Detailed tracking information for orders."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    track_by_order_number = models.CharField(max_length=20, unique=True)
    track_by_email = models.EmailField()
    
    class Meta:
        db_table = 'order_tracking'
        verbose_name = 'Order Tracking'
        verbose_name_plural = 'Order Trackings'
    
    def __str__(self):
        return f"Tracking for {self.order.order_number}"
