import os
import sqlite3
from flask import Flask, g
from flask_mail import Mail
from app.config import Config

# Initialize extensions
mail = Mail()

def get_db():
    """Get the database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE_PATH)
        db.row_factory = sqlite3.Row  # Return rows as dictionaries
    return db

def close_db(e=None):
    """Close the database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure the instance folder exists
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    # Initialize extensions with the app
    mail.init_app(app)
    
    # Register database teardown
    app.teardown_appcontext(close_db)
    
    # Register blueprints
    from app.routes import main_bp, templates_bp, checklists_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(templates_bp, url_prefix='/templates')
    app.register_blueprint(checklists_bp, url_prefix='/checklists')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Add context processors
    @app.context_processor
    def inject_datetime():
        from datetime import datetime
        return dict(datetime=datetime)
    
    return app
