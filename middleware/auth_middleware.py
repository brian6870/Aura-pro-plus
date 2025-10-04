from flask import request, redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        # For future admin feature implementation
        # if not current_user.is_admin:
        #     flash('Admin access required.', 'error')
        #     return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def check_user_active(f):
    """Decorator to check if user account is active"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Future implementation for account suspension
            # if not current_user.is_active:
            #     flash('Your account has been deactivated.', 'error')
            #     return redirect(url_for('auth.logout'))
            pass
        return f(*args, **kwargs)
    return decorated_function

def api_key_required(f):
    """Decorator for API key authentication (future use)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        # Simple API key validation - extend as needed
        valid_keys = []  # Would be loaded from environment/database
        
        if not api_key or api_key not in valid_keys:
            return {'error': 'Valid API key required'}, 401
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=100, window=900):
    """Simple rate limiting decorator (basic implementation)"""
    from collections import defaultdict
    from time import time
    import functools
    
    requests = defaultdict(list)
    
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                user_id = request.remote_addr  # Use IP for anonymous users
            
            now = time()
            window_start = now - window
            
            # Clean old requests
            requests[user_id] = [req_time for req_time in requests[user_id] if req_time > window_start]
            
            # Check rate limit
            if len(requests[user_id]) >= max_requests:
                flash('Rate limit exceeded. Please try again later.', 'error')
                return redirect(request.referrer or url_for('dashboard.index'))
            
            # Add current request
            requests[user_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_csrf(f):
    """CSRF validation for forms"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # For now, rely on Flask-WTF CSRF protection
            # Future: custom CSRF token validation if needed
            pass
        return f(*args, **kwargs)
    return decorated_function