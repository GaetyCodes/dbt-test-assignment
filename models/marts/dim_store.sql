select
    s.*,
    p.price_list_index,
    p.price_list
from {{ ref('int_store_attributes') }} as s
left join {{ ref('int_store_price_list') }} as p using (store_id)
union all
select -1, 'Unknown', null, null, 'Unknown', null, null, null, false, null, 'Unknown'
