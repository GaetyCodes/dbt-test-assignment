/*
    Monthly sales trend (net sales, gross profit, margin) for trendlines.
*/

select
    transaction_month,
    transaction_year,
    sum(net_revenue)                                          as net_sales,
    sum(gross_profit)                                         as gross_profit,
    round(100.0 * sum(gross_profit) / nullif(sum(net_revenue), 0), 2) as gross_margin_pct,
    sum(quantity)                                             as net_units,
    count(*)                                                  as transactions
from {{ ref('fct_sales') }}
group by transaction_month, transaction_year
order by transaction_month
