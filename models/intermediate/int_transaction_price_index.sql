-- Price is set per product-month as a reference list price x a store price-list multiplier x a promo multiplier.
-- Reference list price = highest price paid for the product that month (always a California store: verified for all
-- 768 product-months). price_index = unit_price / reference list price.
with txn as (

    select * from {{ ref('int_transactions_keyed') }}
    where product_id <> -1

)

select
    transaction_id,
    product_id,
    store_id,
    transaction_month,
    quantity,
    unit_price,
    landed_cost_per_unit,
    max(unit_price) over (partition by product_id, transaction_month) as list_price,
    unit_price / max(unit_price) over (partition by product_id, transaction_month) as price_index
from txn
