from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models.product_analysis import ProductAnalysis
from models.points import PointsHistory
from services.groq_client import groq_client
from services.ocr_service import ocr_service
from services.points_calculator import points_calculator
import json

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/input', methods=['GET'])
@login_required
def input_form():
    return render_template('product_analysis/input.html')

@analysis_bp.route('/process-ocr', methods=['POST'])
@login_required
def process_ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    extracted_text = ocr_service.process_image(image_file)
    if extracted_text is None:
        return jsonify({'error': 'OCR processing failed'}), 500
    
    return jsonify({'extracted_text': extracted_text})

@analysis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_ingredients():
    product_name = request.form.get('product_name', '').strip()
    ingredients_text = request.form.get('ingredients', '').strip()
    
    if not ingredients_text:
        flash('Please provide ingredient list', 'error')
        return redirect(url_for('analysis.input_form'))
    
    print(f"🧪 Starting analysis for user {current_user.id}")
    print(f"📦 Product: {product_name}")
    print(f"📝 Ingredients length: {len(ingredients_text)} characters")
    
    # Analyze with Groq API (now includes product name)
    analysis_result = groq_client.analyze_ingredients(product_name, ingredients_text)
    
    print(f"📊 Analysis result: {analysis_result['detected_product_name']} - {analysis_result['rating']} - {analysis_result['points']} points")
    
    # Calculate final points
    final_points = points_calculator.calculate_points(
        analysis_result['rating'], 
        analysis_result['points']
    )
    
    # ENSURE all data is in correct format for database (extra safety)
    analysis_text = str(analysis_result.get('analysis', 'No analysis available')).strip()
    alternatives_text = str(analysis_result.get('alternatives', 'No alternatives suggested')).strip()
    rating = str(analysis_result.get('rating', 'moderate')).strip()
    detected_product_name = str(analysis_result.get('detected_product_name', product_name)).strip()
    
    # Use detected product name if no product name was provided
    if not product_name and detected_product_name:
        product_name = detected_product_name
    
    # Truncate if too long for database
    if len(analysis_text) > 10000:
        analysis_text = analysis_text[:10000]
    if len(alternatives_text) > 5000:
        alternatives_text = alternatives_text[:5000]
    if len(product_name) > 200:
        product_name = product_name[:200]
    
    # Save analysis to database
    product_analysis = ProductAnalysis(
        user_id=current_user.id,
        product_name=product_name,
        ingredients_text=ingredients_text,
        environmental_rating=rating,
        points_awarded=final_points,
        analysis_result=analysis_text,
        alternative_suggestions=alternatives_text
    )
    db.session.add(product_analysis)
    
    # Award points
    points_history = PointsHistory(
        user_id=current_user.id,
        points=final_points,
        source_type='analysis',
        source_id=product_analysis.id
    )
    db.session.add(points_history)
    
    try:
        db.session.commit()
        print(f"✅ Analysis saved successfully for user {current_user.id}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Database error: {e}")
        flash('Error saving analysis. Please try again.', 'error')
        return redirect(url_for('analysis.input_form'))
    
    return render_template('product_analysis/results.html',
                         analysis=product_analysis,
                         rating_color=points_calculator.get_rating_color(rating),
                         rating_description=points_calculator.get_rating_description(rating))

@analysis_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    analyses = ProductAnalysis.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ProductAnalysis.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template('product_analysis/history.html', analyses=analyses)

# TEMPORARY: Add backward compatibility
@analysis_bp.route('/analysis-history')
@login_required
def analysis_history():
    """Backward compatibility - redirect to the correct history endpoint"""
    return redirect(url_for('analysis.history'))