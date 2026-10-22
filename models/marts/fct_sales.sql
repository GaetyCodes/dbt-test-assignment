-- Grain: one transaction line (transaction_id) per month, store, product. Returns are negative quantity lines.
-- Cost basis: landed_cost_per_unit (what we actually paid). Standard cost kept for sensitivity.
-- unit_cost / standard_unit_cost on the extract are per PACK -> divided by pack_size in staging.
with txn as (

    select * from {{ ref('int_transactions_keyed') }}

)

select
    transaction_id,
    transaction_month,
    year(transaction_month) as transaction_year,
    product_id,
    store_id,
    quantity,
    unit_price,
    landed_cost_per_unit,
    standard_cost_per_unit,
    quantity * unit_price as net_sales,
    quantity * landed_cost_per_unit as cogs_landed,
    quantity * standard_cost_per_unit as cogs_standard,
    quantity * (unit_price - landed_cost_per_unit) as gross_margin,
    quantity * (unit_price - standard_cost_per_unit) as gross_margin_standard,
    is_return,
    source_system,
    ingested_at,
    source_row_count > 1 as was_duplicated,
    is_product_key_recovered,
    is_store_key_recovered,
    is_ingested_before_txn
from txn
