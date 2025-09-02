import os
from pathlib import Path
import dj_database_url
from django.contrib.messages import constants as messages
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------
# Configuración básica
# --------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']
"""DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # Temporal para debug, cambiar a False en producción
ALLOWED_HOSTS = ['cotizador-gcinsumos.onrender.com']  # Dominios permitidos"""

# CSRF para Render
CSRF_TRUSTED_ORIGINS = ["https://cotizador-gcinsumos.onrender.com"]

# --------------------------
# Aplicaciones instaladas
# --------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cotizaciones',
]

# --------------------------
# Middleware
# --------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------
# URLs y Templates
# --------------------------
ROOT_URLCONF = 'proyecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # 👇 Agregamos nuestro context processor
                'cotizaciones.context_processors.info_extra',
            ],
        },
    },
]

WSGI_APPLICATION = 'proyecto.wsgi.application'

# --------------------------
# Base de datos
# --------------------------

load_dotenv()  # carga las variables del .env

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + str(BASE_DIR / "db.sqlite3")  # fallback a SQLite
)

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}
# --------------------------
# Validadores de contraseña
# --------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------
# Internacionalización
# --------------------------
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# --------------------------
# Archivos estáticos y media
# --------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------
# Login
# --------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# --------------------------
# Mensajes personalizados
# --------------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# --------------------------
# Campo por defecto para modelos
# --------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
