#!/usr/bin/env python3
"""
Aura - Carbon Footprint Tracker
Production runner with Gunicorn support
"""
import os
from app import create_app

app = create_app()

def init_database():
    """Initialize database if needed"""
    with app.app_context():
        from database import init_db
        init_db()
        print("✅ Database initialized")

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run the application
    if os.environ.get('FLASK_ENV') == 'production':
        # In production, use Gunicorn (this file won't be executed directly)
        print("🚀 Running in production mode with Gunicorn")
    else:
        # Development mode
        print("🔧 Running in development mode")
        app.run(debug=True, host='0.0.0.0', port=5000)