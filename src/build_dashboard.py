"""Embeds the cleaned data into the HTML template -> dashboard/index.html (self-contained)."""
import json
import pandas as pd

df = pd.read_csv("data/superstore_clean.csv")
def codes(col):
    vals = sorted(df[col].unique()); return vals, df[col].map({v: i for i, v in enumerate(vals)})
ym, c_ym = codes("YearMonth"); reg, c_reg = codes("Region"); seg, c_seg = codes("Segment")
cat, c_cat = codes("Category"); sub, c_sub = codes("Sub-Category")
prod, c_prod = codes("Product Name"); cust, c_cust = codes("Customer Name"); _, c_ord = codes("Order ID")
rows = pd.DataFrame({"a": c_ym, "b": c_reg, "c": c_seg, "d": c_cat, "e": c_sub, "f": df["Sales"].round(2),
                     "g": df["Profit"].round(2), "h": df["Quantity"], "i": df["Discount"], "j": c_ord,
                     "k": c_prod, "l": c_cust}).values.tolist()
data = {"ym": ym, "years": sorted({v[:4] for v in ym}), "reg": reg, "seg": seg, "cat": cat, "sub": sub,
        "prod": prod, "cust": cust, "bands": ["No discount", "Up to 20%", "21-30%", "31-50%", "Over 50%"], "rows": rows}
html = open("src/dashboard_template.html", encoding="utf-8").read().replace("__DATA__", json.dumps(data, separators=(",", ":")))
open("dashboard/index.html", "w", encoding="utf-8").write(html)
print(f"dashboard/index.html written ({len(html)/1024:.0f} KB)")
