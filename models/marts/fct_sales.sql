/*
    Sales fact. Grain: one row per deduplicated transaction (= transaction line,
    monthly). Transaction_id is unique here after de-duplication.

    Scope: transactions with valid product AND store keys. Rows with NULL keys
    (2,618) or the 99901 sentinel (100) are excluded because they cannot be
    attributed to a dimension; their counts are surfaced in stg_data_quality.

    Returns (negative quantity, 4,907 rows) are retained so that all measures are
    NET of returns.

    Injected clone duplicates (1,308 exact economic copies stamped with fresh
    transaction_ids; see stg_consolidated_transactions.is_clone_duplicate) are
    excluded — de-dup by transaction_id cannot catch them, and de-dup by economic
    key would wrongly delete ~241k legitimate repeat sales.

    Costing: unit_cost_landed is the per-unit actual cost (see int_transactions_cleaned).
*/

with txn as (

    select *
    from {{ ref('int_transactions_cleaned') }}
    where not has_invalid_key
      and not is_clone_duplicate

)

select
    transaction_id,
    product_id,
    store_id,
    transaction_month,
    transaction_year,
    quantity,
    unit_price,
    pack_size,
    unit_cost_landed,
    unit_cost_standard,
    net_revenue,
    cogs_landed,
    gross_profit,
    round(100.0 * gross_profit / nullif(net_revenue, 0), 4) as gross_margin_pct,
    is_return,
    source_system
from txn
