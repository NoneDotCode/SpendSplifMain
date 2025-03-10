import os
from datetime import timedelta

import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
env = environ.Env(
    DEBUG=(bool, False)
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production


# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = os.environ.get("SECRET_KEY")
def get_debug_setting():
    debug_str = os.environ.get('DEBUG', 'True')  
    return debug_str.lower() != 'false'  

DEBUG = get_debug_setting()

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    'dj_rest_auth',
    "rest_framework.authtoken",
    "corsheaders",
    # Celery
    "celery",
    "django_celery_results",
    "django_celery_beat",
    # Modules
    "drf_multiple_model",
    # Custom apps
    "colorfield",
    "apps.customuser",
    "apps.space",
    "apps.account",
    "apps.category",
    "apps.history",
    "apps.converter",
    "apps.total_balance",
    "apps.goal",
    "apps.spend",
    "apps.transfer",
    "apps.cryptocurrency",
    "apps.api_stocks",
    "apps.messenger",
    "apps.Dowt",
    "apps.notifications",
    "apps.tickets",
    "apps.store",
    "apps.community",
    "apps.tink",
    "apps.cards",
    'apps.adminpanel',
    "apps.excel"
]

STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_STANDARD_PRICE_ID = os.environ.get('STRIPE_STANDARD_PRICE_ID')
STRIPE_PREMIUM_PRICE_ID = os.environ.get('STRIPE_PREMIUM_PRICE_ID')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Custom user model auth

AUTH_USER_MODEL = "customuser.CustomUser"

FINAPI_CLIENT_ID = os.environ.get('FINAPI_CLIENT_ID')
FINAPI_CLIENT_SECRET = os.environ.get('FINAPI_CLIENT_SECRET')


MIDDLEWARE = [
    'backend.config.middleware.UpdateSpaceLastModifiedMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "backend.config.middleware.UserAgentMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="spendsplif"),
        "USER": env("POSTGRES_USER", default="postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="default_password"),
        "HOST": env("POSTGRES_HOST", default="db"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}


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

TIME_ZONE = "UTC"

USE_I18N = True

DATE_FORMAT = 'Y-m-d'  # ISO 8601 format

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}


# jwt

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=15),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),


    # custom
    'REFRESH_TOKEN_COOKIE_NAME': 'refresh',
    'REFRESH_TOKEN_COOKIE_OPTIONS': {
        'max_age': 604800,
        'httponly': True,
        'samesite': "None",
        'secure': True,
        'path': '/',
        },

    # A string like "example.com", or None for standard domain cookie.
    'AUTH_COOKIE_DOMAIN': None,
}

# Cors


CORS_ALLOWED_ORIGINS = [
    "https://spendsplif.com",
    "https://api.spendsplif.com"
]
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTP_ONLY = True
CSRF_TRUSTED_ORIGINS = [
    "https://spendsplif.com",
    "https://api.spendsplif.com"
]
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"
CORS_ORIGIN_WHITELIST = [
    "https://spendsplif.com",
    "https://api.spendsplif.com"
]

# Security headers
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# X_FRAME_OPTIONS = "DENY"  # Prevent clickjacking

# # Rate limiting (e.g., using Django Ratelimit or DRF extensions)
# REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
#     'rest_framework.throttling.UserRateThrottle',
# ]
# REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
#     'user': '8000/day',
# }

# SQL Injection prevention is handled by Django ORM automatically.

# Celery

CELERY_TIMEZONE = "UTC"
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

# Email settings

SITE_ID = 2

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True

EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER


# Anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Google Auth

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID")

# Custom variables

BASE_BACKEND_URL = env('BASE_BACKEND_URL', default='http://localhost:8000')
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')
MOBILE_APP_ACTUAL_VERSION = "0.0.1"

SUBSCRIBES_DATA = {
    "Standard": {
        "price": "10€",
        "period": "Month ~+2 weeks~"
    },
    "Premium": {
        "price": "20€",
        "period": "Month ~+2 weeks~"
    }
}

EXPO_APP_KEY = os.environ.get("EXPO_APP_KEY")

# For Tink sync

TINK = {
    "CLIENT_ID": os.environ.get("TINK_CLIENT_ID"),
    "CLIENT_SECRET": os.environ.get("TINK_CLIENT_SECRET"),
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
