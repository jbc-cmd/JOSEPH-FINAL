from django.contrib import admin
from .models import Order, OrderItem, OrderTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'bouquet', 'quantity', 'price', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'status', 'payment_status', 'total_amount', 'delivery_date', 'created_at']
    list_filter = ['status', 'payment_status', 'delivery_date', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'delivery_completed_at', 'cancelled_at', 'cancellation_requested_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'delivery_date'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_postal_code', 'delivery_date', 'delivery_time_window')
        }),
        ('Special Requests', {
            'fields': ('gift_message', 'anonymous_sender', 'special_instructions'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancellation_requested_at', 'cancellation_request_reason'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'total_amount')
        }),
        ('Delivery Tracking', {
            'fields': ('delivery',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivery_completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_preparing', 'mark_as_out_for_delivery', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='PROCESSING')
    mark_as_processing.short_description = "Mark selected orders as Processing"
    
    def mark_as_preparing(self, request, queryset):
        queryset.update(status='PREPARING')
    mark_as_preparing.short_description = "Mark selected orders as Preparing Bouquet"
    
    def mark_as_out_for_delivery(self, request, queryset):
        queryset.update(status='OUT_FOR_DELIVERY')
    mark_as_out_for_delivery.short_description = "Mark selected orders as Out for Delivery"
    
    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.mark_as_delivered()
    mark_as_delivered.short_description = "Mark selected orders as Delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'get_item_name', 'quantity', 'price', 'subtotal']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'product__name', 'bouquet__name']
    readonly_fields = ['subtotal']
    
    def get_item_name(self, obj):
        return obj.get_item_name()
    get_item_name.short_description = 'Item'


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'track_by_order_number', 'track_by_email']
    search_fields = ['track_by_order_number', 'track_by_email', 'order__order_number']
    readonly_fields = ['order', 'track_by_order_number', 'track_by_email']
