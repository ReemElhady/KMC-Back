import os
import sentry_sdk


from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")


def strip_list(line):
    return [value.strip() for value in line.split(",") if value.strip()]


CSRF_TRUSTED_ORIGINS = strip_list(os.environ.get("CSRF_TRUSTED_ORIGINS"))
if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
    CSRF_TRUSTED_ORIGINS.append("http://localhost")
else:
    CORS_ALLOWED_ORIGINS = strip_list(os.environ.get("CORS_ALLOWED_ORIGINS"))


SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", False) == "True"
)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 60))
SECURE_CONTENT_TYPE_NOSNIFF = (
    os.environ.get("SECURE_CONTENT_TYPE_NOSNIFF", False) == "True"
)
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", False) == "True"
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", False) == "True"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", False) == "True"
SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", False) == "True"

# Max Data Upload
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

THIRD_PARTY_APPS = [
    "rest_framework_simplejwt",
    "corsheaders",
    "rest_framework",
    "translations",
    "django_filters",
    "nested_inline",
    "django_crontab",
]

LOCAL_APPS = [
    "contact_us",
    "about_us",
    "product",
    "user",
    "courses",
    "cart",
    "coupon",
    "general",
    "points",
    "order",
    "article",
    "home",
    "footer",
    "FAQ",
    "offers",
    "smsa",
    "common",
]

# Application definition
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

AUTH_USER_MODEL = "user.User"


ROOT_URLCONF = "kmc_back.urls"


WSGI_APPLICATION = "kmc_back.wsgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"

LANGUAGES = (  # supported languages
    ("en", "English"),
    ("ar", "Arabic"),
)
TIME_ZONE = "Africa/Cairo"

USE_I18N = True

USE_L10N = True

USE_TZ = True

ORDER_EXPIRES_AFTER_IN_HOURS = 5

# Media Files
MEDIA_URL = "media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "kmc_back/media")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Static Files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = "static"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Front-end Integration
FRONT_URL = os.environ.get("FRONT_URL")
BACKEND_URL = os.environ.get("BACKEND_URL")

DJANGO_RESIZED_DEFAULT_SIZE = [1920, 1080]


# WASAGE Credentials
WASAGE_USER = os.environ.get("WASAGE_USER")
WASAGE_PASSWORD = os.environ.get("WASAGE_PASSWORD")
WASAGE_SECRET = os.environ.get("WASAGE_SECRET")

# Celery
REDIS_HOST_LOCATION = os.environ.get("REDIS_HOST_LOCATION", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_DB_NUMBER = os.environ.get("REDIS_DB_NUMBER", "0")
REDIS_LOCATION = f"redis://{REDIS_HOST_LOCATION}:{REDIS_PORT}/{REDIS_DB_NUMBER}"

CELERY_BROKER_URL = REDIS_LOCATION
CELERY_RESULT_BACKEND = REDIS_LOCATION
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


sentry_sdk.init(
    dsn="https://513fd8076ef1a85f40f35b98882d6b15@o4507362125414400.ingest.de.sentry.io/4507362130133072",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    # profiles_sample_rate=1.0,
)