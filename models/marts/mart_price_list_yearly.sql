-- Price list x year: the lens that explains store profitability. Same opex basis as mart_store_yearly.
select
    price_list,
    transaction_year,
    count(*) as stores,
    sum(case when is_first_trading_year then 1 else 0 end) as new_stores,
    sum(units) as units,
    sum(net_sales) as net_sales,
    sum(gross_margin) as gross_margin,
    sum(gross_margin) / nullif(sum(net_sales), 0) as gross_margin_pct,
    sum(store_opex) as store_opex,
    sum(store_contribution) as store_contribution,
    sum(store_contribution_opex_prorated) as store_contribution_opex_prorated,
    sum(store_contribution_opex_monthly) as store_contribution_opex_monthly,
    sum(case when not is_profitable then 1 else 0 end) as loss_making_stores,
    sum(case when not is_profitable_opex_prorated then 1 else 0 end) as loss_making_stores_opex_prorated,
    sum(units) / nullif(sum(store_sqft), 0) * 1000 as units_per_1k_sqft,
    sum(net_sales) / nullif(sum(store_sqft), 0) as net_sales_per_sqft,
    sum(store_opex) / nullif(sum(store_sqft), 0) as opex_per_sqft
from {{ ref('mart_store_yearly') }}
where store_id <> -1
group by all
