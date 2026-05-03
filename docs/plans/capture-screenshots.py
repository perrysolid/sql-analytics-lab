#!/usr/bin/env python3
"""
Capture screenshots of Superset UI for role permission testing report.
Uses separate browser instances per user to avoid session conflicts.
"""

import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8088"
SCREENSHOT_DIR = "/mnt/c/Users/konra/sql-playgrounds/docs/plans/screenshots"

USERS = {
    "admin": {"username": "admin", "password": "admin123"},
    "viewer": {"username": "test-viewer", "password": "testpass123"},
    "owner": {"username": "test-owner", "password": "testpass123"},
}

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def wait_and_screenshot(page, name, wait_sec=3):
    """Wait then take screenshot."""
    time.sleep(wait_sec)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path)
    print(f"  Saved: {name}.png")


def login(page, user_key):
    """Login to Superset."""
    user = USERS[user_key]
    page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded")
    time.sleep(2)
    page.fill('#username', user["username"])
    page.fill('#password', user["password"])
    page.click('button[type="submit"], input[type="submit"]')
    time.sleep(4)
    # Verify login succeeded by checking URL
    if "/login" in page.url:
        print(f"  WARNING: Login may have failed for {user_key}, still on login page")
        # Try again
        time.sleep(2)
        page.fill('#username', user["username"])
        page.fill('#password', user["password"])
        page.click('button[type="submit"], input[type="submit"]')
        time.sleep(4)


def navigate(page, path, wait_sec=4):
    """Navigate to a page."""
    page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded")
    time.sleep(wait_sec)


def capture_user_session(playwright_instance, user_key):
    """Capture all screenshots for a user using a fresh browser instance."""
    browser = playwright_instance.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    print(f"\n--- Capturing for {user_key} ---")

    # Login
    login(page, user_key)
    wait_and_screenshot(page, f"{user_key}-01-home")

    # Dashboard list
    navigate(page, "/dashboard/list/")
    wait_and_screenshot(page, f"{user_key}-02-dashboard-list")

    # View published dashboard (Revenue Analysis - not owned by test-owner)
    navigate(page, "/superset/dashboard/test-revenue-analysis/", wait_sec=6)
    wait_and_screenshot(page, f"{user_key}-03-dashboard-revenue")

    # View owned dashboard (Trip Patterns - owned by admin + test-owner)
    navigate(page, "/superset/dashboard/test-trip-patterns/", wait_sec=6)
    wait_and_screenshot(page, f"{user_key}-04-dashboard-trip-patterns")

    # Try to find edit button on owned dashboard
    try:
        edit_btn = page.locator('[aria-label="Edit dashboard"]').first
        if edit_btn.is_visible(timeout=3000):
            edit_btn.click()
            time.sleep(2)
            wait_and_screenshot(page, f"{user_key}-05-dashboard-edit-mode")
            try:
                discard = page.locator('button:has-text("Discard")').first
                if discard.is_visible(timeout=2000):
                    discard.click()
                    time.sleep(1)
            except Exception:
                pass
        else:
            wait_and_screenshot(page, f"{user_key}-05-no-edit-button")
    except Exception:
        wait_and_screenshot(page, f"{user_key}-05-no-edit-button")

    # Chart list
    navigate(page, "/chart/list/")
    wait_and_screenshot(page, f"{user_key}-06-chart-list")

    # Dataset list
    navigate(page, "/tablemodelview/list/")
    wait_and_screenshot(page, f"{user_key}-07-dataset-list")

    # SQL Lab
    navigate(page, "/sqllab/", wait_sec=4)
    wait_and_screenshot(page, f"{user_key}-08-sqllab")

    # Database list
    navigate(page, "/databaseview/list/")
    wait_and_screenshot(page, f"{user_key}-09-database-list")

    # Navigation: try + button
    navigate(page, "/")
    time.sleep(2)
    try:
        plus_btn = page.locator('[data-test="new-dropdown"]').first
        if plus_btn.is_visible(timeout=2000):
            plus_btn.click()
            time.sleep(1)
            wait_and_screenshot(page, f"{user_key}-10-create-menu")
            page.keyboard.press("Escape")
        else:
            wait_and_screenshot(page, f"{user_key}-10-no-create-menu")
    except Exception:
        wait_and_screenshot(page, f"{user_key}-10-no-create-menu")

    browser.close()


def capture_admin_session(playwright_instance):
    """Capture admin-specific views."""
    browser = playwright_instance.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    print("\n--- Capturing admin-specific views ---")
    login(page, "admin")

    # Dashboard list (admin sees all including drafts)
    navigate(page, "/dashboard/list/")
    wait_and_screenshot(page, "admin-01-dashboard-list-all")

    # Users list
    navigate(page, "/users/list/")
    wait_and_screenshot(page, "admin-02-users-list")

    # Roles list
    navigate(page, "/roles/list/")
    wait_and_screenshot(page, "admin-03-roles-list")

    # Sublime Starter role
    navigate(page, "/roles/edit/6")
    wait_and_screenshot(page, "admin-04-sublime-starter-role")

    # Sublime User Management role
    navigate(page, "/roles/edit/7")
    wait_and_screenshot(page, "admin-05-sublime-user-mgmt-role")

    browser.close()


def main():
    print("=" * 60)
    print("CAPTURING SCREENSHOTS FOR PERMISSION TESTING REPORT")
    print("=" * 60)

    with sync_playwright() as p:
        # Use separate browser instances to avoid session conflicts
        capture_user_session(p, "viewer")
        capture_user_session(p, "owner")
        capture_admin_session(p)

    files = sorted([f for f in os.listdir(SCREENSHOT_DIR) if f.endswith('.png') and f != 'debug-login.png'])
    print(f"\nTotal screenshots: {len(files)}")
    for f in files:
        print(f"  {f}")


if __name__ == "__main__":
    main()
