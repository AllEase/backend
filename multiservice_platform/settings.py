# """
# MongoDB Multi-Service Platform Settings
# """
import os
from pathlib import Path
from decouple import config
import datetime
from mongoengine import connect


SECRET_KEY = 'qwertyuiopqwertyuiop'
JWT_EXPIRATION_SECONDS = 3600
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "192.168.0.7"
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    # 'apps.food_service.apps.FoodServiceConfig',
    # 'apps.grocery_service.apps.GroceryServiceConfig',
    # 'apps.travel_service.apps.TravelServiceConfig',
    # 'apps.shopping_service.apps.ShoppingServiceConfig',
    # 'apps.vendor_management.apps.VendorManagementConfig',
    # 'apps.payment_service.apps.PaymentServiceConfig',
    # 'apps.notifications.apps.NotificationsConfig',
    # 'apps.analytics.apps.AnalyticsConfig',
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

connect(
    db="testDB",
    host="mongodb+srv://allease2025:1122334455@allease.rvbltg5.mongodb.net/?retryWrites=true&w=majority&appName=allease",
)

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True
LANGUAGE_CODE = 'en-us'


# REST Framework
REST_FRAMEWORK = {
     'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
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
