from django.contrib import admin
from .models import BouquetSize, WrappingStyle, RibbonColor, Extra, Bouquet, BouquetItem, BouquetExtra


@admin.register(BouquetSize)
class BouquetSizeAdmin(admin.ModelAdmin):
    list_display = ['get_size_display', 'flower_count_min', 'flower_count_max', 'base_price']
    fieldsets = (
        ('Size Information', {
            'fields': ('size', 'description')
        }),
        ('Flower Count Range', {
            'fields': ('flower_count_min', 'flower_count_max')
        }),
        ('Pricing', {
            'fields': ('base_price',)
        }),
    )


@admin.register(WrappingStyle)
class WrappingStyleAdmin(admin.ModelAdmin):
    list_display = ['get_style_display', 'price']
    fieldsets = (
        ('Style Information', {
            'fields': ('style', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
    )


@admin.register(RibbonColor)
class RibbonColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'hex_color_display']
    fieldsets = (
        ('Color Information', {
            'fields': ('name', 'hex_color', 'description')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
    )
    
    def hex_color_display(self, obj):
        return f'<div style="width: 30px; height: 30px; background-color: {obj.hex_color};"></div>'
    hex_color_display.short_description = 'Color'
    hex_color_display.allow_tags = True


@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    list_display = ['get_name_display', 'price', 'stock_quantity']
    list_filter = ['stock_quantity']
    fieldsets = (
        ('Extra Information', {
            'fields': ('name', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Stock', {
            'fields': ('stock_quantity',)
        }),
    )


class BouquetItemInline(admin.TabularInline):
    model = BouquetItem
    extra = 1


class BouquetExtraInline(admin.TabularInline):
    model = BouquetExtra
    extra = 1


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ['name', 'size', 'base_price', 'total_price', 'created_at']
    list_filter = ['size', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'base_price', 'total_price']
    inlines = [BouquetItemInline, BouquetExtraInline]
    fieldsets = (
        ('Bouquet Information', {
            'fields': ('name', 'description', 'image')
        }),
        ('Components', {
            'fields': ('size', 'wrapping', 'ribbon_color')
        }),
        ('Message', {
            'fields': ('personal_message',),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('base_price', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BouquetItem)
class BouquetItemAdmin(admin.ModelAdmin):
    list_display = ['bouquet', 'flower', 'quantity', 'price_per_unit']
    list_filter = ['bouquet', 'flower']
    search_fields = ['bouquet__name', 'flower__name']


@admin.register(BouquetExtra)
class BouquetExtraAdmin(admin.ModelAdmin):
    list_display = ['bouquet', 'extra', 'quantity']
    list_filter = ['bouquet', 'extra']
    search_fields = ['bouquet__name', 'extra__name']
