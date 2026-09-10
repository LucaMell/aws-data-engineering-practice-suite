CREATE TABLE customers (
  customer_id text PRIMARY KEY,
  email text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO customers VALUES ('c-1','luca@example.com',now());

