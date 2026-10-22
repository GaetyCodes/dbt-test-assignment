-- One attribute set per product. Product 19 is always 'Cosmetics' on the transaction but the catalog
-- alternates with 'Vanities' on ~60% of rows in every year (not a dated rename) -> keep transaction name, retain catalog alias.
-- Product 99901 ('Unknown Bundle', 100 manual rows in Jun-2022) is a placeholder -> unknown member.
with stg as (

    select * from {{ ref('stg_consolidated_transactions') }}
    where product_id is not null and product_id <> 99901

)

select
    product_id,
    mode(product_name_on_transaction) as product_name,
    string_agg(distinct product_name_catalog, ' / ') as product_catalog_names,
    mode(product_category) as product_category,
    mode(pack_size) as pack_size,
    min(product_effective_from) as product_effective_from,
    max(product_effective_to) as product_effective_to
from stg
group by product_id
