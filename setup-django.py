#!/usr/bin/env python3
"""
Automated Django Multi-Service Platform Setup Script
This script automates the initial setup process for your Django backend.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """Execute a shell command and handle errors"""
    print(f"\n⏳ {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {description} completed successfully")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    required = {
        'python': 'python --version',
        'pip': 'pip --version',
        'postgresql': 'psql --version',
        'redis': 'redis-server --version'
    }
    
    missing = []
    for name, command in required.items():
        if not run_command(command, f"Checking {name}"):
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing required software: {', '.join(missing)}")
        print("Please install the missing software and run this script again.")
        return False
    
    print("✅ All prerequisites are installed!")
    return True

def create_project_structure():
    """Create the Django project structure"""
    print("\n🏗️ Creating project structure...")
    
    # Create main project directory structure
    directories = [
        'multiservice_platform',
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
        if directory.startswith('apps'):
            init_file = Path(directory) / '__init__.py'
            init_file.touch()
    
    print("✅ Project structure created successfully!")

def create_virtual_environment():
    """Create and setup virtual environment"""
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
    else:  # Unix-like (Linux, macOS)
        activate_script = "source venv/bin/activate"
        pip_command = "venv/bin/pip"
    
    # Upgrade pip in virtual environment
    if not run_command(f"{pip_command} install --upgrade pip", "Upgrading pip"):
        return False
    
    print("✅ Virtual environment created successfully!")
    print(f"To activate it, run: {activate_script}")
    return True

def install_django_and_create_project():
    """Install Django and create the project"""
    pip_command = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    python_command = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python"
    
    # Install Django
    if not run_command(f"{pip_command} install Django==4.2.15", "Installing Django"):
        return False
    
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

def create_essential_files():
    """Create essential configuration files"""
    print("\n📄 Creating essential configuration files...")
    
    # Create .env.example file
    env_content = """# Environment Configuration Template
# Copy this file to .env and fill in your actual values

SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=multiservice_platform
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

RAZORPAY_API_KEY=your_razorpay_key
RAZORPAY_API_SECRET=your_razorpay_secret
"""
    
    with open('.env.example', 'w') as f:
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

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Static files
/static/
/staticfiles/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Essential configuration files created!")

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python requirements...")
    
    pip_command = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    if Path('requirements.txt').exists():
        return run_command(f"{pip_command} install -r requirements.txt", 
                          "Installing requirements from requirements.txt")
    else:
        # Install basic packages
        basic_packages = [
            "Django==4.2.15",
            "djangorestframework==3.14.0",
            "django-cors-headers==4.3.1",
            "djangorestframework-simplejwt==5.3.0",
            "python-decouple==3.8",
            "drf-yasg==1.21.7",
            "Pillow==10.0.0",
            "redis==4.6.0"
        ]
        
        for package in basic_packages:
            if not run_command(f"{pip_command} install {package}", f"Installing {package}"):
                return False
        
        print("✅ Basic packages installed successfully!")
        return True

def create_database_setup_script():
    """Create database setup script"""
    db_script = """-- PostgreSQL Database Setup Script
-- Run this script in PostgreSQL as superuser

-- Create user
CREATE USER multiservice_user WITH PASSWORD 'your_secure_password';

-- Create database
CREATE DATABASE multiservice_platform OWNER multiservice_user;

-- Connect to database
\\c multiservice_platform;

-- Enable PostGIS extension
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE multiservice_platform TO multiservice_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO multiservice_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO multiservice_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO multiservice_user;

-- Create schema for different services (optional)
CREATE SCHEMA IF NOT EXISTS food_service;
CREATE SCHEMA IF NOT EXISTS grocery_service;
CREATE SCHEMA IF NOT EXISTS travel_service;
CREATE SCHEMA IF NOT EXISTS shopping_service;

-- Grant schema privileges
GRANT ALL ON SCHEMA food_service TO multiservice_user;
GRANT ALL ON SCHEMA grocery_service TO multiservice_user;
GRANT ALL ON SCHEMA travel_service TO multiservice_user;
GRANT ALL ON SCHEMA shopping_service TO multiservice_user;
"""
    
    with open('database_setup.sql', 'w') as f:
        f.write(db_script)
    
    print("✅ Database setup script created: database_setup.sql")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 DJANGO SETUP COMPLETED SUCCESSFULLY! 🎉")
    print("="*60)
    
    activation_cmd = "venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"
    
    print(f"""
📋 NEXT STEPS:

1. 🔧 ACTIVATE VIRTUAL ENVIRONMENT:
   {activation_cmd}

2. 🗄️ SET UP DATABASE:
   • Start PostgreSQL service
   • Run: sudo -u postgres psql
   • Execute the commands in database_setup.sql
   
3. ⚙️ CONFIGURE ENVIRONMENT:
   • Copy .env.example to .env
   • Fill in your database and API credentials
   
4. 📊 CREATE DATABASE TABLES:
   python manage.py makemigrations
   python manage.py migrate
   
5. 👤 CREATE SUPERUSER:
   python manage.py createsuperuser
   
6. 🚀 START DEVELOPMENT SERVER:
   python manage.py runserver
   
7. ✅ TEST YOUR SETUP:
   • Visit: http://127.0.0.1:8000/admin/
   • Visit: http://127.0.0.1:8000/api/docs/

📁 PROJECT STRUCTURE:
   • Main project: multiservice_platform/
   • Apps: apps/ (accounts, food_service, etc.)
   • Static files: static/
   • Media files: media/
   • Requirements: requirements.txt
   • Environment: .env.example

🔗 USEFUL COMMANDS:
   • Run server: python manage.py runserver
   • Make migrations: python manage.py makemigrations
   • Apply migrations: python manage.py migrate
   • Create superuser: python manage.py createsuperuser
   • Collect static: python manage.py collectstatic

💡 NEED HELP?
   • Check django-setup-guide.md for detailed instructions
   • Django Documentation: https://docs.djangoproject.com/
   • DRF Documentation: https://www.django-rest-framework.org/
""")

def main():
    """Main setup function"""
    print("🚀 Django Multi-Service Platform Setup")
    print("=====================================")
    
    # Check if we're in the right directory
    if os.path.exists('multiservice_platform'):
        print("❌ Directory 'multiservice_platform' already exists!")
        print("Please run this script in an empty directory or remove the existing directory.")
        return False
    
    # Run setup steps
    steps = [
        ("Checking prerequisites", check_prerequisites),
        ("Creating project structure", create_project_structure),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing requirements", install_requirements),
        ("Creating configuration files", create_essential_files),
        ("Creating database setup script", create_database_setup_script)
    ]
    
    for description, function in steps:
        print(f"\n{'='*60}")
        print(f"🔄 {description.upper()}")
        print('='*60)
        
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