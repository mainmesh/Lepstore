import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lepstore.settings')
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not username or not password:
    print('DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set; skipping superuser creation')
else:
    if User.objects.filter(username=username).exists():
        print(f'Superuser {username} already exists')
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Superuser created: username={username}')
