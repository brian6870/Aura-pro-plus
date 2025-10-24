from app import db
from datetime import datetime

class PlasticAnalysis(db.Model):
    __tablename__ = 'plastic_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plastic_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    environmental_rating = db.Column(db.String(20), nullable=False)
    points_awarded = db.Column(db.Integer, nullable=False)
    analysis_result = db.Column(db.Text)
    alternative_suggestions = db.Column(db.Text)
    recycling_guidance = db.Column(db.Text)
    carbon_footprint = db.Column(db.String(200))
    decomposition_time = db.Column(db.String(100))
    detection_count = db.Column(db.Integer, default=1)
    all_predictions = db.Column(db.Text)
    bounding_boxes = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with back_populates
    user = db.relationship('User', back_populates='plastic_analyses')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plastic_type': self.plastic_type,
            'confidence': self.confidence,
            'description': self.description,
            'environmental_rating': self.environmental_rating,
            'points_awarded': self.points_awarded,
            'analysis_result': self.analysis_result,
            'alternative_suggestions': self.alternative_suggestions,
            'recycling_guidance': self.recycling_guidance,
            'carbon_footprint': self.carbon_footprint,
            'decomposition_time': self.decomposition_time,
            'detection_count': self.detection_count,
            'all_predictions': self.all_predictions,
            'bounding_boxes': self.bounding_boxes,
            'image_filename': self.image_filename,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PlasticAnalysis {self.plastic_type} - {self.environmental_rating}>'