from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'bouquet', 'quantity', 'price_at_purchase']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['get_user_info', 'get_total_items', 'get_total_price', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_user_info(self, obj):
        return obj.user.username if obj.user else f"Guest ({obj.session_id[:10]}...)"
    get_user_info.short_description = 'User/Session'
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total_price(self, obj):
        return f"₱{obj.get_total_price():.2f}"
    get_total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['get_item_name', 'quantity', 'price_at_purchase', 'get_subtotal', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['product__name', 'bouquet__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_item_name(self, obj):
        return obj.get_item_name()
    get_item_name.short_description = 'Item'
    
    def get_subtotal(self, obj):
        return f"₱{obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'
