-- Minimal seed for demo
INSERT INTO products (sku, name, category, price, active) VALUES
('SKU-001','Чайник','Kitchen',1990,true),
('SKU-002','Кофеварка','Kitchen',4990,true),
('SKU-003','Кружка','Kitchen',390,true)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO customers (email, city, zip) VALUES
('alice@example.com','Москва','101000'),
('bob@example.com','Санкт-Петербург','190000'),
('charlie@example.com','Новосибирск','630000')
ON CONFLICT DO NOTHING;

-- Create a couple of orders over last days
INSERT INTO orders (order_no, customer_id, created_at, status, total) VALUES
('A1001', 1, NOW() - INTERVAL '3 day', 'delivered', 129.99),
('A1002', 2, NOW() - INTERVAL '1 day', 'processing', 79.50)
ON CONFLICT (order_no) DO NOTHING;

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-001' WHERE o.order_no='A1001';
INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-003' WHERE o.order_no='A1002';
