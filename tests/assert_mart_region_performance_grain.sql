-- Composite primary key for mart_region_performance.
-- Fails if any (region_name, transaction_year) appears more than once.
select
    region_name,
    transaction_year,
    count(*) as row_count
from {{ ref('mart_region_performance') }}
group by region_name, transaction_year
having count(*) > 1
