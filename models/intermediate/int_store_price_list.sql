-- Each store sells on one regular price list (its typical price_index); lower indices in some months are promotions.
-- Observed lists: 1.00 (all California stores), 0.59 (base, all other states), 0.53 (Township stores), 2 one-offs.
with idx as (

    select * from {{ ref('int_transaction_price_index') }}
    where store_id <> -1

)

select
    store_id,
    round(median(price_index), 3) as price_list_index,
    case round(median(price_index), 2)
        when 1.00 then 'Premium (1.00)'
        when 0.59 then 'Base (0.59)'
        when 0.53 then 'Township (0.53)'
        else 'Other'
    end as price_list
from idx
group by store_id
