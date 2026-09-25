from types import SimpleNamespace

from conftest import ADMIN_ID, BUYER_ID, FARMER_ID


# ---------- access control ----------

def test_requires_authorization_header(client):
    assert client.get('/api/admin/overview').status_code == 401


def test_rejects_invalid_token(client):
    res = client.get('/api/admin/overview', headers={'Authorization': 'Bearer nope'})
    assert res.status_code == 401


def test_rejects_non_admin(client):
    res = client.get('/api/admin/overview', headers={'Authorization': 'Bearer farmer-token'})
    assert res.status_code == 403


# ---------- overview ----------

def test_overview(client, admin_headers):
    res = client.get('/api/admin/overview', headers=admin_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body['users']['total'] == 3
    assert body['products']['total'] == 2
    assert body['products']['out_of_stock'] == 1
    assert len(body['recent_products']) == 2
    assert len(body['recent_users']) == 3


# ---------- users ----------

def test_list_users_filters_by_role_and_adds_counts(client, admin_headers, db):
    db.auth.admin.users = [SimpleNamespace(id=FARMER_ID, app_metadata={'suspended': True})]
    res = client.get('/api/admin/users?role=farmer', headers=admin_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert [u['id'] for u in body['users']] == [FARMER_ID]
    assert body['users'][0]['product_count'] == 2
    assert body['users'][0]['suspended'] is True
    assert body['pagination']['total'] == 1


def test_list_users_search_is_sanitized(client, admin_headers, db):
    client.get('/api/admin/users?q=jean),role.eq.admin', headers=admin_headers)
    or_params = [c[2] for c in db.calls if c[:2] == ('param', 'or')]
    assert or_params == ['(username.ilike.*jean  role.eq.admin*,email.ilike.*jean  role.eq.admin*)']


def test_ilike_any_builds_real_postgrest_param():
    from postgrest import SyncPostgrestClient
    from app.routes.admin import _ilike_any

    query = SyncPostgrestClient('http://localhost').table('users').select('*', count='exact')
    query = _ilike_any(query, ('username', 'email'), 'jean')
    assert query.params['or'] == '(username.ilike.*jean*,email.ilike.*jean*)'


def test_change_role(client, admin_headers, db):
    res = client.patch(f'/api/admin/users/{BUYER_ID}/role', json={'role': 'farmer'}, headers=admin_headers)
    assert res.status_code == 200
    buyer = next(u for u in db.tables['users'] if u['id'] == BUYER_ID)
    assert buyer['role'] == 'farmer'
    log = db.tables['admin_audit_log'][-1]
    assert log['action'] == 'user.role_changed'
    assert log['details'] == {'username': 'paul', 'from': 'buyer', 'to': 'farmer'}
    assert log['admin_id'] == ADMIN_ID


def test_change_role_rejects_invalid_role(client, admin_headers):
    res = client.patch(f'/api/admin/users/{BUYER_ID}/role', json={'role': 'superuser'}, headers=admin_headers)
    assert res.status_code == 400


def test_cannot_change_own_role(client, admin_headers):
    res = client.patch(f'/api/admin/users/{ADMIN_ID}/role', json={'role': 'buyer'}, headers=admin_headers)
    assert res.status_code == 400


def test_change_role_unknown_user(client, admin_headers):
    res = client.patch('/api/admin/users/11111111-1111-1111-1111-111111111111/role',
                       json={'role': 'buyer'}, headers=admin_headers)
    assert res.status_code == 404


def test_suspend_and_restore(client, admin_headers, db):
    assert client.post(f'/api/admin/users/{FARMER_ID}/suspend', headers=admin_headers).status_code == 200
    assert client.post(f'/api/admin/users/{FARMER_ID}/restore', headers=admin_headers).status_code == 200
    (uid1, attrs1), (uid2, attrs2) = db.auth.admin.updates
    assert uid1 == uid2 == FARMER_ID
    assert attrs1['app_metadata'] == {'suspended': True} and attrs1['ban_duration'] != 'none'
    assert attrs2 == {'ban_duration': 'none', 'app_metadata': {'suspended': False}}
    assert [e['action'] for e in db.tables['admin_audit_log']] == ['user.suspended', 'user.restored']
    assert db.tables['admin_audit_log'][0]['details'] == {'username': 'jean'}


def test_cannot_suspend_self(client, admin_headers):
    assert client.post(f'/api/admin/users/{ADMIN_ID}/suspend', headers=admin_headers).status_code == 400


# ---------- products ----------

def test_list_products_with_filters(client, admin_headers):
    res = client.get('/api/admin/products?stock=out', headers=admin_headers)
    assert [p['id'] for p in res.get_json()['products']] == [2]

    res = client.get('/api/admin/products?q=maï', headers=admin_headers)
    assert [p['id'] for p in res.get_json()['products']] == [1]


def test_list_products_pagination(client, admin_headers):
    res = client.get('/api/admin/products?per_page=1&page=2', headers=admin_headers)
    body = res.get_json()
    assert len(body['products']) == 1
    assert body['pagination'] == {'page': 2, 'per_page': 1, 'total': 2, 'pages': 2}


def test_remove_product_logs_reason(client, admin_headers, db):
    res = client.delete('/api/admin/products/1', json={'reason': 'Spam'}, headers=admin_headers)
    assert res.status_code == 200
    assert [p['id'] for p in db.tables['products']] == [2]
    log = db.tables['admin_audit_log'][-1]
    assert log['action'] == 'product.removed'
    assert log['details']['reason'] == 'Spam'


def test_remove_missing_product(client, admin_headers):
    assert client.delete('/api/admin/products/999', headers=admin_headers).status_code == 404


# ---------- market prices ----------

def test_create_market_price(client, admin_headers, db):
    res = client.post('/api/admin/market-prices',
                      json={'crop_name': 'Riz', 'market_location': 'Ngozi', 'price': '2100'},
                      headers=admin_headers)
    assert res.status_code == 201
    assert db.tables['market_prices'][-1]['price'] == 2100.0


def test_create_market_price_validation(client, admin_headers):
    for payload in (
        {'crop_name': '', 'market_location': 'Ngozi', 'price': 10},
        {'crop_name': 'Riz', 'market_location': 'Ngozi', 'price': 'abc'},
        {'crop_name': 'Riz', 'market_location': 'Ngozi', 'price': -5},
    ):
        assert client.post('/api/admin/market-prices', json=payload, headers=admin_headers).status_code == 400


def test_delete_market_price(client, admin_headers, db):
    assert client.delete('/api/admin/market-prices/1', headers=admin_headers).status_code == 200
    assert db.tables['market_prices'] == []
    assert client.delete('/api/admin/market-prices/1', headers=admin_headers).status_code == 404


# ---------- audit log ----------

def test_audit_log_lists_entries(client, admin_headers):
    client.post(f'/api/admin/users/{FARMER_ID}/suspend', headers=admin_headers)
    res = client.get('/api/admin/audit-log', headers=admin_headers)
    assert res.status_code == 200
    assert res.get_json()['entries'][0]['action'] == 'user.suspended'


def test_fake_query_only_uses_real_postgrest_methods():
    """Guard against the fake drifting from the pinned client's API."""
    from postgrest import SyncPostgrestClient
    from conftest import FakeQuery

    table = SyncPostgrestClient('http://localhost').table('users')
    builder = table.select('*', count='exact')
    for name in ('select', 'insert', 'update', 'delete'):
        assert hasattr(table, name), name
    for name in [n for n in vars(FakeQuery) if not n.startswith('_')]:
        if name in ('select', 'insert', 'update', 'delete'):
            continue
        assert hasattr(builder, name), f'postgrest builder has no {name}()'
