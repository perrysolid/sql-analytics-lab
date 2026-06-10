"""Load transformed book records into PostgreSQL."""

from airflow.providers.postgres.hooks.postgres import PostgresHook

from amazon_books_pipeline.config import BOOK_DATA_XCOM_KEY, POSTGRES_CONN_ID

UPSERT_BOOK_SQL = """
INSERT INTO books (
    title,
    authors,
    price,
    rating,
    price_amount,
    rating_value,
    source_url,
    scraped_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (title) DO UPDATE SET
    authors = EXCLUDED.authors,
    price = EXCLUDED.price,
    rating = EXCLUDED.rating,
    price_amount = EXCLUDED.price_amount,
    rating_value = EXCLUDED.rating_value,
    source_url = EXCLUDED.source_url,
    scraped_at = EXCLUDED.scraped_at,
    updated_at = NOW();
"""


def load_book_data(ti):
    """Upsert transformed book rows into the target table."""
    book_data = ti.xcom_pull(key=BOOK_DATA_XCOM_KEY, task_ids="transform_book_data")
    if not book_data:
        raise ValueError("No transformed book data found")

    postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    for book in book_data:
        postgres_hook.run(
            UPSERT_BOOK_SQL,
            parameters=(
                book["title"],
                book["authors"],
                book["price"],
                book["rating"],
                book["price_amount"],
                book["rating_value"],
                book["source_url"],
                book["scraped_at"],
            ),
        )
