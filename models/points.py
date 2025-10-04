from app import db
from datetime import datetime

class PointsHistory(db.Model):
    __tablename__ = 'points_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # 'analysis', 'streak_bonus'
    source_id = db.Column(db.Integer)  # ID of the source (analysis_id, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LoginStreak(db.Model):
    __tablename__ = 'login_streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    streak_count = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date)
    total_streak_points = db.Column(db.Integer, default=0)