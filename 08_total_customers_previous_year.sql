-- Run after executing setup.sql. First year has no prior-year baseline where relevant.
SELECT y.year, COUNT(*) AS total_customers_previous_year FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 GROUP BY y.year ORDER BY y.year;
