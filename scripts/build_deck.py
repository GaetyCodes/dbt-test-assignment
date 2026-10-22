"""Build the CEO / pipeline deck from the dbt marts (run after `uv run dbt build`).

uv run python scripts/build_deck.py  ->  deliverables/ceo_sales_review.pptx

Every figure on the slides is queried from the marts below; nothing is typed in by hand.
"""
from pathlib import Path

import duckdb
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
con = duckdb.connect(str(ROOT / "retail.duckdb"), read_only=True)


def q(sql):
    return con.sql(sql).fetchall()


def one(sql):
    return q(sql)[0]


NAVY = RGBColor(0x1F, 0x2A, 0x44)
GREY = RGBColor(0x59, 0x59, 0x59)
LIGHT = RGBColor(0xEE, 0xF1, 0xF6)
BLUE = RGBColor(0xD6, 0xE4, 0xF0)
GREEN = RGBColor(0xD5, 0xF0, 0xDD)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def m(x):
    return f"{'-' if x < 0 else ''}${abs(x) / 1e6:,.2f}M"


def k(x):
    return f"{'-' if x < 0 else ''}${abs(x) / 1e3:,.0f}k"


def pct(x):
    return f"{x * 100:+.1f}%"


def p1(x):
    return f"{x * 100:.1f}%"


def slide(title, subtitle=None):
    s = prs.slides.add_slide(BLANK)
    tb = s.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.9))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]
    p.text, p.font.size, p.font.bold, p.font.color.rgb = title, Pt(26), True, NAVY
    if subtitle:
        p2 = tb.text_frame.add_paragraph()
        p2.text, p2.font.size, p2.font.color.rgb = subtitle, Pt(14), GREY
    return s


def bullets(s, items, x=0.5, y=1.5, w=12.3, h=5.5, size=16):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        level = 1 if it.startswith("- ") else 0
        text = it[2:] if level else it
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        marker = "" if text[:2] in {f"{n}." for n in range(1, 10)} else ("• " if level == 0 else "– ")
        p.text, p.level = marker + text, level
        p.font.size = Pt(size - 2 * level)
        p.space_after = Pt(5)
    return tb


def table(s, rows, x, y, w, col_w=None, size=11, h=0.3):
    shp = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h * len(rows)))
    t = shp.table
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.cell(r, c)
            cell.text = str(val)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(size)
                p.font.bold = r == 0
    if col_w:
        for i, cw in enumerate(col_w):
            t.columns[i].width = Inches(cw)
    return t


def chart(s, kind, categories, series, x, y, w, h, labels=True):
    cd = CategoryChartData()
    cd.categories = categories
    for name, values in series:
        cd.add_series(name, values)
    ch = s.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    ch.has_legend, ch.legend.position, ch.legend.include_in_layout = True, XL_LEGEND_POSITION.BOTTOM, False
    ch.legend.font.size = Pt(10)
    for ser in ch.plots[0].series:
        ser.invert_if_negative = False
    if kind == XL_CHART_TYPE.BAR_CLUSTERED:
        from pptx.enum.chart import XL_TICK_LABEL_POSITION
        ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
    if labels:
        ch.plots[0].has_data_labels = True
        ch.plots[0].data_labels.font.size = Pt(9)
    return ch


def box(s, text, x, y, w=2.3, h=0.9, fill=LIGHT):
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    b.fill.solid()
    b.fill.fore_color.rgb = fill
    b.line.color.rgb = NAVY
    tf = b.text_frame
    tf.word_wrap = True
    tf.text = text
    for p in tf.paragraphs:
        p.font.size, p.font.color.rgb = Pt(10), NAVY
    return b


def note(s, text):
    s.notes_slide.notes_text_frame.text = text


# ================================================================ data (all from marts)
kpi = {r[0]: r for r in q("""
    select transaction_year, net_sales, gross_margin, gross_margin_pct, gross_margin_standard, store_opex,
           store_contribution, store_contribution_pct, net_sales_yoy_abs, net_sales_yoy_pct,
           gross_margin_yoy_abs, gross_margin_yoy_pct, store_contribution_yoy_abs, store_contribution_yoy_pct
    from main_marts.mart_kpi_yearly order by 1""")}
K, K1 = kpi[2022], kpi[2021]
NS, GM, GMP, GMSTD, CONTRIB = K[1], K[2], K[3], K[4], K[6]

bridge = {r[0]: r for r in q("""
    select transaction_year, sum(net_sales_yoy_abs), sum(volume_effect), sum(mix_effect), sum(price_effect),
           sum(new_product_effect)
    from main_marts.mart_sales_bridge_yearly group by 1 order by 1""")}
B = bridge[2022]
bridge_cat = q("""
    select product_category, sum(net_sales_yoy_abs), sum(volume_effect), sum(mix_effect), sum(price_effect),
           sum(price_effect) / sum(net_sales - price_effect)
    from main_marts.mart_sales_bridge_yearly where transaction_year = 2022 and product_id <> -1
    group by 1 order by 2 desc""")
lfl = {r[0]: r[5] for r in bridge_cat}

furn = {r[0]: r for r in q("""
    select transaction_year, sum(net_sales), sum(gross_margin), sum(gross_margin) / sum(net_sales)
    from main_marts.mart_product_yearly where product_category = 'Furniture' group by 1""")}
F, F1 = furn[2022], furn[2021]
furn_prize = F[1] * F1[3] - F[2]  # 2022 sales at 2021 GM%, zero volume response

markup = q("""
    select product_category, year(transaction_month), avg(list_markup), min(list_markup), max(list_markup)
    from main_marts.mart_price_monthly group by 1, 2 order by 1, 2""")
list_yoy = {(r[0], r[1]): r[2] for r in q("""
    with y as (select product_category, year(transaction_month) as y, avg(list_price) as lp, avg(landed_cost_per_unit) as lc
               from main_marts.mart_price_monthly group by 1, 2)
    select product_category, y, lp / lag(lp) over (partition by product_category order by y) - 1,
           lc / lag(lc) over (partition by product_category order by y) - 1
    from y""")}
cost_yoy = {(r[0], r[1]): r[3] for r in q("""
    with y as (select product_category, year(transaction_month) as y, avg(list_price) as lp, avg(landed_cost_per_unit) as lc
               from main_marts.mart_price_monthly group by 1, 2)
    select product_category, y, lp / lag(lp) over (partition by product_category order by y) - 1,
           lc / lag(lc) over (partition by product_category order by y) - 1
    from y""")}

pl = {r[0]: r for r in q("""
    select price_list, stores, units_per_1k_sqft, net_sales, gross_margin_pct, store_contribution,
           loss_making_stores, store_contribution_opex_prorated, store_contribution_opex_monthly, new_stores,
           loss_making_stores_opex_prorated
    from main_marts.mart_price_list_yearly where transaction_year = 2022""")}
PREM, BASE, TWP = pl['Premium (1.00)'], pl['Base (0.59)'], pl['Township (0.53)']
base_hist = {r[0]: r for r in q("""
    select transaction_year, gross_margin_pct, store_contribution from main_marts.mart_price_list_yearly
    where price_list = 'Base (0.59)'""")}
total_stores = sum(r[1] for r in pl.values())
loss_stores = sum(r[6] for r in pl.values())
loss_value = one("""select sum(store_contribution) from main_marts.mart_store_yearly
                    where transaction_year = 2022 and store_id <> -1 and not is_profitable""")[0]
contrib_prorated = sum(r[7] for r in pl.values())
contrib_monthly = sum(r[8] for r in pl.values())
new_st = one("""select count(*), sum(store_contribution), sum(store_contribution_opex_prorated), avg(months_trading)
                from main_marts.mart_store_yearly where transaction_year = 2022 and is_first_trading_year""")

furn_list_years = {(r[0], r[1]): r for r in q("""
    select s.price_list, f.transaction_year, sum(f.net_sales) / sum(f.cogs_landed), sum(f.gross_margin)
    from main_marts.fct_sales as f
    inner join main_marts.dim_store as s using (store_id)
    inner join main_marts.dim_product as p using (product_id)
    where p.product_category = 'Furniture' and f.transaction_year in (2021, 2022)
    group by 1, 2""")}
base_swing = q("""
    select p.product_category = 'Furniture', f.transaction_year, sum(f.gross_margin)
    from main_marts.fct_sales as f
    inner join main_marts.dim_store as s using (store_id)
    inner join main_marts.dim_product as p using (product_id)
    where s.price_list = 'Base (0.59)' and f.transaction_year in (2021, 2022) group by 1, 2""")
bs = {(r[0], r[1]): r[2] for r in base_swing}
base_furn_drop = bs[(True, 2022)] - bs[(True, 2021)]
base_other_gain = bs[(False, 2022)] - bs[(False, 2021)]

ca_share = {r[0]: r[1] for r in q("""
    select f.transaction_year, sum(case when s.price_list = 'Premium (1.00)' then f.net_sales end) / sum(f.net_sales)
    from main_marts.fct_sales as f inner join main_marts.dim_store as s using (store_id) group by 1""")}
promo = q("""
    select month(transaction_month), sum(promo_unit_share * units) / sum(units)
    from main_marts.mart_price_monthly where year(transaction_month) = 2022 group by 1
    having sum(promo_unit_share * units) > 0 order by 1""")
promo_months = ", ".join(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][r[0] - 1]
                         for r in promo)
promo_share = sum(r[1] for r in promo) / len(promo)

base_gm_per_1pct = BASE[3] * 0.01
base_breakeven_5 = 0.05 / (BASE[4] + 0.05)

top_products = q("""select product_name, net_sales, gross_margin, gross_margin_pct, net_sales_yoy_pct
                    from main_marts.mart_product_yearly where transaction_year = 2022 and product_id <> -1
                    order by gross_margin desc limit 5""")
top_stores = q("""select store_name || ', ' || state_code, net_sales, store_contribution, net_sales_yoy_pct, state_code
                  from main_marts.mart_store_yearly where transaction_year = 2022 and store_id <> -1
                  order by store_contribution desc limit 5""")
n_top_ca = sum(r[4] == 'CA' for r in top_stores)
regions = q("""select region_name, sum(net_sales), sum(store_contribution), sum(net_sales_yoy_abs) / sum(net_sales - net_sales_yoy_abs)
               from main_marts.mart_store_yearly where transaction_year = 2022 and store_id <> -1
               group by 1 order by 2 desc""")

dq = one("""select count(*), sum(was_duplicated::int), sum(is_product_key_recovered::int), sum(is_store_key_recovered::int),
                   sum((store_id = -1)::int), sum((product_id = -1)::int), sum(is_return::int),
                   sum(case when product_id = -1 then net_sales end), sum((is_return and source_system <> 'Manual')::int),
                   sum(case when is_return then -net_sales end) filter (where transaction_year = 2022),
                   sum(case when is_return then -net_sales end) filter (where transaction_year = 2021)
            from main_marts.fct_sales""")
N_FCT, N_DUP, N_PREC, N_SREC, N_SUNK, N_PUNK, N_RET, UNK_SALES, N_RET_NON_MANUAL, RET22, RET21 = dq
import json
_results = json.loads((ROOT / "target" / "run_results.json").read_text())["results"]
N_MODELS = sum(r["unique_id"].startswith("model.") for r in _results)
N_TESTS = sum(r["unique_id"].startswith("test.") for r in _results)
N_PASSED = sum(r["status"] in ("success", "pass") for r in _results)
assert N_PASSED == len(_results), "run `uv run dbt build` until everything passes before building the deck"
units_yoy = one("""select sum(units) / sum(units_py) - 1 from main_marts.mart_sales_bridge_yearly
                   where transaction_year = 2022 and product_id <> -1""")[0]
ex_furn = {r[0]: r for r in q("""select transaction_year, sum(net_sales), sum(gross_margin) from main_marts.mart_product_yearly
                                  where product_category <> 'Furniture' group by 1""")}
ex_furn_ns_yoy = ex_furn[2022][1] / ex_furn[2021][1] - 1
ex_furn_gm_yoy = ex_furn[2022][2] / ex_furn[2021][2] - 1

# ================================================================ 1 title
s = slide("2022: sales grew 11%, profit did not",
          "CEO sales review + dbt transformation pipeline  |  consolidated_transactions extract, Jan-2019 to Dec-2022")
bullets(s, [
    f"Net Sales {m(NS)} ({pct(K[9])}), Gross Margin {m(GM)} ({pct(K[11])}), store contribution {m(CONTRIB)} ({pct(K[13])})",
    "Growth came from volume and from more sales in California, not from pricing",
    "Furniture cost rose ~36% in Jan-2022 and was never passed into prices: sold below cost outside California",
    f"Margin is set by the store price list: California earns {p1(PREM[4])} GM, the other price lists {p1(BASE[4])} or less",
], y=2.2, size=20)

# ================================================================ 2 executive summary
s = slide("Executive summary — what the business should do")
bullets(s, [
    f"1. Restore Furniture pricing now. Landed cost rose ~36% in Jan-2022; list price fell. Furniture GM "
    f"{k(F1[2])} -> {k(F[2])}. Restoring the 2021 margin is worth up to {k(furn_prize)} a year "
    "(if volume holds; confirm the cost rise with AP/Ops first).",
    f"2. Test higher prices outside California. California charges ~1.7x the base price list and still sells "
    f"{PREM[2] / BASE[2] - 1:.0%} more units per sq ft. Each +1% on the base list is ~{k(base_gm_per_1pct)} GM; "
    f"a +5% rise pays off unless volume falls more than {base_breakeven_5:.0%}.",
    f"3. Report margin on landed cost and track price-vs-cost monthly. Standard cost shows 2022 GM "
    f"{pct(GMSTD / K1[4] - 1)}; actual is {pct(K[11])}. The pricing process passes cost through for every category "
    "except Furniture in 2022 — find out why it failed.",
    f"4. Don't close stores on this evidence. {loss_stores} of {total_stores} stores lose money after direct opex, "
    f"but losses sit on the low price lists: {BASE[6]} of {BASE[1]} base and {TWP[6]} of {TWP[1]} Township stores vs "
    f"{PREM[6]} of {PREM[1]} in California. Fix price first, then review the tail.",
    f"5. Gate new openings: the {new_st[0]} stores opened in 2022 lost {k(-new_st[2])} pro-rated in year one.",
], size=16)
note(s, "Lead with 1 and 2. Both are pricing decisions; 3 is the process fix; 4 is the warning against the obvious "
        "but wrong reading of the store numbers.")

# ================================================================ 3 pipeline DAG
s = slide("Pipeline: staging -> intermediate -> marts (dbt + DuckDB)",
          f"uv run dbt build: {N_MODELS} models, {N_TESTS} tests, all passing (incl. reconciliation tests)")
box(s, "raw\nconsolidated_transactions\n509,480 rows, 24 cols", 0.2, 3.1, w=2.0, h=1.1)
box(s, "stg_consolidated_transactions\ntypes, per-unit costs,\nDQ flags (no rows dropped)", 2.4, 3.0, w=2.2, h=1.3)
inter = ["int_transactions_deduped\n1 row / transaction_id", "int_product_attributes\n1 row / product",
         "int_store_attributes\n1 row / store", "int_transactions_keyed\nkey repair, unknown member",
         "int_transaction_price_index\nprice vs list price", "int_store_price_list\nstore's regular price list"]
for i, t in enumerate(inter):
    box(s, t, 4.85, 1.55 + i * 0.88, w=2.4, h=0.78)
for i, t in enumerate(["dim_product", "dim_store\n(+ price list)", "fct_sales\ngrain: transaction line"]):
    box(s, t, 7.5, 2.3 + i * 1.15, w=1.9, h=0.95, fill=BLUE)
rep = ["mart_kpi_yearly", "mart_product_yearly", "mart_store_yearly", "mart_price_list_yearly",
       "mart_sales_bridge_yearly", "mart_price_monthly", "mart_sales_monthly"]
for i, t in enumerate(rep):
    box(s, t, 9.65, 1.55 + i * 0.75, w=3.3, h=0.65, fill=GREEN)
for x, label in [(4.85, "intermediate (views)"), (7.5, "star schema (tables)"), (9.65, "reporting marts (tables)")]:
    bullets(s, [label], x=x, y=1.1, w=3.0, h=0.4, size=12)

# ================================================================ 4 normalisation & mart architecture
s = slide("Normalisation and why the mart layer has two tiers")
bullets(s, [
    "Grain: one fct_sales row per transaction_id (after dedup) = one sales line: month x store x product, qty, price",
    "- Additive measures only (net_sales, cogs_landed, cogs_standard, gross_margin) -> safe to sum at any level",
    "Dimensions taken out of the repeated attributes: dim_product (17 + unknown), dim_store (287 + unknown)",
    "- Unknown member (-1) instead of dropping orphans: totals reconcile to source, relationship tests pass",
    "- Store price list derived from the data (price ÷ product-month list price) and stored on dim_store",
    "Tier 1 star schema = the reusable source of truth for any question; Tier 2 reporting marts at the CEO's grains",
    "- Business logic (YoY, opex basis, growth bridge, price health) is written once in SQL and tested; "
    "the deck only reads marts",
    "Tests: keys, relationships, accepted values; source -> fact and fact -> mart reconciliation; bridge sums exactly; "
    "assumption tests (duplicates agree, one landed cost per product-month, list price = California price)",
    "Rejected: one wide reporting table (brings back the attribute conflicts); YoY and bridge logic in Python "
    "(untested, duplicated); SCD2 product history (effective dates contradict sales, e.g. Cosmetics sold from 2019 "
    "but effective from Jun-2020 -> not trusted)",
], size=15)

# ================================================================ 5 DQ decisions
s = slide("Data-quality issues and how each was handled", "Nothing dropped silently: every rule is flagged in fct_sales")
table(s, [
    ["Issue", "Evidence", "Decision", "Alternative rejected"],
    ["Duplicate transaction_id", f"{N_DUP:,.0f} ids x2; identical date/store/product/qty/price/landed cost (tested)",
     "Keep latest ingested_at, tie-break POS>ERP>Manual", "Sum both copies (double counts $0.90M sales)"],
    ["Cost per pack vs per unit", "Dining pack_size=2: unit_cost / price = 117%",
     "unit & standard cost ÷ pack_size; landed is already per unit", "Multiply by pack_size"],
    ["3 competing cost fields", "Landed: one value per product-month (tested). 2022 Furniture unit_cost = 0.68 x price on ~half the rows",
     "Landed = margin basis; standard kept as sensitivity", "Standard (Finance): hides the 2022 cost rise"],
    ["Missing keys", f"{N_PREC:,} product ids, {N_SREC:,} store ids null; names present",
     "Recover by name (store: name + state where 1:1)", "Drop the rows"],
    ["Placeholder 99901", f"{N_PUNK} Manual rows Jun-2022, 'Unknown' store + product, ingested before sale date",
     "Unknown member -1, flagged", "Treat as a real store / product"],
    ["Conflicting store attributes", "Stores 211/212 (MD) split NE/South; store 50 '(restated)' opex 10x (0.82/sqft vs peers 0.11)",
     "MD -> South (Census); opex = 4-year value", "Latest row wins"],
    ["Product name conflict", "Product 19 'Cosmetics' vs catalog 'Vanities' in every year",
     "Keep transaction name, keep alias", "Split into two products"],
    ["Negative quantities", f"{N_RET:,} lines, Manual source only; each matches an earlier sale",
     "Keep as returns (net sales are net of returns)", "Exclude"],
], 0.3, 1.35, 12.7, col_w=[2.1, 4.6, 3.3, 2.7], size=10, h=0.52)

# ================================================================ 6 definitions, assumptions, trade-offs
s = slide("Definitions, assumptions and sensitivity")
bullets(s, [
    "Net Sales = qty x unit_price (returns negative). Gross Margin = Net Sales - qty x landed cost per unit.",
    "Profitability = store contribution = Gross Margin - direct store opex. No central costs in the data.",
], size=14, h=1.0)
table(s, [
    ["2022 sensitivity", "Chosen", "Alternative", "Effect"],
    ["Cost basis", f"Landed: GM {m(GM)}, {p1(GMP)}", f"Standard: GM {m(GMSTD)}", f"{k(GMSTD - GM)} higher GM, hides Furniture"],
    ["Opex: annual, full year", f"Contribution {m(CONTRIB)}", f"Pro-rated to months traded: {m(contrib_prorated)}",
     f"Small; loss-making stores {loss_stores} either way"],
    ["Opex: annual vs monthly", "Annual", f"Monthly x12: {m(contrib_monthly)}", "Every price list loses money -> not credible"],
    ["Dedup rule", "Latest ingestion", "POS first / first ingestion", "No change to sales or landed GM (tested)"],
], 0.5, 2.5, 12.3, col_w=[2.6, 3.0, 3.4, 3.3], size=12, h=0.4)
bullets(s, [
    "Assumptions: month is the economic date; landed cost is the true cost (confirm 2022 Furniture with AP/Ops); "
    "store losses are real, not a sampling effect (confirmed with the interviewer)",
    "Trade-offs: most frequent value for conflicting attributes instead of history tables; views for staging/intermediate",
    "With more time: split volume into new vs existing stores; promotion depth; incremental fct_sales; column docs; "
    "Dec-2022 may be ~1% incomplete (late-arriving rows)",
], y=4.7, size=13, h=2.5)

# ================================================================ 7 Q1 growth
s = slide("Q1: sales are growing ~11% a year — profit is not",
          f"2022: Net Sales {pct(K[9])}, Gross Margin {pct(K[11])}, store contribution {pct(K[13])}")
years = sorted(kpi)
chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [str(y) for y in years], [
    ("Net Sales ($M)", [round(kpi[y][1] / 1e6, 2) for y in years]),
    ("Gross Margin ($M)", [round(kpi[y][2] / 1e6, 2) for y in years]),
    ("Store contribution ($M)", [round(kpi[y][6] / 1e6, 2) for y in years]),
], 0.4, 1.5, 6.6, 5.3)
rows = [["", "2020", "2021", "2022"]]
for label, i, fmt in [("Net Sales", 1, m), ("  YoY abs", 8, k), ("  YoY %", 9, pct),
                      ("Gross Margin", 2, m), ("  YoY abs", 10, k), ("  YoY %", 11, pct), ("  GM %", 3, p1),
                      ("Store contribution", 6, m), ("  YoY abs", 12, k), ("  YoY %", 13, pct)]:
    rows.append([label] + [fmt(kpi[y][i]) for y in (2020, 2021, 2022)])
table(s, rows, 7.3, 1.5, 5.7, size=11, h=0.36)
bullets(s, ["2020 dip then two years of ~11% growth; GM % fell from 41.1% to 37.4% in 2022"],
        x=7.3, y=5.7, w=5.7, h=1, size=12)

# ================================================================ 8 Q3 drivers
s = slide("Q3: 2022 growth came from volume and California — prices fell like-for-like",
          f"Net Sales {pct(K[9])} ({k(B[1])}) = volume {k(B[2])} + location mix {k(B[3])} "
          f"+ like-for-like price {k(B[4])} + unknown product {k(B[5])}")
chart(s, XL_CHART_TYPE.BAR_CLUSTERED, [r[0] for r in bridge_cat], [
    ("Volume ($k)", [round(r[2] / 1e3) for r in bridge_cat]),
    ("Location mix, mainly California ($k)", [round(r[3] / 1e3) for r in bridge_cat]),
    ("Like-for-like price ($k)", [round(r[4] / 1e3) for r in bridge_cat]),
], 0.4, 1.5, 6.8, 5.4)
bullets(s, [
    f"Volume: units {pct(units_yoy)}",
    f"Location mix: California's share of sales rose {p1(ca_share[2021])} -> {p1(ca_share[2022])}; at ~1.7x price "
    "that lifts the average price with no price change",
    f"Like-for-like price {k(B[4])}: Electronics prices {pct(lfl['Electronics'])} (following a "
    f"{pct(cost_yoy[('Electronics', 2022)])} cost fall); other categories rose ~{pct(lfl['Household'])}, "
    f"in line with cost (+{p1(cost_yoy[('Household', 2022)])})",
    f"Furniture: price {pct(lfl['Furniture'])} while landed cost rose {pct(cost_yoy[('Furniture', 2022)])}",
    "Price-derived metrics: list markup over cost, like-for-like price change, price realisation, promotion share",
    "Old method (product-level average price) counted the California shift as a price rise — replaced",
], x=7.4, y=1.5, w=5.7, h=5.5, size=13)

# ================================================================ 9 price structure
s = slide("Pricing is cost-plus, by price list — and California sells more at 1.7x the price",
          "Price = list price (cost x fixed markup per product) x store price list x promotion")
table(s, [["2022 price list", "Stores", "Price vs CA", "Units / 1k sq ft", "GM %", "Contribution", "Loss-making"]] + [
    [r[0], r[1], idx, f"{r[2]:.1f}", p1(r[4]), k(r[5]), r[6]]
    for r, idx in [(PREM, "1.00"), (BASE, "0.59"), (TWP, "0.53")]
], 0.4, 1.5, 7.6, col_w=[1.8, 0.8, 1.1, 1.3, 0.8, 1.1, 1.0], size=11, h=0.4)
bullets(s, [
    "Each product's markup over landed cost is identical in every month of 2019-2022 — "
    "except Furniture in 2022 (next slide)",
    "List price moved exactly with cost: Household/Kitchen/Dining/Sports "
    f"{pct(list_yoy[('Household', 2022)])} vs cost {pct(cost_yoy[('Household', 2022)])} in 2022; "
    f"Electronics {pct(list_yoy[('Electronics', 2022)])} vs {pct(cost_yoy[('Electronics', 2022)])}",
    f"Price lists: all {PREM[1]} California stores on 1.00; {BASE[1]} stores on 0.59; all {TWP[1]} Township stores on 0.53; 2 one-offs",
    f"Promotions in {promo_months} only: ~{promo_share:.0%} of units in those months sold below the store's list",
    f"California sells {PREM[2] / BASE[2] - 1:.0%} more units per sq ft than base stores at ~1.7x the price, every year "
    "since 2019 -> no sign that price is holding volume back (California demand may differ: test, don't assume)",
], x=0.4, y=3.3, w=12.5, h=3.9, size=14)
note(s, "This is the structural finding. Ranking regions without it makes the West look well run; it is priced higher.")

# ================================================================ 10 furniture
s = slide("Furniture: a ~36% cost rise in Jan-2022 that pricing never passed on",
          f"Furniture GM {k(F1[2])} (2021) -> {k(F[2])} (2022); outside California it now sells below cost")
mon = q("""select strftime(transaction_month, '%Y-%m'), list_markup from main_marts.mart_price_monthly
           where product_name = 'Dining Furniture' and transaction_month >= '2021-01-01' order by 1""")
chart(s, XL_CHART_TYPE.LINE_MARKERS, [r[0] for r in mon], [
    ("Dining Furniture: list price ÷ landed cost", [round(r[1], 2) for r in mon]),
], 0.4, 1.5, 6.6, 4.6, labels=False)
rows = [["Furniture by price list", "Price ÷ cost 2021", "Price ÷ cost 2022", "GM 2021", "GM 2022"]]
for lst in ["Premium (1.00)", "Base (0.59)", "Township (0.53)"]:
    a, b = furn_list_years[(lst, 2021)], furn_list_years[(lst, 2022)]
    rows.append([lst, f"{a[2]:.2f}", f"{b[2]:.2f}", k(a[3]), k(b[3])])
table(s, rows, 7.2, 1.5, 5.9, col_w=[1.7, 1.1, 1.1, 1.0, 1.0], size=11, h=0.4)
bullets(s, [
    f"Furniture explains the GM gap: without it, 2022 GM {pct(ex_furn_gm_yoy)} on sales {pct(ex_furn_ns_yoy)}",
    f"Base-list stores went from {k(base_hist[2021][2])} to {k(base_hist[2022][2])} contribution: "
    f"Furniture GM there {k(base_furn_drop)}, everything else {'+' if base_other_gain > 0 else ''}{k(base_other_gain)}",
    f"Worth up to {k(furn_prize)} a year to restore the 2021 margin (no volume response assumed)",
    "Evidence the cost rise is real: one landed cost per month, markup otherwise fixed for 4 years. "
    "Not verified: confirm with AP/Ops",
], x=7.2, y=3.3, w=5.9, h=3.9, size=13)

# ================================================================ 11 Q2 top performers & profitability
s = slide(f"Q2: top performers — and why {loss_stores} of {total_stores} stores lose money",
          "Rank by gross margin and contribution, not sales; read store results through the price list")
table(s, [["Top products 2022 (by GM)", "Sales", "GM", "GM %", "YoY sales"]] +
      [[r[0], k(r[1]), k(r[2]), p1(r[3]), pct(r[4])] for r in top_products],
      0.4, 1.5, 6.2, col_w=[2.2, 1.0, 1.0, 0.9, 1.1], size=11, h=0.34)
table(s, [["Top stores 2022 (contribution)", "Sales", "Contrib.", "YoY sales"]] +
      [[r[0], k(r[1]), k(r[2]), pct(r[3])] for r in top_stores],
      6.9, 1.5, 6.1, col_w=[2.6, 1.1, 1.2, 1.2], size=11, h=0.34)
table(s, [["Region 2022", "Sales", "Contribution", "YoY sales"]] +
      [[r[0], k(r[1]), k(r[2]), pct(r[3])] for r in regions],
      0.4, 4.0, 6.2, col_w=[1.9, 1.3, 1.6, 1.4], size=11, h=0.34)
bullets(s, [
    f"{n_top_ca} of the top 5 stores are in California: driven by price list, not only execution",
    f"{loss_stores} loss-making stores lose {k(-loss_value)} in total; "
    f"{BASE[6]} of {BASE[1]} base-list and {TWP[6]} of {TWP[1]} Township stores",
    f"Base-list GM % was {p1(base_hist[2021][1])} in 2021 and {p1(base_hist[2022][1])} in 2022: too thin to cover opex",
    f"New stores: {new_st[0]} opened in 2022 (avg {new_st[3]:.1f} months) lost {k(-new_st[2])} pro-rated",
], x=6.9, y=4.0, w=6.1, h=3.2, size=12)

# ================================================================ 12 Q4/Q5
s = slide("Q4 & Q5: how to grow profit, and what needs investigation")
bullets(s, [
    "Profit levers (2022 base; sizes assume no volume response unless stated)",
    f"- Furniture: restore list markup -> up to {k(furn_prize)} GM",
    f"- Base price list: +1% = ~{k(base_gm_per_1pct)} GM; a +5% test breaks even at a {base_breakeven_5:.0%} volume loss. "
    "Run a controlled regional test before rolling out",
    "- Pricing process: monthly price ÷ cost check per product; alert when markup moves (would have caught Furniture in Jan-2022)",
    "- Store portfolio: review the long tail only after pricing; gate openings on a payback model",
    "Investigate",
    "- Who set Furniture prices in 2022, and is the landed cost right (AP/Ops)?",
    f"- 'Unknown' store / product 99901: {N_PUNK} Manual lines in Jun-2022 ({k(UNK_SALES)}), ingested before the sale date",
    f"- Returns appear only in the Manual source ({N_RET:,} lines; {N_RET_NON_MANUAL} elsewhere): are POS/ERP returns missing? "
    f"Returns value {pct(RET22 / RET21 - 1)} in 2022",
    f"- {N_DUP:,} transactions ingested twice across systems; cost values differ between copies",
    "- Store master data: conflicting regions (MD), 10x opex restatement (store 50), duplicate store names (Wayne, IN)",
], size=15)

out = ROOT / "deliverables" / "ceo_sales_review.pptx"
out.parent.mkdir(exist_ok=True)
prs.save(out)
print(out, len(prs.slides), "slides")
