import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','lepstore.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from store.models import Category, Product, Variant

print('Collecting site statistics...')

User = get_user_model()
print('Users total:', User.objects.count())
print('Superusers:', User.objects.filter(is_superuser=True).count())
print('Active Categories:', Category.objects.filter(is_active=True).count())
print('Total Categories:', Category.objects.count())
print('Products total:', Product.objects.count())
print('Products available:', Product.objects.filter(is_available=True).count())
print('Variants total:', Variant.objects.count())

# Orders may not be present; attempt to import
try:
    from orders.models import Order
    print('Orders total:', Order.objects.count())
    print('Orders (status counts):')
    from django.db.models import Count
    for row in Order.objects.values('status').annotate(cnt=Count('id')):
        print('  ', row['status'], row['cnt'])
except Exception as e:
    print('Orders app not available or error:', e)

# Disk usage for media and static (approx)
import shutil
from pathlib import Path
base = Path(__file__).resolve().parent.parent
static = base / 'static'
media = base / 'media'
print('Static exists:', static.exists())
print('Media exists:', media.exists())

def human(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"

if static.exists():
    total = sum(f.stat().st_size for f in static.rglob('*') if f.is_file())
    print('Static size:', human(total))
if media.exists():
    total = sum(f.stat().st_size for f in media.rglob('*') if f.is_file())
    print('Media size:', human(total))

print('Done.')
