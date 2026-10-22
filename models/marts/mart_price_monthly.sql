-- Product x month price health: reference list price vs landed cost (markup), realised price and promo depth.
-- A line is promotional when sold below its store's regular price list.
with idx as (

    select
        i.*,
        s.price_list_index,
        i.price_index < s.price_list_index - 0.01 as is_promo
    from {{ ref('int_transaction_price_index') }} as i
    inner join {{ ref('dim_store') }} as s using (store_id)

)

select
    i.product_id,
    p.product_name,
    p.product_category,
    i.transaction_month,
    max(i.list_price) as list_price,
    max(i.landed_cost_per_unit) as landed_cost_per_unit,
    max(i.list_price) / max(i.landed_cost_per_unit) as list_markup,
    1 - max(i.landed_cost_per_unit) / max(i.list_price) as list_gross_margin_pct,
    sum(i.quantity) as units,
    sum(i.quantity * i.unit_price) / nullif(sum(i.quantity), 0) as realised_price,
    sum(i.quantity * i.unit_price) / nullif(sum(i.quantity * i.list_price), 0) as price_realisation,
    coalesce(sum(case when i.is_promo then i.quantity end), 0) / nullif(sum(i.quantity), 0) as promo_unit_share
from idx as i
inner join {{ ref('dim_product') }} as p using (product_id)
group by all
