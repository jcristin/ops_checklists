import os
from datetime import datetime

class Config:
    # Secret key for form security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-checklist-app'
    
    # Database configuration
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or \
        os.path.join(BASEDIR, '..', 'instance', 'app.db')
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Application configuration
    APP_NAME = 'Operations Checklists'
    
    @staticmethod
    def get_current_date():
        """Return the current date in the format YYYY-MM-DD"""
        return datetime.now().strftime('%Y-%m-%d')
