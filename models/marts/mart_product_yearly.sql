-- Product x year performance. avg_selling_price mixes price lists (California ~1.7x base), so asp_yoy_pct
-- is NOT a like-for-like price change: use mart_sales_bridge_yearly (price_effect) or mart_price_monthly (list price).
with base as (

    select
        f.product_id,
        p.product_name,
        p.product_category,
        f.transaction_year,
        sum(f.quantity) as units,
        sum(f.net_sales) as net_sales,
        sum(f.cogs_landed) as cogs_landed,
        sum(f.gross_margin) as gross_margin,
        sum(f.gross_margin_standard) as gross_margin_standard
    from {{ ref('fct_sales') }} as f
    inner join {{ ref('dim_product') }} as p using (product_id)
    group by all

),

metrics as (

    select
        *,
        net_sales / nullif(units, 0) as avg_selling_price,
        cogs_landed / nullif(units, 0) as avg_landed_cost,
        gross_margin / nullif(net_sales, 0) as gross_margin_pct,
        gross_margin / nullif(units, 0) as gross_margin_per_unit,
        lag(units) over w as units_py,
        lag(net_sales) over w as net_sales_py,
        lag(gross_margin) over w as gross_margin_py,
        lag(net_sales / nullif(units, 0)) over w as avg_selling_price_py,
        lag(cogs_landed / nullif(units, 0)) over w as avg_landed_cost_py
    from base
    window w as (partition by product_id order by transaction_year)

)

select
    *,
    net_sales - net_sales_py as net_sales_yoy_abs,
    net_sales / nullif(net_sales_py, 0) - 1 as net_sales_yoy_pct,
    gross_margin - gross_margin_py as gross_margin_yoy_abs,
    gross_margin / nullif(gross_margin_py, 0) - 1 as gross_margin_yoy_pct,
    avg_selling_price / nullif(avg_selling_price_py, 0) - 1 as asp_yoy_pct,
    avg_landed_cost / nullif(avg_landed_cost_py, 0) - 1 as landed_cost_yoy_pct
from metrics
