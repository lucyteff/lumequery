
-- LumeQuery | Data Quality Checks

-- 1. Verify record counts
SELECT 'regions' AS entity, COUNT(*) AS total FROM raw.regions
UNION ALL
SELECT 'customers', COUNT(*) FROM raw.customers
UNION ALL
SELECT 'restaurants', COUNT(*) FROM raw.restaurants
UNION ALL
SELECT 'menu_items', COUNT(*) FROM raw.menu_items
UNION ALL
SELECT 'couriers', COUNT(*) FROM raw.couriers
UNION ALL
SELECT 'orders', COUNT(*) FROM raw.orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM raw.order_items
UNION ALL
SELECT 'deliveries', COUNT(*) FROM raw.deliveries
UNION ALL
SELECT 'payments', COUNT(*) FROM raw.payments;


-- 2. Check order totals
SELECT COUNT(*) AS inconsistent_totals
FROM raw.orders
WHERE total_amount <> subtotal + delivery_fee - discount_amount;


-- 3. Check order subtotal against order items
SELECT COUNT(*) AS inconsistent_subtotals
FROM raw.orders o
JOIN (
    SELECT
        order_id,
        ROUND(SUM(quantity * unit_price), 2) AS calculated_subtotal
    FROM raw.order_items
    GROUP BY order_id
) oi ON oi.order_id = o.order_id
WHERE o.subtotal <> oi.calculated_subtotal;


-- 4. Check items belonging to the wrong restaurant
SELECT COUNT(*) AS items_from_wrong_restaurant
FROM raw.order_items oi
JOIN raw.orders o
    ON oi.order_id = o.order_id
JOIN raw.menu_items mi
    ON oi.menu_item_id = mi.menu_item_id
WHERE o.restaurant_id <> mi.restaurant_id;


-- 5. Check region consistency between orders and restaurants
SELECT COUNT(*) AS orders_with_region_mismatch
FROM raw.orders o
JOIN raw.restaurants r
    ON o.restaurant_id = r.restaurant_id
WHERE o.region_id <> r.region_id;


-- 6. Check payments without matching orders
SELECT COUNT(*) AS orphan_payments
FROM raw.payments p
LEFT JOIN raw.orders o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL;


-- 7. Check deliveries without matching orders
SELECT COUNT(*) AS orphan_deliveries
FROM raw.deliveries d
LEFT JOIN raw.orders o
    ON d.order_id = o.order_id
WHERE o.order_id IS NULL;
