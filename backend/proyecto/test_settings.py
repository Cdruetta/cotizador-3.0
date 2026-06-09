from .settings import *

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
