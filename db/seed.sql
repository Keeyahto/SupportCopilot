-- Расширенные тестовые данные для демонстрации аналитики
INSERT INTO products (sku, name, category, price, active) VALUES
('SKU-001','Электрический чайник','Kitchen',1990,true),
('SKU-002','Кофеварка автоматическая','Kitchen',4990,true),
('SKU-003','Керамическая кружка','Kitchen',390,true),
('SKU-004','Блендер погружной','Kitchen',2990,true),
('SKU-005','Микроволновка 20л','Kitchen',8990,true),
('SKU-006','Холодильник двухкамерный','Kitchen',45990,true),
('SKU-007','Смартфон 128GB','Electronics',29990,true),
('SKU-008','Планшет 10"','Electronics',19990,true),
('SKU-009','Наушники беспроводные','Electronics',3990,true),
('SKU-010','Ноутбук 15"','Electronics',59990,true),
('SKU-011','Футболка хлопковая','Clothing',890,true),
('SKU-012','Джинсы классические','Clothing',2990,true),
('SKU-013','Кроссовки спортивные','Clothing',4990,true),
('SKU-014','Куртка зимняя','Clothing',8990,true),
('SKU-015','Рюкзак городской','Accessories',1990,true)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO customers (email, city, zip) VALUES
('alice@example.com','Москва','101000'),
('bob@example.com','Санкт-Петербург','190000'),
('charlie@example.com','Новосибирск','630000'),
('diana@example.com','Екатеринбург','620000'),
('eve@example.com','Казань','420000'),
('frank@example.com','Нижний Новгород','603000'),
('grace@example.com','Самара','443000'),
('henry@example.com','Омск','644000'),
('iris@example.com','Ростов-на-Дону','344000'),
('jack@example.com','Уфа','450000')
ON CONFLICT DO NOTHING;

-- Создаем разнообразные заказы за последние 30 дней
INSERT INTO orders (order_no, customer_id, created_at, status, total) VALUES
('A1001', 1, NOW() - INTERVAL '25 day', 'delivered', 1990),
('A1002', 2, NOW() - INTERVAL '20 day', 'delivered', 4990),
('A1003', 3, NOW() - INTERVAL '18 day', 'delivered', 780),
('A1004', 4, NOW() - INTERVAL '15 day', 'delivered', 29990),
('A1005', 5, NOW() - INTERVAL '12 day', 'delivered', 19990),
('A1006', 6, NOW() - INTERVAL '10 day', 'delivered', 3990),
('A1007', 7, NOW() - INTERVAL '8 day', 'delivered', 1780),
('A1008', 8, NOW() - INTERVAL '6 day', 'delivered', 59990),
('A1009', 9, NOW() - INTERVAL '5 day', 'processing', 29990),
('A1010', 10, NOW() - INTERVAL '4 day', 'processing', 1990),
('A1011', 1, NOW() - INTERVAL '3 day', 'processing', 8990),
('A1012', 2, NOW() - INTERVAL '2 day', 'shipped', 45990),
('A1013', 3, NOW() - INTERVAL '1 day', 'shipped', 890),
('A1014', 4, NOW() - INTERVAL '12 hour', 'pending', 2990),
('A1015', 5, NOW() - INTERVAL '6 hour', 'pending', 4990),
('A1016', 6, NOW() - INTERVAL '2 hour', 'pending', 1990),
('A1017', 7, NOW() - INTERVAL '1 hour', 'pending', 8990),
('A1018', 8, NOW() - INTERVAL '30 minute', 'pending', 29990),
('A1019', 9, NOW() - INTERVAL '15 minute', 'pending', 3990),
('A1020', 10, NOW() - INTERVAL '5 minute', 'pending', 1990)
ON CONFLICT (order_no) DO NOTHING;

-- Добавляем товары в заказы
INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-001' WHERE o.order_no='A1001';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-002' WHERE o.order_no='A1002';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 2, p.price FROM orders o JOIN products p ON p.sku='SKU-003' WHERE o.order_no='A1003';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-007' WHERE o.order_no='A1004';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-008' WHERE o.order_no='A1005';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-009' WHERE o.order_no='A1006';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 2, p.price FROM orders o JOIN products p ON p.sku='SKU-011' WHERE o.order_no='A1007';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-010' WHERE o.order_no='A1008';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-007' WHERE o.order_no='A1009';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-015' WHERE o.order_no='A1010';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-014' WHERE o.order_no='A1011';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-006' WHERE o.order_no='A1012';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-011' WHERE o.order_no='A1013';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-012' WHERE o.order_no='A1014';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-013' WHERE o.order_no='A1015';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-015' WHERE o.order_no='A1016';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-014' WHERE o.order_no='A1017';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-007' WHERE o.order_no='A1018';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-009' WHERE o.order_no='A1019';

INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price FROM orders o JOIN products p ON p.sku='SKU-015' WHERE o.order_no='A1020';
