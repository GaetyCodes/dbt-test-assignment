-- Store x year P&L down to store contribution (gross margin less annual direct opex).
with sales as (

    select
        store_id,
        transaction_year,
        sum(net_sales) as net_sales,
        sum(gross_margin) as gross_margin,
        sum(quantity) as units
    from {{ ref('fct_sales') }}
    group by all

),

pnl as (

    select
        s.*,
        d.store_name,
        d.state_code,
        d.region_name,
        d.store_type,
        d.store_sqft,
        d.store_opex_annual as store_opex,
        s.gross_margin - d.store_opex_annual as store_contribution,
        s.gross_margin / nullif(s.net_sales, 0) as gross_margin_pct,
        s.net_sales / nullif(d.store_sqft, 0) as net_sales_per_sqft
    from sales as s
    inner join {{ ref('dim_store') }} as d using (store_id)

)

select
    *,
    store_contribution > 0 as is_profitable,
    net_sales - lag(net_sales) over w as net_sales_yoy_abs,
    net_sales / nullif(lag(net_sales) over w, 0) - 1 as net_sales_yoy_pct,
    store_contribution - lag(store_contribution) over w as store_contribution_yoy_abs
from pnl
window w as (partition by store_id order by transaction_year)
