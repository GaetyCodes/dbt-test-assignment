# Solution notes

```bash
uv sync && export DBT_PROFILES_DIR="$(pwd)" && uv run dbt build   # 17 models, 40 tests
uv run python scripts/build_deck.py                                # -> deliverables/ceo_sales_review.pptx
```

The deck script reads only the marts and refuses to run unless the last `dbt build` fully passed.

## Layers

- **staging** `stg_consolidated_transactions`: types, per-unit costs (unit / standard cost ÷ `pack_size`), DQ flags; no rows dropped.
- **intermediate**: `int_transactions_deduped` (1 row per transaction_id), `int_product_attributes`, `int_store_attributes`,
  `int_transactions_keyed` (key repair, unknown member -1), `int_transaction_price_index` (price ÷ product-month list price),
  `int_store_price_list` (each store's regular price list).
- **marts, tier 1 (star schema)**: `dim_product`, `dim_store` (+ price list), `fct_sales` (grain: one transaction line).
- **marts, tier 2 (reporting)**: `mart_kpi_yearly`, `mart_product_yearly`, `mart_store_yearly`, `mart_price_list_yearly`,
  `mart_sales_bridge_yearly` (volume / location mix / like-for-like price), `mart_price_monthly`, `mart_sales_monthly`.

## Tests

Keys, relationships and accepted values, plus singular tests in `tests/`: source -> fact and fact -> mart reconciliation,
growth bridge sums exactly, store contribution ties out, and assumption tests (duplicate copies agree, product names and the store name + state pairs used for key recovery map to one id, one landed cost
per product-month, list price is always a California price). Each reconciliation test was checked to fail on an injected error.

## Key decisions

Dedup on latest `ingested_at` (copies are economically identical, tested); landed cost as the margin basis (standard cost
as sensitivity); missing keys recovered by name; placeholder 99901 -> unknown member; Maryland -> South; store 50's
restated 10x opex rejected; store opex treated as annual (pro-rated and monthly shown as sensitivities).
