"""Generate presentation charts from the dbt marts (retail.duckdb).
Palette: dataviz skill validated defaults (colourblind-safe)."""
import duckdb, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as fm

FIG = os.path.join(os.path.dirname(__file__), "..", "reports", "figures")
os.makedirs(FIG, exist_ok=True)
con = duckdb.connect(os.path.join(os.path.dirname(__file__), "..", "retail.duckdb"), read_only=True)

# ---- palette ----
SURFACE="#fcfcfb"; INK="#0b0b0b"; INK2="#52514e"; GRID="#e5e4e0"
BLUE="#2a78d6"; GREEN="#008300"; MAGENTA="#e87ba4"; YELLOW="#eda100"
AQUA="#1baf7a"; ORANGE="#eb6834"; VIOLET="#4a3aa7"; RED="#e34948"
GOOD="#0ca30c"; WARN="#fab219"; CRIT="#d03b3b"
# fixed region identity
REGION_C={"West":BLUE,"Midwest":GREEN,"South":YELLOW,"Northeast":ORANGE}
# ordinal year ramp (blue light->dark)
YEAR_C={2019:"#9ec5f4",2020:"#5598e7",2021:"#2a78d6",2022:"#184f95"}

plt.rcParams.update({
    "figure.facecolor":SURFACE,"axes.facecolor":SURFACE,"savefig.facecolor":SURFACE,
    "font.family":"DejaVu Sans","font.size":12,"text.color":INK,
    "axes.edgecolor":GRID,"axes.labelcolor":INK2,"xtick.color":INK2,"ytick.color":INK2,
    "axes.grid":True,"grid.color":GRID,"grid.linewidth":0.8,"axes.axisbelow":True,
})
def style(ax):
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color(GRID)
    ax.tick_params(length=0)
    ax.xaxis.grid(False)
def m(x,_=None): return f"${x/1e6:.1f}M"
def k(x,_=None): return f"${x/1e3:.0f}k"
def save(fig,name):
    fig.tight_layout(); fig.savefig(os.path.join(FIG,name),dpi=200,bbox_inches="tight"); plt.close(fig)
    print("wrote",name)

df = lambda q: con.execute(q).df()

# ============ C1: Net sales by year + YoY ============
a = df("SELECT transaction_year yr, net_sales, net_sales_yoy_pct FROM main_marts.mart_sales_annual ORDER BY yr")
fig,ax=plt.subplots(figsize=(7.2,4.4))
bars=ax.bar(a.yr.astype(str), a.net_sales, color=[YEAR_C[y] for y in a.yr], width=0.62, zorder=3)
ax.yaxis.set_major_formatter(FuncFormatter(m)); style(ax)
ax.set_title("Net sales grew +22% over 2019–2022",fontsize=15,fontweight="bold",color=INK,loc="left",pad=12)
for i,(yv,ns,g) in enumerate(zip(a.yr,a.net_sales,a.net_sales_yoy_pct)):
    ax.text(i,ns+1.5e5,m(ns),ha="center",va="bottom",fontsize=11,fontweight="bold",color=INK)
    if g==g: ax.text(i,ns/2,f"{g:+.1f}%",ha="center",va="center",fontsize=11,color="white",fontweight="bold")
ax.set_ylim(0,a.net_sales.max()*1.16)
save(fig,"c1_net_sales.png")

# ============ C2: Profit YoY (gross vs operating) ============
b=df("SELECT transaction_year yr, gross_profit, operating_profit, gross_margin_pct, operating_margin_pct FROM main_marts.mart_sales_annual ORDER BY yr")
fig,ax=plt.subplots(figsize=(7.2,4.4))
import numpy as np
x=np.arange(len(b)); w=0.38
ax.bar(x-w/2,b.gross_profit,w,label="Gross profit",color=BLUE,zorder=3)
ax.bar(x+w/2,b.operating_profit,w,label="Operating profit",color=AQUA,zorder=3)
ax.set_xticks(x); ax.set_xticklabels(b.yr.astype(str))
ax.yaxis.set_major_formatter(FuncFormatter(m)); style(ax)
ax.set_title("Profit stalled in 2022 despite record sales",fontsize=15,fontweight="bold",color=INK,loc="left",pad=12)
for i in x:
    ax.text(i-w/2,b.gross_profit[i]+6e4,m(b.gross_profit[i]),ha="center",va="bottom",fontsize=9.5,color=INK2)
    ax.text(i+w/2,b.operating_profit[i]+6e4,m(b.operating_profit[i]),ha="center",va="bottom",fontsize=9.5,color=INK2)
ax.legend(frameon=False,loc="upper left",fontsize=10)
ax.set_ylim(0,b.gross_profit.max()*1.18)
save(fig,"c2_profit_yoy.png")

# ============ C3: Gross margin % trend by year ============
fig,ax=plt.subplots(figsize=(7.2,4.4))
ax.plot(b.yr.astype(str),b.gross_margin_pct,marker="o",ms=9,lw=2.5,color=BLUE,zorder=3,label="Gross margin")
for xi,yi in zip(range(len(b)),b.gross_margin_pct):
    ax.annotate(f"{yi:.1f}%",(xi,yi),textcoords="offset points",xytext=(0,12),ha="center",fontsize=11,fontweight="bold",color=INK)
ax.axvspan(2.5,3.5,color=CRIT,alpha=0.06)
ax.annotate("−3.8 pts",(3,b.gross_margin_pct.iloc[3]),textcoords="offset points",xytext=(-6,-22),ha="right",color=CRIT,fontsize=11,fontweight="bold")
style(ax); ax.set_ylim(34,44); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
ax.set_title("Gross margin held ~41% then fell to 37.3% in 2022",fontsize=14.5,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c3_margin_trend.png")

# ============ C12: YoY growth — net sales vs gross vs operating profit ============
y=df("""SELECT transaction_year yr, net_sales_yoy_pct ns, gross_profit_yoy_pct gp, operating_profit_yoy_pct op
        FROM main_marts.mart_sales_annual WHERE net_sales_yoy_pct IS NOT NULL ORDER BY yr""")
fig,ax=plt.subplots(figsize=(7.4,4.5))
xx=np.arange(len(y)); w=0.26
series=[("Net sales",y.ns,BLUE),("Gross profit",y.gp,AQUA),("Operating profit",y.op,VIOLET)]
for j,(lab,vals,col) in enumerate(series):
    ax.bar(xx+(j-1)*w,vals,w,color=col,label=lab,zorder=3)
    for xi,v in zip(xx,vals):
        ax.text(xi+(j-1)*w,v+(0.8 if v>=0 else -0.8),f"{v:+.1f}",ha="center",va="bottom" if v>=0 else "top",fontsize=8.6,color=col,fontweight="bold")
ax.axhline(0,color=INK2,lw=1)
ax.set_xticks(xx); ax.set_xticklabels(y.yr.astype(str))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:+.0f}%")); style(ax)
ax.legend(frameon=False,ncol=3,fontsize=9.5,loc="upper center",bbox_to_anchor=(0.5,1.02))
ax.set_ylim(y[['ns','gp','op']].min().min()-8, y[['ns','gp','op']].max().max()+9)
ax.set_title("2022: sales grew +10.5%, but gross profit was flat (+0.4%)",fontsize=13.5,fontweight="bold",color=INK,loc="left",pad=26)
save(fig,"c12_yoy_growth.png")

# ============ C4: 2022 Gross-profit bridge (waterfall) ============
w4=df("""SELECT product_category, gross_profit_delta FROM main_marts.mart_growth_drivers_2022 ORDER BY gross_profit_delta DESC""")
start=float(df("SELECT gross_profit FROM main_marts.mart_sales_annual WHERE transaction_year=2021").iloc[0,0])
end=float(df("SELECT gross_profit FROM main_marts.mart_sales_annual WHERE transaction_year=2022").iloc[0,0])
labels=["2021\ngross profit"]+list(w4.product_category)+["2022\ngross profit"]
deltas=list(w4.gross_profit_delta)
fig,ax=plt.subplots(figsize=(9.2,4.8))
cum=start; xs=range(len(labels))
ax.bar(0,start,color=INK2,width=0.6,zorder=3)
ax.text(0,start+8e3,m(start),ha="center",va="bottom",fontsize=9.5,color=INK)
for i,d in enumerate(deltas,start=1):
    col=GOOD if d>=0 else CRIT
    ax.bar(i,d,bottom=cum,color=col,width=0.6,zorder=3)
    ax.text(i,cum+d+(1.2e4 if d>=0 else -1.2e4),f"{d/1e3:+.0f}k",ha="center",va="bottom" if d>=0 else "top",fontsize=9.5,color=col,fontweight="bold")
    cum+=d
ax.bar(len(labels)-1,end,color=INK2,width=0.6,zorder=3)
ax.text(len(labels)-1,end+8e3,m(end),ha="center",va="bottom",fontsize=9.5,color=INK)
ax.set_xticks(list(xs)); ax.set_xticklabels(labels,fontsize=9.5)
ax.yaxis.set_major_formatter(FuncFormatter(m)); style(ax)
ax.set_ylim(4.4e6,5.42e6)
ax.set_title("Every category grew profit — except Furniture, which erased it all",
             fontsize=14,fontweight="bold",color=INK,loc="left",pad=16)
save(fig,"c4_gp_bridge.png")

# ============ C5: Furniture cost step-change ============
f5=df("""SELECT f.transaction_month mth,
  sum(f.cogs_landed)/sum(f.quantity) avg_cost, sum(f.net_revenue)/sum(f.quantity) avg_price
FROM main_marts.fct_sales f JOIN main_marts.dim_product p ON f.product_id=p.product_id
WHERE p.product_category='Furniture' AND f.transaction_year IN (2021,2022)
GROUP BY 1 ORDER BY 1""")
fig,ax=plt.subplots(figsize=(9.2,4.4))
ax.plot(f5.mth,f5.avg_price,marker="o",ms=4,lw=2,color=BLUE,label="Avg selling price",zorder=3)
ax.plot(f5.mth,f5.avg_cost,marker="o",ms=4,lw=2,color=CRIT,label="Avg unit cost",zorder=3)
ax.axvline(f5.mth.iloc[12],color=INK2,ls="--",lw=1.2)
ax.annotate("+36% cost step\nJan 2022,\nno price change",(f5.mth.iloc[12],95),textcoords="offset points",xytext=(10,-4),fontsize=10,color=CRIT,fontweight="bold")
style(ax); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"${v:.0f}"))
ax.legend(frameon=False,loc="center left",fontsize=10)
ax.set_title("Furniture: supplier cost jumped 36%, price stayed flat",fontsize=14.5,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c5_furniture_cost.png")

# ============ C6: Region net sales by year (grouped) ============
r=df("SELECT region_name, transaction_year yr, net_sales, gross_margin_pct FROM main_marts.mart_region_performance ORDER BY yr")
regions=["West","Midwest","South","Northeast"]; years=[2019,2020,2021,2022]
fig,ax=plt.subplots(figsize=(7.4,4.6))
x=np.arange(len(regions)); w=0.2
for j,y in enumerate(years):
    vals=[float(r[(r.region_name==rg)&(r.yr==y)].net_sales.iloc[0]) for rg in regions]
    ax.bar(x+(j-1.5)*w,vals,w,color=YEAR_C[y],label=str(y),zorder=3)
ax.set_xticks(x); ax.set_xticklabels(regions); ax.yaxis.set_major_formatter(FuncFormatter(m)); style(ax)
ax.legend(frameon=False,ncol=4,fontsize=9.5,loc="upper right")
ax.set_title("West drives 60% of sales and keeps growing",fontsize=14.5,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c6_region_sales.png")

# ============ C7: Region margin by year (grouped) ============
fig,ax=plt.subplots(figsize=(7.4,4.6))
for j,y in enumerate(years):
    vals=[float(r[(r.region_name==rg)&(r.yr==y)].gross_margin_pct.iloc[0]) for rg in regions]
    ax.bar(x+(j-1.5)*w,vals,w,color=YEAR_C[y],label=str(y),zorder=3)
ax.set_xticks(x); ax.set_xticklabels(regions); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%")); style(ax)
ax.legend(frameon=False,ncol=4,fontsize=9.5,loc="upper right")
ax.set_title("West earns ~2× the margin of every other region",fontsize=14.5,fontweight="bold",color=INK,loc="left",pad=12)
ax.set_ylim(0,58)
save(fig,"c7_region_margin.png")

# ============ C8: Regional pricing gap (same product) ============
pg=df("""SELECT d.region_name, p.product_name,
  sum(f.net_revenue)/sum(f.quantity) price, sum(f.cogs_landed)/sum(f.quantity) unit_cost
FROM main_marts.fct_sales f JOIN main_marts.dim_store d ON f.store_id=d.store_id
JOIN main_marts.dim_product p ON f.product_id=p.product_id
WHERE p.product_name IN ('Candles','Computers') AND f.transaction_year=2022
GROUP BY 1,2""")
fig,axes=plt.subplots(1,2,figsize=(9.4,4.4))
for ax,prod in zip(axes,["Candles","Computers"]):
    d=pg[pg.product_name==prod].set_index("region_name").reindex(regions)
    ax.bar(regions,d.price,color=[REGION_C[rg] for rg in regions],width=0.66,zorder=3)
    ax.axhline(float(d.unit_cost.iloc[0]),color=INK2,ls="--",lw=1.3)
    ax.text(3.4,float(d.unit_cost.iloc[0]),f" cost ${d.unit_cost.iloc[0]:.0f}",va="center",ha="left",fontsize=9,color=INK2)
    for i,(rg,pv) in enumerate(zip(regions,d.price)):
        ax.text(i,pv,f"${pv:.0f}",ha="center",va="bottom",fontsize=9.5,color=INK,fontweight="bold")
    style(ax); ax.set_title(prod,fontsize=12,fontweight="bold",color=INK,loc="left")
    ax.tick_params(axis="x",labelrotation=30,labelsize=9)
    ax.set_ylim(0,d.price.max()*1.2)
fig.suptitle("Same product, same cost — West prices 40–55% higher",fontsize=14.5,fontweight="bold",color=INK,x=0.02,ha="left",y=1.02)
save(fig,"c8_pricing_gap.png")

# ============ C9: Top products by net sales, coloured by margin ============
tp=df("SELECT product_name, net_sales, gross_margin_pct FROM main_marts.mart_product_performance ORDER BY net_sales DESC LIMIT 10")
tp=tp.iloc[::-1]
fig,ax=plt.subplots(figsize=(7.6,4.8))
# sequential blue by margin
import matplotlib.colors as mcol
norm=mcol.Normalize(tp.gross_margin_pct.min(),tp.gross_margin_pct.max())
cmap=mcol.LinearSegmentedColormap.from_list("b",["#cde2fb","#184f95"])
bars=ax.barh(tp.product_name,tp.net_sales,color=[cmap(norm(v)) for v in tp.gross_margin_pct],zorder=3)
for yi,(ns,gm) in enumerate(zip(tp.net_sales,tp.gross_margin_pct)):
    ax.text(ns+4e4,yi,f"{m(ns)}  ·  {gm:.0f}% GM",va="center",fontsize=9.5,color=INK2)
ax.xaxis.set_major_formatter(FuncFormatter(m)); style(ax); ax.set_xlim(0,tp.net_sales.max()*1.28)
ax.set_title("Top products by net sales (shade = gross margin)",fontsize=14,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c9_top_products.png")

# ============ C10: Store concentration (Pareto) ============
sp=df("SELECT net_sales FROM main_marts.mart_store_performance ORDER BY net_sales DESC")
sp["cum"]=sp.net_sales.cumsum()/sp.net_sales.sum()*100
sp["rank"]=range(1,len(sp)+1)
fig,ax=plt.subplots(figsize=(7.6,4.4))
ax.plot(sp["rank"],sp["cum"],lw=2.5,color=BLUE,zorder=3)
ax.fill_between(sp["rank"],sp["cum"],color=BLUE,alpha=0.08)
for rk,lab in [(10,"Top 10 stores\n= 35% of sales"),(25,"Top 25 = 49%")]:
    cval=float(sp[sp["rank"]==rk]["cum"].iloc[0])
    ax.plot([rk],[cval],marker="o",ms=8,color=VIOLET,zorder=4)
    ax.annotate(lab,(rk,cval),textcoords="offset points",xytext=(12,-6),fontsize=10,color=VIOLET,fontweight="bold")
style(ax); ax.set_xlabel("Store rank (by net sales)"); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
ax.set_title("Sales are concentrated: 287 stores, top 25 = half of revenue",fontsize=13.5,fontweight="bold",color=INK,loc="left",pad=12)
ax.set_ylim(0,105)
save(fig,"c10_concentration.png")

# ============ C11: Monthly net sales trend coloured by year ============
mo=df("SELECT transaction_month mth, transaction_year yr, net_sales FROM main_marts.mart_sales_monthly ORDER BY 1")
fig,ax=plt.subplots(figsize=(9.4,4.2))
ax.plot(mo.mth,mo.net_sales,lw=1.6,color="#b7d3f6",zorder=2)
for y in years:
    d=mo[mo.yr==y]; ax.plot(d.mth,d.net_sales,lw=2.4,color=YEAR_C[y],zorder=3,label=str(y))
ax.yaxis.set_major_formatter(FuncFormatter(m)); style(ax)
ax.legend(frameon=False,ncol=4,fontsize=9.5,loc="upper left")
ax.set_title("Monthly net sales — steady growth with a strong December peak",fontsize=14,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c11_monthly.png")

# ============ C13: Monthly net sales with rolling trend ============
mo2=df("SELECT transaction_month mth, transaction_year yr, net_sales, gross_margin_pct FROM main_marts.mart_sales_monthly ORDER BY 1")
mo2["roll"]=mo2.net_sales.rolling(12,min_periods=1).mean()
import numpy as np
xi=np.arange(len(mo2))
coef=np.polyfit(xi,mo2.net_sales,1); trend=np.poly1d(coef)(xi)
fig,ax=plt.subplots(figsize=(9.6,4.5))
ax.plot(mo2.mth,mo2.net_sales,lw=1.4,color="#b7d3f6",zorder=2,label="Monthly net sales")
ax.plot(mo2.mth,mo2.roll,lw=2.8,color=BLUE,zorder=4,label="12-month rolling avg")
ax.plot(mo2.mth,trend,lw=1.6,ls="--",color=INK2,zorder=3,label="Linear trend")
ax.annotate("steady underlying uptrend",(mo2.mth.iloc[24],trend[24]),
            textcoords="offset points",xytext=(6,30),fontsize=10.5,color=INK2,fontweight="bold")
ax.yaxis.set_major_formatter(FuncFormatter(m)); style(ax)
ax.legend(frameon=False,ncol=3,fontsize=9.5,loc="upper left")
ax.set_title("Underlying growth is steady beneath strong December seasonality",fontsize=14,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c13_monthly_trend.png")

# ============ C14: Monthly gross margin with 2022 step-down ============
fig,ax=plt.subplots(figsize=(9.6,4.5))
for y in years:
    d=mo2[mo2.yr==y]; ax.plot(d.mth,d.gross_margin_pct,lw=2.4,color=YEAR_C[y],zorder=3,label=str(y))
ax.axvline(mo2.mth.iloc[36],color=CRIT,ls="--",lw=1.3)
ax.annotate("Jan 2022:\nmargin steps down\n(Furniture cost shock)",(mo2.mth.iloc[36],38.5),
            textcoords="offset points",xytext=(10,10),fontsize=10,color=CRIT,fontweight="bold")
ax.axhline(mo2[mo2.yr<2022].gross_margin_pct.mean(),color=INK2,ls=":",lw=1)
style(ax); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%")); ax.set_ylim(34,45)
ax.legend(frameon=False,ncol=4,fontsize=9.5,loc="lower left")
ax.set_title("Gross margin was stable ~41% until a clean step-down in 2022",fontsize=14,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c14_monthly_margin.png")

# ============ C15: Region x Category margin heatmap (2022) ============
import matplotlib.colors as mcol
hm=df("""SELECT d.region_name reg, p.product_category cat, 100.0*sum(f.gross_profit)/sum(f.net_revenue) gm
FROM main_marts.fct_sales f JOIN main_marts.dim_store d ON f.store_id=d.store_id
JOIN main_marts.dim_product p ON f.product_id=p.product_id WHERE f.transaction_year=2022 GROUP BY 1,2""")
rows=["West","South","Midwest","Northeast"]; cols=["Household","Dining","Sports","Kitchen","Electronics","Furniture"]
M=hm.pivot(index='reg',columns='cat',values='gm').reindex(index=rows,columns=cols)
fig,ax=plt.subplots(figsize=(9.2,4.4))
# diverging red(neg)->gray->blue(pos), centered at 0  (CVD-safe: red vs blue)
cmap=mcol.LinearSegmentedColormap.from_list("div",[CRIT,"#f0efec",BLUE])
norm=mcol.TwoSlopeNorm(vmin=-25,vcenter=0,vmax=65)
im=ax.imshow(M.values,cmap=cmap,norm=norm,aspect="auto")
ax.grid(False)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols,fontsize=10.5)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows,fontsize=11,fontweight="bold")
ax.tick_params(length=0)
for sp in ax.spines.values(): sp.set_visible(False)
for i in range(len(rows)):
    for j in range(len(cols)):
        v=M.values[i,j]
        tc="white" if (v<-2 or v>40) else INK
        ax.text(j,i,f"{v:.0f}%",ha="center",va="center",fontsize=11,color=tc,fontweight="bold")
# grid gaps
ax.set_xticks(np.arange(-.5,len(cols),1),minor=True); ax.set_yticks(np.arange(-.5,len(rows),1),minor=True)
ax.grid(which="minor",color=SURFACE,lw=3); ax.tick_params(which="minor",length=0)
ax.set_title("West is premium across the board; Furniture loses money everywhere but West",
             fontsize=13.5,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c15_region_cat_heatmap.png")

# ============ C16: Furniture price vs cost by region (2022) ============
fu=df("""SELECT d.region_name reg, sum(f.net_revenue)/sum(f.quantity) price, sum(f.cogs_landed)/sum(f.quantity) ucost,
  100.0*sum(f.gross_profit)/sum(f.net_revenue) gm
FROM main_marts.fct_sales f JOIN main_marts.dim_store d ON f.store_id=d.store_id
JOIN main_marts.dim_product p ON f.product_id=p.product_id
WHERE p.product_category='Furniture' AND f.transaction_year=2022 GROUP BY 1""").set_index('reg').reindex(rows)
fig,ax=plt.subplots(figsize=(8.2,4.6))
x=np.arange(len(rows)); w=0.38
ax.bar(x-w/2,fu.price,w,color=BLUE,label="Avg selling price",zorder=3)
ax.bar(x+w/2,fu.ucost,w,color=INK2,label="Avg unit cost",zorder=3)
for i,rg in enumerate(rows):
    gm=fu.gm.iloc[i]; col=GOOD if gm>=0 else CRIT
    ax.text(i,max(fu.price.iloc[i],fu.ucost.iloc[i])+3,f"{gm:+.0f}% margin",ha="center",va="bottom",fontsize=10.5,color=col,fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(rows); ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"${v:.0f}")); style(ax)
ax.legend(frameon=False,ncol=2,fontsize=10,loc="upper right")
ax.set_ylim(0,max(fu.price.max(),fu.ucost.max())*1.22)
ax.set_title("Furniture: only the West prices above cost — the rest sell at a loss",fontsize=13.5,fontweight="bold",color=INK,loc="left",pad=12)
save(fig,"c16_furniture_region.png")

print("ALL CHARTS DONE")
