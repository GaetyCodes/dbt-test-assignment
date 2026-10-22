-- Assumption behind the price model: the product-month reference list price is a Premium (California) price,
-- and every product-month has Premium-list sales.
with pm as (
    select
        f.product_id,
        f.transaction_month,
        max(f.unit_price) as list_price,
        max(case when s.price_list = 'Premium (1.00)' then f.unit_price end) as premium_price
    from {{ ref('fct_sales') }} as f
    inner join {{ ref('dim_store') }} as s using (store_id)
    where f.product_id <> -1
    group by 1, 2
)

select * from pm
where premium_price is null or premium_price <> list_price
