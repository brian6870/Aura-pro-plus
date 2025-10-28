from app import db

class SoilAnalysis(db.Model):
    __tablename__ = 'soil_analysis'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    result_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=db.func.now())
