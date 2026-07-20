-- Fact must never contain null keys or the 99901 sentinel.
select
    transaction_id,
    product_id,
    store_id
from {{ ref('fct_sales') }}
where product_id is null
   or store_id is null
   or product_id = 99901
   or store_id = 99901
