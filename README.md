# Amazon Books Data Pipeline

An Airflow ETL project that extracts Amazon book search results, transforms text fields into analysis-ready columns, and loads the data into PostgreSQL for SQL analysis.

![Pipeline design](images/pipeline_design.png)

## What This Project Shows

- Airflow DAG orchestration with extract, transform, load, quality check, and analytics-view tasks.
- Docker Compose based local stack with Airflow, PostgreSQL, Redis, Celery worker, and pgAdmin.
- Web scraping with `requests` and `BeautifulSoup`.
- Data cleaning with parsed numeric price and rating columns.
- Idempotent PostgreSQL loading with `ON CONFLICT` upserts.
- SQL queries for schema setup, data quality checks, profiling, and analysis.

## Project Structure

```text
.
├── .env.example
├── .gitignore
├── README.md
├── dags/
│   ├── app.py
│   └── amazon_books_pipeline/
│       ├── __init__.py
│       ├── config.py
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── sql_queries.py
├── docker-compose.yaml
├── images/
│   └── pipeline_design.png
├── requirements.txt
└── sql/
    ├── 01_schema_and_quality.sql
    ├── 02_analysis_queries.sql
    └── 03_data_quality_checks.sql
```

## File Details

| File | Purpose |
| --- | --- |
| `.env.example` | Example local environment values for Docker Compose, Airflow credentials, and runtime Python packages. |
| `.gitignore` | Excludes virtual environments, caches, logs, Airflow local output, and OS-generated files. |
| `README.md` | Main project documentation with setup, structure, and pipeline flow. |
| `dags/app.py` | Airflow DAG entrypoint. Airflow discovers `fetch_and_store_amazon_books` from this file and wires all tasks together. |
| `dags/amazon_books_pipeline/__init__.py` | Marks `amazon_books_pipeline` as an importable Python package for Airflow. |
| `dags/amazon_books_pipeline/config.py` | Central constants such as the Postgres connection ID, search query, book limit, request timeout, and XCom keys. |
| `dags/amazon_books_pipeline/extract.py` | Extract step. Scrapes Amazon search result pages and pushes raw book records to XCom. |
| `dags/amazon_books_pipeline/transform.py` | Transform step. Cleans text, deduplicates titles, and parses `price_amount` and `rating_value`. |
| `dags/amazon_books_pipeline/load.py` | Load step. Upserts transformed records into the PostgreSQL `books` table. |
| `dags/amazon_books_pipeline/sql_queries.py` | SQL constants used by the DAG for table creation, indexes, data quality validation, and analytics views. |
| `docker-compose.yaml` | Local Airflow stack with PostgreSQL, Redis, webserver, scheduler, worker, triggerer, and pgAdmin. |
| `images/pipeline_design.png` | Visual architecture diagram used in the README. |
| `requirements.txt` | Minimal Python dependencies used by the DAG modules during local development. |
| `sql/01_schema_and_quality.sql` | Standalone SQL for creating/upgrading the `books` table, indexes, quality checks, and reporting views. |
| `sql/02_analysis_queries.sql` | Analysis query set for catalog health, rankings, author summaries, price bands, rating bands, and load inspection. |
| `sql/03_data_quality_checks.sql` | Read-only quality checks for duplicates, missing values, rating range, price sanity, and freshness. |

## Why `dags/app.py` Is Needed

The ETL logic is split into separate modules, but `dags/app.py` is still required because Airflow scans the `dags/` folder for DAG definitions. This file keeps orchestration separate from implementation: the DAG dependencies live in `app.py`, while extract, transform, load, and SQL logic live under `dags/amazon_books_pipeline/`.

## Pipeline Flow

1. `extract_book_data` scrapes raw Amazon search result fields.
2. `transform_book_data` deduplicates by title and parses:
   - `price_amount` from price text.
   - `rating_value` from rating text.
   - `scraped_at` and `source_url` metadata.
3. `create_table` creates or upgrades the `books` table and indexes.
4. `load_book_data` upserts rows into PostgreSQL so repeated DAG runs do not duplicate books.
5. `data_quality_check` fails the DAG if the target table is empty or contains duplicate titles.
6. `create_analytics_views` creates reporting views for SQL analysis.

```text
extract_book_data
  -> transform_book_data
  -> create_table
  -> load_book_data
  -> data_quality_check
  -> create_analytics_views
```

## Run Locally

Create an optional `.env` file:

```bash
cp .env.example .env
```

Start Airflow:

```bash
docker compose up airflow-init
docker compose up
```

Open the services:

- Airflow UI: `http://localhost:8080`
- pgAdmin: `http://localhost:5050`
- PostgreSQL host: `localhost`
- PostgreSQL port: `5432`
- PostgreSQL database/user/password: `airflow` / `airflow` / `airflow`

In Airflow, create a PostgreSQL connection:

```text
Connection Id: books_connection
Connection Type: Postgres
Host: postgres
Schema: airflow
Login: airflow
Password: airflow
Port: 5432
```

Then unpause and trigger the DAG named `fetch_and_store_amazon_books`.

## SQL Queries

After a DAG run, open pgAdmin and run:

```sql
SELECT * FROM book_catalog_metrics;
SELECT * FROM top_rated_affordable_books;
```

The `sql/` folder also includes standalone scripts for schema setup, analysis, and quality checks:

- `sql/01_schema_and_quality.sql`
- `sql/02_analysis_queries.sql`
- `sql/03_data_quality_checks.sql`

## Project Summary

This project is a small batch ETL pipeline with orchestration, scraping, transformation, idempotent loading, data quality checks, and SQL-ready outputs. The code is organized so each pipeline stage can be understood independently while Airflow manages execution order and observability.
