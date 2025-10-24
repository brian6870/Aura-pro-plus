from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from services.plastic_classifier import plastic_classifier
from services.groq_client import groq_client
from models.plastic_analysis import PlasticAnalysis  # Import the new model
from models.points import PointsHistory
import json

# CREATE THE BLUEPRINT - THIS LINE WAS MISSING
plastic_bp = Blueprint('plastic', __name__)

@plastic_bp.route('/analyze', methods=['GET'])
@login_required
def analyze_plastic():
    """Show plastic analysis form"""
    model_info = plastic_classifier.get_model_info()
    return render_template('plastic_analysis/input.html', model_info=model_info)

@plastic_bp.route('/predict', methods=['POST'])
@login_required
def predict_plastic():
    """Predict plastic type using Roboflow API"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    print(f"🔍 Analyzing plastic type for user {current_user.id} using Roboflow")
    
    # Predict plastic type with Roboflow
    result = plastic_classifier.predict_plastic_type(image_file)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    return jsonify(result)

@plastic_bp.route('/analyze-environmental-impact', methods=['POST'])
@login_required
def analyze_environmental_impact():
    """Analyze environmental impact of the identified plastic MATERIAL"""
    plastic_type = request.form.get('plastic_type')
    description = request.form.get('description')
    confidence = request.form.get('confidence', 0)
    all_predictions = request.form.get('all_predictions', '{}')
    
    if not plastic_type:
        flash('Plastic type information missing', 'error')
        return redirect(url_for('plastic.analyze_plastic'))
    
    print(f"🌱 Analyzing environmental impact of {plastic_type} plastic material")
    
    # Use the specialized plastic analysis method
    analysis_result = groq_client.analyze_plastic_material(plastic_type, description)
    
    # Calculate points
    from services.points_calculator import points_calculator
    final_points = points_calculator.calculate_points(
        analysis_result['rating'], 
        analysis_result['points']
    )
    
    # Save to PLASTIC_ANALYSES table
    plastic_analysis = PlasticAnalysis(
        user_id=current_user.id,
        plastic_type=plastic_type,
        confidence=float(confidence),
        description=description,
        environmental_rating=analysis_result['rating'],
        points_awarded=final_points,
        analysis_result=analysis_result.get('analysis', ''),
        alternative_suggestions=analysis_result.get('alternatives', ''),
        recycling_guidance=analysis_result.get('recycling_guidance', ''),
        carbon_footprint=analysis_result.get('carbon_footprint', ''),
        decomposition_time=analysis_result.get('decomposition_time', ''),
        all_predictions=all_predictions
    )
    db.session.add(plastic_analysis)
    
    # Award points
    points_history = PointsHistory(
        user_id=current_user.id,
        points=final_points,
        source_type='plastic_analysis',
        source_id=plastic_analysis.id
    )
    db.session.add(points_history)
    
    try:
        db.session.commit()
        print(f"✅ Plastic material analysis saved for user {current_user.id}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Database error: {e}")
        flash('Error saving analysis. Please try again.', 'error')
        return redirect(url_for('plastic.analyze_plastic'))
    
    return render_template('plastic_analysis/results.html',
                         plastic_type=plastic_type,
                         description=description,
                         analysis=plastic_analysis,
                         rating_color=points_calculator.get_rating_color(analysis_result['rating']),
                         rating_description=points_calculator.get_rating_description(analysis_result['rating']),
                         additional_info={
                             'carbon_footprint': analysis_result.get('carbon_footprint', 'Not specified'),
                             'decomposition_time': analysis_result.get('decomposition_time', 'Not specified'),
                             'recycling_guidance': analysis_result.get('recycling_guidance', 'Not specified')
                         })

@plastic_bp.route('/model-info')
@login_required
def model_info():
    """Get model information"""
    return jsonify(plastic_classifier.get_model_info())