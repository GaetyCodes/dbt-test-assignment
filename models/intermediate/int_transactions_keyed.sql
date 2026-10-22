-- Repair missing keys and route orphans to unknown members (-1) so nothing is silently dropped.
-- * Missing product_id (1,310 rows): name is present and 1:1 with id -> recover by product name.
-- * Missing store_id (1,308 rows): recover by (store_name, state_code) when that pair maps to exactly one store
--   (Wayne, IN maps to two stores -> stays unknown).
-- * 99901 placeholder product/store -> -1.
with txn as (

    select * from {{ ref('int_transactions_deduped') }}

),

products as (

    select product_id, product_name from {{ ref('int_product_attributes') }}

),

store_lookup as (

    select store_name, state_code, min(store_id) as store_id
    from {{ ref('int_store_attributes') }}
    group by 1, 2
    having count(*) = 1

)

select
    txn.* exclude (product_id, store_id),
    case
        when txn.product_id = 99901 then -1
        when txn.product_id is not null then txn.product_id
        else coalesce(p.product_id, -1)
    end as product_id,
    case
        when txn.store_id = 99901 then -1
        when txn.store_id is not null then txn.store_id
        else coalesce(s.store_id, -1)
    end as store_id,
    txn.product_id is null as is_product_key_recovered,
    txn.store_id is null as is_store_key_recovered
from txn
left join products as p
    on txn.product_id is null and txn.product_name_on_transaction = p.product_name
left join store_lookup as s
    on txn.store_id is null and txn.store_name = s.store_name and txn.state_code = s.state_code
