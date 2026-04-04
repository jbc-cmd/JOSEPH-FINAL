# Joseph Flowershop - Setup Guide

This guide will walk you through setting up the Joseph Flowershop web application on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Database Setup](#database-setup)
4. [Running the Development Server](#running-the-development-server)
5. [Loading Initial Data](#loading-initial-data)
6. [Creating Admin Account](#creating-admin-account)
7. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Usually comes with Python installation
- **Git** (optional but recommended) - [Download Git](https://git-scm.com/)

### Verify Installation

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
python --version
pip --version
```

Both should return version numbers.

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd "c:\Users\user\JOSEPH FINAL"
```

### Step 2: Create Virtual Environment

It's best practice to use a virtual environment to isolate dependencies.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, your command prompt should show `(venv)` at the beginning.

### Step 3: Install Dependencies

With virtual environment activated:

```bash
pip install -r flowershop/requirements.txt
```

This installs all required Python packages (Django, Pillow, django-crispy-forms, etc.).

**Expected output:** "Successfully installed [packages]..."

### Step 4: Set Up Environment Variables

Create a `.env` file in the `flowershop_project` directory:

```bash
# Windows
copy flowershop_project\.env.example flowershop_project\.env

# Mac/Linux
cp flowershop_project/.env.example flowershop_project/.env
```

Open `flowershop_project/.env` and update with your settings:

```ini
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Email (optional, for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stripe (optional, add later)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=

# PayPal (optional, add later)
PAYPAL_CLIENT_ID=
PAYPAL_SECRET_KEY=
```

---

## Database Setup

### Step 1: Navigate to Project Folder

```bash
cd flowershop
```

### Step 2: Run Migrations

Migrations create all database tables defined in models:

```bash
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, products, accounts, cart, custom_bouquet, orders, delivery, payments, configurations
Running migrations:
  ...
  Applying accounts.0001_initial... OK
  Applying products.0001_initial... OK
  ...
```

This creates `db.sqlite3` file in the `flowershop` directory.

---

## Running the Development Server

### Start Django Development Server

```bash
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Access the Application

Open your web browser and navigate to:

- **Home Page:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

You should see the flowershop home page with a banner and navigation menu.

---

## Loading Initial Data

### Step 1: Initialize Database with Flowers and Categories

Run the custom management command we created:

```bash
python manage.py init_data
```

**Expected output:**
```
Initializing database...
✓ Categories created
✓ Flowers created
✓ Bouquet sizes created
✓ Wrapping styles created
✓ Ribbon colors created
✓ Extras created
✓ Delivery time windows created
✓ Database initialization complete!
```

This creates:
- **9 product categories** (Roses, Sunflower, Mixed, etc.)
- **14 flower types** (Rose, Gerbera, Mum, etc.)
- **4 bouquet sizes** (Small to Premium)
- **5 wrapping styles** (Kraft, Cellophane, Fabric, etc.)
- **7 ribbon colors** (Red, Pink, Gold, etc.)
- **6 extras** (Chocolate, Teddy Bear, Balloons, etc.)
- **2 delivery time windows** (Morning 8am-1pm, Afternoon 1pm-8pm)

---

## Creating Admin Account

### Step 1: Create Superuser

While the development server is running (or in another terminal), run:

```bash
python manage.py createsuperuser
```

### Step 2: Follow the Prompts

```
Username: admin
Email address: admin@josephflorist.com
Password: ••••••••
Password (again): ••••••••
Superuser created successfully.
```

### Step 3: Login to Admin Panel

1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. You should see the Django Admin Dashboard

---

## Admin Panel Overview

### Adding Products

1. Click **Products** → **Products**
2. Click **Add Product**
3. Fill in:
   - **Name:** e.g., "Red Rose Bouquet"
   - **Description:** e.g., "A beautiful arrangement of 15 red roses"
   - **Category:** Select from dropdown (e.g., "Roses")
   - **Base Price:** e.g., 1500.00
   - **Quantity in Stock:** e.g., 10
   - **Is Featured:** Check to show on home page
4. Click **Save**

### Adding Product Images

1. Go to Products → Product Images
2. Click **Add Product Image**
3. Select the product
4. Upload image
5. Check **Is Primary** for the main product image

### Managing Delivery Addresses (for Customers)

1. Navigate to **Accounts** → **Delivery Addresses**
2. These are auto-populated as customers register

### Viewing Orders

1. Navigate to **Orders** → **Orders**
2. Click an order to view details
3. Update status using the **Status** dropdown
4. Change to: PROCESSING → PREPARING → OUT_FOR_DELIVERY → DELIVERED

### Managing Carts

1. Navigate to **Cart** → **Carts**
2. See active shopping carts (user carts and guest carts)

---

## Testing the Application

### Test User Registration

1. Go to http://127.0.0.1:8000/
2. Click **Register**
3. Fill in the form:
   - Username: testuser
   - Email: testuser@example.com
   - Password: TestPass123!
4. Click Register

### Test Shopping Flow

1. Click **Shop** in navigation
2. Browse products by category
3. Click a product to see details
4. Click **Add to Cart**
5. Click cart icon (top right)
6. Modify quantities or click **Checkout**

### Test Custom Bouquet Builder

1. Click **Custom Bouquet** in navigation
2. Follow 6-step builder:
   - Select size
   - Choose wrapping style
   - Pick ribbon color
   - Select flowers and quantities
   - Add extras (chocolate, teddy, etc.)
   - Add gift message
3. Watch price update in real-time
4. Click **Add to Cart**

### Test Checkout

1. From cart, click **Checkout**
2. Fill in:
   - Delivery address (or create new)
   - Delivery date
   - Delivery time window (Morning or Afternoon)
   - Payment method (Cash on Delivery works for testing)
   - Gift message (optional)
3. Click **Place Order**
4. You should see order confirmation page

### Test Order Tracking

1. Go to http://127.0.0.1:8000/orders/track/
2. Enter order number (from confirmation page)
3. Enter email address
4. Click **Track Order**
5. You should see order status and details

---

## Collecting Static Files (Production)

When deploying to production, run:

```bash
python manage.py collectstatic
```

This gathers all CSS, JavaScript, and images into a single directory for serving.

---

## Next Steps

### 1. Add More Products

Use the admin panel to add more flowers and pre-designed bouquets based on the Facebook page reference:
https://www.facebook.com/share/1BDxmJKthR/

### 2. Configure Payment Gateway (Optional)

To enable online payment:

1. Get Stripe API keys: https://stripe.com
2. Add to `flowershop_project/.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```
3. Uncomment payment integration code in `orders/views.py`

### 3. Configure Email Notifications (Optional)

To enable order confirmation emails:

1. Get SMTP credentials from your email provider (Gmail, SendGrid, etc.)
2. Update `flowershop_project/.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   EMAIL_USE_TLS=True
   ```
3. Create email templates for order confirmations

### 4. Customize Appearance

Edit these files to match your branding:

- `templates/base.html` - Logo, navbar, footer
- `static/css/style.css` - Colors, fonts
- `flowershop_project/settings.py` - App name, display settings

### 5. Deploy to Production

When ready to go live:

1. Switch to PostgreSQL database
2. Deploy to hosting (Heroku, DigitalOcean, AWS)
3. Set `DEBUG=False` in `.env`
4. Configure custom domain
5. Set up SSL certificate

See [Deployment Guide](#) for detailed steps.

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'django'"

**Solution:** Ensure virtual environment is activated and requirements installed:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r flowershop/requirements.txt
```

### Problem: "Port 8000 already in use"

**Solution:** Kill the process using port 8000 or use different port:
```bash
python manage.py runserver 8001
```

### Problem: "Permission denied" when creating database

**Solution:** Ensure you have write permissions in the project directory.

### Problem: Admin panel loads but no CSS styling

**Solution:** Run collectstatic and refresh browser:
```bash
python manage.py collectstatic --noinput
```

### Problem: Can't login to admin panel

**Solution:** Verify superuser was created:
```bash
python manage.py createsuperuser
```

### Problem: Images not showing in product pages

**Solution:** Ensure Pillow is installed:
```bash
pip install Pillow
```

---

## Development Best Practices

### 1. Always Activate Virtual Environment

Before running any commands:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 2. Keep `.env` Secure

Never commit `.env` to version control. It's in `.gitignore` by default.

### 3. Run Tests (Optional)

Create tests in `app_name/tests.py`:
```bash
python manage.py test
```

### 4. Make Database Backups

Periodically backup `db.sqlite3` file before major changes.

### 5. Use Django Shell for Quick Testing

```bash
python manage.py shell
```

Then import and test models:
```python
from products.models import Flower
flowers = Flower.objects.all()
print(flowers.count())
```

---

## Support

For questions or issues:

1. Check the [README.md](README.md) for more detailed documentation
2. Review Django docs: https://docs.djangoproject.com/
3. Check TailwindCSS docs: https://tailwindcss.com/docs

---

## Summary

You now have a fully functional Joseph Flowershop application! 

**Quick command reference:**

```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies (first time only)
pip install -r flowershop/requirements.txt

# Navigate to project
cd flowershop

# Create database
python manage.py migrate

# Load initial data
python manage.py init_data

# Create admin account
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access application
# Home: http://127.0.0.1:8000/
# Admin: http://127.0.0.1:8000/admin/
```

Enjoy your new flower shop! 🌹🌻💐
