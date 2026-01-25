"""
Authentication routes using Supabase Auth.
Note: Most auth is handled on the frontend with Supabase JS client.
These endpoints are for backend token verification and user profile operations.
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from app.supabase_client import get_supabase, verify_token

auth_bp = Blueprint('auth', __name__)


def require_auth(f):
    """Decorator to require authentication for an endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            user = verify_token(token)
            request.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated_function


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get the current authenticated user's profile."""
    try:
        supabase = get_supabase()
        user = request.current_user
        
        # Get user profile from users table
        result = supabase.table('users').select('*').eq('id', user.id).single().execute()
        
        if result.data:
            return jsonify({
                'user': result.data
            }), 200
        else:
            return jsonify({'error': 'User profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update the current user's profile."""
    try:
        supabase = get_supabase()
        user = request.current_user
        data = request.get_json()
        
        # Fields that can be updated
        allowed_fields = ['username', 'phone', 'location']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        result = supabase.table('users').update(update_data).eq('id', user.id).execute()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': result.data[0] if result.data else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
