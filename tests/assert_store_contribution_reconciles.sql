-- Store contribution: store mart (incl. unknown store) and price-list mart (excl. unknown) both tie to mart_kpi_yearly.
with k as (
    select transaction_year, store_contribution, gross_margin from {{ ref('mart_kpi_yearly') }}
),

s as (
    select transaction_year, sum(coalesce(store_contribution, gross_margin)) as store_contribution
    from {{ ref('mart_store_yearly') }} group by 1
),

p as (
    select l.transaction_year, sum(l.store_contribution) + coalesce(max(u.gm), 0) as store_contribution
    from {{ ref('mart_price_list_yearly') }} as l
    left join (
        select transaction_year, sum(gross_margin) as gm from {{ ref('mart_store_yearly') }} where store_id = -1 group by 1
    ) as u using (transaction_year)
    group by 1
)

select k.transaction_year, k.store_contribution, s.store_contribution as store_mart, p.store_contribution as price_list_mart
from k
left join s using (transaction_year)
left join p using (transaction_year)
where abs(k.store_contribution - s.store_contribution) > 0.01
    or abs(k.store_contribution - p.store_contribution) > 0.01
