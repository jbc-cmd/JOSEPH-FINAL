# Joseph Flowershop - Deployment Checklist

Use this checklist to ensure your flower shop is ready for production deployment.

---

## Pre-Launch Verification

### ✅ Section 1: Environment & Dependencies

- [ ] Python 3.10+ installed and verified: `python --version`
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated: `venv\Scripts\activate`
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Django version is 4.2.x: `pip show django`
- [ ] All requirements installed successfully without errors

### ✅ Section 2: Database Setup

- [ ] PostgreSQL installed (for production) OR SQLite ready (for development)
- [ ] Database migrations run: `python manage.py migrate`
- [ ] Initial data loaded: `python manage.py init_data`
- [ ] Database file exists: `db.sqlite3` (or PostgreSQL database created)
- [ ] Database contains tables (verify in Django admin)

### ✅ Section 3: Django Configuration

- [ ] `settings.py` configured with correct DATABASE settings
- [ ] `SECRET_KEY` set in `.env` (not using default)
- [ ] `ALLOWED_HOSTS` configured for your domain (development and production)
- [ ] `DEBUG` set to `False` in `.env` for production
- [ ] `EMAIL_BACKEND` configured (console or SMTP)
- [ ] Static files configuration set: `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`

### ✅ Section 4: Admin Panel

- [ ] Superuser account created: `python manage.py createsuperuser`
- [ ] Admin panel accessible: `http://127.0.0.1:8000/admin/`
- [ ] Can login with superuser credentials
- [ ] All 8 apps visible in admin: Products, Accounts, Cart, Custom Bouquet, Orders, Delivery, Payments, Configurations
- [ ] At least one product category created (in Products → Categories)
- [ ] At least one flower created (in Products → Flowers) - 14 flowers if used `init_data`
- [ ] At least one product created (in Products → Products)
- [ ] Bouquet sizes exist (4 sizes if used `init_data`)
- [ ] Wrapping styles exist (5 styles if used `init_data`)
- [ ] Ribbon colors exist (7 colors if used `init_data`)
- [ ] Extras exist (6 extras if used `init_data`)
- [ ] Delivery time windows exist (2 windows if used `init_data`)

### ✅ Section 5: Frontend Verification

- [ ] Development server starts: `python manage.py runserver`
- [ ] Home page loads without errors: http://127.0.0.1:8000/
- [ ] All templates render correctly with CSS styling
- [ ] Navigation menu displays properly
- [ ] Hero section shows on home page
- [ ] Featured products display on home page
- [ ] Shop page loads and shows products: /shop/
- [ ] Product detail page works: /products/{product-id}/
- [ ] Flower images display correctly

### ✅ Section 6: Shopping Cart Functionality

- [ ] Add to cart button works
- [ ] Cart icon shows correct item count
- [ ] Cart page displays items with prices
- [ ] Update quantity works (increase/decrease)
- [ ] Remove item works
- [ ] Subtotal and total calculate correctly
- [ ] Clear cart button works
- [ ] Cart persists when logged out (session-based) and logs back in (database-based)

### ✅ Section 7: Custom Bouquet Builder

- [ ] Custom Bouquet link accessible: /bouquet/builder/
- [ ] All 6 steps load: size, wrapping, ribbon, flowers, extras, message
- [ ] Size selection works
- [ ] Wrapping style selection works
- [ ] Ribbon color selection works (with color preview)
- [ ] Flower selection works (shows all 14 available flowers)
- [ ] Quantity inputs work and are within range
- [ ] Extras can be selected and deselected
- [ ] Gift message input works
- [ ] Real-time pricing updates via AJAX
- [ ] Price breakdown shows: Size + Wrapping + Ribbon + Flowers + Extras
- [ ] Add to Cart button saves bouquet and adds to cart

### ✅ Section 8: User Authentication

- [ ] Registration page works: /accounts/register/
- [ ] Can register new user with valid email
- [ ] User registration email validation works
- [ ] Login page works: /accounts/login/
- [ ] Can login with registered credentials
- [ ] Logout works
- [ ] User profile page shows: /accounts/profile/
- [ ] Profile form can update user information
- [ ] Password change works
- [ ] Saved delivery addresses display
- [ ] Can add new delivery address
- [ ] Can edit existing delivery address
- [ ] Can set default delivery address
- [ ] Order history shows user's past orders

### ✅ Section 9: Checkout & Orders

- [ ] Checkout page accessible from cart: /orders/checkout/
- [ ] Delivery address form displays with fields (street, city, postal code, etc.)
- [ ] Delivery date picker works
- [ ] Delivery time window selection shows options (Morning, Afternoon)
- [ ] Payment method options display (Cash on Delivery, Credit Card, etc.)
- [ ] Gift message field works
- [ ] Anonymous purchase option works
- [ ] Order summary displays correctly with items and total
- [ ] Form validation works (required fields highlighted)
- [ ] Order creation works (creates unique order number)
- [ ] Order confirmation page displays with order details
- [ ] Confirmation email sent (check console or email service)

### ✅ Section 10: Order Tracking

- [ ] Order tracking page accessible: /orders/track/
- [ ] Lookup by order number + email works
- [ ] Order detail page displays all information:
  - [ ] Order number
  - [ ] Order date
  - [ ] Current status (Pending, Processing, etc.)
  - [ ] Customer name and email
  - [ ] Delivery address
  - [ ] Delivery date and time window
  - [ ] Items ordered
  - [ ] Total price
  - [ ] Payment method
  - [ ] Support contact information
- [ ] Status timeline displays order progression

### ✅ Section 11: Admin Order Management

- [ ] Orders display in admin: /admin/orders/order/
- [ ] Can update order status (Pending → Processing → Preparing → Out for Delivery → Delivered)
- [ ] Delivery information can be added
- [ ] Can assign delivery personnel
- [ ] Can add delivery proof of delivery image (POD)
- [ ] Delivery tracking shows status history

### ✅ Section 12: API Integration Points

- [ ] Cart count AJAX endpoint works: `/cart/count/`
- [ ] Bouquet pricing AJAX endpoint works: `/bouquet/pricing/`
- [ ] Can save custom bouquet: `/bouquet/save/`
- [ ] Search functionality ready (endpoint exists but may need refinement)

### ✅ Section 13: Static Files

- [ ] CSS styles load correctly (TailwindCSS utilities apply)
- [ ] Color scheme displays (pink/rose primary colors)
- [ ] FontAwesome icons load and display
- [ ] JavaScript utilities work (cart count, form validation)
- [ ] Images display in products and extras
- [ ] Responsive design works on mobile (test with browser dev tools)
- [ ] Responsive design works on tablet (test with browser dev tools)
- [ ] Responsive design works on desktop

### ✅ Section 14: Data Integrity

- [ ] No duplicate product categories
- [ ] No duplicate flower types
- [ ] All foreign key relationships intact (no orphaned records)
- [ ] Order items linked to order correctly
- [ ] Bouquet items linked to bouquet correctly
- [ ] Prices stored at purchase time (no dynamic price changes after order)
- [ ] Database has backup (before major deployments)

### ✅ Section 15: Security Checklist

- [ ] `SECRET_KEY` is unique and not default
- [ ] `DEBUG` is `False` in production
- [ ] Sensitive data in `.env` file, not in code
- [ ] `.env` file not committed to Git (in `.gitignore`)
- [ ] CSRF protection enabled (token in forms)
- [ ] SQL injection prevented (using Django ORM)
- [ ] XSS protection enabled (template escaping)
- [ ] HTTPS enabled in production (SSL certificate)
- [ ] password hashing implemented (using Django auth)
- [ ] Session timeout configured (optional)
- [ ] Admin panel protected (only authenticated users)
- [ ] User passwords not visible in admin panel
- [ ] API endpoints don't expose sensitive data

### ✅ Section 16: Email Configuration (Optional)

- [ ] Email backend configured in `.env`
- [ ] Email credentials set (if using SMTP)
- [ ] Order confirmation emails send
- [ ] Customer receives order notification
- [ ] Admin receives order notification
- [ ] Password reset emails work (if enabled)
- [ ] Email templates created and styled

### ✅ Section 17: Payment Gateway Setup (Optional)

- [ ] Stripe account created (if using Stripe)
- [ ] Stripe API keys obtained
- [ ] Stripe keys added to `ServiceConfig` table in admin
- [ ] Stripe.js loaded on checkout page
- [ ] Credit card form renders
- [ ] Payment processing works
- [ ] PayPal alternative configured (if using PayPal)
- [ ] Payment status updates order status

### ✅ Section 18: Production Deployment Readiness

- [ ] All dependencies listed in `requirements.txt`
- [ ] Python version specified in `requirements.txt` or `.python-version`
- [ ] Static files will be collected: `python manage.py collectstatic`
- [ ] Database migrations can be run: `python manage.py migrate`
- [ ] Logs configured for production monitoring
- [ ] Error monitoring tool configured (Sentry, etc.) - optional
- [ ] Backup strategy for database
- [ ] Backup strategy for media files (uploaded images)

### ✅ Section 19: Documentation

- [ ] README.md complete with setup instructions
- [ ] SETUP.md comprehensive setup guide
- [ ] QUICKSTART.md available for getting started fast
- [ ] Troubleshooting guide complete
- [ ] Database schema documented
- [ ] API endpoints documented (if applicable)
- [ ] Deployment instructions provided

### ✅ Section 20: Performance & Optimization

- [ ] Database queries optimized (using `select_related` and `prefetch_related` where needed)
- [ ] Static files minified (CSS, JS)
- [ ] Images optimized (compressed, appropriate sizes)
- [ ] Pagination implemented on list pages (admin and customer)
- [ ] Caching considered for frequently accessed data
- [ ] Database indexes created on frequently queried fields
- [ ] Page load time acceptable (< 3 seconds target)
- [ ] Asset loading optimized (no render-blocking resources)

---

## Pre-Production Checklist

Before going live:

- [ ] All admin users have strong passwords
- [ ] Superuser account renamed (not "admin")
- [ ] Production database backup completed
- [ ] `.env` file with production credentials ready
- [ ] Logging configured for error tracking
- [ ] Uptime monitoring configured (optional)
- [ ] Error reporting tool configured (Sentry, etc.) - optional
- [ ] DNS records configured for domain
- [ ] SSL/TLS certificate installed
- [ ] CDN configured for static files (optional)
- [ ] Load balancer configured (if needed)
- [ ] Database replication configured (if needed)
- [ ] Automated backups scheduled

---

## Post-Launch Monitoring

After going live, monitor:

- [ ] Application uptime (check daily)
- [ ] Error logs (check daily)
- [ ] User registrations (track sign-ups)
- [ ] Order volume (track orders)
- [ ] Cart abandonment rate (identify issues)
- [ ] Payment success rate
- [ ] Delivery completion rate
- [ ] Customer support requests
- [ ] Database size growth
- [ ] Server resource usage (CPU, memory, disk)

---

## Troubleshooting Reference

**If something fails, check:**

1. **Migrations failed?**
   - Check: `python manage.py makemigrations && python manage.py migrate`
   - Verify: `python manage.py check`

2. **Static files not loading?**
   - Run: `python manage.py collectstatic --noinput`
   - Check: `STATIC_URL` and `STATIC_ROOT` in settings

3. **Database not found?**
   - Check: `DB_NAME` in `.env` file
   - Verify: Database file/connection string correct
   - Run: `python manage.py migrate --run-syncdb`

4. **Admin panel not accessible?**
   - Create superuser: `python manage.py createsuperuser`
   - Verify: `INSTALLED_APPS` includes 'django.contrib.admin'

5. **Pages showing 404?**
   - Check: URL routing in `urls.py` files
   - Verify: View functions/classes exist
   - Check: Template files exist in correct directories

6. **Forms not working?**
   - Check: CSRF token in template
   - Verify: Form class exists and imports correctly
   - Check: POST method in template form

---

## Final Sign-Off

**All items checked?** Your flower shop is ready to launch! 🚀

**Missing items?** Go back to relevant section and complete.

**Deployment?** Refer to deployment instructions in README.md

---

## Emergency Contacts

- **Django Issues:** https://docs.djangoproject.com/
- **Python Errors:** https://stackoverflow.com/questions/tagged/python
- **Database Help:** PostgreSQL documentation
- **Deployment Help:** Platform-specific docs (Heroku, AWS, DigitalOcean, etc.)

---

**When completed, your Joseph Flowershop is production-ready! 🌹🌻💐**
