from flask import Blueprint, render_template
from app import db
from models.user import User
from models.product_analysis import ProductAnalysis

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    """Landing page for first-time visitors"""
    # Get stats for the landing page
    total_users = User.query.count()
    total_analyses = ProductAnalysis.query.count()
    
    # Calculate estimated carbon saved (simplified calculation)
    # Assuming each analysis leads to 0.5kg CO2 saved on average through better choices
    carbon_saved = total_analyses * 0.5
    
    return render_template('landing/index.html',
                         total_users=total_users,
                         total_analyses=total_analyses,
                         carbon_saved=int(carbon_saved))

@landing_bp.route('/home')
def home():
    """Alternative home route that redirects based on authentication"""
    from flask_login import current_user
    if current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))
    return index()