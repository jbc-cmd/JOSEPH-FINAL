from django.db import models
from products.models import Flower
from django.core.validators import MinValueValidator, MaxValueValidator
from django.templatetags.static import static


class BouquetSize(models.Model):
    """Different bouquet sizes with pricing."""
    SIZE_CHOICES = [
        ('SMALL', 'Small'),
        ('MEDIUM', 'Medium'),
        ('LARGE', 'Large'),
        ('PREMIUM', 'Premium'),
    ]
    
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, unique=True)
    flower_count_min = models.PositiveIntegerField(help_text='Minimum flowers for this size')
    flower_count_max = models.PositiveIntegerField(help_text='Maximum flowers for this size')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'bouquet_size'
        verbose_name = 'Bouquet Size'
        verbose_name_plural = 'Bouquet Sizes'
        ordering = ['base_price']
    
    def __str__(self):
        return f"{self.get_size_display()} (₱{self.base_price:.2f})"


class WrappingStyle(models.Model):
    """Wrapping options for bouquets."""
    WRAPPING_CHOICES = [
        ('KRAFT', 'Kraft Paper'),
        ('CELLOPHANE', 'Cellophane'),
        ('FABRIC', 'Fabric Wrap'),
        ('BURLAP', 'Burlap'),
        ('SATIN', 'Satin'),
    ]
    
    style = models.CharField(max_length=50, choices=WRAPPING_CHOICES, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='wrapping_styles/', blank=True, null=True)
    
    class Meta:
        db_table = 'wrapping_style'
        verbose_name = 'Wrapping Style'
        verbose_name_plural = 'Wrapping Styles'
        ordering = ['style']
    
    def __str__(self):
        return f"{self.get_style_display()} (+₱{self.price:.2f})"


class RibbonColor(models.Model):
    """Available ribbon colors."""
    name = models.CharField(max_length=50, unique=True)
    hex_color = models.CharField(max_length=7, default='#000000', help_text='Hex color code')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'ribbon_color'
        verbose_name = 'Ribbon Color'
        verbose_name_plural = 'Ribbon Colors'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (+₱{self.price:.2f})"


class Extra(models.Model):
    """Extra items to add to bouquets."""
    EXTRA_CHOICES = [
        ('CHOCOLATE', 'Chocolate Box'),
        ('TEDDY', 'Teddy Bear'),
        ('BALLOON', 'Balloon'),
        ('CARD', 'Greeting Card'),
        ('CANDLE', 'Scented Candle'),
        ('WINE', 'Wine Bottle'),
    ]
    
    name = models.CharField(max_length=100, choices=EXTRA_CHOICES, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='extras/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'extra'
        verbose_name = 'Extra'
        verbose_name_plural = 'Extras'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_name_display()} (+₱{self.price:.2f})"


class Bouquet(models.Model):
    """Custom-built bouquets."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    size = models.ForeignKey(BouquetSize, on_delete=models.PROTECT)
    is_custom_size = models.BooleanField(default=False)
    custom_flower_count = models.PositiveIntegerField(null=True, blank=True)
    wrapping = models.ForeignKey(WrappingStyle, on_delete=models.PROTECT)
    ribbon_color = models.ForeignKey(RibbonColor, on_delete=models.PROTECT)
    personal_message = models.TextField(blank=True, max_length=500)
    image = models.ImageField(upload_to='custom_bouquets/', blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bouquet'
        verbose_name = 'Custom Bouquet'
        verbose_name_plural = 'Custom Bouquets'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

    def size_label(self):
        """Return the display label for the selected size."""
        if self.is_custom_size and self.custom_flower_count:
            return f"Custom ({self.custom_flower_count} stems)"
        return self.size.get_size_display()

    def get_image_url(self):
        """Return the bouquet image URL or the shared custom bouquet fallback."""
        if self.image and self.image.name:
            return self.image.url
        return static('images/custom-bouquet.png')
    
    def get_flower_count(self):
        """Get total number of flowers in this bouquet."""
        return self.items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    def calculate_total_price(self):
        """Recalculate total price based on all components."""
        flowers_price = sum(item.subtotal() for item in self.items.all())
        wrapping_price = float(self.wrapping.price)
        ribbon_price = float(self.ribbon_color.price)
        extras_price = sum(float(extra.extra.price) * extra.quantity for extra in self.extras.all())
        
        total = flowers_price + wrapping_price + ribbon_price + extras_price
        self.total_price = total
        self.save()
        return total


class BouquetItem(models.Model):
    """Individual flower items in a custom bouquet."""
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE, related_name='items')
    flower = models.ForeignKey(Flower, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'bouquet_item'
        verbose_name = 'Bouquet Item'
        verbose_name_plural = 'Bouquet Items'
    
    def __str__(self):
        return f"{self.quantity}x {self.flower.get_name_display()} - {self.bouquet.name}"
    
    def subtotal(self):
        """Calculate subtotal for this flower type in the bouquet."""
        return float(self.price_per_unit) * self.quantity


class BouquetExtra(models.Model):
    """Extras added to a custom bouquet."""
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE, related_name='extras')
    extra = models.ForeignKey(Extra, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    class Meta:
        db_table = 'bouquet_extra'
        verbose_name = 'Bouquet Extra'
        verbose_name_plural = 'Bouquet Extras'
    
    def __str__(self):
        return f"{self.quantity}x {self.extra.get_name_display()} - {self.bouquet.name}"
