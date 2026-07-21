import os
from pathlib import Path

from proyecto.settings import *  # noqa: F403,F401

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "cotizaciones": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
}

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_TZ = True
LANGUAGE_CODE = "es-ar"
USE_I18N = True
USE_L10N = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

