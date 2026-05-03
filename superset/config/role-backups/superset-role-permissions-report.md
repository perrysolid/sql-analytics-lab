# Superset Role Permissions Report

**Generated:** 2026-03-02
**Superset Instance:** http://localhost:8088

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Navigation Menu Access](#navigation-menu-access)
- [Permission Matrix by Object](#permission-matrix-by-object)
  - [1. Dashboards](#1-dashboards)
  - [2. Charts](#2-charts)
  - [3. Datasets (Option 1 — Managed by Notebook)](#3-datasets-option-1--managed-by-notebook)
  - [4. Databases](#4-databases)
  - [5. SQL Lab](#5-sql-lab)
  - [6. Tags](#6-tags)
  - [7. Explore / Visualization](#7-explore--visualization)
  - [8. User & Security](#8-user--security)
  - [9. Themes](#9-themes)
- [Backup and Restore](#backup-and-restore)

---

## Overview

Two custom roles designed based on requirements document defining per-object permission model.
Datasets are managed exclusively via external tooling (Jupyter notebook) — not editable from UI (Option 1).
Dashboard deletion is excluded from both roles — handled by external automation ("maszynka").

| Role | ID | Purpose | Permission Count |
|------|----|---------|-----------------|
| Sublime Starter | 6 | Viewer — read-only access with copy/save-as | 72 |
| Sublime User Management | 7 | Owner — full management of owned objects + SQL Lab | 120 |

---

## Design Decisions

1. **Dataset management (Option 1):** Neither role has `can_write Dataset`. All dataset changes are performed by Jupyter notebook automation. This avoids permission complexity around dataset ownership.

2. **Dashboard deletion excluded:** Both roles lack delete permissions for dashboards. Deletion is handled by the external "maszynka" (Jupyter notebook), providing a controlled cleanup process.

3. **Chart deletion excluded:** Neither role can delete charts from UI. Charts are managed through the dashboard lifecycle.

4. **Owner-scoped editing:** Superset enforces that `can_write Dashboard` only allows editing dashboards where the user is listed as an owner. Non-owned dashboards remain read-only even for the Owner role.

5. **SQL Lab for Owner only:** SQL Lab provides direct database query access. Restricted to Owner role to prevent uncontrolled queries against production data by viewer users.

6. **Datasource-level access control:** Both roles use explicit `datasource_access` grants per dataset rather than broad `all_datasource_access`. New datasets require permission updates.

---

## Navigation Menu Access

| Menu Item | Sublime Starter | Sublime User Management |
|-----------|:-:|:-:|
| Home | Y | Y |
| Dashboards | Y | Y |
| Charts | Y | Y |
| Datasets | Y | Y |
| Databases | Y | Y |
| Data | Y | Y |
| Tags | Y | Y |
| SQL Lab | - | Y |
| SQL Editor | - | Y |
| Saved Queries | - | Y |
| Query Search | - | Y |
| Action Log | - | Y |
| Themes | - | Y |
| Plugins | - | - |

---

## Permission Matrix by Object

### 1. Dashboards

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View dashboards | Y | Y | `can_read Dashboard` |
| Copy / Save as | Y | Y | Via `can_explore`, `can_slice` |
| Export / Download | Y | Y | `can_export Dashboard` |
| Edit (when owner) | - | Y | `can_write Dashboard` |
| Assign owners | - | Y | Via `can_write Dashboard` |
| Publish / Draft toggle | - | Y | Via `can_write Dashboard` |
| Tag dashboards | - | Y | `can_tag Dashboard` |
| Set/Delete embedded | - | Y | `can_set_embedded`, `can_delete_embedded` |
| Delete dashboard | - | - | Blocked on both roles; handled by notebook |
| Drill into data | Y | Y | `can_drill Dashboard` |
| View chart as table | Y | Y | `can_view_chart_as_table Dashboard` |
| View underlying query | Y | Y | `can_view_query Dashboard` |
| Cache screenshot | Y | Y | `can_cache_dashboard_screenshot Dashboard` |
| Share dashboard link | Y | Y | `can_share_dashboard Superset` |
| Filter state (read/write) | Y | Y | `DashboardFilterStateRestApi` |
| Permalink (read/write) | Y | Y | `DashboardPermalinkRestApi` |

### 2. Charts

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View charts | Y | Y | `can_read Chart` |
| Export charts | Y | Y | `can_export Chart` |
| Create new charts | - | Y | `can_write Chart` |
| Save as copy | Y | Y | Via explore + slice |
| Edit (when owner) | - | Y | `can_write Chart` |
| Tag charts | - | Y | `can_tag Chart` |
| Warm up cache | - | Y | `can_warm_up_cache Chart` |
| Share chart link | Y | Y | `can_share_chart Superset` |
| Delete charts | - | - | Blocked on both roles |

### 3. Datasets (Option 1 — Managed by Notebook)

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View datasets | Y | Y | `can_read Dataset` |
| Drill info | Y | Y | `can_get_drill_info Dataset` |
| Edit datasets | - | - | Blocked — Option 1 |
| Create datasets | - | - | Blocked — Option 1 |
| Duplicate datasets | - | Y | `can_duplicate Dataset` |
| Export datasets | - | Y | `can_export Dataset` |
| Get/Create dataset ref | - | Y | `can_get_or_create_dataset` (for chart creation) |
| Warm up cache | - | Y | `can_warm_up_cache Dataset` |
| View column values | - | Y | `can_get_column_values Datasource` |
| View samples | - | Y | `can_samples Datasource` |

### 4. Databases

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View databases | Y | Y | `can_read Database` |
| Edit databases | - | - | Blocked on both roles |
| Upload to database | - | - | Blocked on both roles |

### 5. SQL Lab

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| Access SQL Lab | - | Y | `can_sqllab Superset` |
| Execute queries | - | Y | `can_execute_sql_query SQLLab` |
| Format SQL | - | Y | `can_format_sql SQLLab` |
| Export CSV | - | Y | `can_export_csv SQLLab` |
| Estimate query cost | - | Y | `can_estimate_query_cost SQLLab` |
| View results | - | Y | `can_get_results SQLLab` |
| Query history | - | Y | `can_sqllab_history Superset` |
| Saved queries (read) | Y | Y | `can_read SavedQuery` |
| Saved queries (write) | - | Y | `can_write SavedQuery` |
| Saved queries (export) | - | Y | `can_export SavedQuery` |
| Tab state management | - | Y | `TabStateView` (activate, get, post, put, delete) |
| Table schema browser | - | Y | `TableSchemaView` (post, expanded, delete) |
| SQL Lab permalink | - | Y | `SqlLabPermalinkRestApi` |

### 6. Tags

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View tags | Y | Y | `can_read Tag`, `can_list Tags` |
| Create/Edit tags | - | Y | `can_write Tag`, `can_bulk_create Tag` |

### 7. Explore / Visualization

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| Explore view | Y | Y | `can_read Explore` |
| Explore JSON data | Y | Y | `can_explore_json Superset` |
| Form data (read/write) | Y | Y | `ExploreFormDataRestApi` |
| Permalink (read/write) | Y | Y | `ExplorePermalinkRestApi` |
| Fetch datasource metadata | Y | Y | `can_fetch_datasource_metadata Superset` |
| CSV export | Y | Y | `can_csv Superset` |

### 8. User & Security

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View own user info | Y | Y | `can_userinfo UserDBModelView` |
| Reset own password | Y | Y | `resetmypassword`, `ResetMyPasswordView` |
| Read security info | Y | Y | `can_read security`, `SecurityRestApi` |
| Read user info | Y | Y | `can_read user` |
| Write current user | - | Y | `can_write CurrentUserRestApi` |
| View audit log | - | Y | `can_read Log`, `menu_access Action Log` |
| Row level security (read) | Y | Y | `can_read RowLevelSecurity` |

### 9. Themes

| Capability | Sublime Starter | Sublime User Management | Notes |
|-----------|:-:|:-:|-------|
| View themes | Y | Y | `can_read Theme` |
| Edit themes | - | Y | `can_write Theme` |
| Export themes | - | Y | `can_export Theme` |

---

## Backup and Restore

Role configurations are stored as artifacts in `superset/config/role-backups/`:

| File | Purpose |
|------|---------|
| `sublime-roles-backup.json` | JSON snapshot of both roles with all permission mappings |
| `restore-roles.py` | Python script that restores roles from the JSON backup into Superset |

### Backup contents

`sublime-roles-backup.json` contains for each role:
- Role ID and name
- Full list of permissions, each with `permission_view_id`, `permission` name, and `view_menu` name
- Export timestamp and source instance URL

### Restoring roles

After a fresh `docker-compose down -v && docker-compose up -d --build` or on a new Superset instance:

```bash
# 1. Copy backup files into the running container
docker cp superset/config/role-backups/restore-roles.py <SUPERSET_CONTAINER>:/app/
docker cp superset/config/role-backups/sublime-roles-backup.json <SUPERSET_CONTAINER>:/app/

# 2. Run the restore script
docker exec <SUPERSET_CONTAINER> python3 /app/restore-roles.py
```

The script will:
1. Create roles if they don't exist, or update their names if IDs already exist
2. Clear any existing permissions on each role
3. Re-insert all permissions by matching `permission` + `view_menu` names (not IDs)
4. Report how many permissions were restored and list any that were skipped

### Portability

The restore script matches permissions by **name** rather than by internal ID. This means:
- It works across different Superset instances where IDs may differ
- If the target instance is missing a permission (e.g. a datasource was not yet created), it will be skipped with a warning

### Datasource-specific permissions

The backup JSON file (`sublime-roles-backup.json`) contains permissions that reference specific database connections, schemas, and datasets. These are **project-specific** and must be updated in the JSON file to match the target Superset instance before restoring:

| Permission type | Format in `view_menu` | Example |
|----------------|----------------------|---------|
| `schema_access` | `[<DATABASE_NAME>].[<DB_NAME>].[<SCHEMA_NAME>]` | `[PostgreSQL].[playground].[nyc_taxi]` |
| `datasource_access` | `[<DATABASE_NAME>].[<DATASET_NAME>](id:<DATASET_ID>)` | `[PostgreSQL].[trips_by_hour](id:1)` |

Before restoring roles on a different project:
1. Open `sublime-roles-backup.json`
2. Find all entries where `permission` is `datasource_access` or `schema_access`
3. Update the `view_menu` values to match the database name, schema, and dataset names in your Superset instance
4. The corresponding datasets and database connections must already exist in the target Superset before restore

### Creating a new backup

To export the current role state as a new backup:

```bash
docker exec <SUPERSET_CONTAINER> python3 -c "
import sqlite3, json
from datetime import datetime

conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()

backup = {
    'exported_at': datetime.utcnow().isoformat() + 'Z',
    'superset_instance': 'http://localhost:8088',
    'roles': []
}

for role_id in [6, 7]:
    c.execute('SELECT id, name FROM ab_role WHERE id = ?', (role_id,))
    role_row = c.fetchone()
    c.execute('''
        SELECT pvr.id, p.name, vm.name
        FROM ab_permission_view_role pvr_role
        JOIN ab_permission_view pvr ON pvr_role.permission_view_id = pvr.id
        JOIN ab_permission p ON pvr.permission_id = p.id
        JOIN ab_view_menu vm ON pvr.view_menu_id = vm.id
        WHERE pvr_role.role_id = ?
        ORDER BY vm.name, p.name
    ''', (role_id,))
    permissions = [{'permission_view_id': r[0], 'permission': r[1], 'view_menu': r[2]} for r in c.fetchall()]
    backup['roles'].append({'id': role_row[0], 'name': role_row[1], 'permission_count': len(permissions), 'permissions': permissions})

conn.close()
print(json.dumps(backup, indent=2))
" > superset/config/role-backups/sublime-roles-backup.json
```
