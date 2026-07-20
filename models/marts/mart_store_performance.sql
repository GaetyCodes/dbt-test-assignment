/*
    Store performance (CEO Q2 - top stores) with an operating-profit lens.
    Uses each store's ANNUAL direct operating cost, charged per active year, to
    approximate contribution after direct store costs.
*/

with by_store_year as (

    select
        f.store_id,
        f.transaction_year,
        sum(f.net_revenue)      as net_sales,
        sum(f.gross_profit)     as gross_profit,
        sum(f.quantity)         as net_units
    from {{ ref('fct_sales') }} f
    group by f.store_id, f.transaction_year

),

with_opex as (

    select
        b.store_id,
        d.store_name,
        d.state_code,
        d.region_name,
        d.store_type,
        d.store_sqft,
        d.annual_operating_costs,
        count(*)                                    as active_years,
        sum(b.net_sales)                            as net_sales,
        sum(b.gross_profit)                         as gross_profit,
        sum(b.net_units)                            as net_units,
        -- annual opex charged once per active year
        sum(d.annual_operating_costs)               as operating_costs,
        sum(b.gross_profit) - sum(d.annual_operating_costs) as operating_profit
    from by_store_year b
    join {{ ref('dim_store') }} d on b.store_id = d.store_id
    group by 1,2,3,4,5,6,7

)

select
    *,
    round(100.0 * gross_profit / nullif(net_sales, 0), 2)     as gross_margin_pct,
    round(100.0 * operating_profit / nullif(net_sales, 0), 2) as operating_margin_pct
from with_opex
order by net_sales desc
