from django.db import models


class DeliveryTimeWindow(models.Model):
    """Available delivery time windows."""
    WINDOW_CHOICES = [
        ('MORNING', 'Morning (8am - 1pm)'),
        ('AFTERNOON', 'Afternoon (1pm - 8pm)'),
    ]
    
    window = models.CharField(max_length=20, choices=WINDOW_CHOICES, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_orders = models.PositiveIntegerField(default=20, help_text='Maximum orders for this time window per day')
    
    class Meta:
        db_table = 'delivery_time_window'
        verbose_name = 'Delivery Time Window'
        verbose_name_plural = 'Delivery Time Windows'
        ordering = ['start_time']
    
    def __str__(self):
        return self.get_window_display()


class Delivery(models.Model):
    """Delivery tracking and management."""
    DELIVERY_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Delivery Failed'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    
    delivery_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='PENDING')
    
    # Delivery details
    delivery_address = models.TextField()
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=20)
    delivery_date = models.DateField()
    delivery_time_window = models.ForeignKey(DeliveryTimeWindow, on_delete=models.SET_NULL, null=True)
    
    # Tracking
    assigned_to = models.CharField(max_length=255, blank=True, help_text='Assigned delivery personnel')
    current_location = models.CharField(max_length=255, blank=True)
    delivery_notes = models.TextField(blank=True)
    proof_of_delivery = models.ImageField(upload_to='delivery_proofs/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'delivery'
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-delivery_date']
    
    def __str__(self):
        return f"Delivery {self.delivery_number}"


class DeliveryStatusHistory(models.Model):
    """Track all status changes for a delivery."""
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    updated_by = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'delivery_status_history'
        verbose_name = 'Delivery Status History'
        verbose_name_plural = 'Delivery Status Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.delivery.delivery_number} - {self.status}"
