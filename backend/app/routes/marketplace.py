"""
Marketplace routes using Supabase.
"""
from flask import Blueprint, request, jsonify
from app.supabase_client import get_supabase, verify_token
from functools import wraps

marketplace_bp = Blueprint('marketplace', __name__)


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


@marketplace_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filters."""
    try:
        supabase = get_supabase()
        
        # Get query parameters
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Build query
        query = supabase.table('products').select(
            '*, farmer:users!farmer_id(username, phone, location)'
        ).order('created_at', desc=True)
        
        if category:
            query = query.eq('category', category)
        
        if min_price is not None:
            query = query.gte('price_per_kg', min_price)
        
        if max_price is not None:
            query = query.lte('price_per_kg', max_price)
        
        result = query.execute()
        
        # Transform data to match expected format
        products = []
        for product in result.data:
            farmer = product.pop('farmer', {}) or {}
            products.append({
                **product,
                'farmer_name': farmer.get('username'),
                'farmer_phone': farmer.get('phone'),
                'farmer_location': farmer.get('location')
            })
        
        return jsonify({
            'products': products,
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@marketplace_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    try:
        supabase = get_supabase()
        
        result = supabase.table('products').select(
            '*, farmer:users!farmer_id(username, phone, location)'
        ).eq('id', product_id).single().execute()
        
        if not result.data:
            return jsonify({'error': 'Product not found'}), 404
        
        product = result.data
        farmer = product.pop('farmer', {}) or {}
        
        return jsonify({
            **product,
            'farmer_name': farmer.get('username'),
            'farmer_phone': farmer.get('phone'),
            'farmer_location': farmer.get('location')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@marketplace_bp.route('/products', methods=['POST'])
@require_auth
def create_product():
    """Create a new product listing (farmers only)."""
    try:
        supabase = get_supabase()
        user = request.current_user
        
        # Get user profile to check role
        user_result = supabase.table('users').select('role').eq('id', user.id).single().execute()
        
        if not user_result.data or user_result.data.get('role') != 'farmer':
            return jsonify({'error': 'Only farmers can create product listings'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'price_per_kg', 'quantity_available']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate numeric fields
        try:
            price = float(data['price_per_kg'])
            quantity = float(data['quantity_available'])
            
            if price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Price and quantity must be valid numbers'}), 400
        
        # Create product
        product_data = {
            'farmer_id': user.id,
            'name': data['name'],
            'category': data['category'],
            'price_per_kg': price,
            'quantity_available': quantity,
            'description': data.get('description'),
            'image_url': data.get('image_url')
        }
        
        result = supabase.table('products').insert(product_data).execute()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': result.data[0] if result.data else None
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create product', 'details': str(e)}), 500


@marketplace_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_auth
def update_product(product_id):
    """Update a product listing (owner only)."""
    try:
        supabase = get_supabase()
        user = request.current_user
        
        # Check if product exists and user owns it
        product_result = supabase.table('products').select('farmer_id').eq('id', product_id).single().execute()
        
        if not product_result.data:
            return jsonify({'error': 'Product not found'}), 404
        
        if product_result.data.get('farmer_id') != user.id:
            return jsonify({'error': 'You can only update your own products'}), 403
        
        data = request.get_json()
        
        # Fields that can be updated
        allowed_fields = ['name', 'category', 'price_per_kg', 'quantity_available', 'description', 'image_url']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        result = supabase.table('products').update(update_data).eq('id', product_id).execute()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': result.data[0] if result.data else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update product', 'details': str(e)}), 500


@marketplace_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    """Delete a product listing (owner only)."""
    try:
        supabase = get_supabase()
        user = request.current_user
        
        # Check if product exists and user owns it
        product_result = supabase.table('products').select('farmer_id').eq('id', product_id).single().execute()
        
        if not product_result.data:
            return jsonify({'error': 'Product not found'}), 404
        
        if product_result.data.get('farmer_id') != user.id:
            return jsonify({'error': 'You can only delete your own products'}), 403
        
        supabase.table('products').delete().eq('id', product_id).execute()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete product', 'details': str(e)}), 500


@marketplace_bp.route('/market-prices', methods=['GET'])
def get_market_prices():
    """Get latest market prices."""
    try:
        supabase = get_supabase()
        
        crop_name = request.args.get('crop')
        limit = request.args.get('limit', 20, type=int)
        
        query = supabase.table('market_prices').select('*').order('date_recorded', desc=True).limit(limit)
        
        if crop_name:
            query = query.eq('crop_name', crop_name)
        
        result = query.execute()
        
        return jsonify({
            'prices': result.data,
            'count': len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
