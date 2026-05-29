import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse
from django.contrib.messages import constants as messages
from dotenv import load_dotenv
import dj_database_url

# --------------------------
# Base del proyecto
# --------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent

# --------------------------
# Carga de variables de entorno
# --------------------------
load_dotenv(REPO_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

# --------------------------
# Monitoreo de Errores (Sentry)
# --------------------------
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

if sentry_sdk:
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

# --------------------------
# Seguridad
# --------------------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-change-this-in-production"
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,gcsof.duckdns.org,cotizador-gcinsumos.onrender.com"
).split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "https://cotizador-gcinsumos.onrender.com"
).split(",")

# Configuración de CORS necesaria para que el Frontend consuma la API sin bloqueos
CORS_ALLOW_ALL_ORIGINS = DEBUG  # En desarrollo permite todo, en producción configuralo si es necesario
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if not DEBUG else []

# --------------------------
# Aplicaciones instaladas
# --------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Librerías de Terceros agregadas para la API
    "corsheaders",          # Manejo de CORS
    "rest_framework",       # Django Rest Framework
    "django_filters",       # Filtros avanzados
    "drf_yasg",             # Documentación automática Swagger
    
    # Aplicación local
    "cotizaciones",
]

# --------------------------
# Middleware
# --------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # <-- Agregado antes de CommonMiddleware para CORS
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------
# Configuración de Django Rest Framework (DRF)
# --------------------------
REST_FRAMEWORK = {
    # Sistema Seguro de Autenticación Global (Exige JWT por defecto)
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Permisos Globales: Endpoints cerrados por defecto a menos que se especifique lo contrario
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Motores de Búsqueda y Filtrado Avanzado integrados a nivel global
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# Configuración del comportamiento y expiración de los JWT Tokens
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),   # Duración del Token de acceso
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Duración del Token de refresco
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),                # Formato en cabecera: Authorization: Bearer <token>
}

# --------------------------
# URLs
# --------------------------
ROOT_URLCONF = "proyecto.urls"

# --------------------------
# Templates
# --------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cotizaciones.config.context_processors.info_extra",
            ],
        },
    },
]

WSGI_APPLICATION = "proyecto.wsgi.application"

# --------------------------
# Base de datos (Railway / Render / SQLite local)
# --------------------------
def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DB_SSL_REQUIRE = env_bool("DB_SSL_REQUIRE", default=False)
parsed_database_url = urlparse(DATABASE_URL) if DATABASE_URL else None
valid_db_schemes = {"postgres", "postgresql", "mysql", "sqlite", "oracle", "mssql"}
is_database_url_valid = bool(
    parsed_database_url and parsed_database_url.scheme in valid_db_schemes
)

if is_database_url_valid:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=DB_SSL_REQUIRE,
        )
    }
elif all(os.environ.get(key) for key in ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")):
    db_options = {}
    if DB_SSL_REQUIRE:
        db_options["sslmode"] = "require"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_HOST"],
            "PORT": os.environ.get("DB_PORT", "5432"),
            "CONN_MAX_AGE": 600,
            "OPTIONS": db_options,
        }
    }
elif DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    invalid_database_url_msg = ""
    if DATABASE_URL and not is_database_url_valid:
        invalid_database_url_msg = (
            " DATABASE_URL es invalida (debe comenzar con un esquema soportado, por ejemplo: postgresql://...)."
        )
    raise Exception(
        "No hay configuración de base de datos."
        f"{invalid_database_url_msg} "
        "Definí DATABASE_URL o DB_NAME/DB_USER/DB_PASSWORD/DB_HOST."
    )

# --------------------------
# Validadores de contraseña
# --------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------
# Internacionalización
# --------------------------
LANGUAGE_CODE = "es-es"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True

# --------------------------
# Archivos estáticos
# --------------------------
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --------------------------
# Archivos media
# --------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------
# Login
# --------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# --------------------------
# Mensajes Bootstrap
# --------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# --------------------------
# Default PK
# --------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------
# Email SMTP
# --------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")

EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")

EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "GCinsumos <noreply@gcinsumos.com>"
)