import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','lepstore.settings')
import django
django.setup()
from django.test import Client
c=Client()
try:
    r=c.get('/admin/')
    print('STATUS_CODE', r.status_code)
    print(r.content.decode('utf-8','replace')[:2000])
except Exception as e:
    import traceback
    traceback.print_exc()
