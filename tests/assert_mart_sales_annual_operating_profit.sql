-- operating_profit must equal gross_profit - operating_costs.
select
    transaction_year,
    gross_profit,
    operating_costs,
    operating_profit
from {{ ref('mart_sales_annual') }}
where abs(operating_profit - (gross_profit - operating_costs)) > 0.01
