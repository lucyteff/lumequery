
import pytest

from src.ai.sql_agent import validate_sql


def test_accepts_authorized_view():
    query = """
        SELECT restaurant_name, total_orders
        FROM analytics.vw_restaurant_performance
        ORDER BY total_orders DESC
    """

    result = validate_sql(query)

    assert "analytics.vw_restaurant_performance" in result
    assert "LIMIT 100" in result


@pytest.mark.parametrize("query", [
    "DELETE FROM analytics.vw_order_summary",
    "SELECT * FROM raw.orders",
    "SELECT * FROM public.vw_order_summary",
    "SELECT * FROM analytics.vw_order_summary; SELECT 1",
    "UPDATE analytics.vw_order_summary SET total_orders = 0",
    "SELECT * FROM analytics.customers",
])
def test_rejects_unsafe_queries(query):
    with pytest.raises(ValueError):
        validate_sql(query)


def test_preserves_existing_limit():
    query = """
        SELECT *
        FROM analytics.vw_order_summary
        LIMIT 10
    """

    result = validate_sql(query)

    assert "LIMIT 10" in result
    assert "LIMIT 100" not in result
