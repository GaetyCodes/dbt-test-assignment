-- Assumption behind choosing landed cost as the margin basis: it behaves like a real cost
-- (one value per product per month, independent of the selling price).
select product_id, transaction_month, count(distinct landed_cost_per_unit) as n_costs
from {{ ref('fct_sales') }}
where product_id <> -1
group by 1, 2
having count(distinct landed_cost_per_unit) > 1
