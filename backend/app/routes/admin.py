"""
Admin routes: dashboard metrics, user management, listing moderation,
market price management and an audit trail of admin actions.

All endpoints require a Supabase JWT belonging to a user whose profile
role is 'admin'. Writes go through the service role key, which bypasses
RLS, so every action here is checked and logged explicitly.
"""
import re
from functools import wraps

from flask import Blueprint, request, jsonify

from app.supabase_client import get_supabase, verify_token
from app.services.admin_metrics import ROLES, build_overview

admin_bp = Blueprint('admin', __name__)

# Effectively permanent; Supabase has no "ban forever" value.
SUSPEND_DURATION = '876000h'
MAX_PER_PAGE = 100


def require_admin(f):
    """Decorator: valid token AND an 'admin' profile role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401

        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            user = verify_token(token)
        except Exception as e:
            return jsonify({'error': str(e)}), 401

        try:
            profile = get_supabase().table('users').select('id, role').eq('id', user.id).execute()
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        if not profile.data or profile.data[0].get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        request.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def _page_args():
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 20, type=int), 1), MAX_PER_PAGE)
    return page, per_page, (page - 1) * per_page, page * per_page - 1


def _page_meta(page, per_page, total):
    total = total or 0
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': max((total + per_page - 1) // per_page, 1),
    }


def _search_term(value):
    """Strip characters that would break PostgREST's or() filter syntax."""
    return re.sub(r'[,()%*"\\]', ' ', value or '').strip()


def _ilike_any(query, columns, term):
    """
    Match `term` against any of `columns`.

    The pinned postgrest client (0.13) has no or_() helper, so the
    PostgREST `or=(...)` parameter is added the same way its own filters are.
    """
    clauses = ','.join(f'{column}.ilike.*{term}*' for column in columns)
    query.params = query.params.add('or', f'({clauses})')
    return query


def _log_action(action, target_type, target_id, details=None):
    """Record an admin action. Never fails the request if logging fails."""
    try:
        get_supabase().table('admin_audit_log').insert({
            'admin_id': request.current_user.id,
            'action': action,
            'target_type': target_type,
            'target_id': str(target_id),
            'details': details or {},
        }).execute()
    except Exception as e:
        print(f"Failed to write admin audit log: {e}")


def _suspended_ids():
    """IDs of auth users currently suspended (tracked in app_metadata)."""
    try:
        auth_users = get_supabase().auth.admin.list_users(page=1, per_page=1000)
    except Exception as e:
        print(f"Failed to list auth users: {e}")
        return set()
    return {
        u.id for u in auth_users
        if (u.app_metadata or {}).get('suspended')
    }


# ============================================
# OVERVIEW
# ============================================
@admin_bp.route('/overview', methods=['GET'])
@require_admin
def get_overview():
    """Headline metrics and 30-day activity for the dashboard."""
    try:
        supabase = get_supabase()
        users = supabase.table('users').select('id, role, created_at').execute().data or []
        products = supabase.table('products').select(
            'id, category, price_per_kg, quantity_available, created_at'
        ).execute().data or []
        chat = supabase.table('chat_messages').select('sender, timestamp').execute().data or []

        overview = build_overview(users, products, chat)

        recent = supabase.table('products').select(
            'id, name, category, price_per_kg, quantity_available, created_at, '
            'farmer:users!farmer_id(username)'
        ).order('created_at', desc=True).limit(5).execute().data or []
        overview['recent_products'] = [
            {**p, 'farmer_name': (p.pop('farmer', None) or {}).get('username')}
            for p in recent
        ]

        overview['recent_users'] = supabase.table('users').select(
            'id, username, email, role, location, created_at'
        ).order('created_at', desc=True).limit(5).execute().data or []

        return jsonify(overview), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# USERS
# ============================================
@admin_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """Paginated users, filterable by role and username/email search."""
    try:
        supabase = get_supabase()
        page, per_page, start, end = _page_args()
        role = request.args.get('role')
        search = _search_term(request.args.get('q'))

        query = supabase.table('users').select('*', count='exact').order('created_at', desc=True)
        if role in ROLES:
            query = query.eq('role', role)
        if search:
            query = _ilike_any(query, ('username', 'email'), search)

        result = query.range(start, end).execute()
        users = result.data or []

        ids = [u['id'] for u in users]
        product_counts = {}
        if ids:
            rows = supabase.table('products').select('farmer_id').in_('farmer_id', ids).execute().data or []
            for row in rows:
                product_counts[row['farmer_id']] = product_counts.get(row['farmer_id'], 0) + 1

        suspended = _suspended_ids()
        for u in users:
            u['product_count'] = product_counts.get(u['id'], 0)
            u['suspended'] = u['id'] in suspended

        return jsonify({'users': users, 'pagination': _page_meta(page, per_page, result.count)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<uuid:user_id>/role', methods=['PATCH'])
@require_admin
def update_user_role(user_id):
    """Change a user's role."""
    user_id = str(user_id)
    data = request.get_json(silent=True) or {}
    role = data.get('role')

    if role not in ROLES:
        return jsonify({'error': f"Role must be one of: {', '.join(ROLES)}"}), 400
    if user_id == request.current_user.id:
        return jsonify({'error': 'You cannot change your own role'}), 400

    try:
        supabase = get_supabase()
        existing = supabase.table('users').select('id, username, role').eq('id', user_id).execute()
        if not existing.data:
            return jsonify({'error': 'User not found'}), 404

        previous = existing.data[0]['role']
        result = supabase.table('users').update({'role': role}).eq('id', user_id).execute()
        _log_action('user.role_changed', 'user', user_id, {
            'username': existing.data[0].get('username'), 'from': previous, 'to': role,
        })

        return jsonify({
            'message': 'Role updated successfully',
            'user': result.data[0] if result.data else None
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _set_suspended(user_id, suspended):
    user_id = str(user_id)
    if user_id == request.current_user.id:
        return jsonify({'error': 'You cannot suspend your own account'}), 400

    try:
        supabase = get_supabase()
        existing = supabase.table('users').select('id, username').eq('id', user_id).execute()
        if not existing.data:
            return jsonify({'error': 'User not found'}), 404

        supabase.auth.admin.update_user_by_id(user_id, {
            'ban_duration': SUSPEND_DURATION if suspended else 'none',
            'app_metadata': {'suspended': suspended},
        })
        _log_action('user.suspended' if suspended else 'user.restored', 'user', user_id, {
            'username': existing.data[0].get('username'),
        })

        return jsonify({
            'message': 'User suspended' if suspended else 'User restored',
            'user_id': user_id,
            'suspended': suspended
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<uuid:user_id>/suspend', methods=['POST'])
@require_admin
def suspend_user(user_id):
    """Block a user from signing in."""
    return _set_suspended(user_id, True)


@admin_bp.route('/users/<uuid:user_id>/restore', methods=['POST'])
@require_admin
def restore_user(user_id):
    """Lift a suspension."""
    return _set_suspended(user_id, False)


# ============================================
# PRODUCTS (moderation)
# ============================================
@admin_bp.route('/products', methods=['GET'])
@require_admin
def list_products():
    """Paginated listings across all farmers."""
    try:
        supabase = get_supabase()
        page, per_page, start, end = _page_args()
        category = request.args.get('category')
        search = _search_term(request.args.get('q'))
        stock = request.args.get('stock')  # 'in' | 'out'

        query = supabase.table('products').select(
            '*, farmer:users!farmer_id(username, email, phone, location)', count='exact'
        ).order('created_at', desc=True)
        if category:
            query = query.eq('category', category)
        if search:
            query = query.ilike('name', f'%{search}%')
        if stock == 'out':
            query = query.lte('quantity_available', 0)
        elif stock == 'in':
            query = query.gt('quantity_available', 0)

        result = query.range(start, end).execute()

        products = []
        for product in result.data or []:
            farmer = product.pop('farmer', None) or {}
            products.append({
                **product,
                'farmer_name': farmer.get('username'),
                'farmer_email': farmer.get('email'),
                'farmer_phone': farmer.get('phone'),
                'farmer_location': farmer.get('location'),
            })

        return jsonify({'products': products, 'pagination': _page_meta(page, per_page, result.count)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_admin
def remove_product(product_id):
    """Remove any listing (e.g. spam, fraud, policy violation)."""
    data = request.get_json(silent=True) or {}
    reason = (data.get('reason') or '').strip()[:500]

    try:
        supabase = get_supabase()
        existing = supabase.table('products').select('id, name, farmer_id').eq('id', product_id).execute()
        if not existing.data:
            return jsonify({'error': 'Product not found'}), 404

        product = existing.data[0]
        supabase.table('products').delete().eq('id', product_id).execute()
        _log_action('product.removed', 'product', product_id, {
            'name': product['name'],
            'farmer_id': product['farmer_id'],
            'reason': reason,
        })

        return jsonify({'message': 'Product removed successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# MARKET PRICES
# ============================================
@admin_bp.route('/market-prices', methods=['POST'])
@require_admin
def create_market_price():
    """Record a new market price observation."""
    data = request.get_json(silent=True) or {}
    crop_name = (data.get('crop_name') or '').strip()
    market_location = (data.get('market_location') or '').strip()

    if not crop_name or not market_location:
        return jsonify({'error': 'crop_name and market_location are required'}), 400
    try:
        price = float(data.get('price'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Price must be a valid number'}), 400
    if price <= 0:
        return jsonify({'error': 'Price must be greater than 0'}), 400

    try:
        result = get_supabase().table('market_prices').insert({
            'crop_name': crop_name[:100],
            'market_location': market_location[:100],
            'price': price,
        }).execute()
        created = result.data[0] if result.data else None
        _log_action('market_price.created', 'market_price', created['id'] if created else '', {
            'crop_name': crop_name, 'market_location': market_location, 'price': price,
        })

        return jsonify({'message': 'Market price recorded', 'price': created}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/market-prices/<int:price_id>', methods=['DELETE'])
@require_admin
def delete_market_price(price_id):
    """Delete an incorrect market price entry."""
    try:
        supabase = get_supabase()
        existing = supabase.table('market_prices').select('*').eq('id', price_id).execute()
        if not existing.data:
            return jsonify({'error': 'Market price not found'}), 404

        supabase.table('market_prices').delete().eq('id', price_id).execute()
        entry = existing.data[0]
        _log_action('market_price.deleted', 'market_price', price_id, {
            'crop_name': entry.get('crop_name'),
            'market_location': entry.get('market_location'),
            'price': entry.get('price'),
        })

        return jsonify({'message': 'Market price deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# AUDIT LOG
# ============================================
@admin_bp.route('/audit-log', methods=['GET'])
@require_admin
def get_audit_log():
    """Most recent admin actions."""
    try:
        page, per_page, start, end = _page_args()
        result = get_supabase().table('admin_audit_log').select(
            '*, admin:users!admin_id(username)', count='exact'
        ).order('created_at', desc=True).range(start, end).execute()

        entries = [
            {**e, 'admin_name': (e.pop('admin', None) or {}).get('username')}
            for e in result.data or []
        ]
        return jsonify({'entries': entries, 'pagination': _page_meta(page, per_page, result.count)}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
