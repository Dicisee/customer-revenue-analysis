-- SQLite setup. Load the supplied CSV into a staging table (staging_orders) with
-- customer_email TEXT, net_revenue TEXT, year INTEGER, and optional index column.
-- The provided Python preparation script loads/normalizes the original ZIP directly.
-- If loading manually, execute the statements below after importing into staging_orders.
CREATE TABLE customer_year AS
SELECT CAST(year AS INTEGER) AS year, LOWER(TRIM(customer_email)) AS customer_email,
       SUM(CAST(ROUND(CAST(net_revenue AS REAL)*100,0) AS INTEGER)) AS revenue_cents
FROM staging_orders WHERE TRIM(COALESCE(customer_email,'')) <> ''
GROUP BY CAST(year AS INTEGER), LOWER(TRIM(customer_email));
CREATE UNIQUE INDEX idx_customer_year ON customer_year(year,customer_email);
