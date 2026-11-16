# LumeQuery — Data Model

## 1. Overview

The LumeQuery database represents a fictional marketplace and delivery platform. It stores operational data related to regions, customers, restaurants, menu items, couriers, orders, deliveries, and payments.

The database uses PostgreSQL and follows a relational model with primary keys, foreign keys, unique constraints, and data integrity checks.

## 2. Database Schemas

- `raw`: operational source tables.
- `analytics`: analytical views and transformed datasets.

## 3. Tables

### 3.1 regions

Stores the service regions where the platform operates.

- `region_id`: BIGINT, Primary Key
- `name`: VARCHAR(100), NOT NULL
- `city`: VARCHAR(100), NOT NULL
- `state`: CHAR(2), NOT NULL
- `is_active`: BOOLEAN, NOT NULL

### 3.2 customers

Stores fictional customer information.

- `customer_id`: BIGINT, Primary Key
- `region_id`: BIGINT, Foreign Key → regions
- `customer_name`: VARCHAR(150), NOT NULL
- `email`: VARCHAR(150), UNIQUE
- `created_at`: TIMESTAMPTZ, NOT NULL
- `is_active`: BOOLEAN, NOT NULL

### 3.3 restaurants

Stores restaurants registered on the platform.

- `restaurant_id`: BIGINT, Primary Key
- `region_id`: BIGINT, Foreign Key → regions
- `restaurant_name`: VARCHAR(150), NOT NULL
- `cuisine_type`: VARCHAR(80), NOT NULL
- `created_at`: TIMESTAMPTZ, NOT NULL
- `is_active`: BOOLEAN, NOT NULL

### 3.4 menu_items

Stores restaurant menu products.

- `menu_item_id`: BIGINT, Primary Key
- `restaurant_id`: BIGINT, Foreign Key → restaurants
- `item_name`: VARCHAR(150), NOT NULL
- `category`: VARCHAR(80)
- `current_price`: NUMERIC(10,2), NOT NULL
- `is_active`: BOOLEAN, NOT NULL

### 3.5 couriers

Stores fictional courier information.

- `courier_id`: BIGINT, Primary Key
- `region_id`: BIGINT, Foreign Key → regions
- `vehicle_type`: VARCHAR(30), NOT NULL
- `joined_at`: TIMESTAMPTZ, NOT NULL
- `is_active`: BOOLEAN, NOT NULL

### 3.6 orders

Stores customer orders.

- `order_id`: BIGINT, Primary Key
- `customer_id`: BIGINT, Foreign Key → customers
- `restaurant_id`: BIGINT, Foreign Key → restaurants
- `region_id`: BIGINT, Foreign Key → regions
- `ordered_at`: TIMESTAMPTZ, NOT NULL
- `status`: VARCHAR(30), NOT NULL
- `subtotal`: NUMERIC(10,2), NOT NULL
- `delivery_fee`: NUMERIC(10,2), NOT NULL
- `discount_amount`: NUMERIC(10,2), NOT NULL
- `total_amount`: NUMERIC(10,2), NOT NULL

### 3.7 order_items

Stores the products included in each order.

- `order_item_id`: BIGINT, Primary Key
- `order_id`: BIGINT, Foreign Key → orders
- `menu_item_id`: BIGINT, Foreign Key → menu_items
- `quantity`: INTEGER, NOT NULL
- `unit_price`: NUMERIC(10,2), NOT NULL

The unit price represents the product price at the time of the order, preserving historical values independently of the current menu price.

### 3.8 deliveries

Stores delivery information.

- `delivery_id`: BIGINT, Primary Key
- `order_id`: BIGINT, UNIQUE Foreign Key → orders
- `courier_id`: BIGINT, nullable Foreign Key → couriers
- `status`: VARCHAR(30), NOT NULL
- `estimated_delivery_at`: TIMESTAMPTZ
- `accepted_at`: TIMESTAMPTZ
- `picked_up_at`: TIMESTAMPTZ
- `delivered_at`: TIMESTAMPTZ

### 3.9 payments

Stores payment information for orders.

- `payment_id`: BIGINT, Primary Key
- `order_id`: BIGINT, UNIQUE Foreign Key → orders
- `payment_method`: VARCHAR(30), NOT NULL
- `payment_status`: VARCHAR(30), NOT NULL
- `amount`: NUMERIC(10,2), NOT NULL
- `paid_at`: TIMESTAMPTZ

## 4. Relationships

- One region can have multiple customers, restaurants, and couriers.
- One customer can place multiple orders.
- One restaurant can receive multiple orders and have multiple menu items.
- One order can contain multiple order items.
- One menu item can appear in multiple order items.
- One order can have zero or one delivery record.
- One courier can handle multiple deliveries.
- One order can have zero or one payment record.

## 5. Business Rules and Constraints

- The dataset uses synthetically generated information.
- Monetary values use `NUMERIC(10,2)` to avoid floating-point precision issues.
- Order item prices preserve the price at the time of purchase.
- Order quantities must be greater than zero.
- Monetary values cannot be negative.
- Order totals must equal subtotal plus delivery fee minus discount.
- Orders, deliveries, and payments are restricted to predefined status values.
- Cancelled orders are not counted as completed sales.
- Analytical revenue metrics must explicitly define which order and payment statuses they include.

## 6. Status Values

**Orders**

- `pending`
- `confirmed`
- `preparing`
- `ready`
- `out_for_delivery`
- `delivered`
- `cancelled`

**Deliveries**

Allowed by the database constraint:

- `pending`
- `assigned`
- `picked_up`
- `delivered`
- `failed`
- `cancelled`

The current data generator produces `pending`, `assigned`, `picked_up`, and `delivered`.

**Payments**

- `pending`
- `paid`
- `failed`
- `refunded`

## 7. Synthetic Dataset

The generated dataset contains approximately six months of fictional marketplace activity.

| Entity | Records |
|---|---:|
| Regions | 10 |
| Customers | 5,000 |
| Restaurants | 100 |
| Menu items | 500 |
| Couriers | 150 |
| Orders | 20,000 |
| Order items | 49,570 |
| Deliveries | 19,002 |
| Payments | 20,000 |

All records are synthetically generated and do not represent real customers, restaurants, or transactions.