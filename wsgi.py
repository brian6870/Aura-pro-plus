import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/aura-carbon-tracker'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['PYTHONANYWHERE_DOMAIN'] = 'pythonanywhere.com'

# Import your application
from app import create_app
application = create_app()

# Optional: Initialize database
with application.app_context():
    from database import init_db
    init_db()