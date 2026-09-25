from datetime import datetime, timezone

from app.services.admin_metrics import build_overview, daily_series, parse_timestamp

NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)


def test_parse_timestamp_handles_supabase_formats():
    assert parse_timestamp('2026-09-24T10:00:00.12345+00:00').microsecond == 123450
    assert parse_timestamp('2026-09-24T10:00:00Z').tzinfo is not None
    assert parse_timestamp('2026-09-24T10:00:00').tzinfo == timezone.utc
    assert parse_timestamp(None) is None


def test_daily_series_buckets_by_day_and_fills_gaps():
    rows = [
        {'created_at': '2026-09-25T01:00:00+00:00'},
        {'created_at': '2026-09-25T20:00:00+00:00'},
        {'created_at': '2026-09-23T08:00:00+00:00'},
        {'created_at': '2026-01-01T08:00:00+00:00'},  # outside window
    ]
    series = daily_series(rows, 'created_at', 3, NOW)
    assert series == [
        {'date': '2026-09-23', 'count': 1},
        {'date': '2026-09-24', 'count': 0},
        {'date': '2026-09-25', 'count': 2},
    ]


def test_build_overview_totals():
    users = [
        {'id': 'a', 'role': 'admin', 'created_at': '2026-01-01T00:00:00+00:00'},
        {'id': 'f', 'role': 'farmer', 'created_at': '2026-09-24T00:00:00+00:00'},
        {'id': 'b', 'role': 'buyer', 'created_at': '2026-09-10T00:00:00+00:00'},
    ]
    products = [
        {'id': 1, 'category': 'Céréales', 'price_per_kg': '1200.00', 'quantity_available': '10',
         'created_at': '2026-09-24T00:00:00+00:00'},
        {'id': 2, 'category': 'Céréales', 'price_per_kg': 500, 'quantity_available': 0,
         'created_at': '2026-07-01T00:00:00+00:00'},
        {'id': 3, 'category': None, 'price_per_kg': 100, 'quantity_available': 5,
         'created_at': '2026-09-20T00:00:00+00:00'},
    ]
    chat = [
        {'sender': 'user', 'timestamp': '2026-09-24T00:00:00+00:00'},
        {'sender': 'bot', 'timestamp': '2026-09-24T00:00:00+00:00'},
    ]

    overview = build_overview(users, products, chat, now=NOW)

    assert overview['users']['total'] == 3
    assert overview['users']['by_role'] == {'farmer': 1, 'buyer': 1, 'admin': 1}
    assert overview['users']['new_7d'] == 1
    assert overview['users']['new_30d'] == 2
    assert overview['products']['total'] == 3
    assert overview['products']['new_7d'] == 2
    assert overview['products']['out_of_stock'] == 1
    assert overview['products']['stock_kg'] == 15
    assert overview['products']['stock_value'] == 12500
    assert overview['products']['by_category'][0] == {'category': 'Céréales', 'count': 2}
    assert {'category': 'Autres', 'count': 1} in overview['products']['by_category']
    assert overview['chatbot']['questions_7d'] == 1
    assert len(overview['timeseries']['signups']) == 30


def test_build_overview_empty():
    overview = build_overview([], [], [], now=NOW)
    assert overview['users']['total'] == 0
    assert overview['products']['stock_value'] == 0
    assert overview['products']['by_category'] == []
