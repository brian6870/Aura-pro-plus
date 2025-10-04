from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    google_id = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255), default='/static/images/avatars/default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    current_streak = db.Column(db.Integer, default=0)
    
    # Relationships - use string references to avoid circular imports
    analyses = db.relationship('ProductAnalysis', backref='user', lazy=True)
    points_history = db.relationship('PointsHistory', backref='user', lazy=True)
    login_streak = db.relationship('LoginStreak', backref='user', uselist=False, lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_total_points(self):
        from .points import PointsHistory  # Import here to avoid circular imports
        return db.session.query(db.func.sum(PointsHistory.points)).filter(
            PointsHistory.user_id == self.id
        ).scalar() or 0
    
    def update_login_streak(self):
        from .points import PointsHistory, LoginStreak  # Import here to avoid circular imports
        
        today = datetime.utcnow().date()
        if not self.login_streak:
            self.login_streak = LoginStreak(user_id=self.id, total_streak_points=0)
            db.session.add(self.login_streak)
        
        last_login = self.login_streak.last_login_date
        if last_login:
            days_diff = (today - last_login).days
            if days_diff == 1:
                self.login_streak.streak_count += 1
            elif days_diff > 1:
                self.login_streak.streak_count = 1
        else:
            self.login_streak.streak_count = 1
        
        self.login_streak.last_login_date = today
        self.current_streak = self.login_streak.streak_count
        
        # Award streak points - ensure total_streak_points is not None
        if self.login_streak.streak_count > 0:
            streak_points = PointsHistory(
                user_id=self.id,
                points=5,  # Daily login bonus
                source_type='streak_bonus'
            )
            db.session.add(streak_points)
            
            # Initialize total_streak_points if it's None
            if self.login_streak.total_streak_points is None:
                self.login_streak.total_streak_points = 0
            self.login_streak.total_streak_points += 5
        
        self.last_login = datetime.utcnow()
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))