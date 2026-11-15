
import random
from datetime import datetime, timedelta, timezone

import pandas as pd
from faker import Faker
from sqlalchemy import text

from src.database import engine

fake = Faker("pt_BR")
Faker.seed(42)
random.seed(42)

# Dataset configuration
DATASET_CONFIG = {
    "regions": 10,
    "customers": 5000,
    "restaurants": 100,
    "menu_items": 500,
    "couriers": 150,
    "orders": 20000,
}

END_DATE = datetime.now(timezone.utc)
START_DATE = END_DATE - timedelta(days=180)

# Fictional service regions
REGIONS = [
    ("Centro", "Porto Alegre", "RS"),
    ("Zona Norte", "Porto Alegre", "RS"),
    ("Zona Sul", "Porto Alegre", "RS"),
    ("Centro", "São Paulo", "SP"),
    ("Zona Sul", "São Paulo", "SP"),
    ("Centro", "Rio de Janeiro", "RJ"),
    ("Zona Oeste", "Rio de Janeiro", "RJ"),
    ("Centro", "Curitiba", "PR"),
    ("Centro", "Florianópolis", "SC"),
    ("Centro", "Belo Horizonte", "MG"),
]

CUISINE_TYPES = [
    "Brazilian", "Italian", "Japanese", "Mexican",
    "Hamburger", "Pizza", "Healthy", "Bakery",
]

MENU_CATALOG = {
    "Brazilian": {
        "category": "Main course",
        "items": [
            "Feijoada", "Strogonoff de frango", "Escondidinho",
            "Frango grelhado", "Picanha com fritas",
            "Parmegiana", "Arroz carreteiro",
        ],
        "price": (22, 65),
    },
    "Italian": {
        "category": "Main course",
        "items": [
            "Lasanha bolonhesa", "Spaghetti carbonara",
            "Fettuccine Alfredo", "Ravioli de queijo",
            "Nhoque ao sugo", "Penne ao molho pesto",
        ],
        "price": (25, 70),
    },
    "Japanese": {
        "category": "Japanese food",
        "items": [
            "Combo sushi", "Temaki salmão",
            "Hot roll", "Yakisoba", "Sashimi",
            "Uramaki especial",
        ],
        "price": (25, 85),
    },
    "Mexican": {
        "category": "Mexican food",
        "items": [
            "Burrito de carne", "Tacos de frango",
            "Quesadilla", "Nachos com guacamole",
            "Burrito vegetariano",
        ],
        "price": (20, 55),
    },
    "Hamburger": {
        "category": "Hamburger",
        "items": [
            "Cheeseburger", "Bacon burger",
            "Chicken burger", "Double burger",
            "Veggie burger", "Smash burger",
        ],
        "price": (18, 45),
    },
    "Pizza": {
        "category": "Pizza",
        "items": [
            "Pizza Margherita", "Pizza Calabresa",
            "Pizza Portuguesa", "Pizza Quatro Queijos",
            "Pizza Frango com Catupiry",
        ],
        "price": (35, 80),
    },
    "Healthy": {
        "category": "Healthy food",
        "items": [
            "Salada Caesar", "Bowl de frango",
            "Bowl vegetariano", "Wrap integral",
            "Filé de frango com legumes",
        ],
        "price": (20, 48),
    },
    "Bakery": {
        "category": "Bakery",
        "items": [
            "Pão de queijo", "Croissant",
            "Sanduíche natural", "Bolo de chocolate",
            "Torta de frango", "Empada",
        ],
        "price": (6, 30),
    },
}

VEHICLE_TYPES = ["motorcycle", "bicycle", "car"]


# -----------------------------------------
# REGIONS
# -----------------------------------------

def generate_regions():
    return pd.DataFrame([
        {
            "name": name,
            "city": city,
            "state": state,
            "is_active": True,
        }
        for name, city, state in REGIONS
    ])


def insert_regions(df):
    with engine.connect() as connection:
        existing = connection.execute(
            text("SELECT COUNT(*) FROM raw.regions")
        ).scalar()

    if existing > 0:
        print("Regions already exist. Insertion skipped.")
        return

    df.to_sql(
        "regions", engine, schema="raw",
        if_exists="append", index=False,
    )
    print(f"{len(df)} regions inserted successfully.")


# -----------------------------------------
# CUSTOMERS
# -----------------------------------------

def generate_customers():
    with engine.connect() as connection:
        region_ids = connection.execute(
            text("SELECT region_id FROM raw.regions")
        ).scalars().all()

        existing = connection.execute(
            text("SELECT COUNT(*) FROM raw.customers")
        ).scalar()

    if existing > 0:
        print("Customers already exist. Generation skipped.")
        return None

    customers = []

    for _ in range(DATASET_CONFIG["customers"]):
        customers.append({
            "region_id": random.choice(region_ids),
            "customer_name": fake.name(),
            "email": fake.unique.email(),
            "created_at": fake.date_time_between(
                start_date=START_DATE,
                end_date=END_DATE,
                tzinfo=timezone.utc,
            ),
            "is_active": random.choices(
                [True, False], weights=[95, 5], k=1
            )[0],
        })

    return pd.DataFrame(customers)


def insert_customers(df):
    if df is None:
        return

    df.to_sql(
        "customers", engine, schema="raw",
        if_exists="append", index=False, chunksize=1000,
    )
    print(f"{len(df)} customers inserted successfully.")


# -----------------------------------------
# RESTAURANTS
# -----------------------------------------

def generate_restaurants():
    with engine.connect() as connection:
        region_ids = connection.execute(
            text("SELECT region_id FROM raw.regions")
        ).scalars().all()

        existing = connection.execute(
            text("SELECT COUNT(*) FROM raw.restaurants")
        ).scalar()

    if existing > 0:
        print("Restaurants already exist. Generation skipped.")
        return None

    restaurants = []

    for _ in range(DATASET_CONFIG["restaurants"]):
        restaurants.append({
            "region_id": random.choice(region_ids),
            "restaurant_name": fake.company(),
            "cuisine_type": random.choice(CUISINE_TYPES),
            "created_at": fake.date_time_between(
                start_date=START_DATE,
                end_date=END_DATE,
                tzinfo=timezone.utc,
            ),
            "is_active": random.choices(
                [True, False], weights=[90, 10], k=1
            )[0],
        })

    return pd.DataFrame(restaurants)


def insert_restaurants(df):
    if df is None:
        return

    df.to_sql(
        "restaurants", engine, schema="raw",
        if_exists="append", index=False, chunksize=1000,
    )
    print(f"{len(df)} restaurants inserted successfully.")


# -----------------------------------------
# MENU ITEMS
# -----------------------------------------

def generate_menu_items():
    with engine.connect() as connection:
        restaurants = connection.execute(
            text("""
                SELECT restaurant_id, cuisine_type
                FROM raw.restaurants
            """)
        ).mappings().all()

        existing = connection.execute(
            text("SELECT COUNT(*) FROM raw.menu_items")
        ).scalar()

    if existing > 0:
        print("Menu items already exist. Generation skipped.")
        return None

    menu_items = []

    for restaurant in restaurants:
        catalog = MENU_CATALOG[restaurant["cuisine_type"]]

        for _ in range(5):
            menu_items.append({
                "restaurant_id": restaurant["restaurant_id"],
                "item_name": random.choice(catalog["items"]),
                "category": catalog["category"],
                "current_price": round(
                    random.uniform(*catalog["price"]), 2
                ),
                "is_active": random.choices(
                    [True, False], weights=[95, 5], k=1
                )[0],
            })

    return pd.DataFrame(menu_items)


def insert_menu_items(df):
    if df is None:
        return

    df.to_sql(
        "menu_items", engine, schema="raw",
        if_exists="append", index=False, chunksize=1000,
    )
    print(f"{len(df)} menu items inserted successfully.")


# -----------------------------------------
# COURIERS
# -----------------------------------------

def generate_couriers():
    with engine.connect() as connection:
        region_ids = connection.execute(
            text("SELECT region_id FROM raw.regions")
        ).scalars().all()

        existing = connection.execute(
            text("SELECT COUNT(*) FROM raw.couriers")
        ).scalar()

    if existing > 0:
        print("Couriers already exist. Generation skipped.")
        return None

    couriers = []

    for _ in range(DATASET_CONFIG["couriers"]):
        couriers.append({
            "region_id": random.choice(region_ids),
            "vehicle_type": random.choice(VEHICLE_TYPES),
            "joined_at": fake.date_time_between(
                start_date=START_DATE,
                end_date=END_DATE,
                tzinfo=timezone.utc,
            ),
            "is_active": random.choices(
                [True, False], weights=[90, 10], k=1
            )[0],
        })

    return pd.DataFrame(couriers)


def insert_couriers(df):
    if df is None:
        return

    df.to_sql(
        "couriers", engine, schema="raw",
        if_exists="append", index=False, chunksize=1000,
    )
    print(f"{len(df)} couriers inserted successfully.")


# -----------------------------------------
# MAIN EXECUTION
# -----------------------------------------

if __name__ == "__main__":
    print("Starting LumeQuery data generation...")

    regions_df = generate_regions()
    insert_regions(regions_df)

    customers_df = generate_customers()
    insert_customers(customers_df)

    restaurants_df = generate_restaurants()
    insert_restaurants(restaurants_df)

    menu_items_df = generate_menu_items()
    insert_menu_items(menu_items_df)

    couriers_df = generate_couriers()
    insert_couriers(couriers_df)

    print("Data generation process finished.")
