"""SQL used by the Amazon books Airflow DAG."""

CREATE_BOOKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    price TEXT,
    rating TEXT,
    price_amount NUMERIC(10, 2),
    rating_value NUMERIC(3, 2),
    source_url TEXT,
    scraped_at TIMESTAMPTZ,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE books ADD COLUMN IF NOT EXISTS price_amount NUMERIC(10, 2);
ALTER TABLE books ADD COLUMN IF NOT EXISTS rating_value NUMERIC(3, 2);
ALTER TABLE books ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE books ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMPTZ;
ALTER TABLE books ADD COLUMN IF NOT EXISTS inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE books ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

DELETE FROM books a
USING books b
WHERE a.id < b.id
  AND a.title = b.title;

CREATE UNIQUE INDEX IF NOT EXISTS idx_books_unique_title ON books (title);
CREATE INDEX IF NOT EXISTS idx_books_rating_value ON books (rating_value DESC);
CREATE INDEX IF NOT EXISTS idx_books_price_amount ON books (price_amount);
"""


CREATE_ANALYTICS_VIEWS_SQL = """
CREATE OR REPLACE VIEW book_catalog_metrics AS
SELECT
    COUNT(*) AS total_books,
    COUNT(*) FILTER (WHERE price_amount IS NOT NULL) AS books_with_price,
    COUNT(*) FILTER (WHERE rating_value IS NOT NULL) AS books_with_rating,
    ROUND(AVG(price_amount), 2) AS avg_price,
    ROUND(AVG(rating_value), 2) AS avg_rating,
    MIN(scraped_at) AS first_scraped_at,
    MAX(scraped_at) AS latest_scraped_at
FROM books;

CREATE OR REPLACE VIEW top_rated_affordable_books AS
SELECT
    title,
    authors,
    price_amount,
    rating_value,
    scraped_at
FROM books
WHERE rating_value >= 4.0
  AND price_amount IS NOT NULL
ORDER BY rating_value DESC, price_amount ASC
LIMIT 10;
"""


DATA_QUALITY_SQL = """
DO $$
DECLARE
    total_rows INTEGER;
    duplicate_titles INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_rows FROM books;

    IF total_rows = 0 THEN
        RAISE EXCEPTION 'Data quality failed: books table is empty';
    END IF;

    SELECT COUNT(*) INTO duplicate_titles
    FROM (
        SELECT title
        FROM books
        GROUP BY title
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_titles > 0 THEN
        RAISE EXCEPTION 'Data quality failed: duplicate book titles found';
    END IF;
END $$;
"""
