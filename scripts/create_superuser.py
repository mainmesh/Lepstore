import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lepstore.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'adminpass'
if User.objects.filter(username=username).exists():
    print('Superuser already exists')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created: username=admin password=adminpass')
