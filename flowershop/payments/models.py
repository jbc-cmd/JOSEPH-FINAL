from django.db import models
from orders.models import Order


class Payment(models.Model):
    """Payment records for orders."""
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
        ('GCASH', 'GCash'),
        ('PAYMAYA', 'PayMaya'),
        ('COD', 'Cash on Delivery'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    # Payment gateway transaction details
    transaction_id = models.CharField(max_length=255, blank=True, unique=True, null=True)
    payment_gateway = models.CharField(max_length=50, blank=True)  # Stripe, PayPal, etc.
    
    # References
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = Payment.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        super().save(*args, **kwargs)

        order_payment_status_map = {
            'PENDING': 'PENDING',
            'COMPLETED': 'COMPLETED',
            'FAILED': 'FAILED',
            'CANCELLED': 'FAILED',
            'REFUNDED': 'REFUNDED',
        }
        next_payment_status = order_payment_status_map.get(self.status, 'PENDING')

        updates = {}
        if self.order.payment_status != next_payment_status:
            updates['payment_status'] = next_payment_status

        # Once payment is confirmed, move the customer-facing order flow forward.
        if self.status == 'COMPLETED' and self.order.status == 'PENDING':
            updates['status'] = 'PROCESSING'

        if previous_status == self.status and not updates:
            return

        if updates:
            Order.objects.filter(pk=self.order_id).update(**updates)
            for field, value in updates.items():
                setattr(self.order, field, value)

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"


class RefundRequest(models.Model):
    """Handle refund requests from customers."""
    REFUND_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PROCESSED', 'Processed'),
    ]
    
    REFUND_REASON = [
        ('DAMAGED', 'Damaged Product'),
        ('NOT_DELIVERED', 'Not Delivered'),
        ('WRONG_ITEMS', 'Wrong Items Delivered'),
        ('CUSTOMER_CHANGE_MIND', 'Customer Change of Mind'),
        ('OTHER', 'Other Reason'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refund_requests')
    reason = models.CharField(max_length=50, choices=REFUND_REASON)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='PENDING')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Admin response
    admin_notes = models.TextField(blank=True)
    rejected_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'refund_request'
        verbose_name = 'Refund Request'
        verbose_name_plural = 'Refund Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund for {self.payment.order.order_number}"
