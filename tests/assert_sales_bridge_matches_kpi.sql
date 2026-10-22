-- Summed bridge YoY change must equal the company-level YoY change in mart_kpi_yearly.
select k.transaction_year, k.net_sales_yoy_abs, b.yoy
from {{ ref('mart_kpi_yearly') }} as k
inner join (
    select transaction_year, sum(net_sales_yoy_abs) as yoy
    from {{ ref('mart_sales_bridge_yearly') }}
    group by 1
) as b using (transaction_year)
where abs(k.net_sales_yoy_abs - b.yoy) > 0.01
