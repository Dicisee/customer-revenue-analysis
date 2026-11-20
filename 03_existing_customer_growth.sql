-- Run after executing setup.sql. First year has no prior-year baseline where relevant.
SELECT c.year, ROUND(SUM(c.revenue_cents - p.revenue_cents) / 100.0, 2) AS existing_customer_growth FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;
