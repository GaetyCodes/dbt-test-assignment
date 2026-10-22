-- Company KPIs per year with YoY (abs and %). Store opex treated as ANNUAL (FP&A view):
-- with monthly opex x12 every store would lose money by ~6x revenue, which is not credible.
with sales as (

    select
        transaction_year,
        sum(net_sales) as net_sales,
        sum(gross_margin) as gross_margin,
        sum(gross_margin_standard) as gross_margin_standard,
        sum(quantity) as units,
        sum(case when is_return then -net_sales else 0 end) as returns_value
    from {{ ref('fct_sales') }}
    group by 1

),

opex as (

    select f.transaction_year, sum(distinct_store.store_opex_annual) as store_opex
    from (select distinct transaction_year, store_id from {{ ref('fct_sales') }}) as f
    inner join {{ ref('dim_store') }} as distinct_store using (store_id)
    group by 1

),

kpi as (

    select
        s.*,
        o.store_opex,
        s.gross_margin - o.store_opex as store_contribution,
        s.net_sales / s.units as avg_selling_price,
        s.gross_margin / s.net_sales as gross_margin_pct,
        (s.gross_margin - o.store_opex) / s.net_sales as store_contribution_pct
    from sales as s
    left join opex as o using (transaction_year)

)

select
    *,
    net_sales - lag(net_sales) over w as net_sales_yoy_abs,
    net_sales / lag(net_sales) over w - 1 as net_sales_yoy_pct,
    gross_margin - lag(gross_margin) over w as gross_margin_yoy_abs,
    gross_margin / lag(gross_margin) over w - 1 as gross_margin_yoy_pct,
    store_contribution - lag(store_contribution) over w as store_contribution_yoy_abs,
    store_contribution / lag(store_contribution) over w - 1 as store_contribution_yoy_pct,
    -- includes product and location mix; like-for-like price is in mart_sales_bridge_yearly
    avg_selling_price / lag(avg_selling_price) over w - 1 as avg_selling_price_yoy_pct
from kpi
window w as (order by transaction_year)
