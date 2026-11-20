# Customer Revenue and Retention Case Study (2015–2017)

## Deliverables
- `sql/01_...sql` through `sql/10_...sql`: ten requested SQL analyses (SQLite).
- `sql/all_10_queries.sql`: all ten queries in one file.
- `sql/setup.sql`: create `customer_year` from a manually imported `staging_orders` table.
- `analyze.py`: independently reproduces calculations from the original `Case Study.zip` and checks each SQL result.
- `data/tableau_yearly_metrics.csv`: aggregate, Tableau-ready metrics (no customer email identifiers).
- `data/validation.json`: row counts and validation information.
- `dashboard_preview.png`: illustrative dashboard preview; **not a published Tableau dashboard**.

## Reproduce
1. Place the original `Case Study.zip` in this repository folder locally (do **not** upload it to GitHub), or provide its location using `--input`.
2. Run `python analyze.py --input "Case Study.zip"` with Python 3, or specify another path such as `python analyze.py --input "C:/Users/you/Downloads/Case Study.zip"`. No third-party Python packages are needed for the data calculations.
3. The script uses an in-memory SQLite database and compares all 10 SQL outputs to independently computed customer-year set metrics.
4. Alternatively, import `casestudy.csv` into SQLite as `staging_orders` (columns `customer_email`, `net_revenue`, `year`), run `sql/setup.sql`, then execute the ten queries.

## Definitions and caveats
- A customer is identified by normalized `LOWER(TRIM(customer_email))`.
- Revenue is aggregated at the customer/year level before comparisons; amounts are computed in integer cents.
- **New customer** means present in current year but absent in the **immediately previous year**, even if present in an older year. **Lost customer** means present in prior year but absent in current year.
- Existing-customer growth = revenue of retained customers in current year minus revenue of those same customers in prior year.
- Attrition revenue = **prior-year** revenue of customers absent in current year, reported as a positive amount.
- 2015 has no 2014 baseline; prior-year-dependent metrics are **N/A**, not zero.
- Total customers are distinct customer identifiers within each year. In this dataset, one row corresponds to each customer/year.

## Data checks
- Total current-year revenue = new customer revenue + existing customer revenue current year.
- Revenue change vs prior year = new customer revenue + existing customer growth − revenue lost from attrition.
- Current customers = new customers + retained customers; prior customers = lost customers + retained customers.
- All 10 SQL results were checked against independent Python set-based calculations.

## Tableau dashboard instructions
1. Open Tableau Public or Tableau Desktop and connect to `data/tableau_yearly_metrics.csv` as a **Text file**.
2. Treat `Year` as a discrete dimension, and set all monetary fields to Currency (USD), all customer counts to Number (whole).
3. Create a year filter. Display KPIs for total revenue, new customer revenue, existing-customer growth, attrition revenue, total customers, new customers, and lost customers.
4. Add a line chart for total revenue by year, a grouped bar chart for new vs lost customers (2016–2017), and bars for new revenue vs existing revenue (2016–2017).
5. Label 2015 comparison KPIs as N/A (no 2014 baseline), and prominently show the selected year.
6. Publish to Tableau Public, verify it is accessible in a signed-out browser, and add its URL below.

**Tableau Public URL:** [add after publishing]
**GitHub repository URL:** [add after uploading]

**Privacy:** Upload only aggregate results and scripts. Do not publish the original CSV or ZIP because they contain email-like identifiers.
