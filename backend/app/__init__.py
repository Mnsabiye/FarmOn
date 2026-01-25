from flask import Flask
from flask_cors import CORS
from config import config


def create_app(config_name='default'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to FarmOn API',
            'version': '2.0.0',
            'database': 'Supabase',
            'endpoints': {
                'auth': '/api/auth',
                'products': '/api/products',
                'chatbot': '/api/chatbot'
            }
        }
    
    return app
