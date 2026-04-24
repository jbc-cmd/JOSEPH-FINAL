from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: 09124169887. Up to 15 digits allowed.'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.TextField(blank=True)
    default_delivery_address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_subscribed_to_newsletter = models.BooleanField(default=True)
    last_active_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"

    def sync_default_delivery_address(self):
        """Mirror the user's default saved delivery address into the profile."""
        primary_address = self.user.delivery_addresses.filter(is_default=True).first() or self.user.delivery_addresses.first()

        if not primary_address:
            self.default_delivery_address = ''
            self.address = ''
        else:
            address_parts = [primary_address.address.strip(), primary_address.city.strip()]
            if primary_address.postal_code:
                address_parts.append(primary_address.postal_code.strip())

            formatted_address = ', '.join(part for part in address_parts if part)
            self.default_delivery_address = formatted_address
            self.address = formatted_address

        self.save(update_fields=['address', 'default_delivery_address', 'updated_at'])


class DeliveryAddress(models.Model):
    """Saved delivery addresses for quick checkout."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    label = models.CharField(max_length=100, help_text='e.g., Home, Office, Mom\'s place')
    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True, help_text='Special instructions for delivery')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'delivery_address'
        verbose_name = 'Delivery Address'
        verbose_name_plural = 'Delivery Addresses'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.label} - {self.recipient_name}"


@receiver(post_save, sender=DeliveryAddress)
def sync_profile_delivery_address_on_save(sender, instance, **kwargs):
    profile, _ = UserProfile.objects.get_or_create(user=instance.user)
    profile.sync_default_delivery_address()


@receiver(post_delete, sender=DeliveryAddress)
def sync_profile_delivery_address_on_delete(sender, instance, **kwargs):
    profile, _ = UserProfile.objects.get_or_create(user=instance.user)
    profile.sync_default_delivery_address()
