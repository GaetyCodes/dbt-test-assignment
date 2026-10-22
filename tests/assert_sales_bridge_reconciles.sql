-- The bridge components must add up to the YoY Net Sales change for every product-year.
select product_id, transaction_year,
    net_sales_yoy_abs - (volume_effect + mix_effect + price_effect + new_product_effect) as gap
from {{ ref('mart_sales_bridge_yearly') }}
where abs(net_sales_yoy_abs - (volume_effect + mix_effect + price_effect + new_product_effect)) > 0.01
