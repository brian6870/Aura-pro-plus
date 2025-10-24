from app import db
from datetime import datetime

class PointsHistory(db.Model):
    __tablename__ = 'points_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(50), nullable=False)
    source_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with back_populates
    user = db.relationship('User', back_populates='points_history')

class LoginStreak(db.Model):
    __tablename__ = 'login_streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    streak_count = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date)
    total_streak_points = db.Column(db.Integer, default=0)
    
    # Relationship with back_populates
    user = db.relationship('User', back_populates='login_streak')
    
    def __init__(self, **kwargs):
        if 'total_streak_points' not in kwargs:
            kwargs['total_streak_points'] = 0
        super().__init__(**kwargs)