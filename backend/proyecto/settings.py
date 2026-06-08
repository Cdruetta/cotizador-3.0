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
# Sentry (opcional)
# --------------------------
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

if sentry_sdk:
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "").strip()
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

# Por seguridad, el default es False en caso de no especificar DEBUG.
DEBUG = os.environ.get("DEBUG", "False").lower() in {"1", "true", "yes", "on"}

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://cotizador-gcinsumos.onrender.com"
    ).split(",")
    if origin.strip()
]

# If ALLOWED_HOSTS wasn't provided explicitly, try to auto-add the Render
# external hostname (Render injects RENDER_EXTERNAL_HOSTNAME / RENDER_EXTERNAL_URL).
# This helps avoid 400 Bad Request responses when deploying on Render without
# having to manually set ALLOWED_HOSTS in the UI. We only append this as a
# fallback and do not override an explicit ALLOWED_HOSTS value.
if (not ALLOWED_HOSTS) or set(ALLOWED_HOSTS) <= {"localhost", "127.0.0.1"}:
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME") or os.environ.get("RENDER_EXTERNAL_URL")
    if render_host:
        # Normalize: strip scheme and trailing slashes
        render_host = render_host.replace("https://", "").replace("http://", "").strip("/ ")
        if render_host and render_host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(render_host)

    # Ensure CSRF_TRUSTED_ORIGINS contains the https:// origin for the host
    for host in ALLOWED_HOSTS:
        if host and host not in ("localhost", "127.0.0.1"):
            origin = host
            if not origin.startswith("http://") and not origin.startswith("https://"):
                origin = f"https://{origin}"
            if origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(origin)

# --------------------------
# CORS (CORREGIDO)
# --------------------------
raw_cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in raw_cors_origins.split(",")
    if origin.strip()
]

# Solo permitir todos los orígenes en modo DEBUG explícito.
CORS_ALLOW_ALL_ORIGINS = bool(DEBUG)

# --------------------------
# Seguridad adicional
# --------------------------
# Aseguramos valores seguros por defecto en producción
if not DEBUG:
    # Exigir SECRET_KEY real en producción
    if not os.environ.get("SECRET_KEY") or SECRET_KEY == "django-insecure-change-this-in-production":
        raise Exception("En producción es necesario definir SECRET_KEY en las variables de entorno.")

    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")

    # Forzar HTTPS y HSTS
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() in {"1","true","yes"}
    SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "True").lower() in {"1","true","yes"}
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# En entornos de desarrollo locales se permiten configuraciones menos estrictas
else:
    # Por claridad, si se está en DEBUG dejamos explicítamente estos valores para desarrollo
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = "Lax"

# --------------------------
# Apps
# --------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "corsheaders",
    "rest_framework",
    "django_filters",
    "drf_yasg",
    "axes",
    "simple_history",
    "csp",

    # Local
    "cotizaciones",
]

# --------------------------
# Middleware
# --------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Django-axes middleware para mitigación de fuerza bruta
    "axes.middleware.AxesMiddleware",
    # middleware de historial para registrar cambios en modelos
    "simple_history.middleware.HistoryRequestMiddleware",
    # CSP middleware
    "csp.middleware.CSPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------
# Authentication backends
# --------------------------
# AxesStandaloneBackend is required by django-axes v5+ to perform lockouts.
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# --------------------------
# DRF
# --------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}

# Throttling y límites por defecto para la API
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_CLASSES", (
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
))
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_RATES", {
    "anon": os.environ.get("DRF_THROTTLE_ANON", "20/min"),
    "user": os.environ.get("DRF_THROTTLE_USER", "200/min"),
})

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --------------------------
# URLs / WSGI
# --------------------------
ROOT_URLCONF = "proyecto.urls"
WSGI_APPLICATION = "proyecto.wsgi.application"

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

# --------------------------
# Base de datos
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

elif all(os.environ.get(k) for k in ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")):
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
    raise Exception(
        "No hay configuración de base de datos válida. "
        "Definí DATABASE_URL o DB_NAME/DB_USER/DB_PASSWORD/DB_HOST."
    )

# --------------------------
# Password validators
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
# Static files
# --------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --------------------------
# Media
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
# Messages
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
# Email
# --------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() in {"true", "1", "yes", "on"}
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "GCinsumos <noreply@gcinsumos.com>"
)

# ----------------------------------
# Django-Axes (bloqueo por intentos)
# ----------------------------------
AXES_ENABLED = os.environ.get("AXES_ENABLED", "True").lower() in {"1", "true", "yes"}
AXES_FAILURE_LIMIT = int(os.environ.get("AXES_FAILURE_LIMIT", 5))
AXES_COOLOFF_TIME = int(os.environ.get("AXES_COOLOFF_TIME", 1))  # minutos
    # AXES_ONLY_USER_FAILURES was deprecated in django-axes v5+; do not set it here.
AXES_LOCKOUT_CALLABLE = None
# Template used when a request is locked out by django-axes. Create the template
# at backend/templates/axes/lockout.html (provided in repo changes below). The middleware will
# use this template when a user/IP is locked out.
AXES_LOCKOUT_TEMPLATE = "axes/lockout.html"

# Spanish user-facing messages (used when cooloff enabled/disabled)
AXES_COOLOFF_MESSAGE = os.environ.get(
    "AXES_COOLOFF_MESSAGE",
    "Cuenta bloqueada: se han realizado demasiados intentos de inicio de sesión. Inténtalo de nuevo más tarde."
)
AXES_PERMALOCK_MESSAGE = os.environ.get(
    "AXES_PERMALOCK_MESSAGE",
    "Cuenta bloqueada: contacta al administrador para desbloquearla."
)

# Configure django-axes granularity: lock by username only (no IP lock)
# - AXES_LOCK_OUT_BY_USERNAME: consider only the username for counting failures
# - AXES_LOCK_OUT_BY_IP_ADDRESS: do not lock based on IP
# - AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP: do not require both
# These can be overridden via environment variables if needed.
AXES_LOCK_OUT_BY_USERNAME = os.environ.get("AXES_LOCK_OUT_BY_USERNAME", "True").lower() in {"1", "true", "yes"}
AXES_LOCK_OUT_BY_IP_ADDRESS = os.environ.get("AXES_LOCK_OUT_BY_IP_ADDRESS", "False").lower() in {"1", "true", "yes"}
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = os.environ.get(
    "AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP", "False"
).lower() in {"1", "true", "yes"}

# If you're behind a proxy/load-balancer, ensure AXES inspects the correct header
# Example: AXES_META_PRECEDENCE_ORDER = ['HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
AXES_META_PRECEDENCE_ORDER = os.environ.get(
    "AXES_META_PRECEDENCE_ORDER", "HTTP_X_FORWARDED_FOR,REMOTE_ADDR"
).split(',')

# -------------------------------
# Content Security Policy (CSP) - django-csp 4.x+ format
# Define explicit directives here. Adjust to allow any external CDNs you need.
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
    'script-src': ("'self'", "https://cdn.jsdelivr.net"),
        # Allow external CDN for styles and permit inline styles which are
        # still used by some templates. Also allow Google Fonts resources.
        'style-src': ("'self'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com", "'unsafe-inline'"),
        'img-src': ("'self'", "data:"),
        'font-src': ("'self'", "https://cdn.jsdelivr.net", "https://fonts.gstatic.com"),
        'connect-src': ("'self'",),
    }
}

# In development we allow some inline styles/scripts and external APIs used by the UI.
if DEBUG:
    CONTENT_SECURITY_POLICY['DIRECTIVES'].update({
        # Allow inline styles/scripts in dev to keep existing templates working
        'script-src': ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"),
        'style-src': ("'self'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com", "'unsafe-inline'"),
        'font-src': ("'self'", "https://cdn.jsdelivr.net", "https://fonts.gstatic.com"),
        # Allow client-side fetches to these external services used by the UI
        'connect-src': ("'self'", "https://dolarapi.com", "https://api.open-meteo.com"),
    })
