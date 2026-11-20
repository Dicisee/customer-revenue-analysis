-- Run after executing setup.sql. First year has no prior-year baseline where relevant.
SELECT year, COUNT(*) AS total_customers_current_year FROM customer_year GROUP BY year ORDER BY year;
