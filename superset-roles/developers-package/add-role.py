#!/usr/bin/env python3
"""
Add 'Sublime User Maintainer' role to Apache Superset.

Supports both SQLite (default dev) and PostgreSQL metadata databases.
Idempotent — safe to re-run. Creates the role if missing, updates if exists.

Usage (SQLite — default):
    docker cp add-role.py <SUPERSET_CONTAINER>:/app/
    docker cp sublime-user-maintainer.json <SUPERSET_CONTAINER>:/app/
    docker exec <SUPERSET_CONTAINER> python3 /app/add-role.py

Usage (PostgreSQL metadata DB):
    docker exec <SUPERSET_CONTAINER> python3 /app/add-role.py --pg \
        --host <HOST> --port 5432 --dbname superset --user <USER> --password <PASS>

The script matches permissions by name (permission + view_menu), not by ID.
Permissions that do not exist on the target instance are skipped and reported.
This is expected for datasource-specific permissions (schema_access,
datasource_access) which reference environment-specific tables.
"""
import argparse
import json
import os
import sys

BACKUP_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sublime-user-maintainer.json",
)


def get_connection(args):
    """Return a DB-API 2.0 connection and a placeholder character ('?' or '%s')."""
    if args.pg:
        try:
            import psycopg2
        except ImportError:
            print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
            sys.exit(1)
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            dbname=args.dbname,
            user=args.user,
            password=args.password,
        )
        conn.autocommit = False
        return conn, "%s"
    else:
        import sqlite3

        db_path = args.sqlite_path
        if not os.path.exists(db_path):
            print(f"ERROR: SQLite database not found at {db_path}")
            sys.exit(1)
        return sqlite3.connect(db_path), "?"


def add_role(conn, ph, role_data):
    """Add a single role with permissions. Returns (added, skipped) counts."""
    c = conn.cursor()
    role_name = role_data["name"]

    # Find or create role by name
    c.execute(f"SELECT id FROM ab_role WHERE name = {ph}", (role_name,))
    row = c.fetchone()

    if row:
        role_id = row[0]
        print(f"Role '{role_name}' exists (ID={role_id}). Updating permissions...")
    else:
        c.execute(f"INSERT INTO ab_role (name) VALUES ({ph})", (role_name,))
        conn.commit()
        c.execute(f"SELECT id FROM ab_role WHERE name = {ph}", (role_name,))
        role_id = c.fetchone()[0]
        print(f"Role '{role_name}' created (ID={role_id}).")

    # Clear existing permissions for this role
    c.execute(
        f"DELETE FROM ab_permission_view_role WHERE role_id = {ph}", (role_id,)
    )

    added = 0
    skipped = []

    for perm in role_data["permissions"]:
        perm_name = perm["permission"]
        view_name = perm["view_menu"]

        c.execute(
            f"""
            SELECT pv.id FROM ab_permission_view pv
            JOIN ab_permission p ON pv.permission_id = p.id
            JOIN ab_view_menu vm ON pv.view_menu_id = vm.id
            WHERE p.name = {ph} AND vm.name = {ph}
            """,
            (perm_name, view_name),
        )
        row = c.fetchone()

        if row:
            c.execute(
                f"INSERT INTO ab_permission_view_role (permission_view_id, role_id) VALUES ({ph}, {ph})",
                (row[0], role_id),
            )
            added += 1
        else:
            skipped.append(f"{perm_name} on {view_name}")

    conn.commit()
    return added, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Add Sublime User Maintainer role to Superset"
    )
    parser.add_argument(
        "--pg",
        action="store_true",
        help="Use PostgreSQL instead of SQLite",
    )
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--dbname", default="superset", help="PostgreSQL database name")
    parser.add_argument("--user", default="superset", help="PostgreSQL user")
    parser.add_argument("--password", default="", help="PostgreSQL password")
    parser.add_argument(
        "--sqlite-path",
        default="/app/superset_home/superset.db",
        help="Path to SQLite metadata DB (default: /app/superset_home/superset.db)",
    )
    parser.add_argument(
        "--json",
        default=BACKUP_FILE,
        dest="json_file",
        help="Path to role JSON file",
    )
    args = parser.parse_args()

    # Load backup
    json_path = args.json_file
    if not os.path.exists(json_path):
        print(f"ERROR: JSON file not found at {json_path}")
        sys.exit(1)

    with open(json_path, "r") as f:
        backup = json.load(f)

    db_type = "PostgreSQL" if args.pg else "SQLite"
    print(f"Connecting to {db_type} metadata database...")
    conn, ph = get_connection(args)

    for role_data in backup["roles"]:
        added, skipped = add_role(conn, ph, role_data)
        total = len(role_data["permissions"])
        print(f"  '{role_data['name']}': added {added}/{total} permissions")

        if skipped:
            print(f"  Skipped ({len(skipped)} not found on target instance):")
            for s in skipped:
                print(f"    - {s}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
