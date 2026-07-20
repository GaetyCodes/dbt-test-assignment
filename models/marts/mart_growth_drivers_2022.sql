/*
    Growth drivers 2021 -> 2022 (CEO Q3), decomposed by category.

    Explains both the revenue growth and the gross-margin decline by exposing, per
    category: unit volume, net sales, COGS, gross profit, average selling price,
    average unit cost and margin for each year plus the deltas.

    Volume vs price vs cost effects (approximate, per category):
      volume_effect = (units_22 - units_21) * price_21
      price_effect  = (price_22 - price_21) * units_22
      cost_effect   = -(cost_22  - cost_21) * units_22   (negative = cost headwind)
*/

with by_cat_year as (

    select
        p.product_category,
        f.transaction_year,
        sum(f.quantity)                                          as net_units,
        sum(f.net_revenue)                                       as net_sales,
        sum(f.cogs_landed)                                       as cogs,
        sum(f.gross_profit)                                      as gross_profit,
        sum(f.net_revenue) / nullif(sum(f.quantity), 0)         as avg_price,
        sum(f.cogs_landed) / nullif(sum(f.quantity), 0)         as avg_unit_cost
    from {{ ref('fct_sales') }} f
    join {{ ref('dim_product') }} p on f.product_id = p.product_id
    where f.transaction_year in (2021, 2022)
    group by p.product_category, f.transaction_year

),

pivoted as (

    select
        product_category,
        max(net_units)  filter (where transaction_year = 2021) as units_2021,
        max(net_units)  filter (where transaction_year = 2022) as units_2022,
        max(net_sales)  filter (where transaction_year = 2021) as net_sales_2021,
        max(net_sales)  filter (where transaction_year = 2022) as net_sales_2022,
        max(gross_profit) filter (where transaction_year = 2021) as gross_profit_2021,
        max(gross_profit) filter (where transaction_year = 2022) as gross_profit_2022,
        max(avg_price)  filter (where transaction_year = 2021) as avg_price_2021,
        max(avg_price)  filter (where transaction_year = 2022) as avg_price_2022,
        max(avg_unit_cost) filter (where transaction_year = 2021) as avg_cost_2021,
        max(avg_unit_cost) filter (where transaction_year = 2022) as avg_cost_2022
    from by_cat_year
    group by product_category

)

select
    product_category,
    units_2021, units_2022,
    net_sales_2021, net_sales_2022,
    net_sales_2022 - net_sales_2021                                       as net_sales_delta,
    gross_profit_2021, gross_profit_2022,
    gross_profit_2022 - gross_profit_2021                                 as gross_profit_delta,
    round(100.0 * gross_profit_2021 / nullif(net_sales_2021, 0), 2)       as margin_2021_pct,
    round(100.0 * gross_profit_2022 / nullif(net_sales_2022, 0), 2)       as margin_2022_pct,
    avg_price_2021, avg_price_2022,
    avg_cost_2021, avg_cost_2022,
    -- effect decomposition on revenue/profit
    round((units_2022 - units_2021) * avg_price_2021, 0)                  as volume_effect,
    round((avg_price_2022 - avg_price_2021) * units_2022, 0)              as price_effect,
    round(-(avg_cost_2022 - avg_cost_2021) * units_2022, 0)               as cost_effect
from pivoted
order by net_sales_2022 desc
