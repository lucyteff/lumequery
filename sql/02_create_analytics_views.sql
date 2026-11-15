
-- LumeQuery | Analytics Layer

-- 1. Order-level analytical view
-- One row per order, avoiding duplicated order values.

CREATE OR REPLACE VIEW analytics.vw_order_summary AS
SELECT
    o.order_id,
    o.ordered_at,
    o.status AS order_status,

    c.customer_id,
    c.customer_name,

    r.restaurant_id,
    r.restaurant_name,
    r.cuisine_type,

    rg.region_id,
    rg.name AS region_name,
    rg.city,
    rg.state,

    o.subtotal,
    o.delivery_fee,
    o.discount_amount,
    o.total_amount,

    COALESCE(oi.item_count, 0) AS item_count,
    COALESCE(oi.total_quantity, 0) AS total_quantity,
    COALESCE(oi.calculated_subtotal, 0) AS calculated_subtotal,

    p.payment_method,
    p.payment_status,
    p.amount AS payment_amount,
    p.paid_at,

    d.status AS delivery_status,
    d.courier_id,
    d.estimated_delivery_at,
    d.delivered_at

FROM raw.orders o

JOIN raw.customers c
    ON o.customer_id = c.customer_id

JOIN raw.restaurants r
    ON o.restaurant_id = r.restaurant_id

JOIN raw.regions rg
    ON o.region_id = rg.region_id

LEFT JOIN (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(quantity) AS total_quantity,
        ROUND(SUM(quantity * unit_price), 2) AS calculated_subtotal
    FROM raw.order_items
    GROUP BY order_id
) oi
    ON o.order_id = oi.order_id

LEFT JOIN raw.payments p
    ON o.order_id = p.order_id

LEFT JOIN raw.deliveries d
    ON o.order_id = d.order_id;


-- 2. Daily business performance

CREATE OR REPLACE VIEW analytics.vw_daily_performance AS
SELECT
    DATE(ordered_at) AS order_date,

    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE order_status = 'cancelled'
    ) AS cancelled_orders,

    ROUND(SUM(total_amount), 2) AS total_order_value,

    ROUND(
        SUM(total_amount) FILTER (
            WHERE order_status = 'delivered'
        ),
        2
    ) AS delivered_order_value,

    ROUND(
        AVG(total_amount),
        2
    ) AS average_order_value,

    ROUND(
        AVG(total_quantity),
        2
    ) AS average_items_per_order

FROM analytics.vw_order_summary
GROUP BY DATE(ordered_at);


-- 3. Restaurant performance

CREATE OR REPLACE VIEW analytics.vw_restaurant_performance AS
SELECT
    restaurant_id,
    restaurant_name,
    cuisine_type,
    region_name,
    city,
    state,

    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE order_status = 'cancelled'
    ) AS cancelled_orders,

    ROUND(SUM(total_amount), 2) AS total_order_value,

    ROUND(
        AVG(total_amount),
        2
    ) AS average_order_value,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_status = 'cancelled'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate

FROM analytics.vw_order_summary
GROUP BY
    restaurant_id,
    restaurant_name,
    cuisine_type,
    region_name,
    city,
    state;
