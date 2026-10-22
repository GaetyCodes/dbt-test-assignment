# Solution notes

```bash
uv sync && export DBT_PROFILES_DIR="$(pwd)" && uv run dbt build   # 12 models, 23 tests
uv run python scripts/build_deck.py                                # -> deliverables/ceo_sales_review.pptx
```

Layers: `stg_consolidated_transactions` (types, per-unit costs, DQ flags) ->
`int_transactions_deduped`, `int_product_attributes`, `int_store_attributes`, `int_transactions_keyed` ->
`dim_product`, `dim_store`, `fct_sales` (grain: one transaction line) ->
`mart_kpi_yearly`, `mart_product_yearly`, `mart_store_yearly`, `mart_sales_monthly`.

Key decisions (details in model comments and deck slide 5): dedup on latest `ingested_at`; landed cost as margin basis
(standard as sensitivity); unit/standard cost divided by `pack_size`; missing keys recovered by name; placeholder 99901 ->
unknown member -1; Maryland -> South; store 50 restated 10x opex rejected; store opex treated as annual.
