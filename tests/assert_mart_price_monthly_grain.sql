-- mart_price_monthly must have one row per product per month.
select product_id, transaction_month, count(*) as n
from {{ ref('mart_price_monthly') }}
group by 1, 2
having count(*) > 1
