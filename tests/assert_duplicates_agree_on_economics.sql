-- Assumption behind the dedup rule: copies of a transaction_id agree on date, quantity, price and landed cost
-- (store / product ids may be null on one copy). If this fails, "keep latest ingestion" can move Net Sales.
select "Transaction ID"
from {{ source('raw', 'consolidated_transactions') }}
group by 1
having count(distinct "Transaction Date") > 1
    or count(distinct quantity) > 1
    or count(distinct unit_price) > 1
    or count(distinct landed_unit_cost) > 1
    or count(distinct "Store ID") > 1
    or count(distinct "Product index") > 1
