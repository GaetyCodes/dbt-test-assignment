-- Month x category x region trend for seasonality and early-warning views.
select
    f.transaction_month,
    p.product_category,
    s.region_name,
    sum(f.quantity) as units,
    sum(f.net_sales) as net_sales,
    sum(f.gross_margin) as gross_margin,
    sum(f.gross_margin_standard) as gross_margin_standard,
    sum(f.cogs_landed) / nullif(sum(f.net_sales), 0) as landed_cost_to_price
from {{ ref('fct_sales') }} as f
inner join {{ ref('dim_product') }} as p using (product_id)
inner join {{ ref('dim_store') }} as s using (store_id)
group by all
