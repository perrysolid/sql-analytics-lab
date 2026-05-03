# Sublime Roles — Research & Testing Home

This directory contains all artifacts from the research, testing, and validation of two custom Apache Superset roles: **Sublime Starter** (viewer) and **Sublime User Management** (owner).

---

## Quick Links

| What you need | Where to go |
|---------------|-------------|
| Full testing report with screenshots | [report/superset-role-testing-report.md](report/superset-role-testing-report.md) |
| Deploy these roles to another Superset instance | [roles-deployment/DEPLOYMENT-GUIDE.md](roles-deployment/DEPLOYMENT-GUIDE.md) |

---

## Directory Structure

```
.temp/
├── README.md                          <-- You are here
├── report/                            <-- Testing report & visual evidence
│   ├── superset-role-testing-report.md
│   ├── superset-role-test-results.md
│   └── screenshots/                   (26 PNG files)
└── roles-deployment/                  <-- Portable deployment kit
    ├── DEPLOYMENT-GUIDE.md
    ├── sublime-roles-backup.json
    ├── restore-roles.py
    └── test-role-permissions.py
```

---

## `report/` — Testing Report & Visual Evidence

Contains the comprehensive testing report documenting 65 automated API tests across 7 permission categories, plus visual UI screenshots captured via Playwright.

| File | Description |
|------|-------------|
| **[superset-role-testing-report.md](report/superset-role-testing-report.md)** | **Main report.** Includes: table of contents, complete permission listings for both roles (72 + 120 permissions), test environment setup, detailed pass/fail results for all 65 tests, 3 findings with root cause analysis, 16 embedded screenshots showing UI differences between Viewer, Owner, and Admin perspectives, and reproduction instructions. |
| [superset-role-test-results.md](report/superset-role-test-results.md) | Condensed test results — raw pass/fail table with finding summaries. Useful as a quick reference without the full report context. |
| `screenshots/` | 26 PNG screenshots captured via headless Chromium (Playwright). Organized by user perspective: `viewer-*`, `owner-*`, `admin-*`. Each filename follows the pattern `{user}-{sequence}-{page}.png`. |

### Screenshot Inventory

| File | Shows |
|------|-------|
| `viewer-01-home.png` | Viewer home — no SQL menu, no + button |
| `viewer-02-dashboard-list.png` | Viewer sees 2 Published dashboards only |
| `viewer-03-dashboard-revenue.png` | Viewer dashboard view — read-only, no edit controls |
| `viewer-04-dashboard-trip-patterns.png` | Viewer dashboard view — no Edit button, no Published badge |
| `viewer-05-no-edit-button.png` | Confirms no edit button on owned dashboard |
| `viewer-06-chart-list.png` | Chart list — no + Chart button |
| `viewer-07-dataset-list.png` | Dataset list — read-only |
| `viewer-08-sqllab.png` | SQL Lab blocked — "Access is Denied" |
| `viewer-09-database-list.png` | Database list view |
| `viewer-10-no-create-menu.png` | No create menu available |
| `owner-01-home.png` | Owner home — SQL menu and + button visible |
| `owner-02-dashboard-list.png` | Owner sees 3 dashboards (incl. owned Draft) |
| `owner-03-dashboard-revenue.png` | Owner on non-owned dashboard — SQL + but no Edit |
| `owner-04-dashboard-trip-patterns.png` | Owner on owned dashboard — Edit button + Published badge |
| `owner-05-no-edit-button.png` | Non-owned dashboard — no edit button |
| `owner-06-chart-list.png` | Chart list with + Chart button |
| `owner-07-dataset-list.png` | Dataset list with action options |
| `owner-08-sqllab.png` | SQL Lab accessible — full query editor |
| `owner-09-database-list.png` | Database list view |
| `owner-10-no-create-menu.png` | Create menu state |
| `admin-01-dashboard-list-all.png` | Admin sees all 4 dashboards (Published + Drafts) |
| `admin-02-users-list.png` | User management — test users with role assignments |
| `admin-03-roles-list.png` | Role list — Sublime Starter and Sublime User Management |
| `admin-04-sublime-starter-role.png` | Sublime Starter role configuration (72 permissions) |
| `admin-05-sublime-user-mgmt-role.png` | Sublime User Management role configuration (120 permissions) |

---

## `roles-deployment/` — Portable Deployment Kit

Contains everything needed to reproduce the tested Sublime Starter and Sublime User Management roles on any Apache Superset instance.

| File | Description |
|------|-------------|
| **[DEPLOYMENT-GUIDE.md](roles-deployment/DEPLOYMENT-GUIDE.md)** | **Step-by-step deployment instructions.** Covers: preparing the backup JSON for a target environment, updating datasource-specific permissions, copying files to the Superset container, running the restore script, adding missing datasource permissions, creating users, and validating the deployment. Includes adaptation notes for PostgreSQL metadata databases and known limitations. |
| [sublime-roles-backup.json](roles-deployment/sublime-roles-backup.json) | JSON backup of both roles with all 192 permission mappings (72 + 120). Each permission is stored as a `permission` + `view_menu` name pair for cross-instance portability. Contains 5 datasource-specific entries that must be updated for the target environment. |
| [restore-roles.py](roles-deployment/restore-roles.py) | Python restore script. Reads `sublime-roles-backup.json`, creates or updates roles in Superset's metadata database, and maps permissions by name (not ID). Idempotent — safe to re-run. Works with SQLite (default) metadata database; see DEPLOYMENT-GUIDE.md for PostgreSQL adaptation. |
| [test-role-permissions.py](roles-deployment/test-role-permissions.py) | Automated validation script (65 tests). Authenticates via JWT, tests all permission boundaries across 7 categories (Dashboards, Charts, Datasets, SQL Lab, Tags, Databases, Dashboard Visibility). Non-destructive — uses temporary objects for delete tests. Auto-detects object IDs. Run after deployment to verify roles work correctly. |

### Deployment Quick Start

```bash
# 1. Copy files into the Superset container
docker cp roles-deployment/sublime-roles-backup.json <CONTAINER>:/app/
docker cp roles-deployment/restore-roles.py <CONTAINER>:/app/

# 2. Run the restore script
docker exec <CONTAINER> python3 /app/restore-roles.py

# 3. (Optional) Validate with automated tests
docker cp roles-deployment/test-role-permissions.py <CONTAINER>:/app/
docker exec <CONTAINER> python3 /app/test-role-permissions.py
```

For full instructions including datasource permission adaptation, see **[DEPLOYMENT-GUIDE.md](roles-deployment/DEPLOYMENT-GUIDE.md)**.

---

## Key Results

- **65 API tests** executed: **62 passed**, **3 findings**
- **Finding 1 & 3 (High):** Superset's `can_write` permission bundles delete with edit — owners can delete their own dashboards and charts. This is a Superset platform limitation, not a configuration error.
- **Finding 2 (Medium):** Dataset duplicate API returns HTTP 500 — server-side issue, permission is correctly assigned.
- All other permission boundaries work as designed.

---

## Option 2 — Admin-Like Dataset Permissions (Separate Research)

A second research track explored giving the owner role **admin-like access to datasets** (edit/delete/create ANY dataset, not just owned ones) while keeping dashboard/chart ownership restrictions unchanged.

**Key finding:** Superset hardcodes ownership checks — standard permissions alone cannot bypass them. A **Custom Security Manager** is required.

**Result:** 70 tests, 68 passed, all 15 dataset-specific tests PASSED with the custom security manager.

**Full artifacts:** [`../.temp-02/`](../.temp-02/README.md)

| What | Option 1 (this dir) | Option 2 (`.temp-02/`) |
|------|---------------------|------------------------|
| Datasets | Read-only (no UI edits) | Admin-like (edit/delete/create any) |
| Custom Security Manager | Not needed | **Required** |
| Extra permissions | — | +3 (`can_write Dataset`, `can_save Datasource`, `all_datasource_access`) |
