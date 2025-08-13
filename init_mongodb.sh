#!/bin/bash
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
