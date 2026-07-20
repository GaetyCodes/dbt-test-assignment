/*
    Deduplicate the landing extract to one row per transaction and resolve the
    cost representation.

    Duplicates: 9,815 transaction_ids are ingested twice (same economics, different
    ingested_at). Sales-ops rule -> keep the latest ingested_at.

    Cost: landed_unit_cost is the true per-UNIT cost (what we actually paid; it
    reconciles exactly to the source cost). unit_cost / standard_unit_cost are
    per-PACK (= landed_unit_cost * pack_size), so they must be divided by pack_size
    before being compared to the per-unit unit_price. We use landed cost for actual
    margin and expose a standard (budget) cost per unit for sensitivity.
*/

with staged as (

    select * from {{ ref('stg_consolidated_transactions') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by transaction_id
                order by ingested_at desc, source_system
            ) as _row_num
        from staged
    )
    where _row_num = 1

),

costed as (

    select
        transaction_id,
        product_id,
        store_id,
        transaction_month,
        date_trunc('year', transaction_month)                      as transaction_year_start,
        cast(extract(year from transaction_month) as integer)      as transaction_year,
        quantity,
        unit_price,
        pack_size,

        -- chosen per-unit costs
        landed_unit_cost                                           as unit_cost_landed,
        pack_standard_cost / nullif(pack_size, 0)                  as unit_cost_standard,

        -- economics (net of returns: quantity is negative for returns)
        round(quantity * unit_price, 4)                            as net_revenue,
        round(quantity * landed_unit_cost, 4)                      as cogs_landed,
        round(quantity * unit_price - quantity * landed_unit_cost, 4) as gross_profit,

        is_return,
        has_invalid_key,
        is_clone_duplicate,
        source_system,
        ingested_at
    from deduplicated

)

select * from costed
