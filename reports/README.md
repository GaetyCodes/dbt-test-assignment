# Retail Performance Review — deliverables

## Files
- `Retail_Performance_Review.pptx` — 16-slide CEO deck (pipeline + insights).
- `figures/` — source charts (matplotlib, colourblind-safe palette).
- `preview/` — flattened PNG previews of each slide (for quick review; not the deliverable).

Deck sections: title & exec summary (1–2); pipeline — DAG, contamination table, modelling
decisions, de-duplication & sensitivities deep-dive (3–6); insights — sales growth, monthly
evaluation, profit stall, Furniture cost shock, regional performance, region×category heatmap,
regional pricing gap, Furniture pricing (problem segment), products & concentration (7–15);
recommendations (16).

## Reproduce end to end
```bash
export DBT_PROFILES_DIR="$(pwd)"
uv run dbt build          # seed + models + 34 tests  -> PASS=47, ERROR=0
uv run python scripts/build_charts.py   # -> reports/figures/*.png
uv run python scripts/build_deck.py     # -> reports/Retail_Performance_Review.pptx
```

## Pipeline (dbt)
```
raw.consolidated_transactions
  └─ stg_consolidated_transactions        (staging: cast, rename, DQ flags)
       └─ int_transactions_cleaned        (dedup latest ingest + per-unit cost + economics)
            ├─ dim_product                (canonical name/category)
            ├─ dim_store                  (modal attrs; region from seed_state_region)
            └─ fct_sales                  (grain: 1 row / deduped transaction; net of returns)
                 ├─ mart_sales_annual         (net sales, margin, profit YoY)
                 ├─ mart_sales_monthly
                 ├─ mart_region_performance
                 ├─ mart_product_performance
                 ├─ mart_store_performance
                 ├─ mart_growth_drivers_2022  (price/volume/cost decomposition)
                 └─ mart_data_quality         (contamination scorecard)
```

## Cost / profit definitions
- **COGS / margin** use `landed_unit_cost` (actual per-unit cost paid).
  `unit_cost` and `standard_unit_cost` are **per-pack** (= landed × pack_size); using them raw
  understates margin ~10 pts. `standard_unit_cost / pack_size` kept for budget-margin sensitivity.
- **Net sales** = quantity × unit_price, **net of returns** (negative quantities retained).
- **Operating profit** = gross profit − direct store operating cost, treated as **annual**.

## De-duplication (two distinct mechanisms)
1. **Same-id re-ingestion** (9,815 rows): keep latest `ingested_at` per `transaction_id` (−2.0%).
2. **Clone duplicates with fresh ids** (1,308 rows): exact economic copies of real transactions,
   stamped with new `transaction_id`s in a dense block above the organic id range, so id-dedup
   cannot see them. Detected by their only-`landed_unit_cost` signature (per-pack cost columns
   NULL) and excluded. NB: de-duplicating on the *economic key* is rejected — it would delete
   ~241k **legitimate** repeat sales and roughly halve revenue. Validated against the pristine
   pre-contamination file: cleaned figures reconcile to ground truth to the dollar.

## Headline findings
- Net sales $10.4M (2019) → $12.67M (2022); +11.0% (2021), +10.5% (2022).
- Gross margin 41.1% → **37.3%** in 2022; gross profit flat (+0.4%), operating profit −8.9%.
- Cause: **Furniture landed cost +36% on 1 Jan 2022, no price pass-through** → −$490k GP.
- Biggest lever: **non-West regions under-price identical goods 40–55%** (same cost).
- West = 60% of sales at ~2× margin; top 25 of 287 stores = ~half of revenue.
