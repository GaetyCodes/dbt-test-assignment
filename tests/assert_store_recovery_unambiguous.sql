-- Store keys are recovered by (store_name, state_code). Some pairs are genuinely shared by two stores
-- (Wayne, IN -> 192 and 193), so the lookup must only assign a store when the pair maps to exactly one store.
-- Fails if any recovered row was given a store whose name + state is ambiguous.
with pairs as (
    select store_name, state_code, count(*) as n_stores
    from {{ ref('int_store_attributes') }}
    group by 1, 2
)

select k.transaction_id, k.store_id, k.store_name, k.state_code, p.n_stores
from {{ ref('int_transactions_keyed') }} as k
left join pairs as p using (store_name, state_code)
where k.is_store_key_recovered
    and k.store_id <> -1
    and coalesce(p.n_stores, 0) <> 1
