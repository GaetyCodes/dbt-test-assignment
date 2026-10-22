select * from {{ ref('int_store_attributes') }}
union all
select -1, 'Unknown', null, null, 'Unknown', null, null, null, false
