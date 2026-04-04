from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, DeliveryAddress


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'is_subscribed_to_newsletter', 'created_at']
    list_filter = ['is_subscribed_to_newsletter', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Addresses', {
            'fields': ('address', 'default_delivery_address')
        }),
        ('Personal Information', {
            'fields': ('profile_picture', 'date_of_birth')
        }),
        ('Subscription', {
            'fields': ('is_subscribed_to_newsletter',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'recipient_name', 'is_default', 'created_at']
    list_filter = ['is_default', 'city', 'created_at']
    search_fields = ['user__username', 'recipient_name', 'address']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Address Information', {
            'fields': ('label', 'recipient_name', 'phone_number', 'address', 'city', 'postal_code')
        }),
        ('Delivery Notes', {
            'fields': ('notes',)
        }),
        ('Default Address', {
            'fields': ('is_default',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


# Create UserProfile automatically when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
