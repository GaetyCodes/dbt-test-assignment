-- Light cleaning only: snake_case, types, light normalisation of text, and DQ flags.
-- No rows are dropped here; dedup / key repair happens in intermediate.
with source as (

    select * from {{ source('raw', 'consolidated_transactions') }}

),

renamed as (

    select
        row_number() over () as source_row_id,
        cast("Transaction ID" as integer) as transaction_id,
        cast("Transaction Date" as date) as transaction_month,
        cast(quantity as integer) as quantity,
        cast(unit_price as double) as unit_price,
        cast(unit_cost as double) as unit_cost_per_pack,
        cast(standard_unit_cost as double) as standard_cost_per_pack,
        -- landed cost is already expressed per selling unit (landed = unit_cost / pack_size on clean rows)
        cast(landed_unit_cost as double) as landed_cost_per_unit,
        cast(pack_size as integer) as pack_size,
        cast(cast("Product index" as double) as integer) as product_id,
        trim("Product Name") as product_name_on_transaction,
        trim(product_name_catalog) as product_name_catalog,
        trim(product_category) as product_category,
        cast(product_effective_from as date) as product_effective_from,
        cast(product_effective_to as date) as product_effective_to,
        cast(cast("Store ID" as double) as integer) as store_id,
        trim(regexp_replace(store_name, '\s*\(restated\)', '')) as store_name,
        store_name like '%(restated)%' as is_restated_store_row,
        upper(trim(state_code)) as state_code,
        trim(state) as state_name,
        trim(region_name) as region_name,
        trim(store_type) as store_type,
        cast(store_sqft as double) as store_sqft,
        cast(direct_store_operating_costs as double) as store_opex_annual,
        trim(source_system) as source_system,
        cast(ingested_at as date) as ingested_at
    from source

)

select
    *,
    -- costs on the extract are per pack for unit_cost / standard_unit_cost; convert to per selling unit
    unit_cost_per_pack / pack_size as unit_cost_per_unit,
    standard_cost_per_pack / pack_size as standard_cost_per_unit,
    quantity < 0 as is_return,
    ingested_at < transaction_month as is_ingested_before_txn
from renamed
