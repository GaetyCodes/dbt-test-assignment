select * from {{ ref('int_product_attributes') }}
union all
select -1, 'Unknown', 'Unknown Bundle (placeholder 99901)', 'Unknown', 1, null, null
