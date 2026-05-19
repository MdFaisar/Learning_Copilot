from flask import Blueprint, request, jsonify
from firebase_admin import auth
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def verify_token(f):
    """Decorator to verify Firebase token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        try:
            decoded_token = auth.verify_id_token(token)
            request.user_id = decoded_token['uid']
            request.user_email = decoded_token.get('email')
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
    
    return decorated_function

@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Verify Firebase token"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    
    try:
        decoded_token = auth.verify_id_token(token)
        return jsonify({
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'verified': True
        }), 200
    except Exception as e:
        return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
