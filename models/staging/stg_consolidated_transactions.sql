with source as (

    select * from {{ source('raw', 'consolidated_transactions') }}

),

renamed as (

    select
        -- keys
        cast("Transaction ID" as integer)          as transaction_id,
        cast("Product index" as integer)           as product_id,
        cast("Store ID" as integer)                as store_id,

        -- economic date (first-of-month grain)
        cast("Transaction Date" as date)           as transaction_month,

        -- measures
        cast(quantity as integer)                  as quantity,
        cast(unit_price as double)                 as unit_price,

        -- competing cost representations (see int_transactions_cleaned for the choice)
        --   unit_cost / standard_unit_cost are per-PACK; landed_unit_cost is per-UNIT
        cast(unit_cost as double)                  as pack_unit_cost,
        cast(standard_unit_cost as double)         as pack_standard_cost,
        cast(landed_unit_cost as double)           as landed_unit_cost,
        cast(pack_size as integer)                 as pack_size,

        -- product attributes (denormalized, may conflict)
        cast("Product Name" as varchar)            as product_name_on_transaction,
        cast(product_name_catalog as varchar)      as product_name_catalog,
        cast(product_category as varchar)          as product_category,
        cast(product_effective_from as date)       as product_effective_from,
        cast(product_effective_to as date)         as product_effective_to,

        -- store attributes (denormalized, may conflict)
        cast(store_name as varchar)                as store_name,
        cast(state_code as varchar)                as state_code,
        cast(state as varchar)                     as state_name,
        cast(region_name as varchar)               as region_name_raw,
        cast(store_type as varchar)                as store_type,
        cast(store_sqft as double)                 as store_sqft,
        cast(direct_store_operating_costs as double) as direct_store_operating_costs,

        -- lineage (used only to break duplicate ties, not as economic truth)
        cast(source_system as varchar)             as source_system,
        cast(ingested_at as date)                  as ingested_at
    from source

),

flagged as (

    select
        *,
        -- data-quality flags (nothing is dropped here; handled downstream)
        (product_id is null or store_id is null
            or product_id = 99901 or store_id = 99901) as has_invalid_key,
        (quantity < 0)                                 as is_return,
        (store_name like '%(restated)%')               as is_restated_row,
        -- Injected clone duplicates: exact economic copies of real transactions,
        -- stamped with fresh transaction_ids (a dense block above the organic id
        -- range) so de-duplication by transaction_id cannot catch them. Their tell
        -- is that only landed_unit_cost survived the clone: the per-pack cost
        -- columns were left NULL (no genuine transaction has both NULL).
        (pack_unit_cost is null and pack_standard_cost is null
            and landed_unit_cost is not null)          as is_clone_duplicate
    from renamed

)

select * from flagged
