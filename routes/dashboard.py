from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from middleware.auth_middleware import login_required, rate_limit, check_user_active
from app import db
from models.user import User
from models.product_analysis import ProductAnalysis
from models.points import PointsHistory
from sqlalchemy import func, desc
import json
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
@check_user_active
def index():
    # User statistics
    total_points = current_user.get_total_points()
    total_analyses = ProductAnalysis.query.filter_by(user_id=current_user.id).count()
    
    # Recent analyses
    recent_analyses = ProductAnalysis.query.filter_by(
        user_id=current_user.id
    ).order_by(ProductAnalysis.created_at.desc()).limit(5).all()
    
    # Points breakdown (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_points = db.session.query(
        func.sum(PointsHistory.points).label('total_points')
    ).filter(
        PointsHistory.user_id == current_user.id,
        PointsHistory.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Leaderboard (top 10 users by total points)
    leaderboard = db.session.query(
        User.username,
        func.sum(PointsHistory.points).label('total_points')
    ).join(PointsHistory).group_by(User.id).order_by(
        desc('total_points')
    ).limit(10).all()
    
    # Environmental impact statistics
    rating_distribution = db.session.query(
        ProductAnalysis.environmental_rating,
        func.count(ProductAnalysis.id).label('count')
    ).filter(
        ProductAnalysis.user_id == current_user.id
    ).group_by(ProductAnalysis.environmental_rating).all()
     # Ensure all rating types are represented, even if count is 0
    all_ratings = ['friendly', 'moderate', 'harmful', 'hazardous']
    rating_dict = {rating: 0 for rating in all_ratings}
    for rating, count in rating_distribution:
        rating_dict[rating] = count
    
    return render_template('dashboard/index.html',
                         total_points=total_points,
                         total_analyses=total_analyses,
                         recent_analyses=recent_analyses,
                         recent_points=recent_points,
                         leaderboard=leaderboard,
                         rating_distribution=rating_distribution,
                         current_streak=current_user.current_streak)

@dashboard_bp.route('/stats')
@login_required
@rate_limit(max_requests=60, window=300)
def stats_data():
    # Generate data for charts
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Daily points for the last 30 days
    daily_points = db.session.query(
        func.date(PointsHistory.created_at).label('date'),
        func.sum(PointsHistory.points).label('points')
    ).filter(
        PointsHistory.user_id == current_user.id,
        PointsHistory.created_at >= thirty_days_ago
    ).group_by('date').order_by('date').all()
    
    dates = [point.date for point in daily_points]
    points = [point.points for point in daily_points]
    
    return jsonify({
        'dates': dates,
        'points': points
    })