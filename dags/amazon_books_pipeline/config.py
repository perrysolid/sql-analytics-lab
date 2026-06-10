"""Shared settings for the Amazon books pipeline."""

POSTGRES_CONN_ID = "books_connection"

BOOK_SEARCH_QUERY = "data engineering books"
BOOK_LIMIT = 50
MAX_PAGES_TO_SCAN = 5
REQUEST_TIMEOUT_SECONDS = 20

RAW_BOOK_DATA_XCOM_KEY = "raw_book_data"
BOOK_DATA_XCOM_KEY = "book_data"

AMAZON_HEADERS = {
    "Referer": "https://www.amazon.com/",
    "Sec-Ch-Ua": "Not_A Brand",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "macOS",
    "User-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/107.0.0.0 Safari/537.36"
    ),
}
