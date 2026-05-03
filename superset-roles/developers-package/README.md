# Sublime User Maintainer — Developer Package

Role definition and ingestion script for adding the **Sublime User Maintainer** role to any Apache Superset instance.

---

## Contents

| File | Purpose |
|------|---------|
| `sublime-user-maintainer.json` | Role definition — 120 permissions matched by name |
| `add-role.py` | Python ingestion script — supports SQLite and PostgreSQL metadata DBs |
| `README.md` | This file |

---

## What the role provides

**Sublime User Maintainer** is a content-creator role with SQL Lab access and ownership-scoped editing. Users with this role can:

- Create, edit, and publish **own** dashboards and charts
- Copy (Save as) any dashboard
- Access SQL Lab (execute queries, save queries, export CSV)
- View all published dashboards (cannot see others' drafts)
- Export dashboards, charts, and datasets
- Tag and organize objects
- Duplicate datasets

Users with this role **cannot**:
- Edit or delete dashboards/charts they don't own
- Edit or delete datasets (read-only — managed via external automation)
- Manage users, roles, or security settings
- Create or modify database connections

---

## Deployment

### 1. Copy files into the Superset container

```bash
docker cp sublime-user-maintainer.json <CONTAINER>:/app/
docker cp add-role.py <CONTAINER>:/app/
```

### 2. Run the ingestion script

**SQLite metadata DB (default for development):**
```bash
docker exec <CONTAINER> python3 /app/add-role.py
```

**PostgreSQL metadata DB (production):**
```bash
docker exec <CONTAINER> python3 /app/add-role.py --pg \
    --host <METADATA_DB_HOST> \
    --port 5432 \
    --dbname <METADATA_DB_NAME> \
    --user <METADATA_DB_USER> \
    --password <METADATA_DB_PASS>
```

For the PostgreSQL connection string, check the target `superset_config.py`:
```python
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@host:5432/superset"
```

### 3. Assign the role to users

```bash
docker exec <CONTAINER> superset fab create-user \
    --username <USERNAME> \
    --firstname <FIRST> \
    --lastname <LAST> \
    --email <EMAIL> \
    --password <PASSWORD> \
    --role "Sublime User Maintainer"
```

Or assign via **Settings > List Users > Edit** in the Superset UI.

### 4. Verify

```bash
docker exec <CONTAINER> python3 -c "
import sqlite3
conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()
c.execute('''
    SELECT COUNT(*) FROM ab_permission_view_role pvr
    JOIN ab_role r ON pvr.role_id = r.id
    WHERE r.name = \"Sublime User Maintainer\"
''')
print(f'Sublime User Maintainer: {c.fetchone()[0]} permissions')
conn.close()
"
```

Expected: `Sublime User Maintainer: 120 permissions` (or fewer if datasource permissions were skipped — see below).

---

## Datasource-specific permissions — MUST be updated for production

The JSON file contains **5 datasource-specific permissions** that reference the **local development environment** (PostgreSQL, playground database, nyc_taxi schema):

```
datasource_access on [PostgreSQL].[daily_trip_summary](id:4)
datasource_access on [PostgreSQL].[payment_type_breakdown](id:3)
schema_access     on [PostgreSQL].[playground].[nyc_taxi]
datasource_access on [PostgreSQL].[trips_by_borough](id:2)
datasource_access on [PostgreSQL].[trips_by_hour](id:1)
```

### On production Superset (GCP)

These permissions will **NOT match** because production uses different:
- **Database connection name** (not "PostgreSQL")
- **Schema/catalog path** (GCP BigQuery or Cloud SQL, not "playground.nyc_taxi")
- **Dataset names and IDs** (production tables, not NYC taxi demo data)

The script will **skip** these 5 entries and report them:

```
'Sublime User Maintainer': added 115/120 permissions
  Skipped (5 not found on target instance):
    - datasource_access on [PostgreSQL].[daily_trip_summary](id:4)
    - datasource_access on [PostgreSQL].[payment_type_breakdown](id:3)
    - schema_access on [PostgreSQL].[playground].[nyc_taxi]
    - datasource_access on [PostgreSQL].[trips_by_borough](id:2)
    - datasource_access on [PostgreSQL].[trips_by_hour](id:1)
```

### How to add production datasource permissions

After running the script, add the correct permissions manually:

1. Go to **Settings > List Roles > Edit "Sublime User Maintainer"**
2. In the permissions multi-select, search for and add:
   - `schema_access on [<GCP_DB_NAME>].[<catalog>].[<schema>]` — for each schema users need
   - `datasource_access on [<GCP_DB_NAME>].[<table_name>](id:<N>)` — for each dataset/table
3. Click **Save**

To find the correct permission names on your production instance:
```bash
docker exec <CONTAINER> python3 -c "
import sqlite3
conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()
c.execute('''
    SELECT pv.id, p.name, vm.name
    FROM ab_permission_view pv
    JOIN ab_permission p ON pv.permission_id = p.id
    JOIN ab_view_menu vm ON pv.view_menu_id = vm.id
    WHERE p.name IN (\"datasource_access\", \"schema_access\")
    ORDER BY vm.name
''')
for r in c.fetchall():
    print(f\"  ID={r[0]}: {r[1]} on {r[2]}\")
conn.close()
"
```

### Alternative: edit the JSON before ingestion

If you know the exact GCP permission names beforehand, update the 5 entries in `sublime-user-maintainer.json` before running the script:

```json
// Replace LOCAL entries:
{"permission": "schema_access", "view_menu": "[PostgreSQL].[playground].[nyc_taxi]"}

// With PRODUCTION entries (example):
{"permission": "schema_access", "view_menu": "[BigQuery].[my-gcp-project].[analytics]"}
```

---

## Re-running the script

The script is **idempotent**:
- If the role exists, it clears all permissions and re-applies from the JSON
- If the role doesn't exist, it creates it
- Running multiple times produces the same result
- Existing users assigned to the role keep their assignment

---

## Adapting the role name

If you need a different role name, edit the `"name"` field in `sublime-user-maintainer.json`:

```json
"name": "Your Custom Role Name"
```

The script uses the name to find or create the role — no code changes needed.
