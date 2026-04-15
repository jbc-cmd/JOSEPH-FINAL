from django.contrib import admin
from .models import Category, Flower, Product, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ['get_name_display', 'price', 'stock_quantity', 'availability_status', 'is_featured']
    list_filter = ['availability_status', 'is_featured', 'category']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Flower Information', {
            'fields': ('name', 'description', 'color', 'category')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'availability_status')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_featured',)
        }),
    )
    readonly_fields = ['availability_status']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'size', 'price', 'stock_quantity', 'rating', 'is_featured']
    list_filter = ['category', 'product_type', 'size', 'is_featured', 'is_available']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'description', 'category', 'product_type', 'size')
        }),
        ('Composition', {
            'fields': ('composition',),
            'description': 'Add bouquet composition details in JSON format'
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Media', {
            'fields': ('image', 'gallery_images')
        }),
        ('Ratings', {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_featured',)
        }),
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'product']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer_name', 'rating', 'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'product__name']
    actions = ['approve_reviews', 'unapprove_reviews']
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'customer_name', 'customer_email', 'rating', 'comment', 'photo')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
    )
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.product.update_review_stats()

    def delete_model(self, request, obj):
        product = obj.product
        super().delete_model(request, obj)
        product.update_review_stats()

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        affected_products = set(queryset.values_list('product_id', flat=True))
        queryset.update(is_approved=True)
        for product_id in affected_products:
            Product.objects.get(pk=product_id).update_review_stats()

    @admin.action(description='Mark selected reviews as unapproved')
    def unapprove_reviews(self, request, queryset):
        affected_products = set(queryset.values_list('product_id', flat=True))
        queryset.update(is_approved=False)
        for product_id in affected_products:
            Product.objects.get(pk=product_id).update_review_stats()
