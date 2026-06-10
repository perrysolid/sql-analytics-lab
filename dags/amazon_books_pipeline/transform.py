"""Transform raw Amazon book records into analysis-ready rows."""

import re

import pandas as pd

from amazon_books_pipeline.config import BOOK_DATA_XCOM_KEY, RAW_BOOK_DATA_XCOM_KEY


def clean_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text or None


def parse_decimal(value):
    """Return the first decimal number from a text value, or None."""
    if not value:
        return None

    match = re.search(r"\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def transform_book_data(ti):
    """Deduplicate and enrich raw records, then push clean rows to XCom."""
    raw_book_data = ti.xcom_pull(key=RAW_BOOK_DATA_XCOM_KEY, task_ids="extract_book_data")
    if not raw_book_data:
        raise ValueError("No raw book data found")

    df = pd.DataFrame(raw_book_data)
    expected_columns = ["title", "authors", "price", "rating", "source_url", "scraped_at"]

    for column in expected_columns:
        if column not in df.columns:
            df[column] = None
        df[column] = df[column].map(clean_text)

    df = df.dropna(subset=["title"])
    df = df.drop_duplicates(subset="title")
    df["price_amount"] = df["price"].map(parse_decimal)
    df["rating_value"] = df["rating"].map(parse_decimal)

    output_columns = [
        "title",
        "authors",
        "price",
        "rating",
        "price_amount",
        "rating_value",
        "source_url",
        "scraped_at",
    ]
    transformed_books = df[output_columns].to_dict("records")

    if not transformed_books:
        raise ValueError("No valid book data found after transformation")

    ti.xcom_push(key=BOOK_DATA_XCOM_KEY, value=transformed_books)
