-- Fact -> marts: every reporting mart carries the same Net Sales and Gross Margin per year as fct_sales.
with fct as (
    select transaction_year, sum(net_sales) as ns, sum(gross_margin) as gm from {{ ref('fct_sales') }} group by 1
),

marts as (
    select 'mart_kpi_yearly' as mart, transaction_year, net_sales as ns, gross_margin as gm from {{ ref('mart_kpi_yearly') }}
    union all
    select 'mart_product_yearly', transaction_year, sum(net_sales), sum(gross_margin) from {{ ref('mart_product_yearly') }} group by 2
    union all
    select 'mart_store_yearly', transaction_year, sum(net_sales), sum(gross_margin) from {{ ref('mart_store_yearly') }} group by 2
    union all
    select 'mart_sales_monthly', year(transaction_month), sum(net_sales), sum(gross_margin) from {{ ref('mart_sales_monthly') }} group by 2
)

select m.mart, m.transaction_year, m.ns, f.ns as fct_ns, m.gm, f.gm as fct_gm
from marts as m
full outer join fct as f using (transaction_year)
where f.ns is null or m.ns is null or abs(m.ns - f.ns) > 0.01 or abs(m.gm - f.gm) > 0.01
