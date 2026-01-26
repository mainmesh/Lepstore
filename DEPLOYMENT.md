Vercel Deployment Notes
=======================

Follow these steps to deploy the Django project to Vercel.

1. Set required environment variables in the Vercel Project Settings:
   - `DJANGO_SETTINGS_MODULE=lepstore.settings`
   - `SECRET_KEY` (your Django secret key)
   - `DATABASE_URL` (Postgres URL)
   - Any AWS/S3 credentials if using `django-storages` (`USE_S3`, `STATICFILES_ON_S3`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`)
   - Any payment or third-party keys (e.g., `STRIPE_SECRET_KEY`)

2. Build behavior
   - Vercel will run the `vercel-build` script defined in `package.json`, which builds Tailwind CSS and runs `python manage.py collectstatic --noinput`.

3. Static & media files
   - Static files are collected into the `static/` directory during build. Configure your storage backend (S3 or other) for media files in production.
   - By default this project uses WhiteNoise to serve static files collected by `collectstatic`.
   - To use S3 for media (and optionally static files) set `USE_S3=True` in the environment and provide the AWS variables above. The settings detect `USE_S3` and enable S3-backed storage via `django-storages`.

4. Example environment variables
   - See `.env.example` for a template with recommended variables.

4. Notes
   - The repository includes a lightweight `api/wsgi.py` wrapper exposing the Django WSGI app as `app` for hosting adapters.
   - Ensure `requirements.txt` and `runtime.txt` are up-to-date in the project root.
