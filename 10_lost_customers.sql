-- Run after executing setup.sql. First year has no prior-year baseline where relevant.
SELECT y.year, COUNT(*) AS lost_customers FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 LEFT JOIN customer_year c ON c.year = y.year AND c.customer_email = p.customer_email WHERE c.customer_email IS NULL GROUP BY y.year ORDER BY y.year;
