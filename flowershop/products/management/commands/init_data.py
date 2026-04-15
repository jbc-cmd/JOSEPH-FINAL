from django.core.management.base import BaseCommand
from products.models import Category, Flower, Product
from custom_bouquet.models import BouquetSize, WrappingStyle, RibbonColor, Extra
from delivery.models import DeliveryTimeWindow


class Command(BaseCommand):
    help = 'Initialize database with flower types and configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing database...'))
        
        # Create categories
        categories_data = [
            {'name': 'Roses', 'slug': 'roses'},
            {'name': 'Sunflower Bouquet', 'slug': 'sunflower-bouquet'},
            {'name': 'Mixed Bouquet', 'slug': 'mixed-bouquet'},
            {'name': 'Anniversary Flowers', 'slug': 'anniversary'},
            {'name': 'Birthday Flowers', 'slug': 'birthday'},
            {'name': 'Graduation Flowers', 'slug': 'graduation'},
            {'name': 'Funeral Flowers', 'slug': 'funeral'},
            {'name': 'Romantic Flowers', 'slug': 'romantic'},
            {'name': 'Custom Bouquet', 'slug': 'custom'},
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'slug': cat_data['slug'], 'is_active': True}
            )
        self.stdout.write(self.style.SUCCESS('✓ Categories created'))
        
        # Create flowers
        flowers_data = [
            {'name': 'ROSE', 'display': 'Rose', 'price': 150.00, 'color': 'Red'},
            {'name': 'GERBERA', 'display': 'Gerbera', 'price': 120.00, 'color': 'Pink'},
            {'name': 'MUM', 'display': 'Malaysian Mum', 'price': 100.00, 'color': 'White'},
            {'name': 'JIMBA', 'display': 'Jimba', 'price': 180.00, 'color': 'Purple'},
            {'name': 'STARGAZER', 'display': 'Stargazer', 'price': 200.00, 'color': 'Pink'},
            {'name': 'ASTROMERIA', 'display': 'Astromeria', 'price': 90.00, 'color': 'Mixed'},
            {'name': 'BANGKOK', 'display': 'Bangkok Yellow', 'price': 110.00, 'color': 'Yellow'},
            {'name': 'JAGUAR', 'display': 'Jaguar Purple', 'price': 130.00, 'color': 'Purple'},
            {'name': 'GLADIOLA', 'display': 'Gladiola', 'price': 140.00, 'color': 'Red'},
            {'name': 'SUNFLOWER', 'display': 'Sunflower', 'price': 160.00, 'color': 'Yellow'},
            {'name': 'CARNATION', 'display': 'Carnation', 'price': 80.00, 'color': 'Red'},
            {'name': 'GYPSOPHYLLA', 'display': 'Gypsophylla', 'price': 50.00, 'color': 'White'},
            {'name': 'STATICE', 'display': 'Statice', 'price': 70.00, 'color': 'Purple'},
            {'name': 'MISTY', 'display': 'Misty Blue', 'price': 120.00, 'color': 'Blue'},
        ]
        
        mixed_bouquet_category = Category.objects.get(slug='mixed-bouquet')
        
        for flower_data in flowers_data:
            Flower.objects.get_or_create(
                name=flower_data['name'],
                defaults={
                    'description': f"Beautiful {flower_data['display'].lower()} flowers",
                    'price': flower_data['price'],
                    'stock_quantity': 100,
                    'category': mixed_bouquet_category,
                    'color': flower_data['color'],
                    'availability_status': 'IN_STOCK'
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Flowers created'))
        
        # Create products (featured bouquets)
        products_data = [
            {
                'name': 'Crimson Romance',
                'description': 'A stunning bouquet of red roses expressing love and passion. Perfect for anniversaries and special moments.',
                'price': 1200.00,
                'category': 'roses',
                'is_featured': True,
                'size': 'MEDIUM'
            },
            {
                'name': 'Birthday Blast',
                'description': 'Vibrant mix of colorful gerberas and sunflowers to brighten any birthday celebration.',
                'price': 980.00,
                'category': 'birthday',
                'is_featured': True,
                'size': 'MEDIUM'
            },
            {
                'name': 'Royal Elegance',
                'description': 'Mixed bouquet with pink roses, carnations, and greenery for an elegant touch.',
                'price': 2500.00,
                'category': 'mixed-bouquet',
                'is_featured': True,
                'size': 'LARGE'
            },
            {
                'name': 'Sunshine Delight',
                'description': 'Cheerful arrangement of bright sunflowers that brings joy and warmth.',
                'price': 750.00,
                'category': 'sunflower-bouquet',
                'is_featured': True,
                'size': 'MEDIUM'
            },
            {
                'name': 'Blushing Petals',
                'description': 'Romantic arrangement of soft pink and blush-toned flowers with premium wrapping.',
                'price': 1500.00,
                'category': 'romantic',
                'is_featured': True,
                'size': 'LARGE'
            },
            {
                'name': 'Grad Star',
                'description': 'Bold arrangement of red and yellow flowers celebrating graduation achievements.',
                'price': 1350.00,
                'category': 'graduation',
                'is_featured': True,
                'size': 'MEDIUM'
            },
            {
                'name': 'Wildflower Dream',
                'description': 'Colorful mixed bouquet featuring wildflowers and lush greenery.',
                'price': 980.00,
                'category': 'mixed-bouquet',
                'is_featured': True,
                'size': 'MEDIUM'
            },
            {
                'name': 'Anniversary Glory',
                'description': 'Premium arrangement celebrating love and commitment with elegant roses.',
                'price': 2000.00,
                'category': 'anniversary',
                'is_featured': False,
                'size': 'LARGE'
            },
        ]
        
        for product_data in products_data:
            category = Category.objects.get(slug=product_data['category'])
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'slug': product_data['name'].lower().replace(' ', '-'),
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': category,
                    'is_featured': product_data['is_featured'],
                    'is_available': True,
                    'stock_quantity': 50,
                    'size': product_data['size'],
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Products created'))
        
        for product in Product.objects.all():
            product.update_review_stats()

        sizes_data = [
            {'size': 'SMALL', 'min': 5, 'max': 10, 'price': 500.00},
            {'size': 'MEDIUM', 'min': 11, 'max': 20, 'price': 1000.00},
            {'size': 'LARGE', 'min': 21, 'max': 30, 'price': 1500.00},
            {'size': 'PREMIUM', 'min': 31, 'max': 50, 'price': 2500.00},
        ]
        
        for size_data in sizes_data:
            BouquetSize.objects.get_or_create(
                size=size_data['size'],
                defaults={
                    'flower_count_min': size_data['min'],
                    'flower_count_max': size_data['max'],
                    'base_price': size_data['price']
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Bouquet sizes created'))
        
        # Create wrapping styles
        wrapping_data = [
            {'style': 'KRAFT', 'display': 'Kraft Paper', 'price': 50.00},
            {'style': 'CELLOPHANE', 'display': 'Cellophane', 'price': 60.00},
            {'style': 'FABRIC', 'display': 'Fabric Wrap', 'price': 75.00},
            {'style': 'BURLAP', 'display': 'Burlap', 'price': 65.00},
            {'style': 'SATIN', 'display': 'Satin', 'price': 80.00},
        ]
        
        for wrap_data in wrapping_data:
            WrappingStyle.objects.get_or_create(
                style=wrap_data['style'],
                defaults={
                    'description': f"{wrap_data['display']} wrapping",
                    'price': wrap_data['price']
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Wrapping styles created'))
        
        # Create ribbon colors
        ribbon_data = [
            {'name': 'Red', 'hex': '#FF0000', 'price': 30.00},
            {'name': 'Pink', 'hex': '#FF69B4', 'price': 30.00},
            {'name': 'White', 'hex': '#FFFFFF', 'price': 25.00},
            {'name': 'Gold', 'hex': '#FFD700', 'price': 40.00},
            {'name': 'Silver', 'hex': '#C0C0C0', 'price': 40.00},
            {'name': 'Purple', 'hex': '#800080', 'price': 35.00},
            {'name': 'Blue', 'hex': '#0000FF', 'price': 35.00},
        ]
        
        for ribbon_data_item in ribbon_data:
            RibbonColor.objects.get_or_create(
                name=ribbon_data_item['name'],
                defaults={
                    'hex_color': ribbon_data_item['hex'],
                    'price': ribbon_data_item['price']
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Ribbon colors created'))
        
        # Create extras
        extras_data = [
            {'name': 'CHOCOLATE', 'display': 'Chocolate Box', 'price': 200.00},
            {'name': 'TEDDY', 'display': 'Teddy Bear', 'price': 300.00},
            {'name': 'BALLOON', 'display': 'Balloon', 'price': 100.00},
            {'name': 'CARD', 'display': 'Greeting Card', 'price': 50.00},
            {'name': 'CANDLE', 'display': 'Scented Candle', 'price': 150.00},
            {'name': 'WINE', 'display': 'Wine Bottle', 'price': 400.00},
        ]
        
        for extra_data in extras_data:
            Extra.objects.get_or_create(
                name=extra_data['name'],
                defaults={
                    'description': f"{extra_data['display'].lower()} add-on",
                    'price': extra_data['price'],
                    'stock_quantity': 100
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Extras created'))
        
        # Create delivery time windows
        DeliveryTimeWindow.objects.get_or_create(
            window='MORNING',
            defaults={
                'start_time': '08:00',
                'end_time': '13:00',
                'is_available': True,
                'max_orders': 20
            }
        )
        
        DeliveryTimeWindow.objects.get_or_create(
            window='AFTERNOON',
            defaults={
                'start_time': '13:00',
                'end_time': '20:00',
                'is_available': True,
                'max_orders': 20
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Delivery time windows created'))
        
        self.stdout.write(self.style.SUCCESS('✓ Database initialization complete!'))
