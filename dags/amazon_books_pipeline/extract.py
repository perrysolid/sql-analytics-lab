"""Extract book search result data from Amazon."""

from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from amazon_books_pipeline.config import (
    AMAZON_HEADERS,
    BOOK_SEARCH_QUERY,
    MAX_PAGES_TO_SCAN,
    RAW_BOOK_DATA_XCOM_KEY,
    REQUEST_TIMEOUT_SECONDS,
)


def build_search_url(page):
    query = BOOK_SEARCH_QUERY.replace(" ", "+")
    return f"https://www.amazon.com/s?k={query}&page={page}"


def extract_book_data(num_books, ti):
    """Scrape raw book fields and push them to XCom."""
    books = []
    scraped_at = datetime.now(timezone.utc).isoformat()

    for page in range(1, MAX_PAGES_TO_SCAN + 1):
        if len(books) >= num_books:
            break

        url = build_search_url(page)
        response = requests.get(url, headers=AMAZON_HEADERS, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        book_containers = soup.find_all("div", {"class": "s-result-item"})

        for book in book_containers:
            title = book.find("span", {"class": "a-text-normal"})
            author = book.find("a", {"class": "a-size-base"})
            price = book.select_one(".a-price .a-offscreen") or book.find("span", {"class": "a-price-whole"})
            rating = book.find("span", {"class": "a-icon-alt"})

            if not title or not title.text.strip():
                continue

            books.append({
                "title": title.text.strip(),
                "authors": author.text.strip() if author else None,
                "price": price.text.strip() if price else None,
                "rating": rating.text.strip() if rating else None,
                "source_url": url,
                "scraped_at": scraped_at,
            })

            if len(books) >= num_books:
                break

    if not books:
        raise ValueError("No book records were extracted. Amazon markup or blocking may have changed.")

    ti.xcom_push(key=RAW_BOOK_DATA_XCOM_KEY, value=books[:num_books])
