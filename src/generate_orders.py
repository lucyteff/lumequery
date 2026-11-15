
import random
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from sqlalchemy import text

from src.database import engine

random.seed(42)

TOTAL_ORDERS = 20_000

PAYMENT_METHODS = [
    "pix",
    "credit_card",
    "debit_card",
    "cash",
]

ORDER_STATUSES = [
    "pending",
    "confirmed",
    "preparing",
    "ready",
    "out_for_delivery",
    "delivered",
    "cancelled",
]

ORDER_STATUS_WEIGHTS = [3, 8, 8, 5, 8, 63, 5]


def load_reference_data(connection):
    customers = connection.execute(text("""
        SELECT customer_id, region_id, created_at
        FROM raw.customers
    """)).mappings().all()

    restaurants = connection.execute(text("""
        SELECT restaurant_id, created_at
        FROM raw.restaurants
    """)).mappings().all()

    menu_items = connection.execute(text("""
        SELECT menu_item_id, restaurant_id, current_price
        FROM raw.menu_items
        WHERE is_active = TRUE
    """)).mappings().all()

    couriers = connection.execute(text("""
        SELECT courier_id, region_id
        FROM raw.couriers
        WHERE is_active = TRUE
    """)).mappings().all()

    return customers, restaurants, menu_items, couriers


def group_menu_items(menu_items):
    grouped = defaultdict(list)

    for item in menu_items:
        grouped[item["restaurant_id"]].append(item)

    return grouped


def random_order_date(customer, restaurant, end_date):
    start_date = max(
        customer["created_at"],
        restaurant["created_at"],
    )

    seconds_available = int(
        (end_date - start_date).total_seconds()
    )

    if seconds_available <= 0:
        return end_date

    return start_date + timedelta(
        seconds=random.randint(0, seconds_available)
    )


def generate_order_status():
    return random.choices(
        ORDER_STATUSES,
        weights=ORDER_STATUS_WEIGHTS,
        k=1,
    )[0]


def generate_payment_status(order_status):
    if order_status == "cancelled":
        return random.choice(["failed", "refunded", "pending"])

    return random.choices(
        ["paid", "pending", "failed", "refunded"],
        weights=[94, 4, 1, 1],
        k=1,
    )[0]


def generate_delivery(order_id, courier_id, order_status, ordered_at):
    if order_status == "cancelled":
        return None

    estimated = ordered_at + timedelta(minutes=45)

    accepted_at = None
    picked_up_at = None
    delivered_at = None

    if order_status in [
        "confirmed",
        "preparing",
        "ready",
        "out_for_delivery",
        "delivered",
    ]:
        accepted_at = ordered_at + timedelta(
            minutes=random.randint(2, 12)
        )

    if order_status in ["out_for_delivery", "delivered"]:
        picked_up_at = accepted_at + timedelta(
            minutes=random.randint(10, 25)
        )

    if order_status == "delivered":
        delivered_at = picked_up_at + timedelta(
            minutes=random.randint(15, 60)
        )
        delivery_status = "delivered"

    elif order_status == "out_for_delivery":
        delivery_status = "picked_up"

    elif accepted_at is not None:
        delivery_status = "assigned"

    else:
        delivery_status = "pending"
        courier_id = None

    return {
        "order_id": order_id,
        "courier_id": courier_id,
        "status": delivery_status,
        "estimated_delivery_at": estimated,
        "accepted_at": accepted_at,
        "picked_up_at": picked_up_at,
        "delivered_at": delivered_at,
    }


def generate_orders(connection):
    existing = connection.execute(
        text("SELECT COUNT(*) FROM raw.orders")
    ).scalar()

    if existing > 0:
        print("Orders already exist. Generation skipped.")
        return

    customers, restaurants, menu_items, couriers = (
        load_reference_data(connection)
    )

    if not customers or not restaurants or not menu_items or not couriers:
        raise ValueError(
            "Missing reference data. Generate customers, restaurants, "
            "menu items and couriers first."
        )

    menu_by_restaurant = group_menu_items(menu_items)

    restaurant_by_id = {
        restaurant["restaurant_id"]: restaurant
        for restaurant in restaurants
    }

    couriers_by_region = defaultdict(list)

    for courier in couriers:
        couriers_by_region[courier["region_id"]].append(
            courier["courier_id"]
        )

    orders = []
    order_items = []
    deliveries = []
    payments = []

    end_date = datetime.now(timezone.utc)

    for _ in range(TOTAL_ORDERS):
        customer = random.choice(customers)
        restaurant = random.choice(restaurants)

        restaurant_id = restaurant["restaurant_id"]
        customer_id = customer["customer_id"]
        region_id = restaurant["region_id"]

        available_items = menu_by_restaurant.get(restaurant_id, [])

        if not available_items:
            raise ValueError(
                f"Restaurant {restaurant_id} has no active menu items."
            )

        ordered_at = random_order_date(
            customer,
            restaurant,
            end_date,
        )

        selected_items = random.sample(
            available_items,
            k=random.randint(1, min(4, len(available_items))),
        )

        subtotal = 0

        current_order_items = []

        for item in selected_items:
            quantity = random.randint(1, 3)
            unit_price = round(float(item["current_price"]), 2)

            subtotal += quantity * unit_price

            current_order_items.append({
                "menu_item_id": item["menu_item_id"],
                "quantity": quantity,
                "unit_price": unit_price,
            })

        subtotal = round(subtotal, 2)

        delivery_fee = round(random.uniform(3, 15), 2)
        discount_amount = round(
            random.uniform(0, min(20, subtotal)),
            2,
        )

        total_amount = round(
            subtotal + delivery_fee - discount_amount,
            2,
        )

        status = generate_order_status()

        orders.append({
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            "region_id": region_id,
            "ordered_at": ordered_at,
            "status": status,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
        })

        order_items.append(current_order_items)

        payment_status = generate_payment_status(status)

        paid_at = None

        if payment_status in ["paid", "refunded"]:
            paid_at = ordered_at + timedelta(
                minutes=random.randint(1, 10)
            )

        payments.append({
            "payment_method": random.choice(PAYMENT_METHODS),
            "payment_status": payment_status,
            "amount": total_amount,
            "paid_at": paid_at,
        })

    # Reserve generated identity values for all orders
    order_ids = connection.execute(
        text("""
            SELECT nextval(
                pg_get_serial_sequence('raw.orders', 'order_id')
            )
            FROM generate_series(1, :quantity)
        """),
        {"quantity": TOTAL_ORDERS},
    ).scalars().all()

    order_records = []

    for order_id, order in zip(order_ids, orders):
        order_records.append({
            "order_id": order_id,
            **order,
        })

    # Insert orders
    connection.execute(
        text("""
            INSERT INTO raw.orders (
                order_id,
                customer_id,
                restaurant_id,
                region_id,
                ordered_at,
                status,
                subtotal,
                delivery_fee,
                discount_amount,
                total_amount
            )
            OVERRIDING SYSTEM VALUE
            VALUES (
                :order_id,
                :customer_id,
                :restaurant_id,
                :region_id,
                :ordered_at,
                :status,
                :subtotal,
                :delivery_fee,
                :discount_amount,
                :total_amount
            )
        """),
        order_records,
    )

    # Insert order items, deliveries and payments
    item_records = []
    delivery_records = []
    payment_records = []

    for order_id, order, items, payment in zip(
        order_ids,
        orders,
        order_items,
        payments,
    ):
        for item in items:
            item_records.append({
                "order_id": order_id,
                **item,
            })

        region_couriers = couriers_by_region.get(
            order["region_id"],
            [],
        )

        courier_id = (
            random.choice(region_couriers)
            if region_couriers
            else random.choice(couriers)["courier_id"]
        )

        delivery = generate_delivery(
            order_id,
            courier_id,
            order["status"],
            order["ordered_at"],
        )

        if delivery is not None:
            delivery_records.append(delivery)

        payment_records.append({
            "order_id": order_id,
            **payment,
        })

    connection.execute(
        text("""
            INSERT INTO raw.order_items (
                order_id,
                menu_item_id,
                quantity,
                unit_price
            )
            VALUES (
                :order_id,
                :menu_item_id,
                :quantity,
                :unit_price
            )
        """),
        item_records,
    )

    connection.execute(
        text("""
            INSERT INTO raw.deliveries (
                order_id,
                courier_id,
                status,
                estimated_delivery_at,
                accepted_at,
                picked_up_at,
                delivered_at
            )
            VALUES (
                :order_id,
                :courier_id,
                :status,
                :estimated_delivery_at,
                :accepted_at,
                :picked_up_at,
                :delivered_at
            )
        """),
        delivery_records,
    )

    connection.execute(
        text("""
            INSERT INTO raw.payments (
                order_id,
                payment_method,
                payment_status,
                amount,
                paid_at
            )
            VALUES (
                :order_id,
                :payment_method,
                :payment_status,
                :amount,
                :paid_at
            )
        """),
        payment_records,
    )

    print(f"{len(orders)} orders inserted successfully.")
    print(f"{len(item_records)} order items inserted successfully.")
    print(f"{len(delivery_records)} deliveries inserted successfully.")
    print(f"{len(payment_records)} payments inserted successfully.")


if __name__ == "__main__":
    print("Starting order generation...")

    with engine.begin() as connection:
        generate_orders(connection)

    print("Order generation completed.")
