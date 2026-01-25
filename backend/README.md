# FarmOn Backend

This is the backend API for FarmOn, an agri-tech platform connecting farmers in Burundi to markets and information.

## Tech Stack

- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **CORS**: Flask-CORS

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### 2. Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb farmconnect_db

# Or using psql:
psql -U postgres
CREATE DATABASE farmconnect_db;
\q
```

### 4. Environment Configuration

```bash
# Copy example env file
copy .env.example .env

# Edit .env and configure:
# - DATABASE_URL (PostgreSQL connection string)
# - SECRET_KEY (generate a random string)
# - JWT_SECRET_KEY (generate a random string)
```

### 5. Initialize Database

```bash
# Create tables and seed sample data
python init_db.py
```

### 6. Run Development Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Marketplace

- `GET /api/products` - Get all products (with optional filters)
- `GET /api/products/<id>` - Get specific product
- `POST /api/products` - Create product (farmer only, requires JWT)
- `PUT /api/products/<id>` - Update product (owner only, requires JWT)
- `DELETE /api/products/<id>` - Delete product (owner only, requires JWT)

### Chatbot

- `POST /api/chatbot/ask` - Send message to chatbot
- `GET /api/chatbot/history` - Get chat history (requires JWT)

## Sample Data

After running `init_db.py`, you'll have:

**Test Accounts:**
- Farmer: `jean@farmconnect.bi` / `password123`
- Buyer: `paul@farmconnect.bi` / `password123`
- Admin: `admin@farmconnect.bi` / `admin123`

**Sample Products:**
- Haricots, Maïs, Tomates, Bananes, Riz, Manioc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   └── routes/
│       ├── __init__.py      # Blueprint registration
│       ├── auth.py          # Authentication routes
│       ├── marketplace.py   # Marketplace routes
│       └── chatbot.py       # Chatbot routes
├── config.py                # Configuration classes
├── run.py                   # Application entry point
├── init_db.py               # Database initialization script
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables template
```

## Development Notes

- The chatbot currently uses mock responses in French and Kirundi
- JWT tokens expire after 24 hours
- CORS is configured for frontend origins (default: http://localhost:5173)
- All passwords are hashed using Werkzeug's security functions
