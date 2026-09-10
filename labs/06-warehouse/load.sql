create schema if not exists raw;
create table if not exists raw.orders (
  order_id varchar(50), customer_id varchar(50), order_date date, amount decimal(18,2)
);
-- Replace placeholders, then execute as an authorized Redshift user.
copy raw.orders
from 's3://REPLACE_BUCKET/orders.csv'
iam_role 'REPLACE_REDSHIFT_ROLE_ARN'
csv ignoreheader 1;
