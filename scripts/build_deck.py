"""Build the CEO PowerPoint deck from the generated charts + mart figures."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

BASE=os.path.join(os.path.dirname(__file__),"..")
FIG=os.path.join(BASE,"reports","figures")
OUT=os.path.join(BASE,"reports","Retail_Performance_Review.pptx")

# palette
INK=RGBColor(0x0b,0x0b,0x0b); INK2=RGBColor(0x52,0x51,0x4e); MUTE=RGBColor(0x8a,0x89,0x84)
BLUE=RGBColor(0x2a,0x78,0xd6); NAVY=RGBColor(0x10,0x42,0x81); AQUA=RGBColor(0x1b,0xaf,0x7a)
GOOD=RGBColor(0x0c,0xa3,0x0c); CRIT=RGBColor(0xd0,0x3b,0x3b); WARN=RGBColor(0xed,0xa1,0x00)
SURF=RGBColor(0xfc,0xfc,0xfb); PANEL=RGBColor(0xf3,0xf5,0xf8); LINE=RGBColor(0xe5,0xe4,0xe0)
WHITE=RGBColor(0xff,0xff,0xff)

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
SW,SH=prs.slide_width,prs.slide_height
BLANK=prs.slide_layouts[6]
FONT="Calibri"

def slide():
    s=prs.slides.add_slide(BLANK)
    bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,SW,SH)
    bg.fill.solid(); bg.fill.fore_color.rgb=SURF; bg.line.fill.background()
    bg.shadow.inherit=False
    s.shapes._spTree.remove(bg._element); s.shapes._spTree.insert(2,bg._element)
    return s

def tb(s,l,t,w,h,text,size,color=INK,bold=False,align=PP_ALIGN.LEFT,font=FONT,
       anchor=MSO_ANCHOR.TOP,line_spacing=1.0,italic=False):
    box=s.shapes.add_textbox(l,t,w,h); tf=box.text_frame; tf.word_wrap=True
    tf.vertical_anchor=anchor
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    lines=text.split("\n")
    for i,ln in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.line_spacing=line_spacing
        r=p.add_run(); r.text=ln; f=r.font
        f.size=Pt(size); f.bold=bold; f.italic=italic; f.name=font; f.color.rgb=color
    return box

def rect(s,l,t,w,h,fill=None,line=None,lw=1.0,shadow=False,round=False):
    shp=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if round else MSO_SHAPE.RECTANGLE,l,t,w,h)
    if fill is None: shp.fill.background()
    else: shp.fill.solid(); shp.fill.fore_color.rgb=fill
    if line is None: shp.line.fill.background()
    else: shp.line.color.rgb=line; shp.line.width=Pt(lw)
    shp.shadow.inherit=False
    return shp

def header(s,kicker,title,color=BLUE):
    rect(s,Inches(0),Inches(0),Inches(0.18),SH,fill=color)
    tb(s,Inches(0.6),Inches(0.32),Inches(12),Inches(0.3),kicker.upper(),12.5,color=color,bold=True)
    tb(s,Inches(0.6),Inches(0.62),Inches(12.2),Inches(0.7),title,25,color=INK,bold=True)
    rect(s,Inches(0.62),Inches(1.32),Inches(12.1),Pt(1.6),fill=LINE)

_PAGE=[1]
def footer(s,n=None):
    _PAGE[0]+=1
    tb(s,Inches(0.6),Inches(7.06),Inches(8),Inches(0.3),
       "Retail Performance Review  ·  dbt + DuckDB  ·  Confidential",9,color=MUTE)
    tb(s,Inches(12.0),Inches(7.06),Inches(0.9),Inches(0.3),str(_PAGE[0]),9,color=MUTE,align=PP_ALIGN.RIGHT)

def pic(s,name,l,t,w=None,h=None,maxw=None,maxh=None):
    path=os.path.join(FIG,name); iw,ih=Image.open(path).size; ar=iw/ih
    if w is None and h is None:
        w=maxw
        if w/ar>maxh: h=maxh; w=int(maxh*ar)
        else: h=int(w/ar)
    elif w is not None and h is None: h=int(w/ar)
    elif h is not None and w is None: w=int(h*ar)
    s.shapes.add_picture(path,l,t,width=int(w),height=int(h))
    return int(w),int(h)

def pic_center(s,name,cx,t,maxw,maxh):
    w,h=pic(s,name,0,0,maxw=maxw,maxh=maxh)
    p=s.shapes[-1]; p.left=int(cx-w/2); p.top=int(t)
    return w,h

# ============================================================= S1 TITLE
s=slide()
rect(s,0,0,SW,Inches(2.65),fill=NAVY)
rect(s,0,Inches(2.65),SW,Inches(0.09),fill=BLUE)
tb(s,Inches(0.9),Inches(0.72),Inches(11),Inches(0.4),"RETAIL PERFORMANCE REVIEW",15,color=RGBColor(0x9e,0xc5,0xf4),bold=True)
tb(s,Inches(0.9),Inches(1.16),Inches(11.6),Inches(1.2),"Profitable growth, 2019–2022:\nwhere it came from and where it went",30,color=WHITE,bold=True,line_spacing=1.02)
tb(s,Inches(0.9),Inches(2.95),Inches(11),Inches(0.4),
   "A dbt + DuckDB pipeline over a single denormalised extract — cleaned, normalised, and turned into decisions.",13.5,color=INK2)
# KPI strip
kpis=[("Net sales 2022","$12.7M","+10.5% YoY",GOOD),
      ("Gross margin 2022","37.3%","−3.8 pts YoY",CRIT),
      ("Gross profit 2022","$4.73M","+0.4% YoY",WARN),
      ("Operating profit 2022","$1.39M","−9.0% YoY",CRIT)]
x=Inches(0.9); cw=Inches(2.85); gap=Inches(0.16)
for lab,val,delta,col in kpis:
    card=rect(s,x,Inches(3.9),cw,Inches(1.7),fill=WHITE,line=LINE,lw=1,round=True)
    tb(s,x+Inches(0.22),Inches(4.06),cw-Inches(0.4),Inches(0.4),lab,11.5,color=INK2,bold=True)
    tb(s,x+Inches(0.22),Inches(4.4),cw-Inches(0.4),Inches(0.7),val,30,color=NAVY,bold=True)
    tb(s,x+Inches(0.22),Inches(5.12),cw-Inches(0.4),Inches(0.4),delta,13,color=col,bold=True)
    x=Emu(int(x)+int(cw)+int(gap))
tb(s,Inches(0.9),Inches(6.0),Inches(11.6),Inches(1.0),
   "Bottom line: sales hit a record, but profit stalled. The cause is specific and fixable — and the single biggest\nupside is pricing, not cost.",13,color=INK,bold=False,line_spacing=1.1)
tb(s,Inches(0.9),Inches(6.9),Inches(11),Inches(0.3),"Prepared for the CEO  ·  20 July 2026",11,color=MUTE)

# ============================================================= S2 EXEC SUMMARY
s=slide(); header(s,"Executive summary","Record sales, stalled profit — and a clear way back")
findings=[
 ("1","Growth turned unprofitable in 2022",
  "Net sales rose +10.5% to $12.7M, but gross margin fell 3.8 pts (41.1%→37.3%). "
  "Gross profit was flat (+0.4%) and operating profit fell 9.0%.",CRIT),
 ("2","One cause: a Furniture cost shock",
  "Furniture landed cost jumped +36% on 1 Jan 2022 with no price change. That alone cut "
  "gross profit by $490k — wiping out the +$509k every other category added.",WARN),
 ("3","Biggest lever is pricing, not cost",
  "Non-West regions sell identical products (same cost) at 40–55% lower prices. Closing part "
  "of this gap is worth millions in margin at no volume risk.",GOOD),
 ("4","Profit is highly concentrated",
  "The West is 60% of sales at ~2× the margin of every other region; the top 25 of 287 stores "
  "are half of revenue. The winning playbook is known — scale it.",BLUE),
]
y=Inches(1.65); ch=Inches(1.24); gapv=Inches(0.12)
for num,htext,body,col in findings:
    rect(s,Inches(0.6),y,Inches(12.15),ch,fill=WHITE,line=LINE,lw=1,round=True)
    rect(s,Inches(0.6),y,Inches(0.12),ch,fill=col)
    tb(s,Inches(0.9),y+Inches(0.14),Inches(0.8),Inches(1),num,34,color=col,bold=True)
    tb(s,Inches(1.75),y+Inches(0.16),Inches(10.7),Inches(0.4),htext,16,color=INK,bold=True)
    tb(s,Inches(1.75),y+Inches(0.6),Inches(10.8),Inches(0.6),body,12.5,color=INK2,line_spacing=1.05)
    y=Emu(int(y)+int(ch)+int(gapv))
footer(s,2)

# ============================================================= S3 PIPELINE DAG
s=slide(); header(s,"Pipeline · 1 of 3","From one messy extract to decision-ready marts")
layers=[
 ("SOURCE","raw.consolidated_transactions","509,480 rows · 24 cols\nwide, denormalised, contaminated",MUTE),
 ("STAGING","stg_consolidated_transactions","snake_case · cast types\nnon-destructive DQ flags",BLUE),
 ("INTERMEDIATE","int_transactions_cleaned","dedup (latest ingest)\nper-unit cost + economics",AQUA),
 ("MARTS — CORE","dim_product · dim_store · fct_sales","normalised star schema\ntested keys + relationships",NAVY),
]
x=Inches(0.6); bw=Inches(2.92); bh=Inches(1.9); gap=Inches(0.18); ty=Inches(1.75)
for i,(kick,name,desc,col) in enumerate(layers):
    rect(s,x,ty,bw,bh,fill=WHITE,line=col,lw=1.5,round=True)
    rect(s,x,ty,bw,Inches(0.42),fill=col,round=False)
    tb(s,x+Inches(0.12),ty+Inches(0.06),bw-Inches(0.24),Inches(0.32),kick,11,color=WHITE,bold=True)
    tb(s,x+Inches(0.16),ty+Inches(0.56),bw-Inches(0.3),Inches(0.7),name,12.5,color=INK,bold=True,line_spacing=0.98)
    tb(s,x+Inches(0.16),ty+Inches(1.28),bw-Inches(0.3),Inches(0.6),desc,10.5,color=INK2,line_spacing=1.0)
    if i<3:
        ar=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,x+bw+Inches(0.01),ty+Inches(0.8),Inches(0.16),Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb=col; ar.line.fill.background(); ar.shadow.inherit=False
    x=Emu(int(x)+int(bw)+int(gap))
# seed callout
rect(s,Inches(0.6),Inches(3.95),Inches(3.5),Inches(0.95),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(0.78),Inches(4.06),Inches(3.2),Inches(0.3),"SEED",10.5,color=BLUE,bold=True)
tb(s,Inches(0.78),Inches(4.32),Inches(3.2),Inches(0.5),"seed_state_region\ncanonical state → region map",11,color=INK2,line_spacing=1.0)
# CEO marts row
tb(s,Inches(0.6),Inches(5.1),Inches(12),Inches(0.3),"CEO MARTS  (built only from the star schema)",12,color=NAVY,bold=True)
marts=["mart_sales_annual","mart_sales_monthly","mart_region_performance","mart_product_performance","mart_store_performance","mart_growth_drivers_2022","mart_data_quality"]
x=Inches(0.6)
for mname in marts:
    w=Inches(1.72)
    rect(s,x,Inches(5.45),w,Inches(0.62),fill=WHITE,line=NAVY,lw=1,round=True)
    tb(s,x+Inches(0.05),Inches(5.5),w-Inches(0.1),Inches(0.5),mname.replace("mart_","").replace("_","\n"),9.5,color=INK,bold=True,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE,line_spacing=0.9)
    x=Emu(int(x)+int(w)+int(Inches(0.06)))
rect(s,Inches(0.6),Inches(6.35),Inches(12.15),Inches(0.5),fill=RGBColor(0xe8,0xf5,0xe8),line=GOOD,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.44),Inches(11.8),Inches(0.35),
   "✓  uv run dbt build  →  1 seed · 2 views · 8 tables · 34 tests   PASS=47  ERROR=0",12.5,color=RGBColor(0x0a,0x66,0x0a),bold=True)
footer(s,3)

# ============================================================= S4 CONTAMINATION
s=slide(); header(s,"Pipeline · 2 of 3","Data contamination found — and how each was fixed",color=CRIT)
tb(s,Inches(0.6),Inches(1.45),Inches(12),Inches(0.35),
   "Detected by diffing the extract against reproducible logic; every issue is quantified in mart_data_quality (nothing dropped silently).",11.5,color=INK2)
rows=[
 ("Issue","Rows","How it was handled",True),
 ("Duplicate re-ingested transactions","9,815","Keep latest ingested_at per transaction_id (sales-ops rule)",False),
 ("Clone duplicates with fresh ids","1,308","Exact economic copies (only landed cost survived); detected & excluded",False),
 ("Per-pack vs per-unit cost mix-up","75,274","Use landed_unit_cost (per-unit, = actual paid); unit/standard are per-PACK",False),
 ("Product-name corruption (Vanities→Cosmetics)","11,498","Canonical name = modal product_name_catalog",False),
 ("Region mislabelled (MD→NE) / 'Unknown'","2,190","Derive region from state_code via canonical seed",False),
 ("Null product/store keys (orphans)","2,618","Excluded from fact; counted in DQ scorecard",False),
 ("Restated store with 10× inflated opex","174","Modal attribute per store removes the restated row",False),
 ("Sentinel '99901' garbage rows","100","Excluded (not a real product/store)",False),
 ("Returns (negative quantity)","4,907","Kept and netted → all figures are net of returns",False),
 ("Unreliable product SCD dates","6,624","Ignored for the fact (inconsistent with actual sales)",False),
]
y=Inches(1.9); rh=Inches(0.435)
cw1,cw2,cw3=Inches(4.6),Inches(1.2),Inches(6.35)
x0=Inches(0.6)
for i,(a,b,c,hd) in enumerate(rows):
    fill=NAVY if hd else (WHITE if i%2 else PANEL)
    tcol=WHITE if hd else INK; tcol2=WHITE if hd else INK2
    rect(s,x0,y,cw1,rh,fill=fill,line=LINE,lw=0.5)
    rect(s,x0+cw1,y,cw2,rh,fill=fill,line=LINE,lw=0.5)
    rect(s,x0+cw1+cw2,y,cw3,rh,fill=fill,line=LINE,lw=0.5)
    tb(s,x0+Inches(0.12),y,cw1-Inches(0.2),rh,a,11 if not hd else 11.5,color=tcol,bold=hd,anchor=MSO_ANCHOR.MIDDLE)
    tb(s,x0+cw1+Inches(0.08),y,cw2-Inches(0.16),rh,b,11 if not hd else 11.5,color=(WARN if not hd else WHITE),bold=True,anchor=MSO_ANCHOR.MIDDLE,align=PP_ALIGN.RIGHT)
    tb(s,x0+cw1+cw2+Inches(0.12),y,cw3-Inches(0.2),rh,c,10.5 if not hd else 11.5,color=tcol2,bold=hd,anchor=MSO_ANCHOR.MIDDLE)
    y=Emu(int(y)+int(rh))
footer(s,4)

# ============================================================= S5 DECISIONS
s=slide(); header(s,"Pipeline · 3 of 3","Key modelling decisions (and what I rejected)")
dec=[
 ("Cost basis for margin","landed_unit_cost — the actual per-unit cost paid.",
  "unit_cost / standard_unit_cost are per-PACK (= landed × pack_size). Using them raw understates margin by ~10 pts. Standard/pack_size kept for budget-margin sensitivity.",BLUE),
 ("Region source of truth","Derive from state_code via a canonical US-Census seed.",
  "region_name in the extract is corrupted (Maryland split ~50/50 to 'Northeast'; ~100 'Unknown'). Majority-vote fails on a 50/50 split, so a seed is more robust.",AQUA),
 ("Duplicate resolution","Keep the latest ingested_at per transaction_id.",
  "9,815 re-ingested rows share identical economics. Lineage breaks the tie; Transaction Date stays the economic truth.",NAVY),
 ("Returns","Keep negative quantities; report net of returns.",
  "Returns are real economic events (4,907 rows, valid prices). Gross-of-returns available as a sensitivity.",GOOD),
 ("Store opex cadence","Treat direct_store_operating_costs as ANNUAL.",
  "A monthly reading would be ~3.5× total revenue — economically impossible. Used only for an operating-profit lens.",WARN),
 ("Grain & keys","fct_sales = one row per de-duplicated transaction.",
  "Unique, not-null transaction_id; relationship tests to dim_product & dim_store. Star schema, not re-aggregated raw.",BLUE),
]
x=Inches(0.6); y=Inches(1.6); cw=Inches(5.98); ch=Inches(1.62); gx=Inches(0.19); gy=Inches(0.14)
for i,(t,rule,why,col) in enumerate(dec):
    cx=x if i%2==0 else Emu(int(x)+int(cw)+int(gx))
    cy=Emu(int(y)+ (i//2)*(int(ch)+int(gy)))
    rect(s,cx,cy,cw,ch,fill=WHITE,line=LINE,lw=1,round=True)
    rect(s,cx,cy,Inches(0.1),ch,fill=col)
    tb(s,cx+Inches(0.26),cy+Inches(0.12),cw-Inches(0.45),Inches(0.3),t.upper(),11,color=col,bold=True)
    tb(s,cx+Inches(0.26),cy+Inches(0.42),cw-Inches(0.45),Inches(0.45),rule,12.5,color=INK,bold=True,line_spacing=0.98)
    tb(s,cx+Inches(0.26),cy+Inches(0.9),cw-Inches(0.45),Inches(0.7),why,10.3,color=INK2,line_spacing=1.0)
footer(s,5)

# ============================================================= S5b DEDUP & ASSUMPTIONS
s=slide(); header(s,"Pipeline · deep dive","De-duplication done properly — and the assumptions behind the numbers")
tb(s,Inches(0.6),Inches(1.45),Inches(12.1),Inches(0.35),
   "The headline swing hinges on two things: catching every duplicate, and a few explicit accounting choices. Both are shown here.",11.5,color=INK2)
# LEFT: two kinds of duplicate + rejected rule
tb(s,Inches(0.6),Inches(1.95),Inches(6.0),Inches(0.3),"TWO KINDS OF DUPLICATE — ONE IS INVISIBLE TO id-DEDUP",11,color=NAVY,bold=True)
dd=[("Re-ingestion — same transaction_id","9,815",
     "Same sale loaded twice on different ingested_at dates. Keep the latest ingest (−2.0% of raw sales).",NAVY),
    ("Clone copies — fresh transaction_ids","1,308",
     "Exact economic copies appended above the organic id range. id-dedup can't see them; their tell is that only landed_unit_cost survived (per-pack costs NULL).",CRIT),
    ("Rejected — de-dup on the economic key","241k",
     "Same product/store/month/qty/price repeats are legitimate (241k in the clean baseline). That rule would delete ~half of real sales.",WARN)]
y=Inches(2.3); ch=Inches(1.28)
for t,n,body,col in dd:
    rect(s,Inches(0.6),y,Inches(6.05),ch,fill=WHITE,line=LINE,lw=1,round=True)
    rect(s,Inches(0.6),y,Inches(0.1),ch,fill=col)
    tb(s,Inches(0.82),y+Inches(0.11),Inches(4.45),Inches(0.35),t,11.5,color=INK,bold=True)
    tb(s,Inches(5.28),y+Inches(0.11),Inches(1.28),Inches(0.35),n,12,color=col,bold=True,align=PP_ALIGN.RIGHT)
    tb(s,Inches(0.82),y+Inches(0.52),Inches(5.65),Inches(0.72),body,10.2,color=INK2,line_spacing=1.02)
    y=Emu(int(y)+int(ch)+int(Inches(0.1)))
# RIGHT: sensitivity table
tb(s,Inches(6.95),Inches(1.95),Inches(5.8),Inches(0.3),"ACCOUNTING ASSUMPTIONS & THEIR SENSITIVITY",11,color=NAVY,bold=True)
sens=[("Assumption","Choice","If changed",True),
 ("Cost basis","landed (actual)","standard ÷ pack ≈ same margin",False),
 ("Returns","net of returns","exclude → +~$0.13M/yr (gross)",False),
 ("Store opex","annual","monthly = 3.5× revenue (impossible)",False),
 ("Clone dupes","removed","keep → sales +0.25% overstated",False),
 ("Region","state_code seed","trust raw region_name → MD wrong",False)]
ty=Inches(2.3); trh=Inches(0.6); c1w,c2w,c3w=Inches(1.55),Inches(1.75),Inches(2.5); tx=Inches(6.95)
for i,(a,b,c,hd) in enumerate(sens):
    fill=NAVY if hd else (WHITE if i%2 else PANEL)
    tca=WHITE if hd else INK; tcb=WHITE if hd else INK2
    rect(s,tx,ty,c1w,trh,fill=fill,line=LINE,lw=0.5)
    rect(s,tx+c1w,ty,c2w,trh,fill=fill,line=LINE,lw=0.5)
    rect(s,tx+c1w+c2w,ty,c3w,trh,fill=fill,line=LINE,lw=0.5)
    tb(s,tx+Inches(0.1),ty,c1w-Inches(0.16),trh,a,10.5,color=tca,bold=True,anchor=MSO_ANCHOR.MIDDLE)
    tb(s,tx+c1w+Inches(0.08),ty,c2w-Inches(0.14),trh,b,10.3,color=(GOOD if not hd else WHITE),bold=hd if hd else True,anchor=MSO_ANCHOR.MIDDLE)
    tb(s,tx+c1w+c2w+Inches(0.1),ty,c3w-Inches(0.16),trh,c,9.8,color=tcb,anchor=MSO_ANCHOR.MIDDLE,line_spacing=0.95)
    ty=Emu(int(ty)+int(trh))
# validation strip
rect(s,Inches(0.6),Inches(6.2),Inches(12.15),Inches(0.72),fill=RGBColor(0xe8,0xf5,0xe8),line=GOOD,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.3),Inches(11.8),Inches(0.55),
   "✓  Validation: after cleaning, sales reconcile to the pre-contamination baseline to the dollar "
   "($45.34M over 4 years) — confirming no duplicate was missed and no real sale was dropped.",11.5,color=RGBColor(0x0a,0x66,0x0a),bold=True,line_spacing=1.0)
footer(s)

# ============================================================= S6 SALES GROWTH
s=slide(); header(s,"Insight · Q1 — Are we growing?","Yes — steady double-digit top-line growth")
pic(s,"c1_net_sales.png",Inches(0.55),Inches(1.7),maxw=Inches(6.2),maxh=Inches(4.2))
pic(s,"c11_monthly.png",Inches(6.75),Inches(1.9),maxw=Inches(6.4),maxh=Inches(3.6))
rect(s,Inches(0.6),Inches(6.05),Inches(12.15),Inches(0.85),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.14),Inches(11.8),Inches(0.7),
   "Net sales grew from $10.4M (2019) to $12.7M (2022): flat through COVID (2020), then +11.0% and +10.5%. "
   "December is the clear seasonal peak every year — plan inventory and staffing around it.",12,color=INK,line_spacing=1.05)
footer(s,6)

# ============================================================= S6b MONTHLY TRENDS
s=slide(); header(s,"Insight · Q1 — Monthly evaluation","Steady underlying growth; a clean margin break in 2022")
pic(s,"c13_monthly_trend.png",Inches(0.5),Inches(1.62),maxw=Inches(6.35),maxh=Inches(4.35))
pic(s,"c14_monthly_margin.png",Inches(6.95),Inches(1.62),maxw=Inches(6.35),maxh=Inches(4.35))
rect(s,Inches(0.6),Inches(6.05),Inches(12.15),Inches(0.85),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.14),Inches(11.8),Inches(0.7),
   "Stripping out seasonality, the 12-month average climbs steadily — annual net sales rose ~$0.75M/year on average ($10.4M→$12.7M) — real, broad-based demand growth. "
   "But monthly gross margin, stable at ~41% for three years, steps down abruptly in Jan 2022 and stays there — the Furniture cost shock, visible to the month.",
   12,color=INK,line_spacing=1.05)
footer(s)

# ============================================================= S7 PROFIT STALL
s=slide(); header(s,"Insight · Q1 / Q4 — Are we growing profitably?","No — 2022 growth did not reach the bottom line",color=CRIT)
pic(s,"c12_yoy_growth.png",Inches(0.55),Inches(1.7),maxw=Inches(6.3),maxh=Inches(4.2))
pic(s,"c3_margin_trend.png",Inches(6.95),Inches(1.7),maxw=Inches(6.1),maxh=Inches(4.2))
rect(s,Inches(0.6),Inches(6.05),Inches(12.15),Inches(0.85),fill=RGBColor(0xfb,0xea,0xea),line=CRIT,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.14),Inches(11.8),Inches(0.7),
   "Net sales grew +10.5% but gross profit grew just +0.4% and operating profit fell 9.0%. The gap is entirely gross margin, "
   "down 3.8 pts to 37.3% — the business worked harder in 2022 for the same profit. Why? → next slide.",12,color=INK,line_spacing=1.05)
footer(s,7)

# ============================================================= S8 FURNITURE
s=slide(); header(s,"Insight · Q3 — What drove (and drained) 2022?","A single Furniture cost shock erased the gains",color=WARN)
pic(s,"c4_gp_bridge.png",Inches(0.5),Inches(1.6),maxw=Inches(7.4),maxh=Inches(4.35))
pic(s,"c5_furniture_cost.png",Inches(7.95),Inches(1.75),maxw=Inches(5.25),maxh=Inches(3.1))
rect(s,Inches(7.95),Inches(5.05),Inches(5.25),Inches(1.85),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(8.15),Inches(5.16),Inches(4.9),Inches(0.3),"THE MECHANICS",11,color=WARN,bold=True)
tb(s,Inches(8.15),Inches(5.44),Inches(4.9),Inches(1.4),
   "• Furniture landed cost +36% on 1 Jan 2022\n• Selling price unchanged → margin 32%→7%\n"
   "• Furniture gross profit: −$490k\n• All other categories: +$509k combined\n• Net effect: profit flat",11.5,color=INK,line_spacing=1.12)
footer(s,8)

# ============================================================= S9 REGIONS
s=slide(); header(s,"Insight · Q2 — Regional performance","The West carries the business")
pic(s,"c6_region_sales.png",Inches(0.55),Inches(1.7),maxw=Inches(6.2),maxh=Inches(4.2))
pic(s,"c7_region_margin.png",Inches(6.85),Inches(1.7),maxw=Inches(6.2),maxh=Inches(4.2))
rect(s,Inches(0.6),Inches(6.05),Inches(12.15),Inches(0.85),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.14),Inches(11.8),Inches(0.7),
   "West = 60% of sales AND ~47% margin (2× the rest). Northeast is smallest, shrinking (−8.8%) and least profitable (18%). "
   "Every region's margin fell in 2022 — the Furniture shock is nationwide.",12,color=INK,line_spacing=1.05)
footer(s,9)

# ============================================================= S9b REGION x CATEGORY HEATMAP
s=slide(); header(s,"Insight · Q2 — Regional × category profitability","Two problems in one view: a Western premium and a Furniture hole")
pic_center(s,"c15_region_cat_heatmap.png",int(SW/2),Inches(1.68),maxw=Inches(11.4),maxh=Inches(4.15))
rect(s,Inches(0.6),Inches(6.0),Inches(12.15),Inches(0.92),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.1),Inches(11.8),Inches(0.78),
   "Read across each row: the West earns a premium in every single category on the same catalogue (Household 61% vs ~41% elsewhere). "
   "Read down the Furniture column: it is loss-making in the Midwest, South and Northeast — those regions were under-pricing furniture "
   "even before the 2022 cost shock pushed it below water.",12,color=INK,line_spacing=1.04)
footer(s)

# ============================================================= S10 PRICING GAP
s=slide(); header(s,"Insight · Q4 — The biggest profit lever","Non-West regions under-price identical products",color=GOOD)
pic_center(s,"c8_pricing_gap.png",int(SW/2),Inches(1.7),maxw=Inches(10.3),maxh=Inches(3.9))
rect(s,Inches(0.6),Inches(5.85),Inches(12.15),Inches(1.05),fill=RGBColor(0xe8,0xf5,0xe8),line=GOOD,lw=1.2,round=True)
tb(s,Inches(0.85),Inches(5.96),Inches(11.8),Inches(0.9),
   "Cost is identical across regions (it's a product attribute), so this is pure pricing. Candles cost $5.78 everywhere yet "
   "sell for $14 in the West vs $9 in the Northeast; Computers cost $856 yet range $1,458 → $1,000. "
   "Closing even part of this gap adds margin with no extra volume — the single largest, lowest-risk profit opportunity.",12,color=RGBColor(0x0a,0x55,0x0a),line_spacing=1.05)
footer(s,10)

# ============================================================= S10b FURNITURE PRICING (PROBLEM SEGMENT)
s=slide(); header(s,"Insight · Q4 — Pricing the problem segment","Furniture: the pricing gap turned a cost shock into losses",color=CRIT)
pic(s,"c16_furniture_region.png",Inches(0.5),Inches(1.65),maxw=Inches(7.4),maxh=Inches(4.5))
# right: the GP swing and the point
rect(s,Inches(8.05),Inches(1.7),Inches(5.15),Inches(2.55),fill=WHITE,line=LINE,lw=1,round=True)
tb(s,Inches(8.25),Inches(1.82),Inches(4.8),Inches(0.3),"FURNITURE GROSS PROFIT: 2021 → 2022",11,color=CRIT,bold=True)
swing=[("West","+$500k","+$297k",AQUA),("Northeast","+$44k","−$53k",CRIT),
       ("Midwest","+$62k","−$48k",CRIT),("South","+$49k","−$31k",CRIT)]
yy=Inches(2.2)
for rg,a,b,col in swing:
    tb(s,Inches(8.25),yy,Inches(1.6),Inches(0.3),rg,11.5,color=INK,bold=True)
    tb(s,Inches(9.75),yy,Inches(1.2),Inches(0.3),a,11,color=INK2,align=PP_ALIGN.RIGHT)
    tb(s,Inches(11.0),yy,Inches(0.5),Inches(0.3),"→",11,color=INK2,align=PP_ALIGN.CENTER)
    tb(s,Inches(11.5),yy,Inches(1.5),Inches(0.3),b,11.5,color=col,bold=True,align=PP_ALIGN.RIGHT)
    yy=Emu(int(yy)+int(Inches(0.5)))
tb(s,Inches(8.25),Inches(4.28),Inches(4.85),Inches(0.5),
   "All three non-West regions flipped to a loss; only the West stayed profitable.",10.5,color=INK2,italic=True,line_spacing=1.0)
rect(s,Inches(0.6),Inches(6.35),Inches(12.15),Inches(0.6),fill=RGBColor(0xfb,0xea,0xea),line=CRIT,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.44),Inches(11.8),Inches(0.45),
   "The West prices furniture at $119 (23% margin); everyone else sells it below cost. The fix is regional pricing, not just supplier cost.",11.5,color=CRIT,bold=True)
footer(s)

# ============================================================= S11 PRODUCTS & CONCENTRATION
s=slide(); header(s,"Insight · Q2 — Products & concentration","A few products and stores drive the result")
pic(s,"c9_top_products.png",Inches(0.55),Inches(1.7),maxw=Inches(6.4),maxh=Inches(4.4))
pic(s,"c10_concentration.png",Inches(7.0),Inches(1.85),maxw=Inches(6.1),maxh=Inches(3.7))
rect(s,Inches(0.6),Inches(6.05),Inches(12.15),Inches(0.85),fill=PANEL,line=LINE,lw=1,round=True)
tb(s,Inches(0.85),Inches(6.14),Inches(11.8),Inches(0.7),
   "Computers, Dinnerware & Cookware lead sales; highest-margin lines are Home Fragrances (75%), Vanities (66%) & Cocktail Glasses (58%). "
   "The top 25 of 287 stores are ~half of revenue — Los Angeles alone is $3.8M at 58% margin.",12,color=INK,line_spacing=1.05)
footer(s,11)

# ============================================================= S12 RECOMMENDATIONS
s=slide(); header(s,"Recommendations","Four moves to restore profitable growth")
recs=[
 ("Fix Furniture economics — now","Reprice Furniture and/or renegotiate the supplier to reverse the +36% cost step. "
  "Restoring 2021 margins recovers ≈$490k of gross profit.","≈ $0.5M GP","Highest / fastest",CRIT),
 ("Close the regional pricing gap","Test raising non-West prices toward Western levels on identical SKUs. Even a partial "
  "convergence on Electronics & Household adds margin with no volume added.","Multi-$M margin","Highest value",GOOD),
 ("Scale the West playbook","West delivers 2× margin on the same catalogue. Codify its pricing/assortment and extend "
  "to Midwest & South; review the loss-making store tail.","Structural","Medium term",BLUE),
 ("Institutionalise data quality","Keep the dbt tests + mart_data_quality as a standing monitor so cost shocks, dupes and "
  "mis-mappings are caught automatically, not months later.","Risk control","Ongoing",NAVY),
]
y=Inches(1.62); ch=Inches(1.14); gy=Inches(0.12)
for i,(t,body,impact,when,col) in enumerate(recs):
    rect(s,Inches(0.6),y,Inches(12.15),ch,fill=WHITE,line=LINE,lw=1,round=True)
    rect(s,Inches(0.6),y,Inches(0.12),ch,fill=col)
    tb(s,Inches(0.9),y+Inches(0.13),Inches(0.7),Inches(0.8),str(i+1),30,color=col,bold=True)
    tb(s,Inches(1.65),y+Inches(0.13),Inches(7.7),Inches(0.4),t,15,color=INK,bold=True)
    tb(s,Inches(1.65),y+Inches(0.55),Inches(7.8),Inches(0.55),body,11,color=INK2,line_spacing=1.0)
    rect(s,Inches(9.65),y+Inches(0.2),Inches(2.95),Inches(0.74),fill=PANEL,line=LINE,lw=0.75,round=True)
    tb(s,Inches(9.78),y+Inches(0.27),Inches(2.7),Inches(0.3),impact,12.5,color=col,bold=True)
    tb(s,Inches(9.78),y+Inches(0.6),Inches(2.7),Inches(0.28),when,9.5,color=INK2)
    y=Emu(int(y)+int(ch)+int(gy))
tb(s,Inches(0.6),Inches(6.86),Inches(12.2),Inches(0.4),
   "Assumptions: margin = landed cost; opex annual; figures net of returns. With more time: price-elasticity test design, "
   "fully-loaded store P&L, and a Furniture supplier deep-dive.",9.5,color=MUTE,italic=True,line_spacing=1.0)
footer(s,12)

prs.save(OUT)
print("saved",OUT,"slides:",len(prs.slides._sldIdLst))
