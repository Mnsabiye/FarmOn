"""
Aggregations for the admin dashboard.

These functions are pure: they take rows already fetched from Supabase and
return plain dicts, so they can be tested without a database.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone

ROLES = ('farmer', 'buyer', 'admin')


def parse_timestamp(value):
    """Parse a Supabase timestamp string into an aware UTC datetime."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = value.replace('Z', '+00:00')
    # Postgres may return fractional seconds with fewer than 6 digits
    if '.' in text:
        head, tail = text.split('.', 1)
        digits = ''.join(c for c in tail if c.isdigit())
        rest = tail[len(digits):]
        text = f"{head}.{digits[:6].ljust(6, '0')}{rest}"
    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _count_since(rows, field, since):
    return sum(1 for r in rows if (ts := parse_timestamp(r.get(field))) and ts >= since)


def daily_series(rows, field, days, now):
    """Count rows per UTC day for the last `days` days, oldest first."""
    start = (now - timedelta(days=days - 1)).date()
    counts = Counter()
    for row in rows:
        ts = parse_timestamp(row.get(field))
        if ts and ts.date() >= start:
            counts[ts.date()] += 1
    return [
        {'date': (start + timedelta(days=i)).isoformat(), 'count': counts[start + timedelta(days=i)]}
        for i in range(days)
    ]


def build_overview(users, products, chat_messages, now=None, days=30):
    """
    Build the dashboard overview.

    users:         rows with at least id, role, created_at
    products:      rows with at least id, category, price_per_kg, quantity_available, created_at
    chat_messages: rows with at least sender, timestamp
    """
    now = now or datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    role_counts = Counter(u.get('role') for u in users)
    category_counts = Counter(p.get('category') or 'Autres' for p in products)

    stock_kg = sum(float(p.get('quantity_available') or 0) for p in products)
    stock_value = sum(
        float(p.get('price_per_kg') or 0) * float(p.get('quantity_available') or 0)
        for p in products
    )
    out_of_stock = sum(1 for p in products if float(p.get('quantity_available') or 0) <= 0)

    user_questions = [m for m in chat_messages if m.get('sender') == 'user']

    return {
        'generated_at': now.isoformat(),
        'users': {
            'total': len(users),
            'by_role': {role: role_counts.get(role, 0) for role in ROLES},
            'new_7d': _count_since(users, 'created_at', week_ago),
            'new_30d': _count_since(users, 'created_at', month_ago),
        },
        'products': {
            'total': len(products),
            'new_7d': _count_since(products, 'created_at', week_ago),
            'new_30d': _count_since(products, 'created_at', month_ago),
            'out_of_stock': out_of_stock,
            'stock_kg': round(stock_kg, 2),
            'stock_value': round(stock_value, 2),
            'by_category': [
                {'category': c, 'count': n} for c, n in category_counts.most_common()
            ],
        },
        'chatbot': {
            'questions_7d': _count_since(user_questions, 'timestamp', week_ago),
            'questions_30d': _count_since(user_questions, 'timestamp', month_ago),
        },
        'timeseries': {
            'days': days,
            'signups': daily_series(users, 'created_at', days, now),
            'listings': daily_series(products, 'created_at', days, now),
        },
    }


def paginate(rows, page, per_page):
    """Slice a list for page-based pagination; returns (items, meta)."""
    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)
    total = len(rows)
    start = (page - 1) * per_page
    return rows[start:start + per_page], {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': max((total + per_page - 1) // per_page, 1),
    }
