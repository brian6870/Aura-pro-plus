#!/usr/bin/python3
"""
Aura Carbon Footprint Tracker - WSGI Configuration
For production deployment with Apache/Nginx
"""
import sys
import os
import logging

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
    
    # Configure production logging
    if not application.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # File handler for errors
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'aura.log'),
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        application.logger.addHandler(file_handler)
        application.logger.setLevel(logging.INFO)
        application.logger.info('Aura application startup')
        
except Exception as e:
    # Log any startup errors
    import logging
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Failed to start Aura application: {str(e)}")
    raise