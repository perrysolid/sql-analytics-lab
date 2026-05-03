"""
Restore Superset roles from JSON backup.

Usage:
  # Copy into container and run:
  docker cp superset/config/role-backups/restore-roles.py <SUPERSET_CONTAINER>:/app/
  docker cp superset/config/role-backups/sublime-roles-backup.json <SUPERSET_CONTAINER>:/app/
  docker exec <SUPERSET_CONTAINER> python3 /app/restore-roles.py

  # Or run directly from host:
  docker exec <SUPERSET_CONTAINER> python3 -c "
  import json, sqlite3
  exec(open('/app/restore-roles.py').read())
  "
"""
import json
import sqlite3
import os

BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sublime-roles-backup.json")

def restore_roles():
    with open(BACKUP_FILE, "r") as f:
        backup = json.load(f)

    conn = sqlite3.connect("/app/superset_home/superset.db")
    c = conn.cursor()

    for role in backup["roles"]:
        role_id = role["id"]
        role_name = role["name"]

        # Verify role exists
        c.execute("SELECT id, name FROM ab_role WHERE id = ?", (role_id,))
        existing = c.fetchone()

        if not existing:
            print(f"Role ID {role_id} not found. Creating '{role_name}'...")
            c.execute("INSERT INTO ab_role (id, name) VALUES (?, ?)", (role_id, role_name))
        elif existing[1] != role_name:
            print(f"Warning: Role ID {role_id} exists as '{existing[1]}', expected '{role_name}'. Updating name...")
            c.execute("UPDATE ab_role SET name = ? WHERE id = ?", (role_name, role_id))

        # Clear existing permissions
        c.execute("DELETE FROM ab_permission_view_role WHERE role_id = ?", (role_id,))

        # Restore permissions by matching permission+view_menu names (portable across instances)
        restored = 0
        skipped = []
        for perm in role["permissions"]:
            c.execute("""
                SELECT pvr.id FROM ab_permission_view pvr
                JOIN ab_permission p ON pvr.permission_id = p.id
                JOIN ab_view_menu vm ON pvr.view_menu_id = vm.id
                WHERE p.name = ? AND vm.name = ?
            """, (perm["permission"], perm["view_menu"]))
            row = c.fetchone()

            if row:
                c.execute(
                    "INSERT INTO ab_permission_view_role (permission_view_id, role_id) VALUES (?, ?)",
                    (row[0], role_id),
                )
                restored += 1
            else:
                skipped.append(f"{perm['permission']} on {perm['view_menu']}")

        print(f"'{role_name}': restored {restored}/{len(role['permissions'])} permissions")
        if skipped:
            print(f"  Skipped (not found in target instance):")
            for s in skipped:
                print(f"    - {s}")

    conn.commit()
    conn.close()
    print("\nRestore complete.")


if __name__ == "__main__":
    restore_roles()
