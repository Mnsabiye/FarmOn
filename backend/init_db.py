"""Database initialization script with sample data."""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.models import db, User, Product, MarketPrice
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Drop all tables and recreate (WARNING: destroys existing data)
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating all tables...")
    db.create_all()
    
    print("Seeding sample data...")
    
    # Create sample users
    farmer1 = User(
        username='jean_farmer',
        email='jean@farmon.bi',
        role='farmer',
        phone='+25761234567',
        location='Bujumbura'
    )
    farmer1.set_password('password123')
    
    farmer2 = User(
        username='marie_agri',
        email='marie@farmon.bi',
        role='farmer',
        phone='+25761234568',
        location='Gitega'
    )
    farmer2.set_password('password123')
    
    buyer1 = User(
        username='paul_buyer',
        email='paul@farmon.bi',
        role='buyer',
        phone='+25761234569',
        location='Bujumbura'
    )
    buyer1.set_password('password123')
    
    admin1 = User(
        username='admin',
        email='admin@farmon.bi',
        role='admin',
        phone='+25761234570',
        location='Bujumbura'
    )
    admin1.set_password('admin123')
    
    db.session.add_all([farmer1, farmer2, buyer1, admin1])
    db.session.commit()
    
    # Create sample products
    products = [
        Product(
            farmer_id=farmer1.id,
            name='Haricots Rouges',
            category='Légumes',
            price_per_kg=1800,
            quantity_available=150,
            description='Haricots rouges biologiques de haute qualité',
            image_url='https://images.unsplash.com/photo-1615485500704-8e990f9900f7?w=400'
        ),
        Product(
            farmer_id=farmer1.id,
            name='Maïs',
            category='Céréales',
            price_per_kg=1200,
            quantity_available=200,
            description='Maïs frais récolté cette semaine',
            image_url='https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400'
        ),
        Product(
            farmer_id=farmer2.id,
            name='Tomates',
            category='Légumes',
            price_per_kg=800,
            quantity_available=80,
            description='Tomates fraîches et juteuses',
            image_url='https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400'
        ),
        Product(
            farmer_id=farmer2.id,
            name='Bananes',
            category='Fruits',
            price_per_kg=600,
            quantity_available=120,
            description='Bananes mûres et sucrées',
            image_url='https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400'
        ),
        Product(
            farmer_id=farmer1.id,
            name='Riz',
            category='Céréales',
            price_per_kg=1500,
            quantity_available=300,
            description='Riz de qualité supérieure',
            image_url='https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400'
        ),
        Product(
            farmer_id=farmer2.id,
            name='Manioc',
            category='Tubercules',
            price_per_kg=400,
            quantity_available=250,
            description='Manioc frais du jour',
            image_url='https://images.unsplash.com/photo-1615485500634-c8db60c71e5a?w=400'
        )
    ]
    
    db.session.add_all(products)
    
    # Create sample market prices
    market_prices = [
        MarketPrice(
            crop_name='Haricots',
            market_location='Bujumbura Central',
            price=1800,
            date_recorded=datetime.utcnow()
        ),
        MarketPrice(
            crop_name='Maïs',
            market_location='Bujumbura Central',
            price=1200,
            date_recorded=datetime.utcnow()
        ),
        MarketPrice(
            crop_name='Tomates',
            market_location='Gitega',
            price=750,
            date_recorded=datetime.utcnow()
        ),
        MarketPrice(
            crop_name='Riz',
            market_location='Bujumbura Central',
            price=1500,
            date_recorded=datetime.utcnow()
        ),
        MarketPrice(
            crop_name='Bananes',
            market_location='Gitega',
            price=600,
            date_recorded=datetime.utcnow()
        ),
        # Historical prices
        MarketPrice(
            crop_name='Haricots',
            market_location='Bujumbura Central',
            price=1750,
            date_recorded=datetime.utcnow() - timedelta(days=7)
        ),
        MarketPrice(
            crop_name='Maïs',
            market_location='Bujumbura Central',
            price=1150,
            date_recorded=datetime.utcnow() - timedelta(days=7)
        )
    ]
    
    db.session.add_all(market_prices)
    db.session.commit()
    
    print("\n✅ Database initialized successfully!")
    print("\n📊 Sample Data Created:")
    print(f"  - Users: {User.query.count()}")
    print(f"  - Products: {Product.query.count()}")
    print(f"  - Market Prices: {MarketPrice.query.count()}")
    print("\n👤 Test Accounts:")
    print("  Farmer: jean@farmon.bi / password123")
    print("  Buyer: paul@farmon.bi / password123")
    print("  Admin: admin@farmon.bi / admin123")
