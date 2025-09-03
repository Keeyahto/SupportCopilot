CREATE TABLE IF NOT EXISTS products(
  id SERIAL PRIMARY KEY,
  sku TEXT UNIQUE,
  name TEXT,
  category TEXT,
  price NUMERIC,
  active BOOL
);

CREATE TABLE IF NOT EXISTS customers(
  id SERIAL PRIMARY KEY,
  email TEXT,
  city TEXT,
  zip TEXT
);

CREATE TABLE IF NOT EXISTS orders(
  id SERIAL PRIMARY KEY,
  order_no TEXT UNIQUE,
  customer_id INT REFERENCES customers(id),
  created_at TIMESTAMP,
  status TEXT,
  total NUMERIC
);

CREATE TABLE IF NOT EXISTS order_items(
  id SERIAL PRIMARY KEY,
  order_id INT REFERENCES orders(id),
  product_id INT REFERENCES products(id),
  qty INT,
  price NUMERIC
);

CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- Create RO role
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_roles WHERE rolname = 'support_ro') THEN
      CREATE ROLE support_ro LOGIN PASSWORD 'readonly';
   END IF;
END$$;

GRANT CONNECT ON DATABASE support TO support_ro;
GRANT USAGE ON SCHEMA public TO support_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO support_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO support_ro;
