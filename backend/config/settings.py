import os
from datetime import timedelta

import dj_database_url
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
env = environ.Env()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
environ.Env.read_env(os.path.join(BASE_DIR, "dev.env"))


# Quick-start development settings - unsuitable for production


# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG")


ALLOWED_HOSTS = ["*"]


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
    "apps.store",
    "apps.community",
    "apps.tink",
    'apps.adminpanel',
    "apps.excel"
]

# Custom user model auth

AUTH_USER_MODEL = "customuser.CustomUser"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env.int("DB_PORT"),
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
        'samesite': 'Lax',
        'secure': False,
        'path': '/',
        },

    # A string like "example.com", or None for standard domain cookie.
    'AUTH_COOKIE_DOMAIN': None,
}

# Cors

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5473",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTP_ONLY = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5473",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5473",
    "http://127.0.0.1:8000",
    ]
SESSION_COOKIE_SAMESITE = "Lax"
CORS_ORIGIN_WHITELIST = [
    "http://localhost:5173",
    "http://localhost:5473",
    "http://127.0.0.1:8000",
]

# Celery

CELERY_TIMEZONE = "UTC"
CELERY_BROKER_URL = "redis://redis:6379/0"  # "redis://127.0.0.1:6379" if not in docker
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "django-db"

# Email settings

SITE_ID = 2

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True

EMAIL_HOST_USER = "spendsplif@gmail.com"
EMAIL_HOST_PASSWORD = env("EMAIL_SECRET_KEY")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER


# Anthropic

ANTHROPIC_API_KEY = ("sk-ant-api03-mqBtIiFrvSAz50MNcvXzodCEa7GRnv6Q0DGZr6scuTd1_CmXk4rpm6jtytSjrMvpCic_lvKSLpQ36tSny-"
                     "GKEg-UE6i-QAA")

# Google Auth

GOOGLE_CLIENT_ID = "1002186527863-pd1c9naj1kt8hq6cogg80kn3nl4d9vjf.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_PROJECT_ID = "spendsplif-000001"

# Custom variables

BASE_BACKEND_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:5173'
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

STRIPE = {
    "secret": 'sk_test_51OaEz8J4gLcb8EJ9VXMBzxR8ShD3GIV7VgDx0fMxJx7Fnos3TbJKID1bSQPJGQMMLjh0SXt3NqCtNdOOOSNHc75k00LMdADPfK',
    "payment_callback_url": "localhost:8000/api/v1/store/payment/callback/",
    "publishableKey": "pk_test_51OaEz8J4gLcb8EJ9pAxoRfVd7FO61QmZCApJJKnkzwad9IPBXlES7pnOQeOp6el6D2W8inRzmWQkWCR9NNIrNxh800O6IQOFEP",
    "webhook_secret_key": "whsec_1pEYQFoMLQf1OxA12IgZ4M9LUdv4X151"
}

EXPO_APP_KEY = "d142c3a6-34df-4c3e-993e-fa14fa88d94f"

# For Tink sync

TINK = {
    "CLIENT_ID": "df402ff180c743fe988144ac9623c0dd",
    "CLIENT_SECRET": "52e1e6441ecf4e50ba1f0fa92fe586fe"
}
