# Joseph Flowershop - Django Web Application

A complete, fully functional flower shop web application built with Django, featuring an online ordering system, custom bouquet builder, and order tracking.

## Features

### Customer Features
- 🌸 **Product Catalog**: Browse a wide variety of flowers and pre-designed bouquets
- 🎨 **Custom Bouquet Builder**: Create personalized bouquets with interactive selection
- 🛒 **Shopping Cart**: Add items, manage quantities, guest or registered user carts
- 💳 **Checkout**: Secure checkout with delivery scheduling and payment options
- 👤 **User Accounts**: Registration, profile management, order history
- 📍 **Delivery Addresses**: Save multiple delivery addresses for convenience
- 📦 **Order Tracking**: Real-time order status tracking
- ⭐ **Reviews**: Leave and read product reviews

### Admin Features
- 📊 **Product Management**: Manage flowers, categories, and products
- 📋 **Order Management**: View, process, and track orders
- 💰 **Payment Management**: Handle payments and refunds
- 🚚 **Delivery Management**: Manage delivery schedules and status
- ⚙️ **Configuration**: Manage API credentials and shop settings
- 📈 **Analytics**: View sales data and order statistics

## Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Payment**: Integrated payment gateway support (Stripe, PayPal)
- **Email**: Email notifications support

## Project Structure

```
flowershop/
├── flowershop_project/      # Main Django project settings
├── accounts/                # User authentication and profiles
├── products/                # Flower and product catalog
├── cart/                    # Shopping cart management
├── orders/                  # Order management
├── custom_bouquet/          # Bouquet builder functionality
├── payments/                # Payment processing
├── delivery/                # Delivery management
├── configurations/          # API credentials and settings
├── templates/               # HTML templates
├── static/                  # CSS, JavaScript, Images
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Steps

1. **Create and activate virtual environment**:
```bash
cd flowershop
python -m venv venv
source venv/Scripts/activate  # On Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run migrations**:
```bash
python manage.py migrate
```

5. **Create superuser (admin account)**:
```bash
python manage.py createsuperuser
```

6. **Load initial data** (optional):
```bash
python manage.py loaddata initial_data.json
```

7. **Collect static files**:
```bash
python manage.py collectstatic --noinput
```

8. **Run development server**:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## Default Flowers

The system includes these flower types:
- Malaysian Mums
- Gerbera
- Roses
- Jimba
- Stargazer
- Astromeria
- Bangkok Yellow
- Jaguar Purple
- Gladiola
- Sunflower
- Carnation
- Gypsophylla
- Statice
- Misty Blue

## Database Models

### Products
- **Flower**: Individual flower types with pricing and stock
- **Category**: Flower categories for organization
- **Product**: Pre-designed bouquets and arrangements
- **ProductReview**: Customer reviews

### Users & Accounts
- **UserProfile**: Extended user profile information
- **DeliveryAddress**: Saved delivery addresses

### Shopping
- **Cart**: Shopping cart for users/guests
- **CartItem**: Items in the shopping cart

### Custom Bouquet
- **Bouquet**: Custom-built bouquets
- **BouquetItem**: Flowers in a bouquet
- **BouquetSize**: Bouquet size options
- **WrappingStyle**: Wrapping options
- **RibbonColor**: Ribbon color selections
- **Extra**: Add-on items (chocolate, balloons, etc.)

### Orders
- **Order**: Main order information
- **OrderItem**: Items in an order
- **OrderTracking**: Order tracking information

### Delivery
- **Delivery**: Delivery information
- **DeliveryTimeWindow**: Available delivery time slots
- **DeliveryStatusHistory**: Delivery status history

### Payments
- **Payment**: Payment records
- **RefundRequest**: Refund requests from customers

### Configuration
- **ServiceConfig**: API credentials and external service configurations
- **GeneralConfig**: General shop settings

## API Credentials Security

API credentials are stored in the database `ServiceConfig` table, not in code:

```python
from configurations.views import get_service_config

stripe_config = get_service_config('STRIPE')
api_key = stripe_config['api_key'] if stripe_config else None
```

## Admin Interface

Access the admin dashboard at `/admin/`:
- Default URL: `http://127.0.0.1:8000/admin/`
- Login with your superuser credentials

## URLs

| Page | URL |
|------|-----|
| Home | / |
| Shop | /products/shop/ |
| Product Detail | /products/product/<slug>/ |
| Custom Bouquet | /bouquet/builder/ |
| Cart | /cart/ |
| Checkout | /orders/checkout/ |
| Track Order | /orders/track/ |
| Login | /accounts/login/ |
| Register | /accounts/register/ |
| Profile | /accounts/profile/ |
| Admin | /admin/ |

## Configuration

Edit `.env` file to configure:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateway
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## Payment Methods Supported

- Cash on Delivery (COD)
- Credit Card (Stripe)
- Debit Card (Stripe)
- GCash
- PayMaya
- PayPal

## Deployment

For production:

1. Update `ALLOWED_HOSTS` in settings.py
2. Set `DEBUG=False` in .env
3. Set `SECURE_SSL_REDIRECT=True`
4. Use PostgreSQL database
5. Configure email service
6. Set secure cookie settings
7. Use a production WSGI server (Gunicorn)

```bash
gunicorn flowershop_project.wsgi:application --bind 0.0.0.0:8000
```

## Creating Initial Data

### Add Flowers

```python
from products.models import Flower, Category

category = Category.objects.create(name="Roses", slug="roses")

Flower.objects.create(
    name='ROSE',
    description='Beautiful red roses',
    price=150.00,
    stock_quantity=50,
    category=category,
    color='Red'
)
```

### Add Bouquet Sizes

```python
from custom_bouquet.models import BouquetSize

BouquetSize.objects.create(
    size='SMALL',
    flower_count_min=5,
    flower_count_max=10,
    base_price=500.00
)
```

## Troubleshooting

### Database Errors
```bash
# Reset database
python manage.py flush
python manage.py migrate

# Check migrations
python manage.py showmigrations
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Support & Feedback

For Facebook Page: https://www.facebook.com/share/1BDxmJKthR/

## License

This project is created for Joseph Flowershop. All rights reserved.

## Notes

- All prices are in Philippine Pesos (₱)
- Delivery fee can be configured in admin panel
- Phone number validation includes Philippine format support
- Images can be uploaded for all products and flowers
