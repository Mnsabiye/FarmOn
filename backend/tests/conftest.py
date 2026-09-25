import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app  # noqa: E402

ADMIN_ID = '00000000-0000-0000-0000-00000000000a'
FARMER_ID = '00000000-0000-0000-0000-00000000000f'
BUYER_ID = '00000000-0000-0000-0000-00000000000b'


class FakeParams:
    """Records raw params added to a query (used for PostgREST `or=`)."""

    def __init__(self, query):
        self.query = query

    def add(self, key, value):
        self.query.db.calls.append(('param', key, value))
        return self


class FakeQuery:
    """Minimal stand-in for the postgrest query builder."""

    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.filters = []
        self.op = 'select'
        self.payload = None
        self.count_requested = False

    def select(self, _columns='*', count=None):
        self.count_requested = count is not None
        return self

    def insert(self, payload):
        self.op, self.payload = 'insert', payload
        return self

    def update(self, payload):
        self.op, self.payload = 'update', payload
        return self

    def delete(self):
        self.op = 'delete'
        return self

    def eq(self, field, value):
        self.filters.append(lambda r: str(r.get(field)) == str(value))
        return self

    def in_(self, field, values):
        values = {str(v) for v in values}
        self.filters.append(lambda r: str(r.get(field)) in values)
        return self

    def gt(self, field, value):
        self.filters.append(lambda r: float(r.get(field) or 0) > value)
        return self

    def lte(self, field, value):
        self.filters.append(lambda r: float(r.get(field) or 0) <= value)
        return self

    def ilike(self, field, pattern):
        needle = pattern.strip('%').lower()
        self.filters.append(lambda r: needle in str(r.get(field, '')).lower())
        return self

    @property
    def params(self):
        return FakeParams(self)

    @params.setter
    def params(self, _value):
        pass

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, n):
        self.limit_ = n
        return self

    def range(self, start, end):
        self.range_ = (start, end)
        return self

    def execute(self):
        rows = self.db.tables.setdefault(self.table, [])
        self.db.calls.append((self.op, self.table, self.payload))
        if self.op == 'insert':
            row = {'id': len(rows) + 1, **self.payload}
            rows.append(row)
            return SimpleNamespace(data=[row], count=None)

        matched = [r for r in rows if all(f(r) for f in self.filters)]
        if self.op == 'update':
            for r in matched:
                r.update(self.payload)
        elif self.op == 'delete':
            self.db.tables[self.table] = [r for r in rows if r not in matched]

        data = [dict(r) for r in matched]
        count = len(data) if self.count_requested else None
        if hasattr(self, 'range_'):
            data = data[self.range_[0]:self.range_[1] + 1]
        if hasattr(self, 'limit_'):
            data = data[:self.limit_]
        return SimpleNamespace(data=data, count=count)


class FakeAuthAdmin:
    def __init__(self):
        self.updates = []
        self.users = []

    def list_users(self, page=None, per_page=None):
        return self.users

    def update_user_by_id(self, uid, attributes):
        self.updates.append((uid, attributes))


class FakeSupabase:
    def __init__(self, tables):
        self.tables = tables
        self.calls = []
        self.auth = SimpleNamespace(admin=FakeAuthAdmin())

    def table(self, name):
        return FakeQuery(self, name)


@pytest.fixture
def db():
    return FakeSupabase({
        'users': [
            {'id': ADMIN_ID, 'username': 'admin', 'email': 'admin@farmon.bi', 'role': 'admin',
             'created_at': '2026-09-20T10:00:00+00:00'},
            {'id': FARMER_ID, 'username': 'jean', 'email': 'jean@farmon.bi', 'role': 'farmer',
             'created_at': '2026-09-24T10:00:00.12345+00:00'},
            {'id': BUYER_ID, 'username': 'paul', 'email': 'paul@farmon.bi', 'role': 'buyer',
             'created_at': '2026-06-01T10:00:00+00:00'},
        ],
        'products': [
            {'id': 1, 'farmer_id': FARMER_ID, 'name': 'Maïs', 'category': 'Céréales',
             'price_per_kg': 1200, 'quantity_available': 100, 'created_at': '2026-09-24T12:00:00+00:00'},
            {'id': 2, 'farmer_id': FARMER_ID, 'name': 'Tomates', 'category': 'Légumes',
             'price_per_kg': 800, 'quantity_available': 0, 'created_at': '2026-08-01T12:00:00+00:00'},
        ],
        'market_prices': [
            {'id': 1, 'crop_name': 'Maïs', 'market_location': 'Gitega', 'price': 1100},
        ],
        'chat_messages': [],
        'admin_audit_log': [],
    })


@pytest.fixture
def client(db, monkeypatch):
    import app.routes.admin as admin_routes

    tokens = {
        'admin-token': SimpleNamespace(id=ADMIN_ID),
        'farmer-token': SimpleNamespace(id=FARMER_ID),
    }

    def fake_verify(token):
        if token not in tokens:
            raise ValueError('Invalid token')
        return tokens[token]

    monkeypatch.setattr(admin_routes, 'get_supabase', lambda: db)
    monkeypatch.setattr(admin_routes, 'verify_token', fake_verify)

    app = create_app('default')
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def admin_headers():
    return {'Authorization': 'Bearer admin-token'}
