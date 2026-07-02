import os

# Evita que settings.py explote por falta de DATABASE_URL en CI
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from .settings import *

# Forzar SQLite en memoria para tests (no depende de Postgres externo)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Deshabilitar django-axes en tests
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'axes.middleware.AxesMiddleware']
AXES_ENABLED = False
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
