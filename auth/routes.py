from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from auth import auth_bp
from models.user import User
from auth.utils import validate_email, validate_password
import requests
from urllib.parse import urlencode

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/register.html')
        
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return render_template('auth/register.html')
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.update_login_streak()
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/google')
def google_login():
    from config import Config
    
    params = {
        'client_id': Config.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': 'http://localhost:5000/auth/google/callback',
        'scope': 'profile email',
        'response_type': 'code'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return redirect(auth_url)

@auth_bp.route('/google/callback')
def google_callback():
    from config import Config
    
    code = request.args.get('code')
    if not code:
        flash('Google authentication failed', 'error')
        return redirect(url_for('auth.login'))
    
    # Exchange code for tokens
    token_data = {
        'client_id': Config.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': Config.GOOGLE_OAUTH_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:5000/auth/google/callback'
    }
    
    token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
    if token_response.status_code != 200:
        flash('Google authentication failed', 'error')
        return redirect(url_for('auth.login'))
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    
    # Get user info
    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    if user_info_response.status_code != 200:
        flash('Failed to fetch user information', 'error')
        return redirect(url_for('auth.login'))
    
    user_info = user_info_response.json()
    
    # Find or create user
    user = User.query.filter_by(google_id=user_info['id']).first()
    if not user:
        user = User.query.filter_by(email=user_info['email']).first()
        if user:
            user.google_id = user_info['id']
        else:
            username = user_info['email'].split('@')[0]
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.query.filter_by(username=username).first():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User(
                username=username,
                email=user_info['email'],
                google_id=user_info['id'],
                avatar_url=user_info.get('picture', '/static/images/avatars/default.png')
            )
            db.session.add(user)
    
    db.session.commit()
    login_user(user)
    user.update_login_streak()
    flash('Google login successful!', 'success')
    return redirect(url_for('dashboard.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # Simplified implementation - in production, integrate with email service
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            flash('If that email exists, instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')