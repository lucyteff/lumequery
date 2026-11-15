
import re

import sqlglot
from sqlglot import exp
from sqlalchemy import text

from src.ai.gemini_client import generate_text
from src.database import engine


ALLOWED_VIEWS = {
    "vw_order_summary",
    "vw_daily_performance",
    "vw_restaurant_performance",
}


def generate_sql(question):
    prompt = f"""
You are the senior SQL Agent of LumeQuery, a marketplace analytics platform.

Generate one PostgreSQL SELECT query to answer the user's question.

Available views:

1. analytics.vw_order_summary
Columns: order_id, ordered_at, order_status, customer_id,
customer_name, restaurant_id, restaurant_name, cuisine_type,
region_id, region_name, city, state, subtotal, delivery_fee,
discount_amount, total_amount, item_count, total_quantity,
calculated_subtotal, payment_method, payment_status,
payment_amount, paid_at, delivery_status, courier_id,
estimated_delivery_at, delivered_at.

2. analytics.vw_daily_performance
Columns: order_date, total_orders, delivered_orders,
cancelled_orders, total_order_value, delivered_order_value,
average_order_value, average_items_per_order.

3. analytics.vw_restaurant_performance
Columns: restaurant_id, restaurant_name, cuisine_type,
region_name, city, state, total_orders, delivered_orders,
cancelled_orders, total_order_value, average_order_value,
cancellation_rate.

Rules:
- Use only these three views, with the analytics schema.
- Generate only one SELECT query.
- Never modify data or database structures.
- Do not invent columns or tables.
- Use PostgreSQL syntax.
- Return only SQL, without Markdown or explanations.
- Limit results to 100 rows.

User question: {question}
"""

    return generate_text(prompt).strip()


def validate_sql(query):
    query = re.sub(r"```(?:sql)?|```", "", query, flags=re.IGNORECASE).strip()
    query = query.rstrip(";").strip()

    statements = sqlglot.parse(query, read="postgres")

    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Only one SELECT statement is allowed.")

    parsed = statements[0]

    cte_names = {
        cte.alias_or_name.lower()
        for cte in parsed.find_all(exp.CTE)
    }

    tables = [
        table for table in parsed.find_all(exp.Table)
        if table.name.lower() not in cte_names
    ]

    if not tables:
        raise ValueError("Query must reference an authorized view.")

    for table in tables:
        if (
            table.name.lower() not in ALLOWED_VIEWS
            or table.db.lower() != "analytics"
            or table.catalog
        ):
            raise ValueError("Query references an unauthorized table or schema.")

    if not parsed.args.get("limit"):
        parsed = parsed.limit(100)

    return parsed.sql(dialect="postgres")


def execute_sql(query):
    safe_query = validate_sql(query)

    with engine.begin() as connection:
        connection.execute(text("SET TRANSACTION READ ONLY"))
        connection.execute(text("SET LOCAL statement_timeout = '5s'"))

        result = connection.execute(text(safe_query))
        columns = list(result.keys())
        rows = result.mappings().all()

    return {
        "columns": columns,
        "rows": [dict(row) for row in rows],
        "row_count": len(rows),
        "sql": safe_query,
    }


def run_sql_agent(question):
    query = generate_sql(question)
    return execute_sql(query)
