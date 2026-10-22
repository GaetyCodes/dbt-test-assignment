-- Net Sales YoY bridge per product: volume + location mix + like-for-like price (+ new product).
-- Cell = product x store price list. With U = units, ASP = net_sales / units, p_c = cell price:
--   volume = (U_t - U_t-1) * ASP_t-1
--   mix    = sum_c u_t,c * p_t-1,c - U_t * ASP_t-1      (shift between price lists at last year's prices)
--   price  = sum_c u_t,c * (p_t,c - p_t-1,c)            (like-for-like price change within a cell)
-- The three sum exactly to the YoY change. A cell with no prior-year sales uses the product's prior-year ASP.
-- Products with no prior year at all go to new_product_effect.
-- Location mix is needed because price lists differ ~1.7x (California vs base): a shift of sales towards
-- California raises the average price without any price change.
with cells as (

    select
        f.product_id,
        coalesce(s.price_list, 'Unknown') as price_list,
        f.transaction_year,
        sum(f.quantity) as units,
        sum(f.net_sales) as net_sales
    from {{ ref('fct_sales') }} as f
    left join {{ ref('dim_store') }} as s using (store_id)
    group by all

),

products as (

    select
        product_id,
        transaction_year,
        sum(units) as units,
        sum(net_sales) as net_sales,
        sum(net_sales) / nullif(sum(units), 0) as asp
    from cells
    group by all

),

years as (

    select distinct transaction_year from products

),

cells_with_prior as (

    select
        c.product_id,
        c.transaction_year,
        c.units,
        c.net_sales / nullif(c.units, 0) as cell_price,
        coalesce(
            prior.net_sales / nullif(prior.units, 0),
            pp.asp
        ) as cell_price_py
    from cells as c
    left join cells as prior
        on c.product_id = prior.product_id
        and c.price_list = prior.price_list
        and c.transaction_year = prior.transaction_year + 1
    left join products as pp
        on c.product_id = pp.product_id
        and c.transaction_year = pp.transaction_year + 1

),

cell_sums as (

    select
        product_id,
        transaction_year,
        sum(units * cell_price_py) as units_at_py_cell_prices,
        sum(units * (cell_price - cell_price_py)) as price_effect
    from cells_with_prior
    group by all

)

select
    p.product_id,
    d.product_name,
    d.product_category,
    p.transaction_year,
    p.net_sales,
    py.net_sales as net_sales_py,
    p.units,
    py.units as units_py,
    coalesce(p.net_sales, 0) - coalesce(py.net_sales, 0) as net_sales_yoy_abs,
    case when py.product_id is not null then (p.units - py.units) * py.asp else 0 end as volume_effect,
    case when py.product_id is not null then cs.units_at_py_cell_prices - p.units * py.asp else 0 end as mix_effect,
    case when py.product_id is not null then cs.price_effect else 0 end as price_effect,
    case when py.product_id is null then p.net_sales else 0 end as new_product_effect
from products as p
inner join years as y on p.transaction_year = y.transaction_year
left join products as py
    on p.product_id = py.product_id
    and p.transaction_year = py.transaction_year + 1
left join cell_sums as cs
    on p.product_id = cs.product_id
    and p.transaction_year = cs.transaction_year
inner join {{ ref('dim_product') }} as d on p.product_id = d.product_id
where p.transaction_year > (select min(transaction_year) from years)
