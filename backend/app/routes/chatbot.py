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
MOCK_RESPONSES = {
    'fr': {
        'weather': [
            "La météo pour demain sera ensoleillée avec une température de 25°C.",
            "Il est prévu des averses légères demain. Préparez-vous!",
            "Temps partiellement nuageux avec des températures autour de 23°C."
        ],
        'farming': [
            "Pour les haricots, plantez pendant la saison des pluies (septembre-décembre).",
            "Utilisez du compost organique pour améliorer la fertilité du sol.",
            "L'espacement idéal pour le maïs est de 75cm entre les rangées."
        ],
        'prices': [
            "Le prix actuel des haricots à Bujumbura est d'environ 1800 FBu/kg.",
            "Les prix du maïs ont augmenté cette semaine à 1200 FBu/kg.",
            "Les tomates se vendent bien à 800 FBu/kg au marché central."
        ],
        'default': [
            "Je suis là pour vous aider avec des conseils agricoles. Posez-moi vos questions!",
            "Pouvez-vous préciser votre question? Je peux vous aider avec la météo, les prix ou les techniques agricoles.",
            "Je suis votre assistant agricole. Comment puis-je vous aider aujourd'hui?"
        ]
    },
    'rn': {  # Kirundi
        'weather': [
            "Ikirere cozoza rizoba hanyuma ubushyuhe bwizoba 25°C.",
            "Hazogwa imvura nkeya ejo. Witegure!",
            "Ikirere kizoba gifise ibicu bike kandi ubushyuhe buzoba hafi ya 23°C."
        ],
        'farming': [
            "Ibiharage, ubishyire mu gihe c'imvura (Nzero-Ukuboza).",
            "Koresha ifumbire kavukire kugira ngo ubone umusaruro mwiza.",
            "Ikigereranyo ciza c'ibigori ni 75cm hagati y'imirongo."
        ],
        'prices': [
            "Igiciro c'ibiharage muri Bujumbura kiri hafi ya 1800 FBu/kg.",
            "Igiciro c'ibigori cyiyongereye muri iki cyumweru kigeze kuri 1200 FBu/kg.",
            "Inyanya zigurishwa neza ku giciro ca 800 FBu/kg ku isoko rikuru."
        ],
        'default': [
            "Ndi hano kugira ngo ngufashe mu bihingwa. Mfata ibibazo!",
            "Urashobora kunsobanurira ibibazo byawe? Ndashobora kugufasha ku kirere, ibiciro canke uburyo bwo guhinga.",
            "Ndi umufasha wawe mu bihingwa. Ese ndakugirira iki uyu munsi?"
        ]
    }
}


def get_mock_response(message, language='fr'):
    """Generate a mock chatbot response based on message content."""
    message_lower = message.lower()
    
    # Detect topic from keywords
    if any(word in message_lower for word in ['météo', 'weather', 'ikirere', 'temps', 'pluie', 'imvura']):
        topic = 'weather'
    elif any(word in message_lower for word in ['prix', 'price', 'igiciro', 'marché', 'market', 'isoko']):
        topic = 'prices'
    elif any(word in message_lower for word in ['planter', 'cultiver', 'guhinga', 'farming', 'agriculture', 'ubuhinzi']):
        topic = 'farming'
    else:
        topic = 'default'
    
    # Get language-specific responses
    # Defaulting to French if not Kirundi
    lang_code = 'rn' if language == 'rn' or language == 'kirundi' else 'fr'
    responses = MOCK_RESPONSES.get(lang_code, MOCK_RESPONSES['fr'])
    
    # Return random response from topic
    return random.choice(responses.get(topic, responses['default']))


@chatbot_bp.route('/ask', methods=['POST'])
def ask_chatbot():
    """Process chatbot message and return response."""
    data = request.get_json()
    
    # Validate required fields
    if 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    language = data.get('language', 'fr')  # Default to French
    
    # Get mock response
    bot_response = get_mock_response(message, language)
    
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
