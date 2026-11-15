
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database import engine


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def load_analytics():
    queries = {
        "orders": "SELECT * FROM analytics.vw_order_summary",
        "daily": "SELECT * FROM analytics.vw_daily_performance",
        "restaurants": "SELECT * FROM analytics.vw_restaurant_performance",
    }

    datasets = {}

    with engine.connect() as connection:
        for name, query in queries.items():
            datasets[name] = pd.read_sql(text(query), connection)

    return datasets


def calculate_kpis(orders):
    delivered = orders[orders["order_status"] == "delivered"]
    cancelled = orders[orders["order_status"] == "cancelled"]

    return pd.DataFrame([{
        "total_orders": len(orders),
        "delivered_orders": len(delivered),
        "cancelled_orders": len(cancelled),
        "delivery_rate_pct": round(len(delivered) / len(orders) * 100, 2),
        "cancellation_rate_pct": round(len(cancelled) / len(orders) * 100, 2),
        "average_order_value": round(delivered["total_amount"].mean(), 2),
        "delivered_sales": round(delivered["total_amount"].sum(), 2),
    }])


def main():
    print("LUMEQUERY - DATA ANALYSIS")
    print("=" * 40)

    datasets = load_analytics()

    # Calculate business indicators using pandas
    kpis = calculate_kpis(datasets["orders"])
    datasets["kpis"] = kpis

    for name, dataframe in datasets.items():
        output_path = DATA_DIR / f"{name}_analysis.csv"
        dataframe.to_csv(output_path, index=False)

        print(f"\n{name.upper()}")
        print(dataframe.head(10).to_string(index=False))
        print(f"Exported: {output_path.name}")

    print("\nANALYSIS COMPLETED")


if __name__ == "__main__":
    main()
