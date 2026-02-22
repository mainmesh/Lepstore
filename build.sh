#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# create superuser from env vars if provided (DJANGO_SUPERUSER_USERNAME & DJANGO_SUPERUSER_PASSWORD)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
	python scripts/create_superuser_env.py
fi
