# Future Interns - Data Science & Analytics
## Task 1: Business Sales Performance Analytics

**Track Code:** DS | **Repository:** `FUTURE_DS_01`

An end-to-end analysis of the Sample Superstore dataset (9,994 order lines, 2014-2017): cleaned in Python, explored with Pandas, delivered as a **client-ready interactive dashboard** and a **written report with recommendations**.

| Deliverable | Where |
|---|---|
| Interactive dashboard (filters: year, region, category, segment) | `dashboard/index.html` (open in any browser, no code needed) |
| Business report (PDF) | `report/Superstore_Sales_Performance_Report.pdf` |
| Cleaned dataset | `data/superstore_clean.csv` |
| Analysis code | `src/` |

**Live dashboard:** `https://<YOUR_GITHUB_USERNAME>.github.io/FUTURE_DS_01/dashboard/` (enable GitHub Pages: Settings > Pages > Deploy from branch `main`, folder `/ (root)`).

---

## Business Questions and Answers

| Question | Answer |
|---|---|
| Which products generate the most revenue? | Technology is the top category ($836K). Top product: Canon imageCLASS 2200 Copier ($61.6K sales, $25.2K profit). Some top sellers lose money (e.g. Cisco TelePresence EX90). |
| How do sales change over time? | $484K (2014), $471K (2015), $609K (2016, +29%), $733K (2017, +20%). September, November and December bring 43% of annual sales. |
| Which categories / regions are most profitable? | Technology (17.4%) and Office Supplies (17.0%) margins; **Furniture only 2.5%**. West is best (14.9%), **Central is weakest (7.9%)**. Tables, Bookcases and Supplies lose money. |
| Where should the business focus? | Fix discounting first: lines at 30%+ discount lose about $135K. Then Furniture pricing and the Central region. |

## Key KPIs
* **Sales:** $2,297,201 | **Profit:** $286,397 | **Margin:** 12.5%
* **Orders:** 5,009 | **Customers:** 793 | **Average discount:** 15.6%

## Recommendations
1. **Cap discounts at 20%.** Margin is 29.5% with no discount, 11.9% up to 20%, and negative above 20%.
2. **Reprice or rationalise Tables, Bookcases and Supplies** (Tables average a 26% discount).
3. **Fix the Central region** (24% average discount vs 11% in West); review Texas, Ohio, Pennsylvania and Illinois first.
4. **Plan for the Sep-Dec peak** with inventory and staffing, without deep discounts.
5. **Protect loyal customers:** 98% reorder and the top 10% give 31% of sales.

## Data Cleaning Steps
* Read the Latin-1 encoded CSV; trimmed whitespace in text columns.
* Parsed order and ship dates (supports `m/d/yyyy` and `m-d-yyyy`); verified no ship date precedes its order date.
* Checked for missing values and duplicates (none found).
* Added `Year`, `Month`, `YearMonth`, `Ship Days` and `Profit Margin %`.

## Project Structure
```text
FUTURE_DS_01/
├── data/
│   ├── raw/Sample - Superstore.csv   # original Kaggle file
│   └── superstore_clean.csv          # cleaned output
├── src/
│   ├── analyze_superstore.py         # clean, KPIs, charts, kpi_summary.json
│   ├── build_dashboard.py            # builds dashboard/index.html
│   ├── dashboard_template.html       # dashboard template
│   └── build_report.py               # builds the PDF report
├── dashboard/index.html              # interactive dashboard
├── report/Superstore_Sales_Performance_Report.pdf
├── output/                           # charts + kpi_summary.json
└── requirements.txt
```

## How to Run
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/FUTURE_DS_01.git
cd FUTURE_DS_01
pip install -r requirements.txt

# run from the project root, in this order
python src/analyze_superstore.py
python src/build_dashboard.py
python src/build_report.py
```

## Tools
Python, Pandas, NumPy, Matplotlib, Seaborn, ReportLab, Chart.js (dashboard), Git and GitHub.

## Limitations
The Superstore data is a sample dataset and may not reflect a real company. Only profit (not separate costs) is available, so the analysis shows where profit is lost rather than why costs are high. Currency is assumed to be USD.
