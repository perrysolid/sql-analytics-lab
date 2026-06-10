-- Standalone data-quality checks for the Amazon books pipeline.
-- These are read-only queries you can run in pgAdmin after a DAG run.

-- 1. Table should contain records.
SELECT
    COUNT(*) AS total_books
FROM books;

-- 2. Duplicate titles should return zero rows.
SELECT
    title,
    COUNT(*) AS duplicate_count
FROM books
GROUP BY title
HAVING COUNT(*) > 1;

-- 3. Key field completeness.
SELECT
    COUNT(*) FILTER (WHERE title IS NULL OR title = '') AS missing_title,
    COUNT(*) FILTER (WHERE authors IS NULL OR authors = '') AS missing_author,
    COUNT(*) FILTER (WHERE price_amount IS NULL) AS missing_price_amount,
    COUNT(*) FILTER (WHERE rating_value IS NULL) AS missing_rating_value
FROM books;

-- 4. Rating range check.
SELECT
    title,
    rating_value
FROM books
WHERE rating_value IS NOT NULL
  AND (rating_value < 0 OR rating_value > 5);

-- 5. Price sanity check.
SELECT
    title,
    price_amount
FROM books
WHERE price_amount IS NOT NULL
  AND price_amount < 0;

-- 6. Freshness check.
SELECT
    MAX(scraped_at) AS latest_scraped_at,
    NOW() - MAX(scraped_at) AS data_age
FROM books;
