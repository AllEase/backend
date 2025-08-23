from mongoengine import Document, StringField, EmailField
from werkzeug.security import generate_password_hash, check_password_hash

class UserLogin(Document):
    username = StringField(required=True, unique=True, max_length=150)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    meta = {
        'collection': 'user_login'
    }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
