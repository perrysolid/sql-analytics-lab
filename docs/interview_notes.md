# Interview Notes

## 30-Second Explanation

This is a batch ETL pipeline for Amazon book search data. Airflow orchestrates the workflow, Python scrapes and cleans semi-structured HTML data, and PostgreSQL stores curated data for analysis. I split the project into extract, transform, and load modules, then added production-style improvements such as idempotent upserts, typed analytical fields, quality checks, indexes, and SQL views.

## Architecture

- Source: Amazon search results for data engineering books.
- Extract: `requests` downloads HTML pages and `BeautifulSoup` parses result cards.
- Transform: Python deduplicates titles and converts price/rating text into numeric fields.
- Load: Airflow writes into PostgreSQL using a `PostgresHook`.
- Quality: `SQLExecuteQueryOperator` fails the DAG if the table is empty or duplicate titles exist.
- Analytics: SQL views and ready-made queries support quick reporting in pgAdmin.

## Code Walkthrough Order

1. `dags/app.py`: DAG orchestration and task dependencies.
2. `dags/amazon_books_pipeline/extract.py`: raw Amazon scraping.
3. `dags/amazon_books_pipeline/transform.py`: cleaning, deduplication, and parsed numeric fields.
4. `dags/amazon_books_pipeline/load.py`: PostgreSQL upsert.
5. `dags/amazon_books_pipeline/sql_queries.py`: schema, indexes, quality checks, and views.

## Improvements I Can Talk About

- Idempotency: The pipeline uses `ON CONFLICT (title) DO UPDATE`, so rerunning the DAG updates existing records instead of creating duplicates.
- Data quality: The DAG has a dedicated post-load quality check.
- Observability: Airflow gives task-level logs, retries, scheduling, and failure visibility.
- Analytical schema: Raw text fields are kept, while `price_amount` and `rating_value` make SQL analysis easier.
- Performance: Indexes support lookups and ordering by title, rating, and price.
- Maintainability: Extract, transform, load, and SQL are separated into focused files.

## Demo Flow

1. Show the DAG graph: `extract_book_data -> transform_book_data -> create_table -> load_book_data -> data_quality_check -> create_analytics_views`.
2. Open `dags/app.py` to show that the DAG file is now only orchestration.
3. Open `extract.py`, `transform.py`, and `load.py` to show separation of concerns.
4. Open the `books` table in pgAdmin and show raw plus parsed columns.
5. Run `SELECT * FROM book_catalog_metrics;`.
6. Open `sql/02_interview_analysis_queries.sql` and show the data-quality queries.

## Questions To Prepare

**Why Airflow?**
Airflow is useful when a data workflow has multiple steps, dependencies, retries, scheduling, and monitoring needs. Here it makes the extract, load, validation, and reporting setup repeatable.

**Why keep both raw and parsed fields?**
The raw values preserve the original scraped data for debugging, while numeric columns support analysis and reporting.

**How do you avoid duplicate data?**
The table has a unique index on `title`, and the load query uses an upsert. If a book appears again in a later run, the pipeline updates it.

**What happens if Amazon changes its HTML?**
The extract task can fail if selectors stop matching. That is intentional because Airflow will show the failure, retry once, and make the issue visible.

**How would you improve this further?**
I would add a custom Airflow Docker image, unit tests for parsing, a staging table, scrape status metrics, and a dashboard layer such as Superset or Metabase.

## One-Minute Project Pitch

I started from a simple Amazon books ETL and made it more interview-ready. The DAG now clearly separates orchestration from extract, transform, and load logic. It also normalizes important fields, upserts data safely, validates the load, and exposes analytics views. That lets me talk about the full data engineering lifecycle: orchestration, extraction, transformation, schema design, data quality, and SQL analysis.
