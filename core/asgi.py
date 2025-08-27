"""
ASGI entrypoint that mounts:
- Django at `/` (root)
- FastAPI at `/api`
Run with: uvicorn core.asgi:application --reload
"""
import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware  # fallback if needed (Django ASGI is fine)
from apiapp.main import app as fastapi_app

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Django ASGI app
django_asgi_app = get_asgi_application()

# Create a small wrapper FastAPI that mounts Django too (or use Starlette Router)
root = FastAPI(title="Django + FastAPI ASGI")

# Mount FastAPI under /api
root.mount("/api", fastapi_app)

# Mount Django under /
# Because Django is already ASGI-capable, we can mount it directly:
root.mount("/", django_asgi_app)

# Uvicorn expects `application` variable
application = root
