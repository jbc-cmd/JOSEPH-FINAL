from django.contrib import admin
from .models import DeliveryTimeWindow, Delivery, DeliveryStatusHistory


@admin.register(DeliveryTimeWindow)
class DeliveryTimeWindowAdmin(admin.ModelAdmin):
    list_display = ['get_window_display', 'start_time', 'end_time', 'is_available', 'max_orders']
    list_filter = ['is_available']


class DeliveryStatusHistoryInline(admin.TabularInline):
    model = DeliveryStatusHistory
    extra = 0
    fields = ['status', 'notes', 'updated_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['delivery_number', 'recipient_name', 'status', 'delivery_date', 'delivery_time_window', 'updated_at']
    list_filter = ['status', 'delivery_date', 'delivery_time_window']
    search_fields = ['delivery_number', 'recipient_name', 'recipient_phone', 'delivery_address']
    readonly_fields = ['delivery_number', 'created_at', 'updated_at', 'delivered_at']
    inlines = [DeliveryStatusHistoryInline]
    date_hierarchy = 'delivery_date'
    
    fieldsets = (
        ('Delivery Information', {
            'fields': ('delivery_number', 'status', 'delivery_date', 'delivery_time_window')
        }),
        ('Recipient Details', {
            'fields': ('recipient_name', 'recipient_phone', 'delivery_address')
        }),
        ('Assignment & Tracking', {
            'fields': ('assigned_to', 'current_location', 'delivery_notes')
        }),
        ('Proof of Delivery', {
            'fields': ('proof_of_delivery',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'status', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['delivery__delivery_number', 'updated_by']
    readonly_fields = ['created_at']
