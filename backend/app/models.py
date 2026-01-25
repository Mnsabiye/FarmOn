from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model for farmers, buyers, and admins."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'farmer', 'buyer', 'admin'
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='farmer', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'location': self.location,
            'created_at': self.created_at.isoformat()
        }


class Product(db.Model):
    """Product model for marketplace listings."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price_per_kg = db.Column(db.Float, nullable=False)
    quantity_available = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'farmer_name': self.farmer.username if self.farmer else None,
            'farmer_phone': self.farmer.phone if self.farmer else None,
            'farmer_location': self.farmer.location if self.farmer else None,
            'name': self.name,
            'category': self.category,
            'price_per_kg': self.price_per_kg,
            'quantity_available': self.quantity_available,
            'description': self.description,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }


class MarketPrice(db.Model):
    """Market price tracking for different crops."""
    __tablename__ = 'market_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    market_location = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert market price to dictionary."""
        return {
            'id': self.id,
            'crop_name': self.crop_name,
            'market_location': self.market_location,
            'price': self.price,
            'date_recorded': self.date_recorded.isoformat()
        }


class ChatMessage(db.Model):
    """Chat message history for the Smart Assistant."""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    message_text = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert chat message to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message_text': self.message_text,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat()
        }
