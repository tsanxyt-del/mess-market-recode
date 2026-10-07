"""Django settings for mess-market-management."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

_allowed = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
# Render auto-hostname (RENDER_EXTERNAL_HOSTNAME) ko allow karo taaki
# render.yaml me har bar domain likhna na pade.
for _env_host in (os.getenv("RENDER_EXTERNAL_HOSTNAME", ""),):
    _env_host = (_env_host or "").strip()
    if _env_host and _env_host not in _allowed:
        _allowed.append(_env_host)
ALLOWED_HOSTS = _allowed

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "apps.market",
    "apps.items",
    "apps.reports",
    "apps.uploads",
    "apps.dashboard",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.StealthAdminMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "config.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Relational DB only for Django auth/sessions (admin users). Business data lives in MongoDB.
# Render: DATABASE_URL set ho to Postgres, warna SQLITE_PATH (/var/data disk) ya local sqlite.
_DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
_SQLITE_PATH = os.getenv("SQLITE_PATH", "").strip()
if _DATABASE_URL:
    try:
        import dj_database_url  # type: ignore
        DATABASES = {"default": dj_database_url.parse(_DATABASE_URL, conn_max_age=600)}
    except ImportError:
        raise RuntimeError("DATABASE_URL set hai par `dj-database-url` installed nahi. requirements.txt install karo.")
elif _SQLITE_PATH:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(_SQLITE_PATH),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# WhiteNoise: hashed names nahi (templates me /static/ paths hardcoded hain),
# sirf compression + cache headers.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
_media_root = os.getenv("MEDIA_ROOT", "media")
if os.path.isabs(_media_root) or _media_root.startswith("/"):
    MEDIA_ROOT = Path(_media_root)
else:
    MEDIA_ROOT = BASE_DIR / _media_root

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/panel/"
LOGOUT_REDIRECT_URL = "/"

# ---- Stealth admin ----
# Public templates must NOT link to these. Obscure the raw Django admin
# via env so scanners hitting /django-admin/ find nothing.
# Example .env: DJANGO_ADMIN_PATH=mgmt-x7q2/
DJANGO_ADMIN_PATH = os.getenv("DJANGO_ADMIN_PATH", "django-admin/")

# ---- App version ----
APP_VERSION = "4.6"
# ---- MongoDB ----
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "mess_market_db")

# ---- Uploads ----
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(5 * 1024 * 1024)))
ALLOWED_BILL_EXTENSIONS = [e.strip().lower() for e in os.getenv("ALLOWED_BILL_EXTENSIONS", "jpg,jpeg,png,webp,pdf").split(",")]

# ---- Security ----
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # JS needs to read csrftoken cookie via getCookie()
X_FRAME_OPTIONS = "DENY"
# Render/Heroku-style TLS-terminating proxy ke peeche sahi scheme detect karo.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
_csrf_origins = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
_render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
if _render_host:
    _auto_origin = f"https://{_render_host}"
    if _auto_origin not in _csrf_origins:
        _csrf_origins.append(_auto_origin)
if not _csrf_origins and not DEBUG:
    # Render default: allow *.onrender.com when env not set.
    _csrf_origins = ["https://*.onrender.com"]
CSRF_TRUSTED_ORIGINS = _csrf_origins
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
