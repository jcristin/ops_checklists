from app import create_app
from app.db import init_db

def init_database():
    """Initialize the database by creating all tables."""
    app = create_app()
    with app.app_context():
        # Create all tables
        init_db()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
