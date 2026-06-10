-- Interview-friendly analysis queries for the Amazon books pipeline.
-- These are designed to be run in pgAdmin after the DAG loads data.

-- 1. Catalog health snapshot.
SELECT
    total_books,
    books_with_price,
    books_with_rating,
    avg_price,
    avg_rating,
    latest_scraped_at
FROM book_catalog_metrics;

-- 2. Best-rated books, using price as a tie breaker.
SELECT
    title,
    authors,
    rating_value,
    price_amount
FROM books
WHERE rating_value IS NOT NULL
ORDER BY rating_value DESC, price_amount ASC NULLS LAST
LIMIT 10;

-- 3. High-rated affordable books for a quick business-style insight.
SELECT
    title,
    authors,
    rating_value,
    price_amount
FROM top_rated_affordable_books;

-- 4. Author-level summary.
SELECT
    COALESCE(authors, 'Unknown') AS author,
    COUNT(*) AS book_count,
    ROUND(AVG(rating_value), 2) AS avg_rating,
    ROUND(AVG(price_amount), 2) AS avg_price
FROM books
GROUP BY COALESCE(authors, 'Unknown')
HAVING COUNT(*) >= 1
ORDER BY book_count DESC, avg_rating DESC NULLS LAST;

-- 5. Price bands for quick distribution analysis.
SELECT
    CASE
        WHEN price_amount IS NULL THEN 'Unknown'
        WHEN price_amount < 20 THEN 'Under $20'
        WHEN price_amount < 40 THEN '$20 to $39.99'
        WHEN price_amount < 60 THEN '$40 to $59.99'
        ELSE '$60 and above'
    END AS price_band,
    COUNT(*) AS book_count,
    ROUND(AVG(rating_value), 2) AS avg_rating
FROM books
GROUP BY price_band
ORDER BY
    CASE price_band
        WHEN 'Under $20' THEN 1
        WHEN '$20 to $39.99' THEN 2
        WHEN '$40 to $59.99' THEN 3
        WHEN '$60 and above' THEN 4
        ELSE 5
    END;

-- 6. Rating distribution for dashboard-style reporting.
SELECT
    CASE
        WHEN rating_value IS NULL THEN 'Unknown'
        WHEN rating_value >= 4.5 THEN '4.5+'
        WHEN rating_value >= 4.0 THEN '4.0 to 4.49'
        WHEN rating_value >= 3.5 THEN '3.5 to 3.99'
        ELSE 'Below 3.5'
    END AS rating_band,
    COUNT(*) AS book_count,
    ROUND(AVG(price_amount), 2) AS avg_price
FROM books
GROUP BY rating_band
ORDER BY
    CASE rating_band
        WHEN '4.5+' THEN 1
        WHEN '4.0 to 4.49' THEN 2
        WHEN '3.5 to 3.99' THEN 3
        WHEN 'Below 3.5' THEN 4
        ELSE 5
    END;

-- 7. Data quality check: duplicate titles should return zero rows.
SELECT
    title,
    COUNT(*) AS duplicate_count
FROM books
GROUP BY title
HAVING COUNT(*) > 1;

-- 8. Data quality check: records missing analytical fields.
SELECT
    COUNT(*) FILTER (WHERE price_amount IS NULL) AS missing_price_amount,
    COUNT(*) FILTER (WHERE rating_value IS NULL) AS missing_rating_value,
    COUNT(*) FILTER (WHERE authors IS NULL OR authors = '') AS missing_author
FROM books;

-- 9. Latest records loaded by the pipeline.
SELECT
    title,
    authors,
    price_amount,
    rating_value,
    scraped_at,
    updated_at
FROM books
ORDER BY scraped_at DESC NULLS LAST, updated_at DESC
LIMIT 20;
