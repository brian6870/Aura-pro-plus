from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from models.user import User
from models.product_analysis import ProductAnalysis
from models.plastic_analysis import PlasticAnalysis
from models.points import PointsHistory
from sqlalchemy import func, desc, or_
import json
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # User statistics
    total_points = current_user.get_total_points()
    
    # Count both product and plastic analyses
    total_product_analyses = ProductAnalysis.query.filter_by(user_id=current_user.id).count()
    total_plastic_analyses = PlasticAnalysis.query.filter_by(user_id=current_user.id).count()
    total_analyses = total_product_analyses + total_plastic_analyses
    
    # Recent analyses (both product and plastic)
    recent_product_analyses = ProductAnalysis.query.filter_by(
        user_id=current_user.id
    ).order_by(ProductAnalysis.created_at.desc()).limit(5).all()
    
    recent_plastic_analyses = PlasticAnalysis.query.filter_by(
        user_id=current_user.id
    ).order_by(PlasticAnalysis.created_at.desc()).limit(5).all()
    
    # Combine and sort recent analyses
    recent_analyses = []
    for analysis in recent_product_analyses:
        recent_analyses.append({
            'type': 'product',
            'analysis': analysis,
            'created_at': analysis.created_at,
            'points_awarded': analysis.points_awarded,
            'environmental_rating': analysis.environmental_rating,
            'display_name': analysis.product_name or 'Product Analysis',
            'icon': 'fas fa-search'
        })
    
    for analysis in recent_plastic_analyses:
        recent_analyses.append({
            'type': 'plastic',
            'analysis': analysis,
            'created_at': analysis.created_at,
            'points_awarded': analysis.points_awarded,
            'environmental_rating': analysis.environmental_rating,
            'display_name': f'{analysis.plastic_type} Plastic',
            'icon': 'fas fa-recycle'
        })
    
    # Sort by creation date
    recent_analyses.sort(key=lambda x: x['created_at'], reverse=True)
    recent_analyses = recent_analyses[:8]  # Take only the 8 most recent
    
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
        User.avatar_url,
        func.sum(PointsHistory.points).label('total_points')
    ).join(PointsHistory).group_by(User.id).order_by(
        desc('total_points')
    ).limit(10).all()
    
    # Environmental impact statistics (both product and plastic)
    product_rating_distribution = db.session.query(
        ProductAnalysis.environmental_rating,
        func.count(ProductAnalysis.id).label('count')
    ).filter(
        ProductAnalysis.user_id == current_user.id
    ).group_by(ProductAnalysis.environmental_rating).all()
    
    plastic_rating_distribution = db.session.query(
        PlasticAnalysis.environmental_rating,
        func.count(PlasticAnalysis.id).label('count')
    ).filter(
        PlasticAnalysis.user_id == current_user.id
    ).group_by(PlasticAnalysis.environmental_rating).all()
    
    # Combine rating distributions
    rating_counts = {'friendly': 0, 'moderate': 0, 'harmful': 0, 'hazardous': 0}
    
    for rating, count in product_rating_distribution:
        if rating in rating_counts:
            rating_counts[rating] += count
    
    for rating, count in plastic_rating_distribution:
        if rating in rating_counts:
            rating_counts[rating] += count
    
    # Convert to list of tuples for template
    rating_distribution = [(rating, count) for rating, count in rating_counts.items() if count > 0]
    
    return render_template('dashboard/index.html',
                         total_points=total_points,
                         total_analyses=total_analyses,
                         recent_analyses=recent_analyses,
                         recent_points=recent_points,
                         leaderboard=leaderboard,
                         rating_distribution=rating_distribution,
                         current_streak=current_user.current_streak,
                         product_analyses_count=total_product_analyses,
                         plastic_analyses_count=total_plastic_analyses)

@dashboard_bp.route('/stats')
@login_required
def stats_data():
    # Generate data for charts (simplified for now)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Daily points for the last 30 days
    daily_points = db.session.query(
        func.date(PointsHistory.created_at).label('date'),
        func.sum(PointsHistory.points).label('points')
    ).filter(
        PointsHistory.user_id == current_user.id,
        PointsHistory.created_at >= thirty_days_ago
    ).group_by('date').order_by('date').all()
    
    dates = [point.date.isoformat() for point in daily_points]
    points = [point.points for point in daily_points]
    
    return jsonify({
        'dates': dates,
        'points': points
    })