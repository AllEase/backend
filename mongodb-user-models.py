"""
MongoDB User Documents for Multi-Service Platform using MongoEngine
"""
from mongoengine import Document, EmbeddedDocument, fields
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime, timedelta
import uuid
import secrets
import string

class UserAddress(EmbeddedDocument):
    """Embedded document for user addresses"""
    
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    id = fields.StringField(default=lambda: str(uuid.uuid4()), primary_key=True)
    address_type = fields.StringField(max_length=10, choices=ADDRESS_TYPE_CHOICES, required=True)
    label = fields.StringField(max_length=50, required=True)
    
    # Address Components
    street_address = fields.StringField(max_length=255, required=True)
    apartment_number = fields.StringField(max_length=50)
    landmark = fields.StringField(max_length=100)
    city = fields.StringField(max_length=100, required=True)
    state = fields.StringField(max_length=100, required=True)
    postal_code = fields.StringField(max_length=10, required=True)
    country = fields.StringField(max_length=100, default='India')
    
    # Geographic Information (MongoDB supports GeoJSON)
    location = fields.PointField()
    
    # Meta Information
    is_default = fields.BooleanField(default=False)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    def clean(self):
        """Validate the address"""
        self.updated_at = datetime.utcnow()


class UserProfile(EmbeddedDocument):
    """Embedded document for user profile information"""
    
    # Preferences
    favorite_cuisines = fields.ListField(fields.StringField(max_length=50))
    dietary_restrictions = fields.ListField(fields.StringField(max_length=50))
    preferred_payment_method = fields.StringField(max_length=50, default='razorpay')
    
    # Statistics
    total_orders = fields.IntField(default=0, min_value=0)
    total_spent = fields.DecimalField(default=0.00, min_value=0, precision=2)
    loyalty_points = fields.IntField(default=0, min_value=0)
    referral_code = fields.StringField(max_length=20, unique=True)
    
    # Settings
    push_notifications = fields.BooleanField(default=True)
    email_notifications = fields.BooleanField(default=True)
    sms_notifications = fields.BooleanField(default=True)
    marketing_emails = fields.BooleanField(default=False)
    
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    def generate_referral_code(self):
        """Generate a unique referral code"""
        if not self.referral_code:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Ensure uniqueness by checking existing users
            while User.objects(profile__referral_code=code).first():
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            self.referral_code = code
        return self.referral_code


class User(Document):
    """Main User Document for multi-service platform"""
    
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('delivery_partner', 'Delivery Partner'),
        ('admin', 'Admin'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]
    
    # Basic Information
    id = fields.StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    email = fields.EmailField(required=True, unique=True)
    phone_number = fields.StringField(max_length=20, required=True, unique=True)
    password = fields.StringField(required=True)
    user_type = fields.StringField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    
    # Personal Information
    first_name = fields.StringField(max_length=30, required=True)
    last_name = fields.StringField(max_length=30, required=True)
    date_of_birth = fields.DateTimeField()
    gender = fields.StringField(max_length=1, choices=GENDER_CHOICES)
    profile_picture = fields.ImageField()
    
    # Verification Status
    email_verified = fields.BooleanField(default=False)
    phone_verified = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    
    # Location Information (MongoDB GeoJSON support)
    current_location = fields.PointField()
    city = fields.StringField(max_length=100)
    state = fields.StringField(max_length=100)
    country = fields.StringField(max_length=100, default='India')
    
    # Preferences
    preferred_language = fields.StringField(max_length=10, default='en')
    notification_preferences = fields.DictField()
    
    # Embedded Documents
    addresses = fields.ListField(fields.EmbeddedDocumentField(UserAddress))
    profile = fields.EmbeddedDocumentField(UserProfile, default=UserProfile)
    
    # Timestamps
    date_joined = fields.DateTimeField(default=datetime.utcnow)
    last_login = fields.DateTimeField()
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Security fields
    password_reset_token = fields.StringField()
    password_reset_expires = fields.DateTimeField()
    email_verification_token = fields.StringField()
    phone_verification_token = fields.StringField()
    
    # Indexing
    meta = {
        'collection': 'users',
        'indexes': [
            'email',
            'phone_number',
            'user_type',
            'date_joined',
            'current_location',
            {'fields': ['email', 'phone_number'], 'unique': True},
            {'fields': ['current_location'], 'type': '2dsphere'},  # Geospatial index
        ]
    }
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f'{self.first_name} {self.last_name}'.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def set_password(self, raw_password):
        """Set password with Django's password hashing"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password against stored hash"""
        return check_password(raw_password, self.password)
    
    def generate_password_reset_token(self):
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        self.save()
        return token
    
    def generate_email_verification_token(self):
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.save()
        return token
    
    def verify_email(self, token):
        """Verify email with token"""
        if self.email_verification_token == token:
            self.email_verified = True
            self.email_verification_token = None
            self.save()
            return True
        return False
    
    def add_address(self, address_data):
        """Add new address to user"""
        # If this is the first address, make it default
        if not self.addresses:
            address_data['is_default'] = True
        
        # If setting as default, unset other defaults
        if address_data.get('is_default'):
            for addr in self.addresses:
                addr.is_default = False
        
        new_address = UserAddress(**address_data)
        self.addresses.append(new_address)
        self.save()
        return new_address
    
    def get_default_address(self):
        """Get user's default address"""
        for address in self.addresses:
            if address.is_default:
                return address
        return self.addresses[0] if self.addresses else None
    
    def clean(self):
        """Custom validation"""
        self.updated_at = datetime.utcnow()
        
        # Ensure email is lowercase
        if self.email:
            self.email = self.email.lower()
        
        # Generate referral code if customer and doesn't have one
        if self.user_type == 'customer' and not self.profile.referral_code:
            self.profile.generate_referral_code()
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'
    
    @property
    def is_vendor(self):
        return self.user_type == 'vendor'
    
    @property
    def is_delivery_partner(self):
        return self.user_type == 'delivery_partner'
    
    @classmethod
    def create_user(cls, email, password, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email must be set')
        
        user = cls(email=email.lower(), **extra_fields)
        user.set_password(password)
        user.clean()
        user.save()
        return user
    
    @classmethod
    def create_superuser(cls, email, password, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return cls.create_user(email, password, **extra_fields)


class UserSession(Document):
    """MongoDB-based user session document"""
    
    user = fields.ReferenceField(User, required=True)
    session_key = fields.StringField(max_length=40, required=True, unique=True)
    session_data = fields.DictField()
    
    # Device Information
    device_type = fields.StringField(max_length=50)
    device_id = fields.StringField(max_length=100)
    ip_address = fields.StringField(max_length=45)
    user_agent = fields.StringField()
    
    # Location
    login_location = fields.PointField()
    country = fields.StringField(max_length=100)
    city = fields.StringField(max_length=100)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    last_activity = fields.DateTimeField(default=datetime.utcnow)
    expires_at = fields.DateTimeField()
    
    # Security
    is_active = fields.BooleanField(default=True)
    logout_at = fields.DateTimeField()
    
    meta = {
        'collection': 'user_sessions',
        'indexes': [
            'user',
            'session_key',
            'expires_at',
            'is_active',
            'created_at',
            {'fields': ['expires_at'], 'expireAfterSeconds': 0}  # TTL index
        ]
    }
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def logout(self):
        """Logout user session"""
        self.is_active = False
        self.logout_at = datetime.utcnow()
        self.save()


class LoginAttempt(Document):
    """Track login attempts for security"""
    
    email = fields.EmailField(required=True)
    ip_address = fields.StringField(max_length=45, required=True)
    success = fields.BooleanField(required=True)
    
    # Device Info
    user_agent = fields.StringField()
    device_type = fields.StringField(max_length=50)
    
    # Location
    country = fields.StringField(max_length=100)
    city = fields.StringField(max_length=100)
    
    # Timestamp
    attempted_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Failure Details
    failure_reason = fields.StringField(max_length=100)
    
    meta = {
        'collection': 'login_attempts',
        'indexes': [
            'email',
            'ip_address',
            'attempted_at',
            'success',
            {'fields': ['attempted_at'], 'expireAfterSeconds': 86400 * 30}  # Keep for 30 days
        ]
    }
    
    @classmethod
    def record_attempt(cls, email, ip_address, success, **kwargs):
        """Record a login attempt"""
        return cls(
            email=email.lower(),
            ip_address=ip_address,
            success=success,
            **kwargs
        ).save()
    
    @classmethod
    def get_recent_failures(cls, email, hours=1):
        """Get recent failed login attempts"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return cls.objects(
            email=email.lower(),
            success=False,
            attempted_at__gte=cutoff
        ).count()
    
    @classmethod
    def is_blocked(cls, email, max_attempts=5, hours=1):
        """Check if email is blocked due to too many failed attempts"""
        return cls.get_recent_failures(email, hours) >= max_attempts


# Signal-like functionality using MongoEngine signals
from mongoengine import signals

def create_user_profile(sender, document, **kwargs):
    """Create user profile when user is created"""
    if not document.profile:
        document.profile = UserProfile()
        document.profile.generate_referral_code()

def update_timestamp(sender, document, **kwargs):
    """Update timestamp on save"""
    document.updated_at = datetime.utcnow()

# Connect signals
signals.pre_save.connect(create_user_profile, sender=User)
signals.pre_save.connect(update_timestamp, sender=User)