# Joseph Flowershop - Quick Start Guide

**Get your flower shop running in 5 minutes!**

---

## Option 1: Automated Setup (Windows)

If you're on Windows and just want to get started fast:

```bash
cd "c:\Users\user\JOSEPH FINAL\flowershop"
setup.bat
```

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create database
- ✅ Load 14 flowers, categories, and bouquet options
- ✅ Show next steps

Then follow the prompts to create your admin account.

---

## Option 2: Manual Setup (All Platforms)

### Step 1: Set Up Environment (60 seconds)

```bash
# Navigate to project
cd "c:\Users\user\JOSEPH FINAL"

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Or Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies (90 seconds)

```bash
# Install all required packages
pip install -r flowershop/requirements.txt
```

### Step 3: Set Up Database (30 seconds)

```bash
# Navigate to Django project
cd flowershop

# Create all database tables
python manage.py migrate

# Load flowers, categories, and options
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

### Step 4: Create Admin Account (60 seconds)

```bash
python manage.py createsuperuser
```

Follow prompts:
- **Username:** admin
- **Email:** admin@josephflorist.com
- **Password:** (choose something secure)

### Step 5: Start Development Server (10 seconds)

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Access Your Flower Shop

**🌹 Home Page:** http://127.0.0.1:8000/
- Browse flowers
- View products
- See featured bouquets

**💼 Admin Panel:** http://127.0.0.1:8000/admin/
- Add products
- Manage orders
- View customer orders
- Configure delivery windows
- Add payment credentials (Stripe, PayPal)

**Login with:** Username: `admin` and your password

---

## What's Included in Initial Data

When you run `python manage.py init_data`, you get:

### Categories (9)
- Roses
- Sunflower Bouquet
- Mixed Bouquet
- Anniversary Flowers
- Birthday Flowers
- Graduation Flowers
- Funeral Flowers
- Romantic Flowers
- Custom Bouquet

### Flowers (14)
- Rose (₱150 each)
- Gerbera (₱120)
- Malaysian Mum (₱100)
- Jimba (₱180)
- Stargazer (₱200)
- Astromeria (₱90)
- Bangkok Yellow (₱110)
- Jaguar Purple (₱130)
- Gladiola (₱140)
- Sunflower (₱160)
- Carnation (₱80)
- Gypsophylla (₱50)
- Statice (₱70)
- Misty Blue (₱120)

### Bouquet Sizes (4)
- Small: 5-10 flowers (₱500)
- Medium: 11-20 flowers (₱1,000)
- Large: 21-30 flowers (₱1,500)
- Premium: 31-50 flowers (₱2,500)

### Wrapping Styles (5)
- Kraft Paper (₱50)
- Cellophane (₱60)
- Fabric Wrap (₱75)
- Burlap (₱65)
- Satin (₱80)

### Ribbon Colors (7)
- Red, Pink, White, Gold, Silver, Purple, Blue (₱25-₱40 each)

### Extras (6)
- Chocolate Box (₱200)
- Teddy Bear (₱300)
- Balloon (₱100)
- Greeting Card (₱50)
- Scented Candle (₱150)
- Wine Bottle (₱400)

### Delivery Windows (2)
- Morning: 8am - 1pm (20 orders max/day)
- Afternoon: 1pm - 8pm (20 orders max/day)

---

## Test the Full Flow

### 1. Go Shopping

1. Open http://127.0.0.1:8000/
2. Click **Shop**
3. Browse products
4. Click a product to see details
5. Click **Add to Cart**

### 2. Build Custom Bouquet

1. Click **Custom Bouquet**
2. Select size → wrapping → ribbon → flowers → extras → message
3. Watch price update in real-time 💰
4. Click **Add to Cart**

### 3. Checkout

1. Click **Cart** icon (top right)
2. Click **Checkout**
3. Enter delivery address
4. Select delivery time window
5. Add gift message
6. Select payment method
7. Click **Place Order**

### 4. Track Order

1. Go to http://127.0.0.1:8000/orders/track/
2. Enter order number from confirmation
3. Enter email
4. See order status!

---

## Next: Add Your Products

Once server is running:

1. Open http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Click **Products** → **+ Add Product**
4. Fill in:
   - Name: "Red Rose Bouquet"
   - Description: "Beautiful arrangement of 15 red roses"
   - Category: Choose "Roses"
   - Base Price: 1500
   - Stock: 10
   - Is Featured: ✓ Check

5. **Save** and add product images:
   - Click **Products** → **Product Images**
   - **+ Add Product Image**
   - Select product
   - Upload flower image
   - Check "Is Primary"

---

## Troubleshooting

### "python: command not found"
- Install Python from https://www.python.org/downloads/
- On Windows, check "Add Python to PATH" during installation
- Restart terminal after installing

### "No module named 'django'"
- Make sure venv is activated: `venv\Scripts\activate`
- Reinstall: `pip install -r flowershop/requirements.txt`

### "Port 8000 already in use"
- Use different port: `python manage.py runserver 8001`
- Or kill process: Kill existing Python process and try again

### "Database is locked"
- Stop all running servers (Ctrl+C)
- Delete `db.sqlite3` and run migrations again

### "collectstatic" error
- Run: `python manage.py collectstatic --noinput`

---

## Commands Cheat Sheet

```bash
# Activate virtual environment
venv\Scripts\activate

# Install/update packages
pip install -r flowershop/requirements.txt

# Create database tables
python manage.py migrate

# Load initial data
python manage.py init_data

# Create admin account
python manage.py createsuperuser

# Start server
python manage.py runserver

# Access Django shell
python manage.py shell

# Create a new app
python manage.py startapp appname

# Check for issues
python manage.py check
```

---

## What You Now Have

✅ **Complete Django Web Application**
- 8 modular apps (products, accounts, cart, custom_bouquet, orders, delivery, payments, configurations)
- 41 database models (Flower, Product, Order, Delivery, Payment, etc.)
- Administrator dashboard
- User authentication (register, login, profile)
- Shopping cart (guest & user support)
- Custom bouquet builder with real-time pricing
- Order tracking by order number + email
- Responsive TailwindCSS design
- Integration-ready for Stripe & PayPal

✅ **Production-Ready Architecture**
- Database security (no hardcoded API keys)
- Session management
- CSRF protection
- Django ORM with 3NF normalized schema
- Proper deployment configuration (.env template)

✅ **Sample Data Loaded**
- 14 flower types
- 9 product categories
- 4 bouquet sizes
- 5 wrapping styles
- 7 ribbon colors
- 6 extras (chocolate, teddy, balloons, etc.)
- 2 delivery time windows

---

## Need Help?

1. **Setup Issues:** Read [SETUP.md](../SETUP.md)
2. **Feature Questions:** See [README.md](flowershop/README.md)
3. **Django Help:** https://docs.djangoproject.com/
4. **TailwindCSS:** https://tailwindcss.com/docs

---

## Next Steps (Optional)

1. **Add Real Products:** Use Facebook page as reference
2. **Customer Support:** Add email templates for order confirmations
3. **Payment Integration:** Configure Stripe/PayPal API keys
4. **Analytics:** Track orders and customer behavior
5. **Mobile App:** Consider React Native / Flutter app
6. **Inventory:** Add low-stock alerts and notifications

---

**Your flower shop is ready! 🌹🌻💐**

Access it now:
- **Home:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/
- **Tracking:** http://127.0.0.1:8000/orders/track/

Enjoy! 🎉
