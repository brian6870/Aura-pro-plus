from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Import models
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
    
    # Main route - redirect to landing page
    @app.route('/')
    def index():
        return redirect(url_for('landing.index'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    
    print("🚀 Starting Aura Carbon Footprint Tracker...")
    print("🌐 Application running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)