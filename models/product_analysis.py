from app import db
from datetime import datetime
import json

class ProductAnalysis(db.Model):
    __tablename__ = 'product_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)  # New field for product name
    ingredients_text = db.Column(db.Text, nullable=False)
    environmental_rating = db.Column(db.String(20), nullable=False)
    points_awarded = db.Column(db.Integer, nullable=False)
    analysis_result = db.Column(db.Text)
    alternative_suggestions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_name': self.product_name,
            'ingredients_text': self.ingredients_text,
            'environmental_rating': self.environmental_rating,
            'points_awarded': self.points_awarded,
            'analysis_result': self.analysis_result,
            'alternative_suggestions': self.alternative_suggestions,
            'created_at': self.created_at.isoformat()
        }