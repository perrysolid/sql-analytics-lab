# Demo Walkthrough

Use this flow for a short interview demo.

## 1. Open The DAG

Start with `dags/app.py`. Explain that this file is intentionally small because it only handles orchestration.

Highlight the task chain:

```text
extract_book_data -> transform_book_data -> create_table -> load_book_data -> data_quality_check -> create_analytics_views
```

## 2. Show Separation Of Concerns

- `extract.py`: reads raw fields from Amazon search result pages.
- `transform.py`: deduplicates rows and parses numeric price/rating values.
- `load.py`: writes records to PostgreSQL with an upsert.
- `sql_queries.py`: keeps schema, quality, and view SQL out of the DAG file.

## 3. Show The Database Layer

Open `sql/01_schema_and_quality.sql` and point out:

- Typed analytical columns.
- Unique index on `title`.
- Post-load quality checks.
- Reporting views.

## 4. Run Two Simple Queries

```sql
SELECT * FROM book_catalog_metrics;
SELECT * FROM top_rated_affordable_books;
```

## 5. Close With The Engineering Value

This is not only a scraper. It is a repeatable ETL workflow with orchestration, transformation, idempotent loading, data quality, and SQL analysis.
