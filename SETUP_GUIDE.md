# Lepstore E-commerce Platform - Complete Setup Guide

## Quick Start (Local Development)

### 1. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Create .env File
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```powershell
python manage.py createsuperuser
```

### 6. Create Static Files Directory
```powershell
New-Item -ItemType Directory -Path static
New-Item -ItemType Directory -Path media
```

### 7. Run Development Server
```powershell
python manage.py runserver
```

Visit http://localhost:8000

---

## Deploy to Render

### Step 1: Prepare Your Repository

1. Initialize Git (if not done):
```powershell
git init
git add .
git commit -m "Initial commit"
```

2. Create GitHub repository and push:
```powershell
git remote add origin https://github.com/yourusername/lepstore.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `lepstore-db`
3. Choose free tier
4. Click "Create Database"
5. Copy the "Internal Database URL" (it will look like: `postgresql://...`)

### Step 4: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** lepstore
   - **Environment:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn lepstore.wsgi`
   - **Instance Type:** Free

### Step 5: Add Environment Variables

In Render dashboard, go to "Environment" and add:

```
SECRET_KEY=your-production-secret-key-here
DEBUG=False
DATABASE_URL=[paste your PostgreSQL Internal Database URL]
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
ALLOWED_HOSTS=.onrender.com
PYTHON_VERSION=3.11.6
```

### Step 6: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your site will be live at `https://lepstore.onrender.com`

### Step 7: Create Superuser on Render

1. Go to your service in Render dashboard
2. Click "Shell" tab
3. Run:
```bash
python manage.py createsuperuser
```

---

## Adding Sample Data

### Option 1: Through Admin Panel

1. Go to `/admin`
2. Login with superuser credentials
3. Add Categories (Laptops, Tablets, Smartphones, Accessories)
4. Add Brands (Apple, Dell, HP, Samsung, etc.)
5. Add Products with images
6. Add Shipping Methods
7. Add Product Reviews

### Option 2: Create Sample Data Script

Create `populate_db.py` in project root:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lepstore.settings')
django.setup()

from store.models import Category, Brand, Product, ShippingMethod

# Create Categories
laptops = Category.objects.create(name='Laptops', description='High-performance laptops')
tablets = Category.objects.create(name='Tablets', description='Portable tablets and iPads')
smartphones = Category.objects.create(name='Smartphones', description='Latest smartphones')
accessories = Category.objects.create(name='Accessories', description='Tech accessories')

# Create Brands
apple = Brand.objects.create(name='Apple')
dell = Brand.objects.create(name='Dell')
hp = Brand.objects.create(name='HP')
samsung = Brand.objects.create(name='Samsung')

# Create Sample Products
Product.objects.create(
    category=laptops,
    brand=apple,
    name='MacBook Pro 14" M3 Chip 16GB RAM 512GB SSD',
    description='Powerful laptop for professionals',
    price=1999.00,
    original_price=2299.00,
    stock=10,
    processor='Apple M3',
    ram='16GB',
    storage='512GB SSD',
    screen_size='14 inches',
    operating_system='macOS',
    is_featured=True,
    is_new=True
)

Product.objects.create(
    category=laptops,
    brand=dell,
    name='Dell XPS 15 Intel Core i7 32GB RAM 1TB SSD',
    description='Premium Windows laptop',
    price=1799.00,
    original_price=1999.00,
    stock=8,
    processor='Intel Core i7 13th Gen',
    ram='32GB',
    storage='1TB SSD',
    screen_size='15.6 inches',
    operating_system='Windows 11',
    is_featured=True
)

# Create Shipping Methods
ShippingMethod.objects.create(
    name='Standard Delivery',
    description='5-7 business days',
    cost=0.00,
    estimated_days='5-7 business days',
    is_active=True
)

ShippingMethod.objects.create(
    name='Express Delivery',
    description='2-3 business days',
    cost=15.00,
    estimated_days='2-3 business days',
    is_active=True
)

ShippingMethod.objects.create(
    name='Next Day Delivery',
    description='Delivered tomorrow',
    cost=30.00,
    estimated_days='1 business day',
    is_active=True
)

print("Database populated successfully!")
```

Run it:
```powershell
python populate_db.py
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'store'"
**Solution:** Make sure you've installed all requirements and activated virtual environment

### Issue: "Table doesn't exist"
**Solution:** Run migrations:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Issue: "Static files not loading"
**Solution:**
```powershell
python manage.py collectstatic
```

### Issue: "ALLOWED_HOSTS error on Render"
**Solution:** Add your Render URL to ALLOWED_HOSTS in .env:
```
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com,your-app.onrender.com
```

### Issue: "Database connection error on Render"
**Solution:** Make sure DATABASE_URL is set correctly in Render environment variables

---

## File Upload Configuration (For Product Images)

### For Development (Local)
Images are stored in `media/` folder automatically.

### For Production (Render)
Render's free tier doesn't persist files. Use Cloudinary or AWS S3:

#### Option 1: Cloudinary (Recommended for Render)

1. Sign up at https://cloudinary.com
2. Install package:
```powershell
pip install django-cloudinary-storage
```

3. Add to settings.py:
```python
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'your-cloud-name',
    'API_KEY': 'your-api-key',
    'API_SECRET': 'your-api-secret'
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

---

## Performance Optimization

### 1. Enable Caching (Production)
Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}
```

Create cache table:
```powershell
python manage.py createcachetable
```

### 2. Optimize Database Queries
Already implemented with `select_related()` and `prefetch_related()`

### 3. Image Optimization
- Use WebP format
- Compress images before upload
- Use lazy loading (already in templates)

---

## Monitoring & Maintenance

### Check Application Logs (Render)
1. Go to Render dashboard
2. Click your service
3. View "Logs" tab

### Database Backup (Important!)
1. Render dashboard → PostgreSQL service
2. Click "Backups" tab
3. Enable automatic backups

### Update Dependencies
```powershell
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

---

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS correctly
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set secure cookie flags (already in settings.py)
- [ ] Keep dependencies updated
- [ ] Regular database backups

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Add sample products
3. ✅ Configure Stripe payments
4. ✅ Test checkout flow
5. ⬜ Set up email notifications (SendGrid/AWS SES)
6. ⬜ Add M-Pesa integration (Daraja API)
7. ⬜ Set up Google Analytics
8. ⬜ Configure custom domain
9. ⬜ Add product reviews system
10. ⬜ Implement wishlist feature

---

## Support & Resources

- **Django Docs:** https://docs.djangoproject.com
- **Render Docs:** https://render.com/docs
- **Stripe Docs:** https://stripe.com/docs
- **Tailwind CSS:** https://tailwindcss.com/docs

---

## Project Structure

```
LepStore/
├── lepstore/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/             # Product catalog app
│   ├── models.py      # Product, Category, Brand, Review
│   ├── views.py       # Homepage, product listing, detail
│   ├── admin.py       # Admin customizations
│   └── urls.py
├── cart/              # Shopping cart app
│   ├── cart.py        # Cart class (session-based)
│   ├── views.py       # Add, remove, update cart
│   └── context_processors.py
├── orders/            # Order management app
│   ├── models.py      # Order, OrderItem
│   ├── views.py       # Checkout, payment
│   └── forms.py
├── accounts/          # User authentication
│   ├── views.py       # Login, register, profile
│   └── forms.py
├── templates/         # HTML templates
│   ├── base.html
│   ├── store/
│   ├── cart/
│   ├── orders/
│   └── accounts/
├── static/            # CSS, JS, images
├── media/             # Uploaded files
├── manage.py
├── requirements.txt
├── Procfile          # Render deployment
├── build.sh          # Build script for Render
└── README.md
```

---

**Your Lepstore e-commerce platform is ready to launch! 🚀**
