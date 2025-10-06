#!/usr/bin/python3
"""
Aura Carbon Footprint Tracker - WSGI Configuration
For production deployment with Apache/Nginx
"""
import sys
import os

# Configure the application
def setup_environment():
    """Set up the production environment"""
    # Add the project directory to Python path
    project_home = os.path.dirname(os.path.abspath(__file__))
    if project_home not in sys.path:
        sys.path.insert(0, project_home)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['PYTHONPATH'] = project_home
    
    # Ensure the .env file is loaded
    env_path = os.path.join(project_home, '.env')
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path)

# Set up the environment
setup_environment()

# Import the application factory
try:
    from app import create_app
    application = create_app()
    
    # No file logging - only console logging for production
    # This prevents the "/var/log/aura/error.log isn't writable" error
    
except Exception as e:
    # Log any startup errors to console only
    print(f"ERROR: Failed to start Aura application: {str(e)}")
    raise