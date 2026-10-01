"""Clean the Superstore data, compute KPIs/insights, save charts + output/kpi_summary.json.
Run from the project root: python src/analyze_superstore.py"""
import os, json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

RAW = "data/raw/Sample - Superstore.csv"
os.makedirs("output", exist_ok=True)
sns.set_theme(style="whitegrid")

# ---------- 1. Load & clean ----------
try:
    df = pd.read_csv(RAW)
except UnicodeDecodeError:           # Kaggle file is Latin-1 encoded
    df = pd.read_csv(RAW, encoding="latin-1")

def parse_dates(s):
    """Handles m/d/yyyy and m-d-yyyy (some Kaggle versions mix both)."""
    s = s.astype(str).str.strip()
    a = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
    return a.fillna(pd.to_datetime(s, format="%m-%d-%Y", errors="coerce"))

for c in df.select_dtypes(include=["object", "string"]).columns:
    df[c] = df[c].str.strip()
df["Order Date"] = parse_dates(df["Order Date"])
df["Ship Date"] = parse_dates(df["Ship Date"])
assert df[["Order Date", "Ship Date"]].isna().sum().sum() == 0, "unparsed dates"
before = len(df)
df = df.drop_duplicates()
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month
df["YearMonth"] = df["Order Date"].dt.strftime("%Y-%m")
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["Profit Margin %"] = df["Profit"] / df["Sales"] * 100
df.to_csv("data/superstore_clean.csv", index=False)
print(f"Cleaned {len(df):,} rows ({before-len(df)} duplicates removed) -> data/superstore_clean.csv")

# ---------- 2. KPIs & insights ----------
def agg(by):
    a = df.groupby(by).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
                           Orders=("Order ID", "nunique"), AvgDiscount=("Discount", "mean")).reset_index()
    a["Margin"] = a["Profit"] / a["Sales"] * 100
    return a

S, P = df["Sales"].sum(), df["Profit"].sum()
bands = pd.cut(df["Discount"], [-0.01, 0, 0.2, 0.3, 0.5, 1],
               labels=["No discount", "Up to 20%", "21-30%", "31-50%", "Over 50%"])
df["DiscBand"] = bands
band = agg("DiscBand")
hi = df[df["Discount"] >= 0.3]
cust = df.groupby("Customer Name").agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
month_share = (df.groupby("Month")["Sales"].sum() / S * 100)
state = df.groupby("State")["Profit"].sum().sort_values()
prod = df.groupby("Product Name").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
rec = lambda d: d.round(2).to_dict("records")

kpi = {
    "total_sales": S, "total_profit": P, "margin": P / S * 100,
    "orders": int(df["Order ID"].nunique()), "lines": len(df), "customers": int(df["Customer ID"].nunique()),
    "avg_discount": df["Discount"].mean() * 100, "units": int(df["Quantity"].sum()),
    "loss_line_share": (df["Profit"] < 0).mean() * 100,
    "start": str(df["Order Date"].min().date()), "end": str(df["Order Date"].max().date()),
    "year": rec(agg("Year").assign(YoY=lambda d: d["Sales"].pct_change() * 100)),
    "category": rec(agg("Category")), "region": rec(agg("Region")), "segment": rec(agg("Segment")),
    "subcat": rec(agg("Sub-Category").sort_values("Profit")), "band": rec(band),
    "top_products": rec(prod.nlargest(5, "Sales")), "worst_products": rec(prod.nsmallest(3, "Profit")),
    "worst_states": {k: round(v) for k, v in state.head(5).items()},
    "best_states": {k: round(v) for k, v in state.tail(3).items()},
    "hi_disc_lines": len(hi), "hi_disc_share": len(hi) / len(df) * 100, "hi_disc_profit": hi["Profit"].sum(),
    "peak_months_share": month_share[[9, 11, 12]].sum(), "q4_share": month_share[[10, 11, 12]].sum(),
    "top10pct_cust_share": cust["Sales"].nlargest(len(cust) // 10).sum() / S * 100,
    "repeat_cust_share": (cust["Orders"] > 1).mean() * 100,
    "region_discount": (df.groupby("Region")["Discount"].mean() * 100).round(1).to_dict(),
    "tables_avg_discount": df[df["Sub-Category"] == "Tables"]["Discount"].mean() * 100,
    "avg_ship_days": df["Ship Days"].mean(),
}
json.dump(kpi, open("output/kpi_summary.json", "w"), indent=2, default=float)

print("=" * 44)
print(f"Sales ${S:,.0f} | Profit ${P:,.0f} | Margin {kpi['margin']:.1f}%")
print(f"Orders {kpi['orders']:,} | Customers {kpi['customers']:,} | Avg discount {kpi['avg_discount']:.1f}%")
print("=" * 44)

# ---------- 3. Charts ----------
ym = df.groupby("YearMonth")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(ym.index, ym["Sales"], marker="o", ms=3, lw=2, label="Sales", color="#1f77b4")
ax.plot(ym.index, ym["Profit"], marker="o", ms=3, lw=2, label="Profit", color="#2ca02c")
ax.set_xticks(range(0, len(ym), 3)); ax.set_xticklabels(ym.index[::3], rotation=45)
ax.set_title("Monthly Sales and Profit, 2014-2017", fontweight="bold"); ax.set_ylabel("USD"); ax.legend()
fig.tight_layout(); fig.savefig("output/monthly_trend.png", dpi=200); plt.close(fig)

sc = agg("Sub-Category").sort_values("Profit")
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.barh(sc["Sub-Category"], sc["Profit"], color=["#d62728" if v < 0 else "#2ca02c" for v in sc["Profit"]])
ax.set_title("Profit by Sub-Category", fontweight="bold"); ax.set_xlabel("Profit (USD)")
fig.tight_layout(); fig.savefig("output/profit_by_subcategory.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(band["DiscBand"].astype(str), band["Margin"], color=["#2ca02c" if v > 0 else "#d62728" for v in band["Margin"]])
ax.axhline(0, color="k", lw=0.8); ax.set_title("Profit Margin by Discount Level", fontweight="bold"); ax.set_ylabel("Margin (%)")
fig.tight_layout(); fig.savefig("output/margin_by_discount.png", dpi=200); plt.close(fig)

rg = agg("Region").sort_values("Margin")
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(rg["Region"], rg["Margin"], color="#1f77b4")
ax.set_title("Profit Margin by Region", fontweight="bold"); ax.set_ylabel("Margin (%)")
fig.tight_layout(); fig.savefig("output/margin_by_region.png", dpi=200); plt.close(fig)
print("Charts + output/kpi_summary.json saved.")
