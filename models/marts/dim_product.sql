/*
    Product dimension: one row per valid product_id.

    Conflicts resolved:
      - name: the transaction-level "Product Name" is corrupted for product 19
        (recorded as "Cosmetics"); the catalog name ("Vanities") is canonical, so
        we take the modal product_name_catalog.
      - category: modal product_category per product.
      - product_effective_from/to are ignored: they are inconsistent with actual
        sales dates (6,624 sales fall outside the stated window) and are not used
        to filter the fact.

    Invalid keys (NULL and the 99901 sentinel "Unknown Bundle") are excluded.
*/

with staged as (

    select *
    from {{ ref('stg_consolidated_transactions') }}
    where not has_invalid_key
      and not is_clone_duplicate

)

select
    product_id,
    mode(product_name_catalog) as product_name,
    mode(product_category)     as product_category
from staged
group by product_id
