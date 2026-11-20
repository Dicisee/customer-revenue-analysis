-- Run after executing setup.sql. First year has no prior-year baseline where relevant.
SELECT c.year, COUNT(*) AS new_customers FROM customer_year c LEFT JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 WHERE p.customer_email IS NULL AND c.year > (SELECT MIN(year) FROM customer_year) GROUP BY c.year ORDER BY c.year;
