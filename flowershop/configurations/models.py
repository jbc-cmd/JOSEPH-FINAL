from django.db import models
from django.utils import timezone


class ServiceConfig(models.Model):
    """
    Store API credentials and configuration for external services.
    This keeps sensitive data out of the source code.
    """
    SERVICE_CHOICES = [
        ('STRIPE', 'Stripe Payment'),
        ('PAYPAL', 'PayPal'),
        ('SMS_GATEWAY', 'SMS Gateway'),
        ('EMAIL', 'Email Service'),
        ('SHIPPING', 'Shipping Service'),
    ]
    
    ENVIRONMENT_CHOICES = [
        ('DEVELOPMENT', 'Development'),
        ('STAGING', 'Staging'),
        ('PRODUCTION', 'Production'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    service_name = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        unique=True
    )
    api_key = models.CharField(max_length=500)
    api_secret = models.CharField(max_length=500, blank=True)
    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default='DEVELOPMENT'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_config'
        verbose_name = 'Service Configuration'
        verbose_name_plural = 'Service Configurations'
    
    def __str__(self):
        return f"{self.get_service_name_display()} - {self.environment}"


class GeneralConfig(models.Model):
    """
    Store general configuration settings for the shop.
    """
    shop_name = models.CharField(max_length=255, default='Joseph Flowershop')
    shop_phone = models.CharField(max_length=20, blank=True)
    shop_email = models.EmailField(blank=True)
    shop_address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'general_config'
        verbose_name = 'General Configuration'
        verbose_name_plural = 'General Configuration'
    
    def __str__(self):
        return 'Shop Configuration'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance
        if not self.pk and GeneralConfig.objects.exists():
            self.pk = GeneralConfig.objects.first().pk
        super().save(*args, **kwargs)
