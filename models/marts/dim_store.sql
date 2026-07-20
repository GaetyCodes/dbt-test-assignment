/*
    Store dimension: one row per valid store_id.

    Conflicts resolved:
      - store_name / state_code / store_type / sqft: modal value per store. This
        removes the "Moreno Valley (restated)" variant whose operating cost was
        inflated 10x (127,817 vs the true 12,782); the modal (majority) row wins.
      - direct_store_operating_costs: modal value per store, treated as an ANNUAL
        figure (a monthly reading would be ~3.5x total revenue -> economically
        impossible).
      - region: DERIVED from state_code via the canonical US-Census seed rather
        than trusting region_name (Maryland is corrupted ~50/50 to "Northeast",
        and ~100 rows carry "Unknown"). This makes region a clean function of state.

    Invalid keys (NULL and the 99901 sentinel) are excluded.
*/

with staged as (

    select *
    from {{ ref('stg_consolidated_transactions') }}
    where not has_invalid_key
      and not is_clone_duplicate

),

store_attrs as (

    select
        store_id,
        mode(store_name)                    as store_name,
        mode(state_code)                    as state_code,
        mode(store_type)                    as store_type,
        mode(store_sqft)                    as store_sqft,
        mode(direct_store_operating_costs)  as annual_operating_costs
    from staged
    group by store_id

)

select
    s.store_id,
    s.store_name,
    s.state_code,
    r.state_name,
    coalesce(r.region_name, 'Unknown') as region_name,
    s.store_type,
    s.store_sqft,
    s.annual_operating_costs
from store_attrs s
left join {{ ref('seed_state_region') }} r
    on s.state_code = r.state_code
