from app import db
from models.user import User
from models.points import PointsHistory
from sqlalchemy import func, desc

class RankingService:
    @staticmethod
    def get_global_leaderboard(limit=20):
        """Get global leaderboard ranked by total points"""
        leaderboard = db.session.query(
            User.id,
            User.username,
            User.avatar_url,
            func.sum(PointsHistory.points).label('total_points')
        ).join(PointsHistory).group_by(
            User.id
        ).order_by(
            desc('total_points')
        ).limit(limit).all()
        
        return [
            {
                'rank': idx + 1,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'total_points': user.total_points or 0
            }
            for idx, user in enumerate(leaderboard)
        ]
    
    @staticmethod
    def get_user_rank(user_id):
        """Get user's current global rank"""
        user_points = db.session.query(
            func.sum(PointsHistory.points).label('total_points')
        ).filter(PointsHistory.user_id == user_id).scalar() or 0
        
        users_ahead = db.session.query(
            User.id
        ).join(PointsHistory).group_by(
            User.id
        ).having(
            func.sum(PointsHistory.points) > user_points
        ).count()
        
        return users_ahead + 1
    
    @staticmethod
    def get_weekly_leaderboard(limit=10):
        """Get leaderboard for the current week"""
        from datetime import datetime, timedelta
        
        start_of_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        
        weekly_leaderboard = db.session.query(
            User.id,
            User.username,
            User.avatar_url,
            func.sum(PointsHistory.points).label('weekly_points')
        ).join(PointsHistory).filter(
            PointsHistory.created_at >= start_of_week
        ).group_by(
            User.id
        ).order_by(
            desc('weekly_points')
        ).limit(limit).all()
        
        return [
            {
                'rank': idx + 1,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'weekly_points': user.weekly_points or 0
            }
            for idx, user in enumerate(weekly_leaderboard)
        ]

ranking_service = RankingService()