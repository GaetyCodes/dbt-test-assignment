-- One row per transaction_id.
-- Collisions (9,815 ids, 2 rows each) agree on date, store, product, quantity and price;
-- they only differ in lineage (source_system / ingested_at) and sometimes unit/standard cost.
-- Rule: keep the latest ingestion (Sales Ops guidance), tie-break POS > ERP > Manual.
-- Economic fields are identical across the pair, so the rule does not move Net Sales.
with stg as (

    select * from {{ ref('stg_consolidated_transactions') }}

),

ranked as (

    select
        *,
        count(*) over (partition by transaction_id) as source_row_count,
        row_number() over (
            partition by transaction_id
            order by
                ingested_at desc,
                case source_system when 'POS' then 1 when 'ERP' then 2 else 3 end,
                source_row_id
        ) as dedup_rank
    from stg

)

select * exclude (dedup_rank)
from ranked
where dedup_rank = 1
