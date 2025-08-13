#!/usr/bin/env python3
"""
Automated Django Multi-Service Platform Setup Script (MongoDB Version)
This script automates the MongoDB setup process for your Django backend.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json

def run_command(command, description="", check_output=False):
    """Execute a shell command and handle errors"""
    print(f"\n⏳ {description}")
    print(f"Running: {command}")
    
    try:
        if check_output:
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"stdout: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    required = {
        'python': 'python --version',
        'pip': 'pip --version',
        'mongodb': 'mongod --version',
        'redis': 'redis-server --version'
    }
    
    missing = []
    for name, command in required.items():
        if not run_command(command, f"Checking {name}"):
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing required software: {', '.join(missing)}")
        print("\n📋 Installation instructions:")
        
        if 'mongodb' in missing:
            print("MongoDB:")
            print("  Ubuntu/Debian: sudo apt-get install -y mongodb-org")
            print("  macOS: brew install mongodb-community")
            print("  Windows: Download from https://www.mongodb.com/try/download/community")
            print("  Cloud: Use MongoDB Atlas (https://www.mongodb.com/atlas)")
        
        if 'redis' in missing:
            print("Redis:")
            print("  Ubuntu/Debian: sudo apt-get install redis-server")
            print("  macOS: brew install redis")
            print("  Windows: Download from https://github.com/microsoftarchive/redis/releases")
        
        return False
    
    print("✅ All prerequisites are installed!")
    return True

def check_mongodb_connection():
    """Check if MongoDB is running and accessible"""
    print("🔗 Testing MongoDB connection...")
    
    try:
        # Try to connect to MongoDB
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible!")
        return True
    except ImportError:
        print("⚠️ PyMongo not installed yet, will install with requirements")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n💡 Solutions:")
        print("1. Start MongoDB service: sudo systemctl start mongod")
        print("2. Or use MongoDB Atlas cloud service")
        print("3. Check MongoDB configuration")
        return False

def create_project_structure():
    """Create the Django project structure"""
    print("\n🏗️ Creating project structure...")
    
    # Create main project directory structure
    directories = [
        # 'multiservice_platform',
        'apps',
        'apps/accounts',
        'apps/food_service',
        'apps/grocery_service', 
        'apps/travel_service',
        'apps/shopping_service',
        'apps/vendor_management',
        'apps/payment_service',
        'apps/notifications',
        'apps/analytics',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'media',
        'media/uploads',
        'templates',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create __init__.py files for Python packages
        # if directory.startswith('apps'):
        #     init_file = Path(directory) / '__init__.py'
        #     init_file.touch()
    
    print("✅ Project structure created successfully!")
    return True

def create_virtual_environment():
    """Create and setup virtual environment"""
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    # Determine activation script and pip command based on OS
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\python.exe -m pip"
        python_command = "venv\\Scripts\\python"
    else:  # Unix-like (Linux, macOS)
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    # Upgrade pip in virtual environment
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        return False
    
    print("✅ Virtual environment created successfully!")
    print(f"💡 To activate it, run: {activate_script}")
    return True

def install_mongodb_requirements():
    """Install MongoDB-specific Python packages"""
    print("\n📦 Installing MongoDB requirements...")
    
    pip_command = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    # Essential MongoDB packages
    mongodb_packages = [
        "Django==4.2.15",
        "mongoengine==0.27.0",
        "django-mongoengine==0.5.4",
        "pymongo==4.5.0",
        "djangorestframework==3.14.0",
        "djangorestframework-mongoengine==3.4.1",
        "django-cors-headers==4.3.1",
        "djangorestframework-simplejwt==5.3.0",
        "python-decouple==3.8",
        "drf-yasg==1.21.7",
        "Pillow==10.0.0",
        "redis==4.6.0",
        "celery==5.3.2",
        "channels==4.0.0",
        "channels-redis==4.1.0"
    ]
    
    for package in mongodb_packages:
        if not run_command(f"{pip_command} install {package}", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing with others...")
    
    print("✅ Core MongoDB packages installed!")
    return True

def setup_mongodb_database():
    """Setup MongoDB database and initial configuration"""
    print("\n🗄️ Setting up MongoDB database...")
    
    try:
        import pymongo
        
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        
        # Create database
        db = client['multiservice_platform']
        
        # Create initial collections
        collections = ['users', 'restaurants', 'products', 'orders', 'user_sessions']
        for collection in collections:
            db.create_collection(collection, check_exists=False)
        
        # Create geospatial indexes
        db.users.create_index([("current_location", pymongo.GEOSPHERE)])
        db.restaurants.create_index([("location", pymongo.GEOSPHERE)])
        db.orders.create_index([("delivery_location", pymongo.GEOSPHERE)])
        
        # Create text indexes for search
        db.restaurants.create_index([("name", pymongo.TEXT), ("cuisine_types", pymongo.TEXT)])
        db.products.create_index([("name", pymongo.TEXT), ("description", pymongo.TEXT)])
        
        # Create other useful indexes
        db.users.create_index("email")
        db.users.create_index("phone_number") 
        db.orders.create_index("user_id")
        db.orders.create_index("created_at")
        
        print("✅ MongoDB database and indexes created successfully!")
        return True
        
    except ImportError:
        print("⚠️ PyMongo not available yet, will be configured later")
        return True
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        print("💡 You can set up the database manually later")
        return True

def create_django_project():
    """Create Django project structure"""
    python_command = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    
    # Create Django project
    if not run_command(f"{python_command} -m django startproject multiservice_platform .", 
                      "Creating Django project"):
        return False
    
    # Create Django apps
    apps = [
        'accounts', 'food_service', 'grocery_service', 'travel_service',
        'shopping_service', 'vendor_management', 'payment_service', 
        'notifications', 'analytics'
    ]
    
    for app in apps:
        if not run_command(f"{python_command} manage.py startapp {app} apps/{app}", 
                          f"Creating {app} app"):
            return False
    
    print("✅ Django project and apps created successfully!")
    return True

def create_configuration_files():
    """Create essential configuration files"""
    print("\n📄 Creating MongoDB configuration files...")
    
    # Create .env file
    env_content = """# MongoDB Multi-Service Platform Configuration
# Copy and modify these values for your setup

# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-mongodb-version
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Configuration
MONGODB_DB_NAME=multiservice_platform
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=
MONGODB_PASSWORD=

# For MongoDB Atlas (Cloud):
# MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/multiservice_platform

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Keys (get these from respective services)
RAZORPAY_API_KEY=your_razorpay_key_here
RAZORPAY_API_SECRET=your_razorpay_secret_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
FIREBASE_SERVER_KEY=your_firebase_key_here

# Email Configuration
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Create .gitignore
    gitignore_content = """# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
media/

# Virtual Environment
venv/
env/

# Environment variables
.env

# MongoDB dumps
dump/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Static files
/static/
/staticfiles/

# Logs
logs/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    # Create initial settings.py content
    settings_content = '''"""
MongoDB Multi-Service Platform Settings
"""
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
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'django_mongoengine',
    
    # Local apps
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

# MongoDB Configuration
mongoengine.connect(
    db=config('MONGODB_DB_NAME', default='multiservice_platform'),
    host=config('MONGODB_HOST', default='localhost'),
    port=config('MONGODB_PORT', default=27017, cast=int),
    username=config('MONGODB_USERNAME', default=''),
    password=config('MONGODB_PASSWORD', default=''),
)

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
'''
    
    # Write to settings file
    settings_path = Path('multiservice_platform/settings.py')
    if settings_path.exists():
        with open(settings_path, 'w') as f:
            f.write(settings_content)
    
    print("✅ Configuration files created successfully!")
    return True

def create_database_init_script():
    """Create MongoDB initialization script"""
    mongodb_script = '''#!/bin/bash
# MongoDB Database Initialization Script

echo "🗄️ Initializing MongoDB for Multi-Service Platform..."

# Start MongoDB service
echo "Starting MongoDB service..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start mongod
elif command -v brew &> /dev/null; then
    brew services start mongodb-community
fi

# Wait for MongoDB to start
sleep 3

echo "Creating database and indexes..."
mongosh multiservice_platform --eval "
// Create collections
db.createCollection('users');
db.createCollection('restaurants'); 
db.createCollection('products');
db.createCollection('orders');

// Create geospatial indexes
db.users.createIndex({ 'current_location': '2dsphere' });
db.restaurants.createIndex({ 'location': '2dsphere' });
db.orders.createIndex({ 'delivery_location': '2dsphere' });

// Create text search indexes
db.restaurants.createIndex({ 'name': 'text', 'cuisine_types': 'text' });
db.products.createIndex({ 'name': 'text', 'description': 'text' });

// Create other indexes
db.users.createIndex({ 'email': 1 });
db.users.createIndex({ 'phone_number': 1 });
db.orders.createIndex({ 'user_id': 1 });
db.orders.createIndex({ 'created_at': 1 });

print('✅ MongoDB database initialized successfully!');
"

echo "✅ MongoDB setup completed!"
'''
    
    with open('init_mongodb.sh', 'w', encoding='utf-8') as f:
        f.write(mongodb_script)
    
    os.chmod('init_mongodb.sh', 0o755)
    print("✅ MongoDB initialization script created!")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*70)
    print("🎉 DJANGO + MONGODB SETUP COMPLETED SUCCESSFULLY! 🎉")
    print("="*70)
    
    activation_cmd = "venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"
    
    print(f"""
📋 NEXT STEPS:

1. 🔧 ACTIVATE VIRTUAL ENVIRONMENT:
   {activation_cmd}

2. 🗄️ ENSURE MONGODB IS RUNNING:
   • Ubuntu/Linux: sudo systemctl start mongod
   • macOS: brew services start mongodb-community
   • Windows: Start MongoDB service
   • Cloud: Use MongoDB Atlas connection string

3. ⚙️ CONFIGURE ENVIRONMENT:
   • Edit .env file with your MongoDB credentials
   • Add API keys for Razorpay, Google Maps, etc.

4. 🔧 INSTALL REMAINING PACKAGES:
   pip install -r requirements-mongodb.txt

5. 📊 INITIALIZE DATABASE:
   ./init_mongodb.sh
   # OR manually run the MongoDB setup commands

6. 🚀 START DEVELOPMENT SERVER:
   python manage.py runserver

7. ✅ TEST YOUR MONGODB SETUP:
   • Visit: http://127.0.0.1:8000/admin/
   • Test API: http://127.0.0.1:8000/api/v1/
   • MongoDB connection: python -c "import mongoengine; mongoengine.connect('multiservice_platform')"

📁 MONGODB PROJECT STRUCTURE:
   • Documents: Use MongoEngine instead of Django models
   • Geospatial: Built-in location queries
   • Flexible Schema: JSON-like document structure
   • Aggregation: Powerful analytics queries

🔗 MONGODB FEATURES FOR YOUR PLATFORM:
   • Geospatial queries for delivery services
   • Flexible schema for different service types
   • Horizontal scaling for growing business
   • Real-time performance for order tracking
   • Text search for restaurants and products

💡 DEVELOPMENT TIPS:
   • Use MongoEngine documents instead of Django models
   • Leverage geospatial indexes for location-based features
   • Use aggregation pipelines for analytics
   • Take advantage of flexible document structure
   • Use GridFS for large file storage

🔍 TESTING MONGODB:
   • MongoDB Shell: mongosh multiservice_platform
   • View collections: db.getCollectionNames()
   • Test queries: db.users.find().pretty()
   • Check indexes: db.users.getIndexes()

📚 DOCUMENTATION:
   • MongoDB: https://docs.mongodb.com/
   • MongoEngine: http://mongoengine.org/
   • Django + MongoDB: Check mongodb-setup-guide.md

❓ NEED HELP?
   • MongoDB Community: https://community.mongodb.com/
   • MongoEngine Docs: http://docs.mongoengine.org/
   • Django REST + MongoDB examples in the guide
""")

def main():
    """Main setup function for MongoDB version"""
    print("🚀 Django Multi-Service Platform Setup (MongoDB Version)")
    print("=" * 65)
    print("🗄️ This setup uses MongoDB for flexible, scalable data storage")
    print("=" * 65)
    
    # Check if we're in the right directory
    if os.path.exists('multiservice_platform'):
        print("❌ Directory 'multiservice_platform' already exists!")
        print("Please run this script in an empty directory or remove the existing directory.")
        return False
    
    # Run setup steps
    steps = [
        # ("Checking prerequisites", check_prerequisites),
        # ("Testing MongoDB connection", check_mongodb_connection),
        ("Creating project structure", create_project_structure),
        # ("Creating virtual environment", create_virtual_environment),
        # ("Installing MongoDB requirements", install_mongodb_requirements),
        ("Creating Django project", create_django_project),
        ("Setting up MongoDB database", setup_mongodb_database),
        ("Creating configuration files", create_configuration_files),
        ("Creating database init script", create_database_init_script)
    ]
    
    for description, function in steps:
        print(f"\n{'='*70}")
        print(f"🔄 {description.upper()}")
        print('='*70)
        
        if not function():
            print(f"\n❌ Setup failed at: {description}")
            print("Please check the errors above and run the script again.")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)