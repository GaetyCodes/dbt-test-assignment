/*
    Data-quality scorecard: quantifies every contamination handled by the pipeline
    so that nothing is dropped silently. One row per issue.
*/

with staged as (
    select * from {{ ref('stg_consolidated_transactions') }}
),

metrics as (

    select 'raw_rows'                         as issue, count(*)                                                      as row_count from staged
    union all
    select 'duplicate_reingested_rows',       count(*) - count(distinct transaction_id)                              from staged
    union all
    select 'clone_duplicate_rows_new_ids',    count(*) filter (where is_clone_duplicate)                             from staged
    union all
    select 'null_product_or_store_key',       count(*) filter (where product_id is null or store_id is null)         from staged
    union all
    select 'sentinel_99901_rows',             count(*) filter (where product_id = 99901 or store_id = 99901)         from staged
    union all
    select 'return_rows_negative_qty',        count(*) filter (where is_return)                                      from staged
    union all
    select 'restated_10x_opex_rows',          count(*) filter (where is_restated_row)                                from staged
    union all
    select 'product_name_conflict_rows',      count(*) filter (where product_name_on_transaction <> product_name_catalog) from staged
    union all
    select 'region_mislabelled_rows',         count(*) filter (
                                                  where region_name_raw = 'Northeast' and state_code = 'MD'
                                                     or region_name_raw = 'Unknown')                                  from staged
    union all
    select 'pack_size_2_rows_costsplit',      count(*) filter (where pack_size = 2)                                  from staged
    union all
    select 'sales_outside_product_scd_window',count(*) filter (
                                                  where transaction_month < product_effective_from
                                                     or transaction_month > product_effective_to)                    from staged
    union all
    select 'ingested_before_transaction',     count(*) filter (where ingested_at < transaction_month)                from staged

)

select * from metrics order by row_count desc
