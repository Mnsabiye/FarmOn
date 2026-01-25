def register_blueprints(app):
    """Register all blueprints."""
    from app.routes.auth import auth_bp
    from app.routes.marketplace import marketplace_bp
    from app.routes.chatbot import chatbot_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(marketplace_bp, url_prefix='/api')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
