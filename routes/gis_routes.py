from flask import Blueprint, render_template, request, jsonify
from services.gis_service import analyze_soil

gis_bp = Blueprint('gis_bp', __name__, template_folder='../templates/gis')

@gis_bp.route('/analyze-soil', methods=['GET'])
def gis_page():
    return render_template('gis/gis.html')

@gis_bp.route('/api/analyze-soil', methods=['POST'])
def gis_analyze():
    data = request.json
    location = data.get('location')
    result = analyze_soil(location)
    return jsonify(result)
