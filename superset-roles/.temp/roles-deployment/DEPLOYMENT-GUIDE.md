# Deploying Sublime Roles to a New Superset Instance

Step-by-step guide for reproducing the tested **Sublime Starter** and **Sublime User Management** roles on any Apache Superset instance.

---

## Prerequisites

- Target Superset instance is running and accessible
- Admin credentials for the target instance
- Shell access to the target Superset container (or host if running natively)
- The target instance uses **SQLite** metadata database (default) or **PostgreSQL** (requires script adaptation — see Section 6)

## Artifacts to Deploy

All files are in `superset/config/role-backups/`:

| File | Purpose |
|------|---------|
| `sublime-roles-backup.json` | Role definitions with 192 permission mappings (72 + 120) |
| `restore-roles.py` | Restore script that creates roles from the JSON backup |
| `superset-role-permissions-report.md` | Human-readable permission matrix (reference) |
| `test-role-permissions.py` | Automated validation script (65 tests) |

---

## Step 1: Prepare the Backup JSON for the Target Environment

The backup JSON contains **datasource-specific permissions** that reference your source environment's database, schema, and dataset names. These must match the target.

### 1.1 Identify datasource-specific entries

Open `sublime-roles-backup.json` and search for these permission types:

```
"permission": "schema_access"
"permission": "datasource_access"
```

In the source environment, these look like:

```json
{"permission": "schema_access",    "view_menu": "[PostgreSQL].[playground].[nyc_taxi]"}
{"permission": "datasource_access", "view_menu": "[PostgreSQL].[trips_by_hour](id:1)"}
{"permission": "datasource_access", "view_menu": "[PostgreSQL].[trips_by_borough](id:2)"}
{"permission": "datasource_access", "view_menu": "[PostgreSQL].[payment_type_breakdown](id:3)"}
{"permission": "datasource_access", "view_menu": "[PostgreSQL].[daily_trip_summary](id:4)"}
```

### 1.2 Update to match the target environment

Replace the `view_menu` values to match the target Superset's:

| Component | Format | How to find on target |
|-----------|--------|----------------------|
| Database name | `[DatabaseName]` | Superset UI > Settings > Database Connections |
| Database + Schema | `[DatabaseName].[db_name].[schema_name]` | SQL Lab > schema dropdown |
| Dataset | `[DatabaseName].[dataset_name](id:N)` | Superset API: `GET /api/v1/dataset/` |

**Example** — if the target environment has a database named "Production" with schema "analytics":

```json
// Before (source)
{"permission": "schema_access", "view_menu": "[PostgreSQL].[playground].[nyc_taxi]"}

// After (target)
{"permission": "schema_access", "view_menu": "[Production].[prod_db].[analytics]"}
```

### 1.3 What happens if you skip this step?

The restore script will **skip** any permission it cannot match by name. You'll see output like:

```
Skipped (not found in target instance):
  - datasource_access on [PostgreSQL].[trips_by_hour](id:1)
  - schema_access on [PostgreSQL].[playground].[nyc_taxi]
```

The roles will still be created with all non-datasource permissions (menu access, read/write capabilities, etc.), but users won't be able to access any specific datasets until the datasource permissions are added manually.

---

## Step 2: Copy Files to the Target Container

```bash
# Replace <CONTAINER> with your Superset container name or ID
docker cp superset/config/role-backups/sublime-roles-backup.json <CONTAINER>:/app/
docker cp superset/config/role-backups/restore-roles.py <CONTAINER>:/app/
```

For non-Docker deployments (e.g., pip-installed Superset):

```bash
cp superset/config/role-backups/sublime-roles-backup.json /path/to/superset/
cp superset/config/role-backups/restore-roles.py /path/to/superset/
```

---

## Step 3: Run the Restore Script

### 3.1 Docker deployment (SQLite metadata DB)

```bash
docker exec <CONTAINER> python3 /app/restore-roles.py
```

### 3.2 Native deployment (SQLite metadata DB)

```bash
cd /path/to/superset
python3 restore-roles.py
```

### 3.3 Expected output

```
'Sublime Starter': restored 72/72 permissions
'Sublime User Management': restored 120/120 permissions

Restore complete.
```

Or with missing datasource permissions:

```
'Sublime Starter': restored 65/72 permissions
  Skipped (not found in target instance):
    - datasource_access on [PostgreSQL].[trips_by_hour](id:1)
    - datasource_access on [PostgreSQL].[trips_by_borough](id:2)
    - ...
'Sublime User Management': restored 113/120 permissions
  Skipped (not found in target instance):
    - datasource_access on [PostgreSQL].[trips_by_hour](id:1)
    - ...

Restore complete.
```

---

## Step 4: Add Datasource Permissions (if skipped)

If datasource-specific permissions were skipped, add them manually via the Superset Admin UI:

1. Navigate to **Settings > List Roles**
2. Click **Edit** on "Sublime Starter"
3. In the permissions multi-select, search for and add:
   - `datasource_access on [YourDB].[dataset_name](id:N)` — for each dataset users need access to
   - `schema_access on [YourDB].[db_name].[schema_name]` — for the schema
4. Repeat for "Sublime User Management"
5. Click **Save**

**Alternatively, via API:**

```bash
# Get the permission_view IDs for your datasources
docker exec <CONTAINER> python3 -c "
import sqlite3
conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()
c.execute('''
    SELECT pv.id, p.name, vm.name
    FROM ab_permission_view pv
    JOIN ab_permission p ON pv.permission_id = p.id
    JOIN ab_view_menu vm ON pv.view_menu_id = vm.id
    WHERE p.name IN ('datasource_access', 'schema_access')
    ORDER BY vm.name
''')
for r in c.fetchall():
    print(f'  ID={r[0]}: {r[1]} on {r[2]}')
conn.close()
"
```

Then add the missing permissions to each role:

```bash
docker exec <CONTAINER> python3 -c "
import sqlite3
conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()

# Replace these IDs with the actual permission_view IDs from the query above
ROLE_ID_STARTER = 6  # or whatever ID was assigned
ROLE_ID_OWNER = 7
PERMISSION_VIEW_IDS = [<id1>, <id2>, ...]  # from the query above

for pv_id in PERMISSION_VIEW_IDS:
    for role_id in [ROLE_ID_STARTER, ROLE_ID_OWNER]:
        c.execute('INSERT OR IGNORE INTO ab_permission_view_role (permission_view_id, role_id) VALUES (?, ?)',
                  (pv_id, role_id))

conn.commit()
conn.close()
print('Datasource permissions added.')
"
```

---

## Step 5: Create Users and Assign Roles

```bash
# Create a viewer user
docker exec <CONTAINER> superset fab create-user \
  --username viewer1 \
  --firstname First \
  --lastname Last \
  --email viewer1@company.com \
  --password '<secure-password>' \
  --role "Sublime Starter"

# Create an owner user
docker exec <CONTAINER> superset fab create-user \
  --username owner1 \
  --firstname First \
  --lastname Last \
  --email owner1@company.com \
  --password '<secure-password>' \
  --role "Sublime User Management"
```

For existing users, assign roles via **Settings > List Users > Edit**.

---

## Step 6: Validate the Deployment

### 6.1 Quick smoke test

```bash
docker exec <CONTAINER> python3 -c "
import sqlite3
conn = sqlite3.connect('/app/superset_home/superset.db')
c = conn.cursor()
for role_name in ['Sublime Starter', 'Sublime User Management']:
    c.execute('''
        SELECT COUNT(*) FROM ab_permission_view_role pvr
        JOIN ab_role r ON pvr.role_id = r.id
        WHERE r.name = ?
    ''', (role_name,))
    count = c.fetchone()[0]
    print(f'{role_name}: {count} permissions')
conn.close()
"
```

Expected: `Sublime Starter: 72 permissions`, `Sublime User Management: 120 permissions` (or fewer if datasource permissions were skipped).

### 6.2 Full automated test (optional)

Copy and run the test script. **Requires test users and test dashboards** (see test script header for setup):

```bash
docker cp superset/config/role-backups/test-role-permissions.py <CONTAINER>:/app/
docker exec <CONTAINER> python3 /app/test-role-permissions.py
```

### 6.3 Manual UI verification

Log in as each user and verify:

| Check | Viewer | Owner |
|-------|:------:|:-----:|
| Top nav shows SQL menu | No | Yes |
| Dashboard list shows only Published | Yes | Yes + owned Drafts |
| Can edit owned dashboard | No | Yes |
| Can create new chart | No | Yes |
| SQL Lab accessible | No | Yes |

---

## Adaptation for PostgreSQL Metadata Database

If the target Superset uses PostgreSQL (not SQLite) for its metadata database, modify `restore-roles.py`:

```python
# Replace this line:
conn = sqlite3.connect("/app/superset_home/superset.db")

# With:
import psycopg2
conn = psycopg2.connect(
    host="<metadata_db_host>",
    port=5432,
    dbname="<superset_metadata_db>",
    user="<username>",
    password="<password>"
)
```

The SQL queries in the script use standard SQL and work with both SQLite and PostgreSQL. The only change needed is the connection method. You'll also need `psycopg2` installed in the Superset environment (`pip install psycopg2-binary`).

For the metadata DB connection string, check the target's `superset_config.py`:

```python
# Look for:
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@host:5432/superset"
```

---

## Adaptation for Superset with Redis-based Sessions

The restore script operates on the metadata database directly, not on sessions or cache. It works identically regardless of whether the target uses Redis, Memcached, or filesystem sessions.

---

## Known Limitations

### Delete permissions cannot be separated from edit

Superset's `can_write` permission bundles create + update + delete for owned objects. The Sublime User Management role grants `can_write Dashboard` and `can_write Chart`, which means owners **can delete** their own dashboards and charts via the API.

This was documented as **Finding 1 and Finding 3** in the test results. Mitigation options:

1. **Custom Security Manager** — subclass `SupersetSecurityManager` and override `can_access` to intercept delete operations
2. **Frontend restriction** — hide delete buttons via custom CSS or Superset plugin
3. **Organizational policy** — instruct users not to delete from UI; handle deletion via automation

### Role IDs may differ

The restore script uses hardcoded role IDs (6 and 7) from the source environment. If those IDs are already taken on the target instance, the script will:
- If IDs 6/7 exist with different names: update the names to "Sublime Starter" / "Sublime User Management"
- If IDs 6/7 don't exist: create new roles with those IDs

If you need different role IDs, edit the `"id"` fields in `sublime-roles-backup.json` before running restore.

### Re-running is safe

The restore script is **idempotent** — it clears existing permissions on the target roles before restoring. Running it multiple times produces the same result.
