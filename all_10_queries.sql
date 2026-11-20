-- 01_total_revenue.sql
SELECT year, ROUND(SUM(revenue_cents) / 100.0, 2) AS total_revenue_current_year FROM customer_year GROUP BY year ORDER BY year;

-- 02_new_customer_revenue.sql
SELECT c.year, ROUND(SUM(CASE WHEN p.customer_email IS NULL THEN c.revenue_cents ELSE 0 END) / 100.0, 2) AS new_customer_revenue FROM customer_year c LEFT JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 WHERE c.year > (SELECT MIN(year) FROM customer_year) GROUP BY c.year ORDER BY c.year;

-- 03_existing_customer_growth.sql
SELECT c.year, ROUND(SUM(c.revenue_cents - p.revenue_cents) / 100.0, 2) AS existing_customer_growth FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;

-- 04_revenue_lost_from_attrition.sql
SELECT y.year, ROUND(SUM(CASE WHEN c.customer_email IS NULL THEN p.revenue_cents ELSE 0 END) / 100.0, 2) AS revenue_lost_from_attrition FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 LEFT JOIN customer_year c ON c.year = y.year AND c.customer_email = p.customer_email GROUP BY y.year ORDER BY y.year;

-- 05_existing_customer_revenue_current_year.sql
SELECT c.year, ROUND(SUM(c.revenue_cents) / 100.0, 2) AS existing_customer_revenue_current_year FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;

-- 06_existing_customer_revenue_prior_year.sql
SELECT c.year, ROUND(SUM(p.revenue_cents) / 100.0, 2) AS existing_customer_revenue_prior_year FROM customer_year c JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 GROUP BY c.year ORDER BY c.year;

-- 07_total_customers_current_year.sql
SELECT year, COUNT(*) AS total_customers_current_year FROM customer_year GROUP BY year ORDER BY year;

-- 08_total_customers_previous_year.sql
SELECT y.year, COUNT(*) AS total_customers_previous_year FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 GROUP BY y.year ORDER BY y.year;

-- 09_new_customers.sql
SELECT c.year, COUNT(*) AS new_customers FROM customer_year c LEFT JOIN customer_year p ON p.customer_email = c.customer_email AND p.year = c.year - 1 WHERE p.customer_email IS NULL AND c.year > (SELECT MIN(year) FROM customer_year) GROUP BY c.year ORDER BY c.year;

-- 10_lost_customers.sql
SELECT y.year, COUNT(*) AS lost_customers FROM (SELECT DISTINCT year FROM customer_year) y JOIN customer_year p ON p.year = y.year - 1 LEFT JOIN customer_year c ON c.year = y.year AND c.customer_email = p.customer_email WHERE c.customer_email IS NULL GROUP BY y.year ORDER BY y.year;
