# Plan: Option 2 — Admin-Like Dataset Permissions for Sublime User Management

**Date:** 2026-03-05
**Status:** Draft — awaiting approval
**Scope:** Research + simulate + test whether `Sublime User Management` role can have admin-like access to datasets (edit, delete, set owner) while keeping dashboard/chart permissions unchanged from Option 1.

---

## Background

### What Option 1 delivered (DONE)
- **Sublime Starter** (72 permissions): Read-only viewer, no SQL Lab, no edit/create
- **Sublime User Management** (120 permissions): Content creator/owner with SQL Lab, ownership-scoped edits on dashboards/charts, **no dataset editing** — all dataset management delegated to external "maszynka" (Jupyter notebook)

### What Option 2 requests (THIS PLAN)
The reviewer wants to check if `Sublime User Management` can be extended so that:
1. Users can **edit datasets they don't own** (or set themselves as owner to edit)
2. Users can **delete datasets** (admin-like capability on datasets)
3. Users can **create new datasets** from UI
4. Everything else (dashboards, charts, SQL Lab, tags) stays **exactly as Option 1**

In other words: **datasets get admin-level treatment**, dashboards/charts keep ownership-scoped restrictions.

---

## Plan

### Phase 1: Research — Superset Dataset Permission Model (no changes to Superset)

**Goal:** Understand exactly what Superset permissions control dataset CRUD and ownership, and whether non-admin roles can bypass ownership checks.

**Steps:**
1. Query the current Superset instance for all dataset-related permissions:
   ```bash
   docker exec sql-playground-superset python3 -c "
   import sqlite3
   conn = sqlite3.connect('/app/superset_home/superset.db')
   c = conn.cursor()
   c.execute('''
       SELECT pv.id, p.name, vm.name
       FROM ab_permission_view pv
       JOIN ab_permission p ON pv.permission_id = p.id
       JOIN ab_view_menu vm ON pv.view_menu_id = vm.id
       WHERE vm.name LIKE '%ataset%' OR vm.name LIKE '%atasource%'
       ORDER BY vm.name, p.name
   ''')
   for r in c.fetchall():
       print(f'  ID={r[0]}: {r[1]} on {r[2]}')
   conn.close()
   "
   ```
2. Check what permissions the **Admin** role has for datasets that `Sublime User Management` currently lacks — this is the "delta" we need to add
3. Research Superset source code behavior for `can_write Dataset`:
   - Does `can_write` enforce ownership on PUT (edit)? Or does it allow editing any dataset?
   - Does `all_datasource_access` bypass ownership checks?
   - Is there a `can_delete Dataset` separate from `can_write Dataset`? (Based on Finding 1 from Option 1, likely NO — they are bundled)
4. Document findings in a research summary

**Deliverable:** Research findings document explaining which permissions to add and any Superset platform limitations

---

### Phase 2: Permission Delta — Define the Exact Permission Changes

**Goal:** Produce the exact list of permission additions to `Sublime User Management` role for admin-like dataset access.

**Steps:**
1. Based on Phase 1 research, identify the specific `permission_view_id`s to add
2. Key candidates to evaluate:
   - `can_write` on `Dataset` — already absent; needed for edit/delete
   - `can_delete` on `Dataset` — may not exist separately (Superset bundles with `can_write`)
   - `all_datasource_access` — global access to all datasources (may bypass ownership)
   - `can_set_owners` or equivalent — for "set self as owner" functionality
   - `can_create` on `Dataset` — for creating new datasets from UI
3. Consider risk: adding `all_datasource_access` might grant broader access than intended
4. Create a permissions diff table: `Option 1 permissions` vs `Option 2 permissions`

**Deliverable:** Clear permission diff and risk assessment

---

### Phase 3: Implement — Modify Role Permissions in Superset

**Goal:** Apply the permission changes to a copy of the role (or modify the existing role) and verify via DB query.

**Steps:**
1. Create a backup of the current `Sublime User Management` role permissions (snapshot before changes)
2. Add the identified dataset permissions to the role via direct SQLite manipulation:
   ```bash
   docker exec sql-playground-superset python3 -c "
   import sqlite3
   conn = sqlite3.connect('/app/superset_home/superset.db')
   c = conn.cursor()
   # Add new permissions...
   conn.commit()
   conn.close()
   "
   ```
3. Verify the permission count increased as expected
4. Quick smoke test: log in as `test-owner` and try editing a non-owned dataset via API

**Deliverable:** Modified role with new permissions applied

---

### Phase 4: Test — Automated API Testing for Option 2 Dataset Behavior

**Goal:** Run a modified test suite that validates the new dataset behavior while confirming dashboards/charts are unchanged.

**New/modified dataset tests (expected behavior changes from Option 1):**

| Test ID | Description | Option 1 Expected | Option 2 Expected |
|---------|-------------|-------------------|-------------------|
| 2.1 | Owner: edit **non-owned** dataset | 403 (blocked) | **200 (allowed)** |
| 2.2 | Owner: create dataset from UI | 403 (blocked) | **201 (allowed)** |
| 2.6 | Owner: delete dataset | 403 (blocked) | **200 (allowed)** |
| 2.7 | Owner: set self as owner on non-owned dataset | 403 (blocked) | **200 (allowed)** |
| 2.8 | Viewer: edit dataset | 403 (blocked) | 403 (still blocked) |
| 2.9 | Viewer: delete dataset | 403 (blocked) | 403 (still blocked) |

**Unchanged tests (must still pass as Option 1):**
- All dashboard tests (1.x) — identical behavior
- All chart tests (3.x) — identical behavior
- All SQL Lab tests (4.x) — identical behavior
- All tag tests (5.x) — identical behavior
- All database tests (6.x) — identical behavior

**Steps:**
1. Create a new test script `test-role-permissions-option2.py` adapted from Option 1's script
2. Modify dataset test section with new expectations
3. Add new test cases for: edit non-owned dataset, delete dataset, set self as owner
4. Run full test suite and capture results
5. Generate markdown report

**Deliverable:** Test script + test results report

---

### Phase 5: Document — Produce Artifacts for `.temp-02`

**Goal:** Create all deployment and documentation artifacts in the `.temp-02` directory.

**Output structure:**
```
superset-roles/.temp-02/
├── README.md                              # Overview of Option 2 research
├── report/
│   ├── option2-research-findings.md       # Phase 1 research results
│   ├── option2-permission-diff.md         # Phase 2 permission delta
│   ├── option2-test-results.md            # Phase 4 test results
│   └── screenshots/                       # UI screenshots (if captured)
└── roles-deployment/
    ├── DEPLOYMENT-GUIDE.md                # Updated deployment instructions
    ├── sublime-roles-backup-option2.json  # JSON backup with Option 2 permissions
    ├── restore-roles-option2.py           # Restore script for Option 2
    └── test-role-permissions-option2.py   # Test script for Option 2
```

**Steps:**
1. Create directory structure
2. Write research findings document
3. Write permission diff document
4. Export updated role to JSON backup
5. Create Option 2-specific restore script
6. Create Option 2-specific test script
7. Write deployment guide
8. Update the `.temp/README.md` (Option 1 home) with a pointer to Option 2

**Deliverable:** Complete `.temp-02` directory with all artifacts

---

### Phase 6: Update Option 1 README

**Goal:** Add a section to `.temp/README.md` pointing to Option 2 research.

**What to add:**
- A new section "Option 2 — Admin-Like Dataset Permissions" explaining:
  - What Option 2 changes
  - Link to `.temp-02/` artifacts
  - Comparison summary (Option 1 vs Option 2)

---

## Key Risks & Open Questions

| # | Risk / Question | Impact | Mitigation |
|---|----------------|--------|------------|
| 1 | Superset may enforce ownership on `can_write Dataset` — even with the permission, editing non-owned datasets may return 403 | Option 2 may be impossible without `all_datasource_access` | Test with minimal permissions first, escalate to `all_datasource_access` if needed |
| 2 | `all_datasource_access` may grant broader access than desired (e.g., access to future datasets automatically) | Security concern | Document the trade-off clearly |
| 3 | `can_write Dataset` includes delete (same as dashboards/charts Finding 1) | Users can delete ANY dataset if ownership check is bypassed | This is intentional for Option 2 — admin-like on datasets |
| 4 | Setting self as owner may require `can_write` on the dataset + no ownership validation | May not be possible without custom code | Test API behavior — Superset may allow `owners` field in PUT body |
| 5 | Viewer (Sublime Starter) must NOT gain any new dataset permissions | Accidental privilege escalation | Run all viewer tests to confirm no regression |

---

## Success Criteria

1. `test-owner` user CAN edit any dataset (owned or not) — HTTP 200
2. `test-owner` user CAN delete any dataset — HTTP 200
3. `test-owner` user CAN create new datasets from UI/API — HTTP 201
4. `test-owner` user CAN set themselves as owner of a non-owned dataset — HTTP 200
5. `test-viewer` user CANNOT do any of the above — HTTP 403
6. All dashboard, chart, SQL Lab, tag, and database tests pass identically to Option 1
7. Complete artifacts in `.temp-02/` directory
8. `.temp/README.md` updated with Option 2 pointer

---

## Estimated Flow

```
Phase 1 (Research)  →  Phase 2 (Permission Delta)  →  Phase 3 (Implement)
                                                            ↓
Phase 6 (Update README)  ←  Phase 5 (Document)  ←  Phase 4 (Test)
```

All Option 1 artifacts in `.temp/` remain untouched. All Option 2 work goes to `.temp-02/`.
