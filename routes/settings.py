from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from auth.utils import validate_password
from models.user import User
from models.product_analysis import ProductAnalysis  # Add this import
from models.points import PointsHistory  # Add this import

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Check if username is taken by another user
        existing_user = User.query.filter(
            User.username == username,
            User.id != current_user.id
        ).first()
        if existing_user:
            flash('Username already taken', 'error')
            return render_template('settings/profile.html')
        
        # Check if email is taken by another user
        existing_email = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()
        if existing_email:
            flash('Email already registered', 'error')
            return render_template('settings/profile.html')
        
        current_user.username = username
        current_user.email = email
        db.session.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('settings.profile'))
    
    # Calculate user rank for the template
    from services.ranking_service import ranking_service
    user_rank = ranking_service.get_user_rank(current_user.id)
    
    # Get product analysis count
    analysis_count = ProductAnalysis.query.filter_by(user_id=current_user.id).count()
    
    return render_template('settings/profile.html', 
                         user_rank=user_rank,
                         analysis_count=analysis_count)

@settings_bp.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return render_template('settings/security.html')
        
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            flash(msg, 'error')
            return render_template('settings/security.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('settings/security.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('settings.security'))
    
    return render_template('settings/security.html')