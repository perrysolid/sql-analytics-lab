#!/usr/bin/env python3
"""Quick recapture of 4 dashboard screenshots with 30s waits."""

import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8088"
SCREENSHOT_DIR = "/mnt/c/Users/konra/sql-playgrounds/.temp/report/screenshots"

USERS = {
    "viewer": {"username": "test-viewer", "password": "testpass123"},
    "owner": {"username": "test-owner", "password": "testpass123"},
}

DASHBOARDS = [
    ("revenue", "/superset/dashboard/test-revenue-analysis/", "03-dashboard-revenue"),
    ("trip-patterns", "/superset/dashboard/test-trip-patterns/", "04-dashboard-trip-patterns"),
]


def login(page, user_key):
    user = USERS[user_key]
    # Navigate with generous timeout, catch failures
    for attempt in range(3):
        try:
            page.goto(f"{BASE_URL}/login/", wait_until="commit", timeout=45000)
            page.wait_for_selector('#username', state='visible', timeout=20000)
            break
        except Exception:
            print(f"  Login page attempt {attempt+1} failed, retrying...")
            time.sleep(5)
    else:
        # Last resort: just wait and hope it loaded
        time.sleep(10)

    page.fill('#username', user["username"])
    page.fill('#password', user["password"])
    page.click('button[type="submit"], input[type="submit"]')
    time.sleep(4)
    print(f"  Logged in as {user_key}")


def capture(playwright_instance, user_key):
    browser = playwright_instance.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.set_default_timeout(60000)

    login(page, user_key)

    for name, path, file_prefix in DASHBOARDS:
        print(f"  {user_key}: {name}...", end=" ", flush=True)
        try:
            page.goto(f"{BASE_URL}{path}", wait_until="commit", timeout=45000)
        except Exception:
            pass
        time.sleep(30)
        # Dismiss toasts
        for btn in page.locator('button[aria-label="close"]').all():
            try:
                btn.click(timeout=500)
            except Exception:
                pass
        filename = f"{user_key}-{file_prefix}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        page.screenshot(path=filepath)
        size = os.path.getsize(filepath)
        print(f"saved ({size:,} bytes)")

    # Navigate away before closing to stop background queries
    try:
        page.goto(f"{BASE_URL}/logout/", wait_until="commit", timeout=10000)
    except Exception:
        pass
    browser.close()


with sync_playwright() as p:
    print("Capturing dashboard screenshots (30s wait each)...")
    capture(p, "viewer")
    print("  Cooldown 10s before owner session...")
    time.sleep(10)
    capture(p, "owner")
    print("Done!")
