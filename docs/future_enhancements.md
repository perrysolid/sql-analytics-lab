# Future Enhancements

These are realistic next steps to mention if an interviewer asks how the project could be productionized.

## Pipeline Reliability

- Add unit tests for parser functions in `transform.py`.
- Add a staging table before merging into the final `books` table.
- Store raw HTML or raw extracted JSON for debugging failed parses.
- Capture scrape counts and missing-field counts as run metrics.

## Deployment

- Build a custom Airflow image instead of installing packages at container startup.
- Move credentials into Airflow connections or secrets.
- Add CI checks for Python syntax, SQL linting, and Docker Compose validation.

## Data Modeling

- Split authors into a separate dimension table.
- Add a scrape-run table to track each DAG execution.
- Keep historical snapshots if price/rating changes need trend analysis.

## Analytics

- Add a dashboard layer such as Apache Superset, Metabase, or Streamlit.
- Create materialized views for frequently used reporting queries.
- Add more queries around price bands, rating bands, and author-level summaries.
