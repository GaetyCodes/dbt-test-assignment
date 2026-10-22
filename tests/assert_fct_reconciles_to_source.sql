-- Source -> fact: one fact row per distinct source transaction_id, and Net Sales equal to the source
-- counted once per transaction_id. Computed straight from the raw source, independent of the dedup model.
with src as (
    select
        count(distinct "Transaction ID") as n_txn,
        sum(line_sales) as net_sales
    from (
        select "Transaction ID", max(cast(quantity as integer) * cast(unit_price as double)) as line_sales
        from {{ source('raw', 'consolidated_transactions') }}
        group by 1
    )
),

fct as (
    select count(*) as n_txn, sum(net_sales) as net_sales from {{ ref('fct_sales') }}
)

select src.*, fct.n_txn as fct_n_txn, fct.net_sales as fct_net_sales
from src cross join fct
where src.n_txn <> fct.n_txn or abs(src.net_sales - fct.net_sales) > 0.01
