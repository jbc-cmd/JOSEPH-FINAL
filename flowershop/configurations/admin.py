from django.contrib import admin
from .models import ServiceConfig, GeneralConfig


@admin.register(ServiceConfig)
class ServiceConfigAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'environment', 'is_active', 'updated_at']
    list_filter = ['service_name', 'environment', 'is_active']
    search_fields = ['service_name']
    fieldsets = (
        ('Service Information', {
            'fields': ('service_name', 'environment', 'is_active')
        }),
        ('Credentials', {
            'fields': ('api_key', 'api_secret'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GeneralConfig)
class GeneralConfigAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'shop_phone', 'delivery_fee', 'updated_at']
    fieldsets = (
        ('Shop Information', {
            'fields': ('shop_name', 'shop_phone', 'shop_email', 'shop_address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Delivery Settings', {
            'fields': ('delivery_fee', 'min_order_amount')
        }),
    )
    readonly_fields = ['updated_at']
