/*
    Regional performance by year (CEO Q2 - regions, and regional analysis).
    Net sales, gross profit, margin, store count and YoY, per region x year.
*/

with joined as (

    select
        d.region_name,
        f.transaction_year,
        f.store_id,
        f.net_revenue,
        f.gross_profit,
        f.quantity
    from {{ ref('fct_sales') }} f
    join {{ ref('dim_store') }} d on f.store_id = d.store_id

),

agg as (

    select
        region_name,
        transaction_year,
        count(distinct store_id)                                  as active_stores,
        sum(net_revenue)                                         as net_sales,
        sum(gross_profit)                                        as gross_profit,
        round(100.0 * sum(gross_profit) / nullif(sum(net_revenue), 0), 2) as gross_margin_pct,
        sum(quantity)                                            as net_units
    from joined
    group by region_name, transaction_year

)

select
    *,
    round(net_sales / nullif(active_stores, 0), 0) as net_sales_per_store,
    round(100.0 * (net_sales / nullif(
        lag(net_sales) over (partition by region_name order by transaction_year), 0) - 1), 2)
        as net_sales_yoy_pct
from agg
order by region_name, transaction_year
