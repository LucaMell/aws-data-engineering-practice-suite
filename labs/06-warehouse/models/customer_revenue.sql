select customer_id, sum(amount) as lifetime_revenue, count(*) as order_count
from {{ source('raw', 'orders') }}
group by customer_id

