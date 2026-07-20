/*
    Product & category performance (CEO Q2 - top products).
    Lifetime and per-year net sales, gross profit and margin per product.
*/

with joined as (

    select
        p.product_id,
        p.product_name,
        p.product_category,
        f.transaction_year,
        f.net_revenue,
        f.gross_profit,
        f.quantity
    from {{ ref('fct_sales') }} f
    join {{ ref('dim_product') }} p on f.product_id = p.product_id

)

select
    product_id,
    product_name,
    product_category,
    sum(net_revenue)                                          as net_sales,
    sum(gross_profit)                                         as gross_profit,
    round(100.0 * sum(gross_profit) / nullif(sum(net_revenue), 0), 2) as gross_margin_pct,
    sum(quantity)                                             as net_units,
    sum(net_revenue) filter (where transaction_year = 2022)  as net_sales_2022,
    sum(net_revenue) filter (where transaction_year = 2021)  as net_sales_2021,
    sum(gross_profit) filter (where transaction_year = 2022) as gross_profit_2022,
    sum(gross_profit) filter (where transaction_year = 2021) as gross_profit_2021
from joined
group by product_id, product_name, product_category
order by net_sales desc
