Production Deployment Guide

1. Environment Variables

Create a .env file in the root directory:

DJANGO_SECRET_KEY=your_super_secret_key_here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,127.0.0.1


2. Static Files

In production, Django does not serve static files by default. We use WhiteNoise for this.
Ensure whitenoise is in INSTALLED_APPS and MIDDLEWARE in settings.py.

Run this command to prepare files:

python manage.py collectstatic


3. Database (PostgreSQL)

SQLite is fine for small demos, but for production concurrency, use PostgreSQL.

Install PostgreSQL.

Update DATABASES in settings.py.

Run migrations:

python manage.py migrate


4. Running with Gunicorn

Do not use python manage.py runserver in production. Use Gunicorn:

gunicorn -c gunicorn_config.py FaceCognitionPlatform.wsgi:application


5. Camera Handling in Production

Critical: Browsers block camera access on non-secure (HTTP) origins.
You MUST serve your application over HTTPS (SSL/TLS).

If deploying on a server:

Use Nginx as a reverse proxy in front of Gunicorn.

Configure Nginx to handle SSL (Let's Encrypt).

Nginx Configuration Snippet:

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/[yourdomain.com/fullchain.pem](https://yourdomain.com/fullchain.pem);
    ssl_certificate_key /etc/letsencrypt/live/[yourdomain.com/privkey.pem](https://yourdomain.com/privkey.pem);

    location / {
        proxy_pass [http://127.0.0.1:8000](http://127.0.0.1:8000);
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
