{% docs transaction_id %}Business transaction id from the source. Unique in fct_sales after dedup; not unique in the raw extract.{% enddocs %}
{% docs transaction_month %}Economic date of the sale (first day of the month). Used for all time series, not ingested_at.{% enddocs %}
{% docs transaction_year %}Calendar year of transaction_month.{% enddocs %}
{% docs product_id %}Product key. -1 = unknown member (placeholder 99901 rows, unresolvable keys).{% enddocs %}
{% docs store_id %}Store key. -1 = unknown member (placeholder 99901 rows, store key not recoverable).{% enddocs %}
{% docs product_name %}Product name as used on transactions (product 19 is 'Cosmetics'; catalog alias kept in dim_product).{% enddocs %}
{% docs product_category %}Product category (Dining, Electronics, Furniture, Household, Kitchen, Sports; 'Unknown' for -1).{% enddocs %}
{% docs quantity %}Units sold on the line; negative = return (Manual source only).{% enddocs %}
{% docs units %}Sum of quantity (net of returns).{% enddocs %}
{% docs unit_price %}Selling price per unit. Set as product-month list price x store price list x promotion.{% enddocs %}
{% docs landed_cost_per_unit %}Landed cost per selling unit ("what we actually paid"). Margin basis. One value per product-month (tested).{% enddocs %}
{% docs standard_cost_per_unit %}Standard (budget) cost per selling unit = standard_unit_cost ÷ pack_size. Sensitivity only; null on 1,308 source rows.{% enddocs %}
{% docs net_sales %}Net Sales = quantity x unit_price, net of returns.{% enddocs %}
{% docs gross_margin %}Gross Margin = Net Sales - quantity x landed cost per unit.{% enddocs %}
{% docs gross_margin_standard %}Gross Margin on standard cost (Finance budget view). Sensitivity only.{% enddocs %}
{% docs gross_margin_pct %}Gross Margin ÷ Net Sales (landed cost basis).{% enddocs %}
{% docs store_opex %}Direct store operating cost, treated as ANNUAL and charged in full to each store trading in the year.{% enddocs %}
{% docs store_contribution %}Profitability measure: Gross Margin - direct store opex (annual, full year). No central costs in the data.{% enddocs %}
{% docs store_contribution_opex_prorated %}Sensitivity: Gross Margin - annual opex x months traded ÷ 12 (part-year and new stores).{% enddocs %}
{% docs store_contribution_opex_monthly %}Sensitivity: Gross Margin - opex x 12 (reading opex as monthly). Not credible: every price list loses money.{% enddocs %}
{% docs price_list %}Store's regular price list: 'Premium (1.00)' all California stores, 'Base (0.59)', 'Township (0.53)' all Township stores, 'Other' (2 one-offs), 'Unknown' for -1.{% enddocs %}
{% docs price_list_index %}Store's regular price as a share of the product-month list price (median price_index of its sales).{% enddocs %}
{% docs yoy_abs %}Change vs the previous year, absolute.{% enddocs %}
{% docs yoy_pct %}Change vs the previous year, %.{% enddocs %}
{% docs prior_year %}Same measure for the previous year.{% enddocs %}
