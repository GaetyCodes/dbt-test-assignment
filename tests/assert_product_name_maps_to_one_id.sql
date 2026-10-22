-- Product keys are recovered by name in int_transactions_keyed. That is only safe if each transaction product
-- name belongs to exactly one product id in the rows that do carry an id (99901 placeholder excluded).
select product_name_on_transaction, count(distinct product_id) as n_ids
from {{ ref('stg_consolidated_transactions') }}
where product_id is not null and product_id <> 99901
group by 1
having count(distinct product_id) > 1
