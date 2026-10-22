-- Store x year P&L down to store contribution (gross margin less direct store opex).
-- Opex basis: ANNUAL, charged in full to every store trading that year (headline, matches mart_kpi_yearly).
-- Sensitivities: pro-rated to months traded (part-year / new stores), and monthly x12 (Store Finance reading).
-- Store losses are expected in this data (confirmed with the interviewer); they track the store price list.
with sales as (

    select
        store_id,
        transaction_year,
        sum(net_sales) as net_sales,
        sum(gross_margin) as gross_margin,
        sum(quantity) as units,
        count(distinct transaction_month) as months_trading
    from {{ ref('fct_sales') }}
    group by all

),

first_year as (

    select store_id, min(transaction_year) as first_trading_year
    from sales
    group by 1

),

pnl as (

    select
        s.*,
        s.transaction_year = fy.first_trading_year and s.transaction_year > 2019 as is_first_trading_year,
        d.store_name,
        d.state_code,
        d.region_name,
        d.store_type,
        d.price_list,
        d.price_list_index,
        d.store_sqft,
        d.store_opex_annual as store_opex,
        s.gross_margin - d.store_opex_annual as store_contribution,
        s.gross_margin - d.store_opex_annual * s.months_trading / 12 as store_contribution_opex_prorated,
        s.gross_margin - d.store_opex_annual * 12 as store_contribution_opex_monthly,
        s.gross_margin / nullif(s.net_sales, 0) as gross_margin_pct,
        s.net_sales / nullif(d.store_sqft, 0) as net_sales_per_sqft,
        s.units / nullif(d.store_sqft, 0) * 1000 as units_per_1k_sqft
    from sales as s
    inner join first_year as fy using (store_id)
    inner join {{ ref('dim_store') }} as d using (store_id)

)

select
    *,
    store_contribution > 0 as is_profitable,
    store_contribution_opex_prorated > 0 as is_profitable_opex_prorated,
    net_sales - lag(net_sales) over w as net_sales_yoy_abs,
    net_sales / nullif(lag(net_sales) over w, 0) - 1 as net_sales_yoy_pct,
    store_contribution - lag(store_contribution) over w as store_contribution_yoy_abs
from pnl
window w as (partition by store_id order by transaction_year)
