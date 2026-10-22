-- Resolve one attribute set per store from conflicting repeated rows.
-- * region: mode across rows, but Maryland is forced to 'South' (US Census region) — stores 211/212 were split 50/50.
-- * opex: the most frequent value; store 50 has a '(restated)' 2022 value exactly 10x the 4-year value -> treated as a decimal error.
-- * store 99901 ('Unknown') is a placeholder, not a real store: excluded here and mapped to the unknown member in the fact.
with stg as (

    select * from {{ ref('stg_consolidated_transactions') }}
    where store_id is not null and store_id <> 99901

)

select
    store_id,
    mode(store_name) as store_name,
    mode(state_code) as state_code,
    mode(state_name) as state_name,
    case when mode(state_code) = 'MD' then 'South' else mode(region_name) end as region_name,
    mode(store_type) as store_type,
    mode(store_sqft) as store_sqft,
    mode(store_opex_annual) as store_opex_annual,
    count(distinct region_name) > 1
        or count(distinct store_opex_annual) > 1
        or count(distinct store_name) > 1 as had_conflicting_attributes
from stg
group by store_id
