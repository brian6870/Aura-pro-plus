from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import os
from datetime import timedelta
import logging

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
flask_session = Session()

def setup_logging():
    """Setup application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            logging.FileHandler('logs/aura.log'),
            logging.StreamHandler()
        ]
    )

def create_app():
    app = Flask(__name__)
    
    # Load configuration based on environment
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
        print("🚀 Production mode enabled")
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("🔧 Development mode enabled")
    
    # Setup logging
    setup_logging()
    
    # Initialize extensions
    db.init_app(app)
    
    # Flask-Login configuration
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = "strong"  # Enhanced session protection
    
    # CSRF Protection
    csrf.init_app(app)
    
    # Session configuration
    flask_session.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    with app.app_context():
        from models.user import User
        from models.product_analysis import ProductAnalysis
        from models.points import PointsHistory, LoginStreak
    
    # Register blueprints
    from auth.routes import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.product_analysis import analysis_bp
    from routes.chat import chat_bp
    from routes.settings import settings_bp
    from routes.landing import landing_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(landing_bp)  # No prefix for landing page
    
    # Session management middleware
    @app.before_request
    def before_request():
        """Execute before each request"""
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)
        
        # Ensure session is clean for new users
        if not hasattr(request, 'user_agent'):
            return
        
        # Log request for debugging
        app.logger.info(f"Request: {request.method} {request.path} - User: {session.get('user_id', 'Anonymous')}")
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CORS headers for API endpoints
        if request.path.startswith('/api/'):
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        
        return response
   
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers and monitoring"""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': str(timedelta())
            }, 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }, 500
    
    # Main route - redirect to landing page
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('landing.index'))
    
    # API info endpoint
    @app.route('/api/info')
    def api_info():
        """API information endpoint"""
        return {
            'name': 'Aura Carbon Footprint Tracker',
            'version': '1.0.0',
            'description': 'Track your carbon footprint through product ingredient analysis',
            'endpoints': {
                'auth': '/auth/*',
                'dashboard': '/dashboard/*',
                'analysis': '/analysis/*',
                'chat': '/chat/*'
            }
        }
    
    # Clear session endpoint (for debugging)
    @app.route('/debug/clear-session')
    def clear_session():
        """Debug endpoint to clear session (remove in production)"""
        if app.config.get('DEBUG'):
            session.clear()
            return {'message': 'Session cleared'}, 200
        return {'error': 'Not available in production'}, 403
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            print("✅ Database tables created/verified successfully!")
            
            # Check if we need sample data
            from models.user import User
            if User.query.count() == 0:
                print("💡 No users found. Consider running: python database.py sample")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            # Don't exit - allow the app to run with potential database issues
    
    print("🚀 Starting Aura Carbon Footprint Tracker...")
    print("🌐 Application running on: http://localhost:5000")
    print("🔧 Debug mode:", app.config.get('DEBUG', False))
    
    # Run the application
    app.run(
        debug=app.config.get('DEBUG', False),
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        threaded=True  # Better for handling multiple requests
    )