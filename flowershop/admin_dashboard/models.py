from django.conf import settings
from django.db import models


class LoginAttempt(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
    )
    username = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'

    def __str__(self):
        return f'{self.username or "unknown"} - {self.status}'

    @property
    def is_suspicious(self):
        return self.status == 'FAILED'


class AdminActivityLog(models.Model):
    CATEGORY_CHOICES = [
        ('AUTH', 'Authentication'),
        ('USER', 'User Management'),
        ('PRODUCT', 'Product Management'),
        ('ORDER', 'Order Management'),
        ('REPORT', 'Reports'),
        ('SETTINGS', 'Settings'),
        ('SECURITY', 'Security'),
    ]

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_activity_logs',
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    action = models.CharField(max_length=120)
    target_type = models.CharField(max_length=120, blank=True)
    target_id = models.CharField(max_length=120, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Activity Log'
        verbose_name_plural = 'Admin Activity Logs'

    def __str__(self):
        return f'{self.admin_user} - {self.action}'


class AdminSetting(models.Model):
    site_title = models.CharField(max_length=120, default='Joseph Flowershop Admin')
    support_email = models.EmailField(blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    currency_symbol = models.CharField(max_length=8, default='PHP ')
    low_stock_threshold = models.PositiveIntegerField(default=5)
    session_timeout_minutes = models.PositiveIntegerField(default=60)
    notify_new_orders = models.BooleanField(default=True)
    notify_new_signups = models.BooleanField(default=True)
    notify_low_stock = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Admin Setting'
        verbose_name_plural = 'Admin Settings'

    def __str__(self):
        return 'Admin Settings'

    def save(self, *args, **kwargs):
        if not self.pk and AdminSetting.objects.exists():
            self.pk = AdminSetting.objects.first().pk
        super().save(*args, **kwargs)
