"""
Chatbot routes using Supabase.
"""
from flask import Blueprint, request, jsonify
from app.supabase_client import get_supabase, verify_token
from datetime import datetime
from functools import wraps
import random

chatbot_bp = Blueprint('chatbot', __name__)


def require_auth(f):
    """Decorator to require authentication for an endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            user = verify_token(token)
            request.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated_function


def optional_auth():
    """Try to get user from auth header, but don't require it."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        return verify_token(token)
    except:
        return None


# Mock responses in French and Kirundi (English removed)
def check_price(keyword, language='fr'):
    """Query market_prices table for a crop."""
    try:
        supabase = get_supabase()
        response = supabase.table('market_prices').select('*').ilike('crop_name', f'%{keyword}%').order('date_recorded', desc=True).limit(1).execute()
        
        data = response.data
        if not data:
            if language == 'rn':
                return f"Ntibishobotse kubona igiciro ca {keyword}."
            return f"Je n'ai pas trouvé de prix récent pour '{keyword}'."
            
        item = data[0]
        price = item['price']
        location = item['market_location']
        
        if language == 'rn':
            return f"Igiciro ca {item['crop_name']} i {location} ni {price} FBu/kg."
        return f"Le prix actuel pour {item['crop_name']} à {location} est de {price} FBu/kg."
    except Exception as e:
        print(f"Error checking price: {e}")
        return "Désolé, je ne peux pas vérifier les prix pour le moment."

def check_availability(keyword, language='fr'):
    """Query products table for availability."""
    try:
        supabase = get_supabase()
        # Find products matching name and with inventory > 0
        response = supabase.table('products').select('*').ilike('name', f'%{keyword}%').gt('quantity_available', 0).limit(3).execute()
        
        data = response.data
        if not data:
            if language == 'rn':
                return f"Nta {keyword} dufite ubu."
            return f"Désolé, nous n'avons pas de '{keyword}' disponible pour le moment."
            
        count = len(data)
        if language == 'rn':
            return f"Ego! Dufise {count} {keyword} zitandukanye. Urajya kuri 'Marché' kugura."
        return f"Oui! Nous avons {count} offres pour '{keyword}'. Visitez la page 'Marché' pour commander."
    except Exception as e:
        print(f"Error checking availability: {e}")
        return "Désolé, je ne peux pas vérifier le stock pour le moment."

def get_smart_response(message, language='fr'):
    """Generate a data-driven response."""
    message_lower = message.lower()
    
    # Keyword extraction (simple)
    # Define common crops to look for
    crops = ['haricot', 'maïs', 'tomate', 'pomme de terre', 'riz', 'oignon', 'carotte', 
             'ibiharage', 'ibigori', 'inyanya', 'ibirayi', 'umuceri']
    
    found_crop = next((crop for crop in crops if crop in message_lower), None)
    
    # 1. Price Check Intent
    if any(word in message_lower for word in ['prix', 'price', 'igiciro', 'coûte', 'gura']):
        if found_crop:
            return check_price(found_crop, language)
        else:
            if language == 'rn':
                return "Ushaka kumenya igiciro c'ikihe gihingwa? (Urugero: Igiciro c'ibiharage)"
            return "De quel produit voulez-vous connaître le prix? (Ex: Prix des haricots)"

    # 2. Availability/Buying Intent
    elif any(word in message_lower for word in ['avez-vous', 'disponible', 'acheter', 'ntabwo', 'dufise', 'shaka']):
        if found_crop:
            return check_availability(found_crop, language)
        else:
            if language == 'rn':
                return "Ushaka kugura iki? (Urugero: Ndashaka ibigori)"
            return "Que cherchez-vous à acheter? (Ex: Avez-vous du maïs?)"
            
    # 3. Weather (Keep generic/mock for now as we don't have a weather API)
    elif any(word in message_lower for word in ['météo', 'weather', 'ikirere', 'imvura']):
        if language == 'rn':
            return "Ikirere kimeze neza uyu munsi. Nta mvura itegenijwe."
        return "La météo est favorable aujourd'hui. Pas de pluie prévue dans l'immédiat."
        
    # 4. Greeting/Default
    elif any(word in message_lower for word in ['bonjour', 'salut', 'bwakeye', 'bite']):
        if language == 'rn':
            return "Bwakeye! Ndi FarmOn Assistant. Ni gute nagufasha?"
        return "Bonjour! Je suis l'assistant FarmOn. Comment puis-je vous aider (Prix, Stocks, Météo)?"
        
    # Default fallback
    if language == 'rn':
        return "Mbabarira, sinumvise neza. Ushobora gusubiramwo?"
    return "Je ne suis pas sûr de comprendre. Pouvez-vous demander le prix d'un produit ou sa disponibilité?"


@chatbot_bp.route('/ask', methods=['POST'])
def ask_chatbot():
    """Process chatbot message and return response."""
    data = request.get_json()
    
    # Validate required fields
    if 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    language = data.get('language', 'fr')  # Default to French
    
    # Get smart response
    bot_response = get_smart_response(message, language)
    
    # Try to get authenticated user (optional)
    user = optional_auth()
    user_id = user.id if user else None
    
    # Save messages to Supabase (if possible)
    try:
        supabase = get_supabase()
        
        # Save user message
        supabase.table('chat_messages').insert({
            'user_id': user_id,
            'message_text': message,
            'sender': 'user'
        }).execute()
        
        # Save bot response
        supabase.table('chat_messages').insert({
            'user_id': user_id,
            'message_text': bot_response,
            'sender': 'bot'
        }).execute()
        
    except Exception as e:
        # Don't fail the request if message saving fails
        print(f"Failed to save chat messages: {e}")
    
    return jsonify({
        'message': message,
        'response': bot_response,
        'language': language,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@chatbot_bp.route('/history', methods=['GET'])
@require_auth
def get_chat_history():
    """Get chat history for authenticated user."""
    try:
        supabase = get_supabase()
        user = request.current_user
        
        # Get limit from query params (default 50)
        limit = request.args.get('limit', 50, type=int)
        
        # Get user's chat messages
        result = supabase.table('chat_messages').select('*').eq(
            'user_id', user.id
        ).order('timestamp', desc=True).limit(limit).execute()
        
        # Reverse to get chronological order
        messages = list(reversed(result.data)) if result.data else []
        
        return jsonify({
            'messages': messages,
            'count': len(messages)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
