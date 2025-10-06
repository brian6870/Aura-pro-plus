#!/usr/bin/env python3
"""
Aura - Carbon Footprint Tracker
Production runner - Only runs in production mode
"""
import os
import sys
from app import create_app

def check_environment():
    """Check if running in production environment"""
    if os.environ.get('FLASK_ENV') != 'production':
        print("❌ This application can only run in production mode!")
        print("💡 Please set FLASK_ENV=production")
        print("💡 Example: export FLASK_ENV=production && python run.py")
        sys.exit(1)
    
    # Check for required environment variables in production
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    

def init_database():
    """Initialize database if needed"""
    try:
        with app.app_context():
            from database import init_db
            init_db()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_wtf
        import groq
        import requests
        import psycopg2  # For PostgreSQL
        print("✅ All dependencies are available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == '__main__':
    # Strict environment check
    check_environment()
    
    # Check dependencies
    check_dependencies()
    
    # Create application instance
    app = create_app()
    
    # Initialize database
    init_database()
    
    # Production configuration checks
    if app.config.get('DEBUG'):
        print("⚠️  Warning: DEBUG mode is enabled in production!")
    
    if not app.config.get('SESSION_COOKIE_SECURE'):
        print("⚠️  Warning: SESSION_COOKIE_SECURE is disabled!")
    
    # Start the production server
    print("🚀 Starting Aura Carbon Footprint Tracker in PRODUCTION mode...")
    print(f"🌐 Environment: {os.environ.get('FLASK_ENV')}")
    print(f"🔒 Debug Mode: {app.config.get('DEBUG')}")
    print(f"📊 Database: {app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'SQLite'}")
    print("📍 Access the application at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Run the production server
    try:
        app.run(
            debug=False,  # Always False in production
            host=os.environ.get('HOST', '0.0.0.0'),
            port=int(os.environ.get('PORT', 5000)),
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)