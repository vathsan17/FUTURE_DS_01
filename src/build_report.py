"""Builds report/Superstore_Sales_Performance_Report.pdf from output/kpi_summary.json + charts."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

k = json.load(open("output/kpi_summary.json"))
ss = getSampleStyleSheet(); NAVY = colors.HexColor("#1f3a5f")
T = ParagraphStyle("T", parent=ss["Title"], fontSize=22, textColor=NAVY, alignment=0)
H = ParagraphStyle("H", parent=ss["Heading2"], fontSize=13, textColor=NAVY, spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["Normal"], fontSize=9.5, leading=13.5, spaceAfter=4)
BL = ParagraphStyle("BL", parent=B, leftIndent=12, bulletIndent=2, spaceAfter=3)
C = ParagraphStyle("C", parent=B, fontSize=8.8, leading=11, spaceAfter=0)
usd = lambda n: ("-" if n < 0 else "") + f"${abs(n):,.0f}"
yr = {int(y["Year"]): y for y in k["year"]}
cat = {c["Category"]: c for c in k["category"]}
reg = {r["Region"]: r for r in k["region"]}
sub = {s["Sub-Category"]: s for s in k["subcat"]}
band = {b["DiscBand"]: b for b in k["band"]}
tp = k["top_products"]
s = []
def p(t): s.append(Paragraph(t, B))
def h(t): s.append(Paragraph(t, H))
def bl(items): [s.append(Paragraph(i, BL, bulletText="\u2022")) for i in items]
def tbl(rows, widths):
    t = Table([[Paragraph(str(c), C) for c in r] for r in rows], colWidths=[w * mm for w in widths])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7f2")), ("GRID", (0, 0), (-1, -1), .4, colors.grey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")])); s.append(t); s.append(Spacer(1, 6))
def img(f, w): s.append(Image(f, width=w * mm, height=w * mm * (4.2 / 10 if "monthly" in f else 5.5 / 8 if "subcat" in f else 4 / 7)))

s.append(Paragraph("Superstore Sales Performance Report", T))
p(f"Business analysis of {k['lines']:,} order lines ({k['orders']:,} orders, {k['customers']} customers), {k['start']} to {k['end']}. Prepared for the business leadership team.")
h("Executive summary")
p(f"The business is growing but is far less profitable than it should be. Sales reached <b>{usd(k['total_sales'])}</b> with <b>{usd(k['total_profit'])}</b> profit "
  f"(<b>{k['margin']:.1f}%</b> margin). Sales grew from {usd(yr[2014]['Sales'])} in 2014 to {usd(yr[2017]['Sales'])} in 2017, but the main profit leak is "
  f"<b>heavy discounting</b>: the {k['hi_disc_share']:.0f}% of order lines sold at 30% discount or more lost <b>{usd(-k['hi_disc_profit'])}</b> in total. "
  f"Profit growth should come from fixing discounts, Furniture and the Central region before adding more volume.")
tbl([["Sales", "Profit", "Margin", "Orders", "Customers", "Avg discount"],
     [usd(k["total_sales"]), usd(k["total_profit"]), f"{k['margin']:.1f}%", f"{k['orders']:,}", k["customers"], f"{k['avg_discount']:.1f}%"]], [30, 30, 25, 25, 28, 32])

h("1. Which products generate the most revenue?")
p(f"Technology is the largest category by sales ({usd(cat['Technology']['Sales'])}), followed by Furniture ({usd(cat['Furniture']['Sales'])}) and Office Supplies ({usd(cat['Office Supplies']['Sales'])}). "
  "The top five products by sales are shown below. Higher sales do not always mean higher profit: the Cisco TelePresence System lost money despite ranking in the top three.")
tbl([["Product", "Sales", "Profit"]] + [[x["Product Name"][:70], usd(x["Sales"]), usd(x["Profit"])] for x in tp], [120, 25, 25])

h("2. How do sales change over time?")
bl([f"Yearly sales: {usd(yr[2014]['Sales'])} (2014), {usd(yr[2015]['Sales'])} (2015, {yr[2015]['YoY']:.0f}%), {usd(yr[2016]['Sales'])} (2016, +{yr[2016]['YoY']:.0f}%), {usd(yr[2017]['Sales'])} (2017, +{yr[2017]['YoY']:.0f}%).",
    f"Strong seasonality: September, November and December together bring <b>{k['peak_months_share']:.0f}%</b> of annual sales; Q4 alone is {k['q4_share']:.0f}%.",
    f"Margins rose from {yr[2014]['Margin']:.1f}% (2014) to about {yr[2016]['Margin']:.1f}% (2016) and eased to {yr[2017]['Margin']:.1f}% in 2017, so 2017 growth was bought partly with lower profitability."])
s.append(PageBreak())
img("output/monthly_trend.png", 170)

h("3. Which categories and regions are most profitable?")
tbl([["Category", "Sales", "Profit", "Margin"]] + [[c, usd(cat[c]["Sales"]), usd(cat[c]["Profit"]), f"{cat[c]['Margin']:.1f}%"] for c in cat], [50, 40, 40, 30])
tbl([["Region", "Sales", "Profit", "Margin", "Avg discount"]] + [[r, usd(reg[r]["Sales"]), usd(reg[r]["Profit"]), f"{reg[r]['Margin']:.1f}%", f"{k['region_discount'][r]}%"] for r in reg], [35, 35, 35, 30, 35])
bl([f"<b>Technology and Office Supplies</b> earn about 17% margins. <b>Furniture earns only {cat['Furniture']['Margin']:.1f}%</b> on {usd(cat['Furniture']['Sales'])} of sales.",
    f"<b>Tables ({usd(sub['Tables']['Profit'])}), Bookcases ({usd(sub['Bookcases']['Profit'])}) and Supplies ({usd(sub['Supplies']['Profit'])})</b> lose money. Tables carry an average discount of {k['tables_avg_discount']:.0f}%.",
    f"<b>West</b> is the most profitable region ({reg['West']['Margin']:.1f}%); <b>Central is the weakest ({reg['Central']['Margin']:.1f}%)</b> and gives the deepest discounts ({k['region_discount']['Central']}% on average).",
    "Largest loss-making states: " + ", ".join(f"{a} ({usd(b)})" for a, b in k["worst_states"].items()) + "."])
img("output/profit_by_subcategory.png", 110)

h("4. Where should the business focus to grow faster?")
p("Discounting is the clearest lever. Margin falls steadily as discount rises and turns negative above 20%:")
tbl([["Discount level", "Sales", "Profit", "Margin"]] + [[b, usd(band[b]["Sales"]), usd(band[b]["Profit"]), f"{band[b]['Margin']:.1f}%"] for b in band], [50, 40, 40, 30])
img("output/margin_by_discount.png", 120)
h("Recommendations")
[p(x) for x in [f"<b>1. Cap discounts at 20%.</b> Lines at 30%+ discount lost {usd(-k['hi_disc_profit'])}, almost as much as the {usd(k['total_profit'])} profit the business earned overall. Require manager approval above 20%.",
    "<b>2. Reprice or rationalise Tables, Bookcases and Supplies.</b> Raise prices or cut discounts, and review supplier cost. Tables are profitable when the discount stays at or below 20%.",
    f"<b>3. Fix the Central region.</b> Its average discount is more than double West's. Align discount policy to West's and review Texas, Ohio, Pennsylvania and Illinois first.",
    f"<b>4. Plan for peak season.</b> September to December brings most sales: secure inventory and staffing early, and run promotions without deep discounts.",
    f"<b>5. Protect and grow loyal customers.</b> {k['repeat_cust_share']:.0f}% of customers reorder and the top 10% generate {k['top10pct_cust_share']:.0f}% of sales. Use loyalty offers and account management rather than price cuts, and check that the largest accounts are profitable.",
    "<b>6. Push high-margin lines.</b> Copiers, Accessories, Paper and Phones combine strong sales or margin and should lead marketing."]]
h("Data and method")
p(f"Source: Sample Superstore (Kaggle), 9,994 order lines. Cleaning: Latin-1 decoding, whitespace trimming, date parsing (m/d/yyyy), duplicate and missing-value checks (none found), derived Year, Month and Profit Margin fields. "
  "Margin = Profit / Sales. Currency assumed USD. The dataset is a sample and may not represent a real company, and cost data is available only as profit, so findings show where profit is lost rather than why costs are what they are. "
  "An interactive version with filters is in dashboard/index.html.")
def foot(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(18 * mm, 10 * mm, "Superstore Sales Performance Report"); c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}"); c.restoreState()
SimpleDocTemplate("report/Superstore_Sales_Performance_Report.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=16*mm, bottomMargin=18*mm, title="Superstore Sales Performance Report").build(s, onFirstPage=foot, onLaterPages=foot)
print("report/Superstore_Sales_Performance_Report.pdf written")
