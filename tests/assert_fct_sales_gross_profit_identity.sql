-- gross_profit must equal net_revenue - cogs_landed within rounding tolerance.
select
    transaction_id,
    net_revenue,
    cogs_landed,
    gross_profit,
    round(net_revenue - cogs_landed, 4) as expected_gross_profit
from {{ ref('fct_sales') }}
where abs(gross_profit - round(net_revenue - cogs_landed, 4)) > 0.01
