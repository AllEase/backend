# """
# MongoDB Multi-Service Platform Settings
# """
import os
import mongoengine
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
#     # Third party apps
#     # 'rest_framework',
#     # 'corsheaders',
#     # 'drf_yasg',
#     # 'django_mongoengine',
    
    # Local apps
    'apps.accounts.apps.AccountsConfig',
    'apps.food_service.apps.FoodServiceConfig',
    'apps.grocery_service.apps.GroceryServiceConfig',
    'apps.travel_service.apps.TravelServiceConfig',
    'apps.shopping_service.apps.ShoppingServiceConfig',
    'apps.vendor_management.apps.VendorManagementConfig',
    'apps.payment_service.apps.PaymentServiceConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.analytics.apps.AnalyticsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'multiservice_platform.urls'
WSGI_APPLICATION = 'multiservice_platform.wsgi.application'


# # MongoDB Configuration
# mongoengine.connect(
#     db=config('MONGODB_DB_NAME', default='multiservice_platform'),
#     host=config('MONGODB_HOST', default='localhost'),
#     port=config('MONGODB_PORT', default=27017, cast=int),
#     username=config('MONGODB_USERNAME', default=''),
#     password=config('MONGODB_PASSWORD', default=''),
# )

# Use SQLite for Django's built-in apps
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True
LANGUAGE_CODE = 'en-us'


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # You can add template directories here if needed
        'APP_DIRS': True,  # Enables loading templates from each app's templates/ folder
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # required for admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
