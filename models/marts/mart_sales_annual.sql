/*
    Annual P&L summary answering: how are sales changing, are we growing, and are
    we growing profitably? (CEO Q1 / Q4)

    - net_sales, cogs, gross_profit, gross_margin_pct from fct_sales
    - operating_costs = sum of each active store's ANNUAL direct operating cost,
      charged once per year the store transacts
    - operating_profit = gross_profit - operating_costs
    - YoY growth on net_sales, gross_profit and operating_profit
*/

with sales as (

    select
        transaction_year,
        sum(net_revenue)                as net_sales,
        sum(cogs_landed)                as cogs,
        sum(gross_profit)               as gross_profit,
        sum(quantity)                   as net_units,
        count(*)                        as transactions
    from {{ ref('fct_sales') }}
    group by transaction_year

),

-- annual direct operating cost of the stores active in each year
store_opex as (

    select
        f.transaction_year,
        sum(d.annual_operating_costs)   as operating_costs
    from (
        select distinct transaction_year, store_id
        from {{ ref('fct_sales') }}
    ) f
    join {{ ref('dim_store') }} d on f.store_id = d.store_id
    group by f.transaction_year

),

combined as (

    select
        s.transaction_year,
        s.net_sales,
        s.cogs,
        s.gross_profit,
        round(100.0 * s.gross_profit / nullif(s.net_sales, 0), 2) as gross_margin_pct,
        o.operating_costs,
        s.gross_profit - o.operating_costs                        as operating_profit,
        round(100.0 * (s.gross_profit - o.operating_costs)
              / nullif(s.net_sales, 0), 2)                        as operating_margin_pct,
        s.net_units,
        s.transactions
    from sales s
    join store_opex o on s.transaction_year = o.transaction_year

)

select
    *,
    round(100.0 * (net_sales / nullif(lag(net_sales) over (order by transaction_year), 0) - 1), 2)
        as net_sales_yoy_pct,
    round(100.0 * (gross_profit / nullif(lag(gross_profit) over (order by transaction_year), 0) - 1), 2)
        as gross_profit_yoy_pct,
    round(100.0 * (operating_profit / nullif(lag(operating_profit) over (order by transaction_year), 0) - 1), 2)
        as operating_profit_yoy_pct
from combined
order by transaction_year
