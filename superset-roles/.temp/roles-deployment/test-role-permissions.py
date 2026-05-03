#!/usr/bin/env python3
"""
Automated Role Permission Testing for Superset
Tests Sublime Starter (viewer) and Sublime User Management (owner) roles
against the original Polish requirements document.

Run inside the Superset container:
  docker cp superset/config/role-backups/test-role-permissions.py sql-playground-superset:/app/
  docker exec sql-playground-superset python3 /app/test-role-permissions.py

NON-DESTRUCTIVE: DELETE tests use temporary objects created specifically for
testing, never real dashboards/charts. All test objects are cleaned up afterward.
"""

import json
import sys
import requests
from collections import defaultdict

BASE_URL = "http://localhost:8088"

USERS = {
    "viewer": {"username": "test-viewer", "password": "testpass123", "role": "Sublime Starter"},
    "owner": {"username": "test-owner", "password": "testpass123", "role": "Sublime User Management"},
}

# Object IDs — auto-detected during setup phase
DASHBOARD_PUBLISHED_OWNED = None      # Published, owned by admin + test-owner
DASHBOARD_PUBLISHED_NOT_OWNED = None  # Published, owned by admin only
DASHBOARD_DRAFT_OWNED = None          # Draft, owned by admin + test-owner
DASHBOARD_DRAFT_NOT_OWNED = None      # Draft, owned by admin only

CHART_OWNED = None          # Owned by admin + test-owner
CHART_OWNED_2 = None        # Owned by admin + test-owner
CHART_NOT_OWNED = None      # Owned by admin only

DATASET_ID = None            # First available dataset
DATABASE_ID = None            # PostgreSQL


class TestRunner:
    def __init__(self):
        self.results = []
        self.tokens = {}
        self.admin_token = None
        self.cleanup_items = []  # (type, id) for cleanup via admin
        self.stats = defaultdict(int)

    def login(self, user_key):
        """Authenticate and store JWT token."""
        user = USERS[user_key]
        resp = requests.post(f"{BASE_URL}/api/v1/security/login", json={
            "username": user["username"],
            "password": user["password"],
            "provider": "db",
        })
        if resp.status_code != 200:
            print(f"FATAL: Cannot login as {user_key}: {resp.status_code} {resp.text}")
            sys.exit(1)
        self.tokens[user_key] = resp.json()["access_token"]

    def login_admin(self):
        resp = requests.post(f"{BASE_URL}/api/v1/security/login", json={
            "username": "admin", "password": "admin123", "provider": "db",
        })
        if resp.status_code != 200:
            print(f"FATAL: Cannot login as admin: {resp.status_code}")
            sys.exit(1)
        self.admin_token = resp.json()["access_token"]

    def admin_headers(self):
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json",
        }

    def headers(self, user_key):
        return {
            "Authorization": f"Bearer {self.tokens[user_key]}",
            "Content-Type": "application/json",
        }

    def record(self, test_id, category, description, user_key, expected, actual, passed, detail=""):
        self.results.append({
            "test_id": test_id,
            "category": category,
            "description": description,
            "user": user_key,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "detail": detail,
        })
        self.stats["total"] += 1
        self.stats["pass" if passed else "fail"] += 1

    def test_status(self, test_id, category, desc, user_key, method, url, expected_status,
                    json_body=None, detail=""):
        """Core test: send request and check HTTP status code."""
        h = self.headers(user_key)
        fn = getattr(requests, method.lower())
        kwargs = {"headers": h}
        if json_body is not None:
            kwargs["json"] = json_body

        try:
            resp = fn(f"{BASE_URL}{url}", **kwargs)
            actual = resp.status_code
            if isinstance(expected_status, list):
                passed = actual in expected_status
                exp_str = f"one of {expected_status}"
            else:
                passed = actual == expected_status
                exp_str = str(expected_status)

            resp_detail = ""
            if not passed:
                try:
                    resp_detail = resp.text[:300]
                except Exception:
                    resp_detail = "(unreadable)"

            self.record(test_id, category, desc, user_key, exp_str, str(actual), passed,
                       detail or resp_detail)
            return resp
        except Exception as e:
            self.record(test_id, category, desc, user_key, str(expected_status), f"ERROR: {e}", False)
            return None

    def test_list_contains(self, test_id, category, desc, user_key, url, result_key,
                           check_field, check_value, should_contain):
        """Test that a list endpoint contains (or doesn't contain) a specific item."""
        h = self.headers(user_key)
        # Fetch all pages to handle pagination
        all_items = []
        page = 0
        while True:
            sep = "&" if "?" in url else "?"
            resp = requests.get(f"{BASE_URL}{url}{sep}q=(page:{page},page_size:100)", headers=h)
            if resp.status_code != 200:
                self.record(test_id, category, desc, user_key,
                           "visible" if should_contain else "hidden",
                           f"HTTP {resp.status_code}", False, resp.text[:200])
                return
            data = resp.json()
            items = data.get("result", [])
            all_items.extend(items)
            if len(items) < 100:
                break
            page += 1

        found = any(item.get(check_field) == check_value for item in all_items)

        if should_contain:
            passed = found
            expected = "visible"
            actual = "visible" if found else "NOT visible"
        else:
            passed = not found
            expected = "hidden"
            actual = "hidden" if not found else "VISIBLE (unexpected)"

        self.record(test_id, category, desc, user_key, expected, actual, passed)

    # =========================================================================
    # AUTO-DETECT OBJECT IDS
    # =========================================================================
    def detect_ids(self):
        """Auto-detect dashboard, chart, dataset, and database IDs."""
        global DASHBOARD_PUBLISHED_OWNED, DASHBOARD_PUBLISHED_NOT_OWNED
        global DASHBOARD_DRAFT_OWNED, DASHBOARD_DRAFT_NOT_OWNED
        global CHART_OWNED, CHART_OWNED_2, CHART_NOT_OWNED
        global DATASET_ID, DATABASE_ID

        h = self.admin_headers()

        # Dashboards
        resp = requests.get(f"{BASE_URL}/api/v1/dashboard/", headers=h)
        dashboards = resp.json().get("result", [])

        for d in dashboards:
            did = d["id"]
            # Fetch full detail to check ownership and published status
            detail = requests.get(f"{BASE_URL}/api/v1/dashboard/{did}", headers=h).json().get("result", {})
            owner_ids = [o["id"] for o in detail.get("owners", [])]
            published = detail.get("published", False)
            title = detail.get("dashboard_title", "")

            if published and 3 in owner_ids and "Draft" not in title:
                DASHBOARD_PUBLISHED_OWNED = did
            elif published and 3 not in owner_ids and "Draft" not in title:
                DASHBOARD_PUBLISHED_NOT_OWNED = did
            elif not published and 3 in owner_ids:
                DASHBOARD_DRAFT_OWNED = did
            elif not published and 3 not in owner_ids:
                DASHBOARD_DRAFT_NOT_OWNED = did

        # Charts
        resp = requests.get(f"{BASE_URL}/api/v1/chart/", headers=h)
        charts = resp.json().get("result", [])

        owned_charts = []
        not_owned_charts = []
        for c in charts:
            cid = c["id"]
            detail = requests.get(f"{BASE_URL}/api/v1/chart/{cid}", headers=h).json().get("result", {})
            owner_ids = [o["id"] for o in detail.get("owners", [])]
            if 3 in owner_ids:
                owned_charts.append(cid)
            else:
                not_owned_charts.append(cid)

        if owned_charts:
            CHART_OWNED = owned_charts[0]
        if len(owned_charts) > 1:
            CHART_OWNED_2 = owned_charts[1]
        if not_owned_charts:
            CHART_NOT_OWNED = not_owned_charts[0]

        # Datasets
        resp = requests.get(f"{BASE_URL}/api/v1/dataset/", headers=h)
        datasets = resp.json().get("result", [])
        if datasets:
            DATASET_ID = datasets[0]["id"]

        # Databases
        resp = requests.get(f"{BASE_URL}/api/v1/database/", headers=h)
        databases = resp.json().get("result", [])
        if databases:
            DATABASE_ID = databases[0]["id"]

        print(f"  Dashboard Published+Owned: {DASHBOARD_PUBLISHED_OWNED}")
        print(f"  Dashboard Published+NotOwned: {DASHBOARD_PUBLISHED_NOT_OWNED}")
        print(f"  Dashboard Draft+Owned: {DASHBOARD_DRAFT_OWNED}")
        print(f"  Dashboard Draft+NotOwned: {DASHBOARD_DRAFT_NOT_OWNED}")
        print(f"  Chart Owned: {CHART_OWNED}, {CHART_OWNED_2}")
        print(f"  Chart NotOwned: {CHART_NOT_OWNED}")
        print(f"  Dataset: {DATASET_ID}, Database: {DATABASE_ID}")

        missing = []
        if not DASHBOARD_PUBLISHED_OWNED: missing.append("Published+Owned dashboard")
        if not DASHBOARD_PUBLISHED_NOT_OWNED: missing.append("Published+NotOwned dashboard")
        if not DASHBOARD_DRAFT_OWNED: missing.append("Draft+Owned dashboard")
        if not DASHBOARD_DRAFT_NOT_OWNED: missing.append("Draft+NotOwned dashboard")
        if not CHART_OWNED: missing.append("Owned chart")
        if not CHART_NOT_OWNED: missing.append("NotOwned chart")
        if not DATASET_ID: missing.append("Dataset")
        if not DATABASE_ID: missing.append("Database")
        if missing:
            print(f"  WARNING: Missing objects: {', '.join(missing)}")
            print("  Some tests may be skipped.")

    # =========================================================================
    # HELPER: Create temp objects for destructive tests
    # =========================================================================
    def create_temp_dashboard(self, owned_by_test_owner=True):
        """Create a temp dashboard via admin for delete testing. Returns ID or None."""
        owners = [1, 3] if owned_by_test_owner else [1]
        resp = requests.post(f"{BASE_URL}/api/v1/dashboard/", headers=self.admin_headers(), json={
            "dashboard_title": f"TEMP_DELETE_TEST_{'owned' if owned_by_test_owner else 'notowned'}",
            "published": False,
            "owners": owners,
        })
        if resp.status_code in [200, 201]:
            return resp.json().get("id")
        return None

    def create_temp_chart(self, owned_by_test_owner=True):
        """Create a temp chart via admin for delete testing. Returns ID or None."""
        owners = [1, 3] if owned_by_test_owner else [1]
        resp = requests.post(f"{BASE_URL}/api/v1/chart/", headers=self.admin_headers(), json={
            "slice_name": f"TEMP_DELETE_TEST_{'owned' if owned_by_test_owner else 'notowned'}",
            "datasource_id": DATASET_ID,
            "datasource_type": "table",
            "viz_type": "table",
            "owners": owners,
            "params": json.dumps({"viz_type": "table"}),
        })
        if resp.status_code in [200, 201]:
            return resp.json().get("id")
        return None

    # =========================================================================
    # 1. DASHBOARD TESTS
    # =========================================================================
    def test_dashboards(self):
        print("\n--- 1. DASHBOARDS ---")

        # 1.1.1 Non-owned: cannot edit
        for user in ["viewer", "owner"]:
            self.test_status("1.1.1", "Dashboards", "Non-owned: cannot edit",
                           user, "PUT",
                           f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_NOT_OWNED}",
                           [403, 422],
                           json_body={"dashboard_title": "SHOULD NOT CHANGE"})

        # 1.1.2 Non-owned: can copy (Save as) — POST new dashboard
        # Note: Viewer needs can_write Dashboard to POST. If viewer lacks it, 403 is expected.
        for user in ["viewer", "owner"]:
            resp = self.test_status("1.1.2", "Dashboards",
                                  f"Non-owned: copy (Save as) [{user}]",
                                  user, "POST", "/api/v1/dashboard/",
                                  [201, 200, 403],  # 403 acceptable for viewer (no can_write)
                                  json_body={
                                      "dashboard_title": f"Copy test by {user}",
                                      "published": False,
                                  })
            if resp and resp.status_code in [200, 201]:
                new_id = resp.json().get("id")
                if new_id:
                    self.cleanup_items.append(("dashboard", new_id))

        # 1.1.3 Non-owned: cannot delete
        # Use temp dashboards to test — never delete real ones
        for user in ["viewer", "owner"]:
            temp_id = self.create_temp_dashboard(owned_by_test_owner=False)
            if temp_id:
                resp = self.test_status("1.1.3", "Dashboards", "Non-owned: cannot delete",
                               user, "DELETE",
                               f"/api/v1/dashboard/{temp_id}",
                               [403, 404, 422])
                # If it wasn't deleted, clean up via admin
                check = requests.get(f"{BASE_URL}/api/v1/dashboard/{temp_id}",
                                    headers=self.admin_headers())
                if check.status_code == 200:
                    self.cleanup_items.append(("dashboard", temp_id))

        # 1.1.4 Non-owned: can export
        for user in ["viewer", "owner"]:
            self.test_status("1.1.4", "Dashboards", "Non-owned: can export",
                           user, "GET",
                           f"/api/v1/dashboard/export/?q=[{DASHBOARD_PUBLISHED_NOT_OWNED}]",
                           200)

        # 1.2.1 Owned: can edit (owner only)
        self.test_status("1.2.1", "Dashboards", "Owned: cannot edit (viewer)",
                        "viewer", "PUT",
                        f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                        [403, 422],
                        json_body={"dashboard_title": "SHOULD NOT CHANGE"})

        # Save original title for revert
        orig = requests.get(f"{BASE_URL}/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                           headers=self.admin_headers()).json().get("result", {})
        orig_title = orig.get("dashboard_title", "Test Dashboard 1 - Trip Patterns")

        resp = self.test_status("1.2.1", "Dashboards", "Owned: can edit (owner)",
                              "owner", "PUT",
                              f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                              200,
                              json_body={"dashboard_title": orig_title + " EDITED"})
        if resp and resp.status_code == 200:
            requests.put(f"{BASE_URL}/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                        headers=self.headers("owner"),
                        json={"dashboard_title": orig_title})

        # 1.2.2 Owned: can assign owner
        self.test_status("1.2.2", "Dashboards", "Owned: cannot assign owner (viewer)",
                        "viewer", "PUT",
                        f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                        [403, 422],
                        json_body={"owners": [1, 2, 3]})

        resp = self.test_status("1.2.2", "Dashboards", "Owned: can assign owner (owner)",
                              "owner", "PUT",
                              f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                              200,
                              json_body={"owners": [1, 2, 3]})
        if resp and resp.status_code == 200:
            requests.put(f"{BASE_URL}/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                        headers=self.headers("owner"),
                        json={"owners": [1, 3]})

        # 1.2.3 Owned: cannot delete (blocked for both)
        # Use TEMP dashboards so we don't destroy real data
        for user_key, label in [("viewer", "viewer"), ("owner", "owner")]:
            owned = (user_key == "owner")
            temp_id = self.create_temp_dashboard(owned_by_test_owner=owned)
            if temp_id:
                resp = self.test_status("1.2.3", "Dashboards",
                               f"Owned: cannot delete ({label})",
                               user_key, "DELETE",
                               f"/api/v1/dashboard/{temp_id}",
                               [403, 422])
                # Check if it was actually deleted (finding = role config issue)
                check = requests.get(f"{BASE_URL}/api/v1/dashboard/{temp_id}",
                                    headers=self.admin_headers())
                if check.status_code == 200:
                    self.cleanup_items.append(("dashboard", temp_id))
                elif resp and resp.status_code == 200:
                    # Dashboard was deleted — record as FINDING
                    pass  # Already recorded as FAIL above

        # 1.2.4 Owned: can toggle publish/draft
        self.test_status("1.2.4", "Dashboards", "Owned: cannot toggle published (viewer)",
                        "viewer", "PUT",
                        f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                        [403, 422],
                        json_body={"published": False})

        resp = self.test_status("1.2.4", "Dashboards", "Owned: can toggle published (owner)",
                              "owner", "PUT",
                              f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                              200,
                              json_body={"published": False})
        if resp and resp.status_code == 200:
            requests.put(f"{BASE_URL}/api/v1/dashboard/{DASHBOARD_PUBLISHED_OWNED}",
                        headers=self.headers("owner"),
                        json={"published": True})

        # 1.2.5 Non-owned: cannot toggle publish/draft
        for user in ["viewer", "owner"]:
            self.test_status("1.2.5", "Dashboards", "Non-owned: cannot toggle published",
                           user, "PUT",
                           f"/api/v1/dashboard/{DASHBOARD_PUBLISHED_NOT_OWNED}",
                           [403, 422],
                           json_body={"published": False})

    # =========================================================================
    # 1b. DASHBOARD DRAFT/PUBLISHED VISIBILITY
    # =========================================================================
    def test_dashboard_visibility(self):
        print("\n--- 1b. DASHBOARD DRAFT/PUBLISHED VISIBILITY ---")

        # 1.3.1 Published dashboards visible to all
        for user in ["viewer", "owner"]:
            self.test_list_contains("1.3.1", "Dashboard Visibility",
                                   f"Published Owned dashboard visible ({user})",
                                   user, "/api/v1/dashboard/", "result",
                                   "id", DASHBOARD_PUBLISHED_OWNED, True)
            self.test_list_contains("1.3.1", "Dashboard Visibility",
                                   f"Published NotOwned dashboard visible ({user})",
                                   user, "/api/v1/dashboard/", "result",
                                   "id", DASHBOARD_PUBLISHED_NOT_OWNED, True)

        # 1.3.2 Owned Draft dashboard visible to owner
        self.test_list_contains("1.3.2", "Dashboard Visibility",
                               "Owned Draft dashboard NOT visible (viewer)",
                               "viewer", "/api/v1/dashboard/", "result",
                               "id", DASHBOARD_DRAFT_OWNED, False)
        self.test_list_contains("1.3.2", "Dashboard Visibility",
                               "Owned Draft dashboard visible (owner)",
                               "owner", "/api/v1/dashboard/", "result",
                               "id", DASHBOARD_DRAFT_OWNED, True)

        # 1.3.3 Non-owned Draft dashboard hidden from all non-owners
        self.test_list_contains("1.3.3", "Dashboard Visibility",
                               "Non-owned Draft dashboard NOT visible (viewer)",
                               "viewer", "/api/v1/dashboard/", "result",
                               "id", DASHBOARD_DRAFT_NOT_OWNED, False)
        self.test_list_contains("1.3.3", "Dashboard Visibility",
                               "Non-owned Draft dashboard NOT visible (owner)",
                               "owner", "/api/v1/dashboard/", "result",
                               "id", DASHBOARD_DRAFT_NOT_OWNED, False)

        # 1.3.4 Owner can toggle owned Draft -> Published
        resp = self.test_status("1.3.4", "Dashboard Visibility",
                              "Owner can toggle owned Draft -> Published",
                              "owner", "PUT",
                              f"/api/v1/dashboard/{DASHBOARD_DRAFT_OWNED}",
                              200,
                              json_body={"published": True})

        # 1.3.5 Owner cannot toggle non-owned Draft (404 = hidden = effectively blocked)
        self.test_status("1.3.5", "Dashboard Visibility",
                        "Owner cannot toggle non-owned Draft",
                        "owner", "PUT",
                        f"/api/v1/dashboard/{DASHBOARD_DRAFT_NOT_OWNED}",
                        [403, 404, 422],
                        json_body={"published": True})

        # 1.3.6 Revert Dashboard 3 back to Draft
        if resp and resp.status_code == 200:
            self.test_status("1.3.6", "Dashboard Visibility",
                            "Revert owned Draft dashboard back to Draft",
                            "owner", "PUT",
                            f"/api/v1/dashboard/{DASHBOARD_DRAFT_OWNED}",
                            200,
                            json_body={"published": False})

    # =========================================================================
    # 2. DATASETS
    # =========================================================================
    def test_datasets(self):
        print("\n--- 2. DATASETS ---")

        # 2.1 Cannot edit datasets
        for user in ["viewer", "owner"]:
            self.test_status("2.1", "Datasets", "Cannot edit datasets",
                           user, "PUT", f"/api/v1/dataset/{DATASET_ID}",
                           [403, 422],
                           json_body={"description": "SHOULD_NOT_CHANGE"})

        # 2.2 Cannot create datasets
        for user in ["viewer", "owner"]:
            self.test_status("2.2", "Datasets", "Cannot create datasets",
                           user, "POST", "/api/v1/dataset/",
                           [403, 422],
                           json_body={
                               "database": DATABASE_ID,
                               "table_name": "test_should_not_create",
                               "schema": "nyc_taxi",
                           })

        # 2.3 Can read/view datasets
        for user in ["viewer", "owner"]:
            self.test_status("2.3", "Datasets", "Can read datasets",
                           user, "GET", f"/api/v1/dataset/{DATASET_ID}",
                           200)

        # 2.4 Owner can duplicate
        self.test_status("2.4", "Datasets", "Viewer cannot duplicate datasets",
                        "viewer", "POST", "/api/v1/dataset/duplicate",
                        [403, 422],
                        json_body={
                            "base_model_id": DATASET_ID,
                            "table_name": "test_dup_viewer",
                        })

        resp = self.test_status("2.4", "Datasets", "Owner can duplicate datasets",
                              "owner", "POST", "/api/v1/dataset/duplicate",
                              [200, 201],
                              json_body={
                                  "base_model_id": DATASET_ID,
                                  "table_name": "test_dup_owner",
                              })
        if resp and resp.status_code in [200, 201]:
            new_id = resp.json().get("id")
            if new_id:
                self.cleanup_items.append(("dataset", new_id))

        # 2.5 Owner can export
        self.test_status("2.5", "Datasets", "Viewer cannot export datasets",
                        "viewer", "GET",
                        f"/api/v1/dataset/export/?q=[{DATASET_ID}]",
                        [403, 422])
        self.test_status("2.5", "Datasets", "Owner can export datasets",
                        "owner", "GET",
                        f"/api/v1/dataset/export/?q=[{DATASET_ID}]",
                        200)

    # =========================================================================
    # 3. CHARTS
    # =========================================================================
    def test_charts(self):
        print("\n--- 3. CHARTS ---")

        # 3.1 Can view charts
        for user in ["viewer", "owner"]:
            self.test_status("3.1", "Charts", "Can view charts",
                           user, "GET", f"/api/v1/chart/{CHART_OWNED}",
                           200)

        # 3.3 Owner can create new charts
        self.test_status("3.3", "Charts", "Viewer cannot create charts",
                        "viewer", "POST", "/api/v1/chart/",
                        [403, 422],
                        json_body={
                            "slice_name": "Test Chart Viewer",
                            "datasource_id": DATASET_ID,
                            "datasource_type": "table",
                            "viz_type": "table",
                            "params": json.dumps({"viz_type": "table"}),
                        })

        resp = self.test_status("3.3", "Charts", "Owner can create charts",
                              "owner", "POST", "/api/v1/chart/",
                              [200, 201],
                              json_body={
                                  "slice_name": "Test Chart Owner",
                                  "datasource_id": DATASET_ID,
                                  "datasource_type": "table",
                                  "viz_type": "table",
                                  "params": json.dumps({"viz_type": "table"}),
                              })
        if resp and resp.status_code in [200, 201]:
            new_id = resp.json().get("id")
            if new_id:
                self.cleanup_items.append(("chart", new_id))

        # 3.4 Owner can edit owned charts
        self.test_status("3.4", "Charts", "Viewer cannot edit owned charts",
                        "viewer", "PUT", f"/api/v1/chart/{CHART_OWNED}",
                        [403, 422],
                        json_body={"description": "SHOULD NOT CHANGE"})

        resp = self.test_status("3.4", "Charts", "Owner can edit owned charts",
                              "owner", "PUT", f"/api/v1/chart/{CHART_OWNED}",
                              200,
                              json_body={"description": "Edited by test"})
        if resp and resp.status_code == 200:
            requests.put(f"{BASE_URL}/api/v1/chart/{CHART_OWNED}",
                        headers=self.headers("owner"),
                        json={"description": ""})

        # 3.5 Cannot edit non-owned charts
        for user in ["viewer", "owner"]:
            self.test_status("3.5", "Charts", "Cannot edit non-owned charts",
                           user, "PUT", f"/api/v1/chart/{CHART_NOT_OWNED}",
                           [403, 422],
                           json_body={"description": "SHOULD NOT CHANGE"})

        # 3.6 Cannot delete charts — use TEMP charts
        for user_key, label in [("viewer", "viewer"), ("owner", "owner")]:
            owned = (user_key == "owner")
            temp_id = self.create_temp_chart(owned_by_test_owner=owned)
            if temp_id:
                resp = self.test_status("3.6", "Charts",
                               f"Cannot delete charts ({label})",
                               user_key, "DELETE",
                               f"/api/v1/chart/{temp_id}",
                               [403, 422])
                check = requests.get(f"{BASE_URL}/api/v1/chart/{temp_id}",
                                    headers=self.admin_headers())
                if check.status_code == 200:
                    self.cleanup_items.append(("chart", temp_id))

        # 3.7 Can export charts
        for user in ["viewer", "owner"]:
            self.test_status("3.7", "Charts", "Can export charts",
                           user, "GET",
                           f"/api/v1/chart/export/?q=[{CHART_OWNED}]",
                           200)

    # =========================================================================
    # 4. SQL LAB
    # =========================================================================
    def test_sqllab(self):
        print("\n--- 4. SQL LAB ---")

        # 4.1 Owner can access SQL Lab (execute queries)
        self.test_status("4.1", "SQL Lab", "Viewer cannot execute SQL",
                        "viewer", "POST", "/api/v1/sqllab/execute/",
                        [403, 422, 400],
                        json_body={
                            "database_id": DATABASE_ID,
                            "sql": "SELECT 1",
                            "schema": "nyc_taxi",
                        })

        self.test_status("4.1", "SQL Lab", "Owner can execute SQL",
                        "owner", "POST", "/api/v1/sqllab/execute/",
                        [200, 201],
                        json_body={
                            "database_id": DATABASE_ID,
                            "sql": "SELECT 1 as test",
                            "schema": "nyc_taxi",
                        })

        # 4.2 Owner can save queries
        self.test_status("4.2", "SQL Lab", "Viewer cannot save queries",
                        "viewer", "POST", "/api/v1/saved_query/",
                        [403, 422],
                        json_body={
                            "db_id": DATABASE_ID,
                            "label": "Test Query Viewer",
                            "sql": "SELECT 1",
                            "schema": "nyc_taxi",
                        })

        resp = self.test_status("4.2", "SQL Lab", "Owner can save queries",
                              "owner", "POST", "/api/v1/saved_query/",
                              [200, 201],
                              json_body={
                                  "db_id": DATABASE_ID,
                                  "label": "Test Query Owner",
                                  "sql": "SELECT 1 as test",
                                  "schema": "nyc_taxi",
                              })
        if resp and resp.status_code in [200, 201]:
            new_id = resp.json().get("id")
            if new_id:
                self.cleanup_items.append(("saved_query", new_id))

        # 4.3 Both can read saved queries
        for user in ["viewer", "owner"]:
            self.test_status("4.3", "SQL Lab", "Can read saved queries",
                           user, "GET", "/api/v1/saved_query/",
                           200)

    # =========================================================================
    # 5. TAGS
    # =========================================================================
    def test_tags(self):
        print("\n--- 5. TAGS ---")

        # 5.1 Both can read tags
        for user in ["viewer", "owner"]:
            self.test_status("5.1", "Tags", "Can read tags",
                           user, "GET", "/api/v1/tag/",
                           200)

        # 5.2 Owner can create tags
        self.test_status("5.2", "Tags", "Viewer cannot create tags",
                        "viewer", "POST", "/api/v1/tag/",
                        [403, 422],
                        json_body={
                            "name": "test-tag-viewer",
                            "description": "Should not be created",
                        })

        resp = self.test_status("5.2", "Tags", "Owner can create tags",
                              "owner", "POST", "/api/v1/tag/",
                              [200, 201],
                              json_body={
                                  "name": "test-tag-owner",
                                  "description": "Test tag created by owner",
                              })
        if resp and resp.status_code in [200, 201]:
            new_id = resp.json().get("id")
            if new_id:
                self.cleanup_items.append(("tag", new_id))

    # =========================================================================
    # 6. DATABASES
    # =========================================================================
    def test_databases(self):
        print("\n--- 6. DATABASES ---")

        # 6.1 Both can read databases
        for user in ["viewer", "owner"]:
            self.test_status("6.1", "Databases", "Can read databases",
                           user, "GET", "/api/v1/database/",
                           200)

        # 6.2 Neither can edit databases
        for user in ["viewer", "owner"]:
            self.test_status("6.2", "Databases", "Cannot edit databases",
                           user, "PUT", f"/api/v1/database/{DATABASE_ID}",
                           [403, 422],
                           json_body={"database_name": "SHOULD NOT CHANGE"})

    # =========================================================================
    # CLEANUP
    # =========================================================================
    def cleanup(self):
        """Delete test objects created during testing via admin."""
        print("\n--- CLEANUP ---")
        for obj_type, obj_id in self.cleanup_items:
            url_map = {
                "dashboard": f"/api/v1/dashboard/{obj_id}",
                "chart": f"/api/v1/chart/{obj_id}",
                "dataset": f"/api/v1/dataset/{obj_id}",
                "saved_query": f"/api/v1/saved_query/{obj_id}",
                "tag": f"/api/v1/tag/{obj_id}",
            }
            url = url_map.get(obj_type)
            if url:
                resp = requests.delete(f"{BASE_URL}{url}", headers=self.admin_headers())
                status = "OK" if resp.status_code in [200, 204] else f"({resp.status_code})"
                print(f"  Cleanup {obj_type} ID={obj_id}: {status}")

    # =========================================================================
    # REPORT
    # =========================================================================
    def print_report(self):
        print("\n" + "=" * 110)
        print("ROLE PERMISSION TEST RESULTS")
        print("=" * 110)

        current_category = None
        for r in self.results:
            if r["category"] != current_category:
                current_category = r["category"]
                print(f"\n{'─' * 110}")
                print(f"  {current_category}")
                print(f"{'─' * 110}")
                print(f"  {'ID':<7} {'Status':<6} {'User':<8} {'Expected':<25} {'Actual':<10} Description")
                print(f"  {'─'*6} {'─'*5} {'─'*7} {'─'*24} {'─'*9} {'─'*50}")

            status = "PASS" if r["passed"] else "FAIL"
            marker = "  " if r["passed"] else ">>"
            print(f"{marker}{r['test_id']:<7} {status:<6} {r['user']:<8} {r['expected']:<25} {r['actual']:<10} {r['description']}")
            if not r["passed"] and r["detail"]:
                detail = r["detail"][:90].replace("\n", " ")
                print(f"         Detail: {detail}")

        # Summary
        print(f"\n{'=' * 110}")
        print(f"SUMMARY: {self.stats['total']} tests | "
              f"{self.stats['pass']} PASSED | "
              f"{self.stats['fail']} FAILED")

        # Categorize failures
        findings = [r for r in self.results if not r["passed"]]
        if findings:
            print(f"\nFINDINGS ({len(findings)}):")
            for r in findings:
                print(f"  [{r['test_id']}] {r['description']} ({r['user']}): "
                      f"expected {r['expected']}, got {r['actual']}")
        else:
            print("\nALL TESTS PASSED")
        print("=" * 110)

    def generate_markdown_report(self):
        """Generate markdown report content."""
        lines = []
        lines.append("# Superset Role Permission Test Results")
        lines.append("")
        lines.append("**Date:** 2026-03-03")
        lines.append(f"**Total Tests:** {self.stats['total']}")
        lines.append(f"**Passed:** {self.stats['pass']}")
        lines.append(f"**Failed:** {self.stats['fail']}")
        lines.append("")

        if self.stats["fail"] == 0:
            lines.append("**Result: ALL TESTS PASSED**")
        else:
            lines.append(f"**Result: {self.stats['fail']} FINDING(S) DETECTED**")
        lines.append("")

        lines.append("## Test Environment")
        lines.append("")
        lines.append("| Parameter | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Dashboard Published+Owned | ID {DASHBOARD_PUBLISHED_OWNED} |")
        lines.append(f"| Dashboard Published+NotOwned | ID {DASHBOARD_PUBLISHED_NOT_OWNED} |")
        lines.append(f"| Dashboard Draft+Owned | ID {DASHBOARD_DRAFT_OWNED} |")
        lines.append(f"| Dashboard Draft+NotOwned | ID {DASHBOARD_DRAFT_NOT_OWNED} |")
        lines.append(f"| Chart Owned | ID {CHART_OWNED} |")
        lines.append(f"| Chart NotOwned | ID {CHART_NOT_OWNED} |")
        lines.append(f"| Dataset | ID {DATASET_ID} |")
        lines.append(f"| Database | ID {DATABASE_ID} |")
        lines.append("")

        lines.append("## Test Users")
        lines.append("")
        lines.append("| User | Username | Role |")
        lines.append("|------|----------|------|")
        lines.append("| Viewer | test-viewer | Sublime Starter |")
        lines.append("| Owner | test-owner | Sublime User Management |")
        lines.append("")

        lines.append("## Detailed Results")
        lines.append("")

        current_category = None
        for i, r in enumerate(self.results):
            if r["category"] != current_category:
                current_category = r["category"]
                lines.append(f"### {current_category}")
                lines.append("")
                lines.append("| ID | Status | User | Expected | Actual | Description |")
                lines.append("|:---|:------:|:-----|:---------|:-------|:------------|")

            status = "PASS" if r["passed"] else "**FAIL**"
            lines.append(f"| {r['test_id']} | {status} | {r['user']} | {r['expected']} | {r['actual']} | {r['description']} |")

            next_cat = self.results[i + 1]["category"] if i + 1 < len(self.results) else None
            if r["category"] != next_cat:
                lines.append("")

        # Findings section
        findings = [r for r in self.results if not r["passed"]]
        if findings:
            lines.append("## Findings")
            lines.append("")
            lines.append("The following tests revealed unexpected behavior:")
            lines.append("")
            for r in findings:
                lines.append(f"### {r['test_id']} - {r['description']} ({r['user']})")
                lines.append(f"- **Expected:** {r['expected']}")
                lines.append(f"- **Actual:** {r['actual']}")
                if r["detail"]:
                    lines.append(f"- **Detail:** `{r['detail'][:200]}`")
                lines.append("")

        return "\n".join(lines)


def main():
    runner = TestRunner()

    print("=" * 60)
    print("SUPERSET ROLE PERMISSION TESTING")
    print("=" * 60)

    # Authenticate
    print("\nAuthenticating...")
    runner.login_admin()
    runner.login("viewer")
    runner.login("owner")
    print("  All users authenticated.")

    # Auto-detect IDs
    print("\nDetecting object IDs...")
    runner.detect_ids()

    # Run all test categories
    runner.test_dashboards()
    runner.test_dashboard_visibility()
    runner.test_datasets()
    runner.test_charts()
    runner.test_sqllab()
    runner.test_tags()
    runner.test_databases()

    # Print results
    runner.print_report()

    # Generate markdown report
    report = runner.generate_markdown_report()
    with open("/tmp/test-role-results.md", "w") as f:
        f.write(report)
    print(f"\nMarkdown report saved to /tmp/test-role-results.md")

    # Cleanup test objects
    runner.cleanup()

    return 0 if runner.stats["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
