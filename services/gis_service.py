from app import db
from models import SoilAnalysis

def analyze_soil(location):
    # Example dummy computation
    # In reality, you’d integrate a GIS library or soil dataset lookup here.
    result = {
        "location": location,
        "ph": 6.8,
        "nitrogen": 2.5,
        "phosphorus": 1.2,
        "potassium": 3.4
    }

    new_entry = SoilAnalysis(**result)
    db.session.add(new_entry)
    db.session.commit()

    return result
