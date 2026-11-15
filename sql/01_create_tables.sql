
-- LumeQuery | Operational database structure

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 1. Regions
CREATE TABLE IF NOT EXISTS raw.regions (
    region_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. Customers
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_id BIGINT NOT NULL REFERENCES raw.regions(region_id),
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Restaurants
CREATE TABLE IF NOT EXISTS raw.restaurants (
    restaurant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_id BIGINT NOT NULL REFERENCES raw.regions(region_id),
    restaurant_name VARCHAR(150) NOT NULL,
    cuisine_type VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 4. Menu items
CREATE TABLE IF NOT EXISTS raw.menu_items (
    menu_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    restaurant_id BIGINT NOT NULL REFERENCES raw.restaurants(restaurant_id),
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(80),
    current_price NUMERIC(10,2) NOT NULL CHECK (current_price >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Couriers
CREATE TABLE IF NOT EXISTS raw.couriers (
    courier_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_id BIGINT NOT NULL REFERENCES raw.regions(region_id),
    vehicle_type VARCHAR(30) NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 6. Orders
CREATE TABLE IF NOT EXISTS raw.orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES raw.customers(customer_id),
    restaurant_id BIGINT NOT NULL REFERENCES raw.restaurants(restaurant_id),
    region_id BIGINT NOT NULL REFERENCES raw.regions(region_id),
    ordered_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(30) NOT NULL
        CHECK (status IN (
            'pending', 'confirmed', 'preparing',
            'ready', 'out_for_delivery', 'delivered', 'cancelled'
        )),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0),
    delivery_fee NUMERIC(10,2) NOT NULL CHECK (delivery_fee >= 0),
    discount_amount NUMERIC(10,2) NOT NULL DEFAULT 0
        CHECK (discount_amount >= 0),
    total_amount NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    CHECK (total_amount = subtotal + delivery_fee - discount_amount)
);

-- 7. Order items
CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES raw.orders(order_id),
    menu_item_id BIGINT NOT NULL REFERENCES raw.menu_items(menu_item_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0)
);

-- 8. Deliveries
CREATE TABLE IF NOT EXISTS raw.deliveries (
    delivery_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES raw.orders(order_id),
    courier_id BIGINT REFERENCES raw.couriers(courier_id),
    status VARCHAR(30) NOT NULL
        CHECK (status IN (
            'pending', 'assigned', 'picked_up',
            'delivered', 'failed', 'cancelled'
        )),
    estimated_delivery_at TIMESTAMPTZ,
    accepted_at TIMESTAMPTZ,
    picked_up_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ
);

-- 9. Payments
CREATE TABLE IF NOT EXISTS raw.payments (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES raw.orders(order_id),
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL
        CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    paid_at TIMESTAMPTZ
);

-- Indexes for commonly used relationships and analytical filters
CREATE INDEX IF NOT EXISTS idx_customers_region
    ON raw.customers(region_id);

CREATE INDEX IF NOT EXISTS idx_restaurants_region
    ON raw.restaurants(region_id);

CREATE INDEX IF NOT EXISTS idx_orders_customer
    ON raw.orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_restaurant
    ON raw.orders(restaurant_id);

CREATE INDEX IF NOT EXISTS idx_orders_region
    ON raw.orders(region_id);

CREATE INDEX IF NOT EXISTS idx_orders_date
    ON raw.orders(ordered_at);

CREATE INDEX IF NOT EXISTS idx_orders_status
    ON raw.orders(status);

CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON raw.order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_deliveries_courier
    ON raw.deliveries(courier_id);

CREATE INDEX IF NOT EXISTS idx_payments_status
    ON raw.payments(payment_status);
