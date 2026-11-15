
from src.ai.sql_agent import validate_sql


def main():
    valid_query = """
        SELECT restaurant_name, total_orders
        FROM analytics.vw_restaurant_performance
        ORDER BY total_orders DESC
    """

    assert "LIMIT 100" in validate_sql(valid_query)

    invalid_queries = [
        "DELETE FROM analytics.vw_order_summary",
        "SELECT * FROM raw.orders",
        "SELECT * FROM public.vw_order_summary",
        "SELECT * FROM analytics.vw_order_summary; SELECT 1",
        "UPDATE analytics.vw_order_summary SET total_orders = 0",
    ]

    for query in invalid_queries:
        try:
            validate_sql(query)
            raise AssertionError(f"Unsafe query was accepted: {query}")
        except ValueError:
            pass

    print("SQL SAFETY TESTS PASSED")


if __name__ == "__main__":
    main()
