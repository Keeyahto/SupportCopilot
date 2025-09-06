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

-- =============================
-- Extra demo data (more variety)
-- =============================

-- More products across categories
INSERT INTO products (sku, name, category, price, active) VALUES
('SKU-101','Настольная лампа','Home',1490,true),
('SKU-102','Удлинитель 5м','Home',690,true),
('SKU-103','Постельное белье','Home',3290,true),
('SKU-104','Триммер для бороды','Beauty',1990,true),
('SKU-105','Фен компактный','Beauty',1590,true),
('SKU-106','Массажер шейный','Beauty',3990,true),
('SKU-107','Бутылка спортивная','Sports',590,true),
('SKU-108','Гантели 2×2 кг','Sports',1990,true),
('SKU-109','Коврик для йоги','Sports',1490,true),
('SKU-110','Мяч футбольный','Sports',1290,true),
('SKU-111','Маркер перманентный','Office',120,true),
('SKU-112','Бумага А4 500л','Office',590,true),
('SKU-113','Ежедневник недатированный','Office',690,true),
('SKU-114','Кресло офисное','Office',9990,true),
('SKU-115','Настольный органайзер','Office',890,true),
('SKU-116','Игровая мышь','Electronics',2990,true),
('SKU-117','Коврик для мыши','Electronics',390,true),
('SKU-118','Колонка Bluetooth','Electronics',3490,true),
('SKU-119','Power bank 20k','Electronics',3990,true),
('SKU-120','Кабель USB-C','Electronics',290,true),
('SKU-121','Секатор садовый','Garden',790,true),
('SKU-122','Шланг поливочный 15м','Garden',1490,true),
('SKU-123','Лейка 10л','Garden',490,true),
('SKU-124','Зонт садовый','Garden',3990,true),
('SKU-125','Перчатки садовые','Garden',190,true),
('SKU-126','Настольная игра','Toys',1490,true),
('SKU-127','Кубик Рубика','Toys',290,true),
('SKU-128','Конструктор 300 деталей','Toys',2990,true),
('SKU-129','Пазл 1000 элементов','Toys',990,true),
('SKU-130','Машинка инерционная','Toys',390,true)
ON CONFLICT (sku) DO NOTHING;

-- More customers (cities across regions)
INSERT INTO customers (email, city, zip) VALUES
('user01@example.com','Пермь','614000'),
('user02@example.com','Воронеж','394000'),
('user03@example.com','Волгоград','400000'),
('user04@example.com','Красноярск','660000'),
('user05@example.com','Саратов','410000'),
('user06@example.com','Тольятти','445000'),
('user07@example.com','Тюмень','625000'),
('user08@example.com','Ижевск','426000'),
('user09@example.com','Барнаул','656000'),
('user10@example.com','Иркутск','664000'),
('user11@example.com','Хабаровск','680000'),
('user12@example.com','Ярославль','150000'),
('user13@example.com','Владивосток','690000'),
('user14@example.com','Махачкала','367000'),
('user15@example.com','Томск','634000'),
('user16@example.com','Оренбург','460000'),
('user17@example.com','Кемерово','650000'),
('user18@example.com','Новокузнецк','654000'),
('user19@example.com','Рязань','390000'),
('user20@example.com','Астрахань','414000'),
('user21@example.com','Пенза','440000'),
('user22@example.com','Липецк','398000'),
('user23@example.com','Калуга','248000'),
('user24@example.com','Тула','300000'),
('user25@example.com','Курск','305000'),
('user26@example.com','Сочи','354000'),
('user27@example.com','Белгород','308000'),
('user28@example.com','Владимир','600000'),
('user29@example.com','Севастополь','299000'),
('user30@example.com','Симферополь','295000'),
('user31@example.com','Чебоксары','428000'),
('user32@example.com','Тверь','170000'),
('user33@example.com','Брянск','241000'),
('user34@example.com','Киров','610000'),
('user35@example.com','Магнитогорск','455000'),
('user36@example.com','Набережные Челны','423800'),
('user37@example.com','Калининград','236000'),
('user38@example.com','Якутск','677000'),
('user39@example.com','Стерлитамак','453000'),
('user40@example.com','Комсомольск-на-Амуре','681000')
ON CONFLICT DO NOTHING;

-- Bulk-generate additional orders over recent days with diverse statuses
-- We spread customers cyclically across existing range, and set totals later by items
WITH s AS (
  SELECT generate_series(1, 80) AS i
)
INSERT INTO orders (order_no, customer_id, created_at, status, total)
SELECT
  'B' || (2000 + i)::text AS order_no,
  ((i - 1) % (SELECT MAX(id) FROM customers)) + 1 AS customer_id,
  NOW() - ((i % 30) || ' days')::interval - ((i % 8) || ' hours')::interval,
  CASE (i % 5)
    WHEN 0 THEN 'delivered'
    WHEN 1 THEN 'processing'
    WHEN 2 THEN 'shipped'
    WHEN 3 THEN 'pending'
    ELSE 'cancelled'
  END AS status,
  0 AS total
FROM s
ON CONFLICT (order_no) DO NOTHING;

-- Add 1–3 items per new order by deterministic joins to products
-- (price copied from product.price)
INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, (1 + (o.id % 3))::int AS qty, p.price
FROM orders o
JOIN products p ON (p.id % 7) = (o.id % 7)
WHERE o.order_no LIKE 'B2%'
  AND NOT EXISTS (
    SELECT 1 FROM order_items oi WHERE oi.order_id = o.id
  );

-- Add a second line item for some orders to increase variety
INSERT INTO order_items (order_id, product_id, qty, price)
SELECT o.id, p.id, 1, p.price
FROM orders o
JOIN products p ON (p.id % 11) = (o.id % 11)
WHERE o.order_no LIKE 'B2%'
  AND (o.id % 2) = 0
  AND NOT EXISTS (
    SELECT 1 FROM order_items oi WHERE oi.order_id = o.id AND oi.product_id = p.id
  );

-- Recalculate totals from items for all orders (ensures consistency)
UPDATE orders o
SET total = sub.sum_total
FROM (
  SELECT oi.order_id, SUM(oi.qty * oi.price) AS sum_total
  FROM order_items oi
  GROUP BY oi.order_id
) sub
WHERE o.id = sub.order_id;
