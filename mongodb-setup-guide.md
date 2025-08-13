# Django Multi-Service Platform Setup Guide (MongoDB Version)

Complete step-by-step guide to set up your Django backend with MongoDB for the multi-service platform.

## 🗄️ Why MongoDB for Multi-Service Platform?

**Perfect for Multi-Service Apps:**
- **Flexible Schema**: Each service (food, grocery, travel) can have different data structures
- **Horizontal Scaling**: Easy to scale as your business grows across cities
- **JSON-Native**: Perfect for mobile app APIs and complex nested data
- **Geospatial Support**: Built-in location-based queries for delivery services
- **Real-time Performance**: Excellent for order tracking and live updates

## Prerequisites

Before starting, ensure you have the following installed:
- Python 3.9+
- MongoDB 5.0+ (Community or Atlas)
- Redis Server 6+
- Git

## Step 1: Install MongoDB

### Option A: Local MongoDB Installation

#### Ubuntu/Debian:
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# Update and install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS (with Homebrew):
```bash
# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb/brew/mongodb-community
```

#### Windows:
1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community
2. Install using the .msi installer
3. Start MongoDB service from Services panel

### Option B: MongoDB Atlas (Cloud) - Recommended

1. Go to https://www.mongodb.com/atlas
2. Create free account and cluster
3. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/dbname`
4. Whitelist your IP address
5. Create database user

## Step 2: Create Project Directory & Virtual Environment

```bash
# Create project directory
mkdir multiservice_platform
cd multiservice_platform

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 3: Install Dependencies

```bash
# Install MongoDB-specific requirements
pip install -r requirements-mongodb.txt

# If you get installation errors, install system dependencies:
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3-dev build-essential
sudo apt-get install redis-server

# macOS (with Homebrew):
brew install redis

# Windows: Install Redis from official GitHub releases
```

## Step 4: MongoDB Database Setup

### For Local MongoDB:
```bash
# Connect to MongoDB shell
mongosh

# Switch to admin database
use admin

# Create database user
db.createUser({
  user: "multiservice_user",
  pwd: "your_secure_password",
  roles: [
    { role: "readWrite", db: "multiservice_platform" },
    { role: "dbAdmin", db: "multiservice_platform" }
  ]
})

# Switch to your application database
use multiservice_platform

# Create initial collections (optional - they'll be created automatically)
db.createCollection("users")
db.createCollection("restaurants")
db.createCollection("products")
db.createCollection("orders")

# Create geospatial indexes for location-based queries
db.users.createIndex({ "current_location": "2dsphere" })
db.restaurants.createIndex({ "location": "2dsphere" })
db.orders.createIndex({ "delivery_location": "2dsphere" })

# Create text indexes for search functionality
db.restaurants.createIndex({ "name": "text", "cuisine_types": "text" })
db.products.createIndex({ "name": "text", "description": "text" })

# Exit MongoDB shell
exit
```

### For MongoDB Atlas:
1. Use the web interface to create database `multiservice_platform`
2. Copy the connection string for your application
3. Replace `<password>` with your actual password

## Step 5: Initialize Django Project

```bash
# Install Django first
pip install Django==4.2.15 mongoengine==0.27.0

# Create Django project
django-admin startproject multiservice_platform .

# Create apps directory
mkdir apps
touch apps/__init__.py

# Create individual apps
cd apps
python ../manage.py startapp accounts
python ../manage.py startapp food_service  
python ../manage.py startapp grocery_service
python ../manage.py startapp travel_service
python ../manage.py startapp shopping_service
python ../manage.py startapp vendor_management
python ../manage.py startapp payment_service
python ../manage.py startapp notifications
python ../manage.py startapp analytics
cd ..
```

## Step 6: Environment Configuration

```bash
# Create .env file from template
cp env-mongodb.txt .env

# Edit .env file with your actual values
nano .env
```

Fill in your MongoDB connection details:
```bash
MONGODB_DB_NAME=multiservice_platform
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=multiservice_user
MONGODB_PASSWORD=your_secure_password

# OR for MongoDB Atlas:
# MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/multiservice_platform
```

## Step 7: Configure Django Settings

Replace the content in `multiservice_platform/settings.py` with the MongoDB-specific settings provided earlier.

## Step 8: Create MongoDB User Documents

Replace Django models with MongoEngine documents:

### In `apps/accounts/documents.py`:
```python
# Copy the content from mongodb-user-models.py
```

### Update `apps/accounts/admin.py`:
```python
from django.contrib import admin
from django_mongoengine import mongo_admin
from .documents import User, UserSession, LoginAttempt

@mongo_admin.register(User)
class UserAdmin(mongo_admin.DocumentAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'email_verified', 'phone_verified')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ['-date_joined']

@mongo_admin.register(UserSession)
class UserSessionAdmin(mongo_admin.DocumentAdmin):
    list_display = ('user', 'device_type', 'ip_address', 'created_at', 'is_active')
    list_filter = ('device_type', 'is_active', 'created_at')
    search_fields = ('user__email', 'ip_address')

@mongo_admin.register(LoginAttempt)
class LoginAttemptAdmin(mongo_admin.DocumentAdmin):
    list_display = ('email', 'ip_address', 'success', 'attempted_at')
    list_filter = ('success', 'attempted_at')
    search_fields = ('email', 'ip_address')
```

## Step 9: Create API Serializers for MongoDB

### Create `apps/accounts/serializers.py`:
```python
from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongo_serializers
from .documents import User, UserAddress

class UserAddressSerializer(mongo_serializers.EmbeddedDocumentSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'

class UserSerializer(mongo_serializers.DocumentSerializer):
    addresses = UserAddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 
                 'user_type', 'profile_picture', 'addresses', 'current_location',
                 'city', 'state', 'email_verified', 'phone_verified')
        read_only_fields = ('id', 'user_type', 'email_verified', 'phone_verified')

class UserRegistrationSerializer(mongo_serializers.DocumentSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 
                 'last_name', 'phone_number', 'user_type')
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required")
        
        try:
            user = User.objects.get(email=email, is_active=True)
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials")
            
            data['user'] = user
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")
```

## Step 10: Create API Views

### Update `apps/accounts/views.py`:
```python
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_mongoengine import viewsets
from django.contrib.auth import authenticate
from .documents import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    LoginSerializer, UserAddressSerializer
)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.last_login = datetime.utcnow()
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_address(request):
    """Add new address to user"""
    serializer = UserAddressSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        address = user.add_address(serializer.validated_data)
        return Response(UserAddressSerializer(address).data, 
                       status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def nearby_users(request):
    """Find nearby users (for delivery partners, etc.)"""
    lat = float(request.GET.get('lat', 0))
    lng = float(request.GET.get('lng', 0))
    radius = int(request.GET.get('radius', 5000))  # meters
    
    users = User.objects(
        current_location__near=[lng, lat],
        current_location__max_distance=radius
    )
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
```

## Step 11: Create URL Patterns

### Update `apps/accounts/urls.py`:
```python
from django.urls import path, include
from rest_framework_mongoengine.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Address management
    path('addresses/', views.add_address, name='add_address'),
    
    # Location-based queries
    path('nearby-users/', views.nearby_users, name='nearby_users'),
    
    # Include router URLs
    path('', include(router.urls)),
]
```

## Step 12: Start Development

```bash
# Start Redis server (if not running)
redis-server

# Create logs directory
mkdir logs

# Test MongoDB connection
python -c "
import mongoengine
try:
    mongoengine.connect('multiservice_platform', host='localhost', port=27017)
    print('✅ MongoDB connection successful!')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
"

# Start Django development server
python manage.py runserver
```

## Step 13: Test Your MongoDB Setup

### Test API Endpoints:

#### 1. Register User:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "password_confirm": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+919876543210"
  }'
```

#### 2. Login User:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

#### 3. Check MongoDB Data:
```bash
mongosh
use multiservice_platform
db.users.find().pretty()
```

## Step 14: MongoDB-Specific Features

### 1. Geospatial Queries:
```python
# Find restaurants within 5km
from apps.food_service.documents import Restaurant

nearby_restaurants = Restaurant.objects(
    location__near=[77.5946, 12.9716],  # [longitude, latitude]
    location__max_distance=5000  # 5km in meters
)
```

### 2. Text Search:
```python
# Search restaurants by name or cuisine
restaurants = Restaurant.objects.search_text('pizza italian')
```

### 3. Complex Aggregation:
```python
# Monthly revenue by service type
from mongoengine import Q
from datetime import datetime, timedelta

pipeline = [
    {"$match": {"created_at": {"$gte": datetime.now() - timedelta(days=30)}}},
    {"$group": {
        "_id": "$service_type",
        "total_revenue": {"$sum": "$amount"},
        "order_count": {"$sum": 1}
    }},
    {"$sort": {"total_revenue": -1}}
]

results = Order.objects.aggregate(pipeline)
```

## Step 15: MongoDB Admin Interface

### Option A: MongoDB Compass (GUI)
1. Download from https://www.mongodb.com/products/compass
2. Connect using: `mongodb://multiservice_user:password@localhost:27017/multiservice_platform`

### Option B: Web-based Admin
```bash
# Install mongo-express
npm install -g mongo-express

# Configure and start
mongo-express -u multiservice_user -p your_password -d multiservice_platform
```

## Production Considerations

### 1. MongoDB Atlas (Recommended for Production):
- Automatic backups and scaling
- Built-in security and monitoring
- Global clusters for better performance

### 2. Replica Sets (For High Availability):
```javascript
// Initialize replica set
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" }
  ]
})
```

### 3. Sharding (For Horizontal Scaling):
```javascript
// Enable sharding on database
sh.enableSharding("multiservice_platform")

// Shard collection by location
sh.shardCollection("multiservice_platform.restaurants", {"location": "2dsphere"})
```

### 4. Security Best Practices:
- Enable authentication: `--auth`
- Use SSL/TLS: `--sslMode requireSSL`
- Regular security updates
- Network security and firewalls

## 🚀 Advantages of MongoDB Setup

### 1. **Flexible Schema**:
- Different services can have different data structures
- Easy to add new fields without migrations
- JSON-native data storage

### 2. **Geospatial Capabilities**:
- Built-in location-based queries
- Distance calculations
- Polygon and area searches

### 3. **Horizontal Scaling**:
- Easy to scale across multiple servers
- Built-in sharding support
- Automatic load balancing

### 4. **Performance**:
- Faster for read-heavy applications
- Excellent for real-time features
- Efficient indexing

### 5. **Developer Experience**:
- Natural mapping to Python objects
- Rich query language
- Built-in aggregation framework

## Next Steps

1. **Create Service Documents**: Define restaurants, products, orders using MongoEngine
2. **Implement Real-time Features**: Use MongoDB Change Streams for live updates  
3. **Add Search Functionality**: Implement text search and filtering
4. **Set up File Storage**: Use GridFS for images and documents
5. **Add Analytics**: Use MongoDB aggregation framework for business intelligence
6. **Implement Caching**: Use Redis with MongoDB for optimal performance

Your Django + MongoDB backend is now ready for building a scalable multi-service platform! The flexible document structure will accommodate the diverse data needs of food delivery, grocery shopping, travel booking, and general shopping services.

## 🔧 Troubleshooting

### Common Issues:

**Issue**: MongoDB connection refused
**Solution**: Ensure MongoDB service is running: `sudo systemctl start mongod`

**Issue**: Authentication failed  
**Solution**: Check username/password in `.env` file and MongoDB user creation

**Issue**: ModuleNotFoundError for mongoengine
**Solution**: Install with: `pip install mongoengine django-mongoengine`

**Issue**: GridFS file upload errors
**Solution**: Ensure proper GridFS configuration in settings

Your MongoDB-powered multi-service platform is ready for development! 🎉