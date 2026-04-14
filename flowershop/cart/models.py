from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from custom_bouquet.models import Bouquet
from django.core.validators import MinValueValidator


class Cart(models.Model):
    """Shopping cart with support for both guest and registered users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_id = models.CharField(max_length=255, null=True, blank=True)  # For guest users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart'
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
    
    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Guest Cart {self.session_id}"
    
    def get_total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_delivery_fee(self):
        """Get delivery fee from configuration."""
        from configurations.views import get_general_config
        config = get_general_config()
        return float(config.delivery_fee) if config else 100.00
    
    def get_grand_total(self):
        """Get grand total including delivery fee."""
        return float(self.get_total_price()) + self.get_delivery_fee()


class CartItem(models.Model):
    """Items in the shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_item'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
    
    def __str__(self):
        item_name = self.product.name if self.product else self.bouquet.name
        return f"{item_name} x {self.quantity}"
    
    def get_subtotal(self):
        """Calculate subtotal for this item."""
        return float(self.price_at_purchase) * self.quantity
    
    def get_item_name(self):
        """Get the name of the product or bouquet."""
        return self.product.name if self.product else self.bouquet.name
    
    def get_item_image(self):
        """Get the image URL of the product or bouquet."""
        if self.product:
            image = self.product.image
            if image and image.name:
                return image.url
            return None
        if self.bouquet:
            return self.bouquet.get_image_url()
        return None
