from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.chat_service import chat_service

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def index():
    return render_template('chat/index.html')

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    message = request.json.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    response = chat_service.get_response(current_user.id, message)
    
    return jsonify({
        'response': response,
        'user_message': message
    })

@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_chat():
    chat_service.clear_history(current_user.id)
    return jsonify({'success': True})