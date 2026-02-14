# Zaza E-commerce Platform

Premium cannabis, curated for Nyeri.

## Features

- Full e-commerce functionality
- Product browsing with advanced filtering
- Shopping cart and checkout
- Payment integration (Stripe, M-Pesa ready)
- Customer reviews and ratings
- Bundle recommendations ("Go In Hand")
- Responsive mobile-first design
- Admin panel for inventory management

## Tech Stack

- Django 5.0
- PostgreSQL
- Tailwind CSS
- Deployed on Render

## Local Development Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd LepStore
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create .env file
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Load sample data (optional)
```bash
python manage.py loaddata sample_data.json
```

8. Run development server
```bash
python manage.py runserver
```

Visit http://localhost:8000

## Tailwind CSS (optional, production build)

This project uses Tailwind for styles. During development the Tailwind CDN is loaded for quick iteration, but for a production-ready CSS file you should build Tailwind locally and serve the compiled CSS from `static/css/styles.css`.

Steps to build Tailwind CSS:

```powershell
npm install
npm run build:css
# then collect static files for Django
python manage.py collectstatic --noinput
```

You can also run `npm run watch:css` during development to rebuild on changes.

## Environment Variables

Create a `.env` file with:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-database-url
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Deployment on Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Set build command: `./build.sh`
5. Set start command: `gunicorn lepstore.wsgi`
6. Add environment variables in Render dashboard
7. Deploy!

## Admin Access

Access admin panel at `/admin` with superuser credentials.

## License

MIT
