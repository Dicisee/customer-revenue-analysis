-- Run after executing setup.sql. First year has no prior-year baseline where relevant.
SELECT year, ROUND(SUM(revenue_cents) / 100.0, 2) AS total_revenue_current_year FROM customer_year GROUP BY year ORDER BY year;
