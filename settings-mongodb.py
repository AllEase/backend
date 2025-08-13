"""
Django settings for Multi-Service Platform (MongoDB Version)
"""
import os
import mongoengine
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',  # API Documentation
    'channels',  # WebSocket support
    'django_celery_beat',  # Periodic tasks
    'phonenumber_field',  # Phone number validation
    'django_mongoengine',  # MongoDB integration
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.food_service',
    'apps.grocery_service',
    'apps.travel_service', 
    'apps.shopping_service',
    'apps.vendor_management',
    'apps.payment_service',
    'apps.notifications',
    'apps.analytics',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'multiservice_platform.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'multiservice_platform.wsgi.application'
ASGI_APPLICATION = 'multiservice_platform.asgi.application'

# MongoDB Configuration
MONGODB_SETTINGS = {
    'db': config('MONGODB_DB_NAME', default='multiservice_platform'),
    'host': config('MONGODB_HOST', default='localhost'),
    'port': config('MONGODB_PORT', default=27017, cast=int),
    'username': config('MONGODB_USERNAME', default=''),
    'password': config('MONGODB_PASSWORD', default=''),
    'authentication_source': config('MONGODB_AUTH_SOURCE', default='admin'),
    'connect': False,  # Don't connect on import
}

# Connect to MongoDB using MongoEngine
try:
    mongoengine.connect(**MONGODB_SETTINGS)
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# Alternative: Using djongo (Django + MongoDB)
# Uncomment this if you prefer djongo over mongoengine
# DATABASES = {
#     'default': {
#         'ENGINE': 'djongo',
#         'NAME': config('MONGODB_DB_NAME', default='multiservice_platform'),
#         'CLIENT': {
#             'host': f"mongodb://{config('MONGODB_HOST', default='localhost')}:{config('MONGODB_PORT', default=27017)}",
#             'username': config('MONGODB_USERNAME', default=''),
#             'password': config('MONGODB_PASSWORD', default=''),
#             'authSource': config('MONGODB_AUTH_SOURCE', default='admin'),
#             'authMechanism': 'SCRAM-SHA-1',
#         }
#     }
# }

# Fallback SQLite database for Django's built-in apps
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Redis Configuration for Caching and Channels
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Channel Layers for WebSocket
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Password validation (for Django's built-in auth)
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (will use GridFS for large files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# GridFS Configuration for MongoDB file storage
GRIDFS_SETTINGS = {
    'collection': 'fs',
    'host': MONGODB_SETTINGS['host'],
    'port': MONGODB_SETTINGS['port'],
    'db': MONGODB_SETTINGS['db'],
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MongoEngine User Authentication
MONGOENGINE_USER_DOCUMENT = 'apps.accounts.documents.User'
SESSION_ENGINE = 'django_mongoengine.sessions'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vue dev server
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# Payment Gateway Configuration
RAZORPAY_API_KEY = config('RAZORPAY_API_KEY', default='')
RAZORPAY_API_SECRET = config('RAZORPAY_API_SECRET', default='')

# Firebase Configuration for Push Notifications
FIREBASE_SERVER_KEY = config('FIREBASE_SERVER_KEY', default='')

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@multiservice.com')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'mongoengine': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Security Settings for Production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# API Documentation Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Custom Settings for Multi-Service Platform
PLATFORM_SETTINGS = {
    'DELIVERY_RADIUS_KM': 10,  # Maximum delivery radius in kilometers
    'DEFAULT_COMMISSION_RATE': 0.15,  # 15% commission rate
    'MIN_ORDER_VALUE': 100,  # Minimum order value in INR
    'FREE_DELIVERY_THRESHOLD': 300,  # Free delivery above this amount
    'MAX_DELIVERY_TIME_MINUTES': 60,  # Maximum delivery time promise
    'SUPPORTED_PAYMENT_METHODS': ['razorpay', 'cod', 'wallet'],
    'DEFAULT_CURRENCY': 'INR',
    'BUSINESS_HOURS': {
        'start': '06:00',
        'end': '23:00'
    },
    'VENDOR_ONBOARDING_FEE': 500,  # One-time vendor registration fee
}

# Google Maps API Key for location services
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# MongoDB Indexing Configuration
MONGODB_INDEXES = {
    'accounts': [
        ('email', 1),
        ('phone_number', 1),
        ('location', '2dsphere'),
        ('user_type', 1),
    ],
    'food_service': [
        ('restaurant_id', 1),
        ('category', 1),
        ('location', '2dsphere'),
        ('status', 1),
    ],
    'orders': [
        ('user_id', 1),
        ('status', 1),
        ('created_at', -1),
        ('delivery_location', '2dsphere'),
    ]
}

# Development Settings
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    
    # Create logs directory if it doesn't exist
    logs_dir = BASE_DIR / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Development MongoDB settings
    MONGODB_SETTINGS.update({
        'connect': True,
        'maxPoolSize': 10,
        'minPoolSize': 1,
        'maxIdleTimeMS': 30000,
        'waitQueueTimeoutMS': 5000,
    })

# MongoDB Connection Testing
def test_mongodb_connection():
    """Test MongoDB connection on startup"""
    try:
        from mongoengine import connection
        db = connection.get_db()
        # Simple ping to test connection
        db.command('ping')
        print("✅ MongoDB connection test passed!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection test failed: {e}")
        return False

# Run connection test if not in testing mode
if not any(test_arg in sys.argv for test_arg in ['test', 'collectstatic']):
    import sys
    if 'runserver' in sys.argv or 'shell' in sys.argv:
        test_mongodb_connection()