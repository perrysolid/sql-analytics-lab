# Option 2 — Admin-Like Dataset Permissions Research

This directory contains all artifacts from researching and testing **Option 2**: giving the owner role (`OPT2_Sublime_UserMgmt`) admin-like access to datasets while keeping dashboard/chart permissions ownership-scoped (same as Option 1).

---

## Key Finding: Requires Custom Security Manager

Superset hardcodes an ownership check in `raise_for_ownership()` — only users with the **Admin role** bypass it. Adding `can_write Dataset` + `all_datasource_access` permissions is **not sufficient** to edit/delete non-owned datasets.

**Solution:** A `CustomSecurityManager` override in `superset_config.py` that skips the ownership check on `SqlaTable` objects for users with the `OPT2_Sublime_UserMgmt` role.

---

## Option 1 vs Option 2 Comparison

| Area | Option 1 | Option 2 |
|------|----------|----------|
| Dashboards | Ownership-scoped edits | **Same** (no change) |
| Charts | Ownership-scoped edits | **Same** (no change) |
| **Datasets** | **No edits from UI** (read-only) | **Admin-like: edit/delete/create ANY dataset** |
| SQL Lab | Full access for owner | **Same** (no change) |
| Custom Security Manager | Not required | **Required** |

### Permission Delta (3 extra permissions in OPT2_Sublime_UserMgmt vs Option 1)

| Permission | View | Purpose |
|-----------|------|---------|
| `can_write` | Dataset | Edit/create/delete datasets |
| `can_save` | Datasource | Save datasource changes |
| `all_datasource_access` | all_datasource_access | Bypass per-dataset data access checks |

---

## Test Results Summary

**70 tests | 68 passed | 2 known findings**

| Category | Tests | Passed | Failed |
|----------|:-----:|:------:|:------:|
| Dashboards | 18 | 17 | 1 (known) |
| Dashboard Visibility | 11 | 11 | 0 |
| **Datasets (Option 2 focus)** | **15** | **15** | **0** |
| Charts | 12 | 11 | 1 (known) |
| SQL Lab | 6 | 6 | 0 |
| Tags | 4 | 4 | 0 |
| Databases | 4 | 4 | 0 |

**All 15 dataset tests PASSED** — owner can edit, delete, create, set owner on ANY dataset.

The 2 findings are the same `can_write` bundles delete issue from Option 1 (dashboards + charts). Not related to Option 2 changes.

---

## Test Users & Roles

| User | Username | ID | Role | Perms |
|------|----------|:--:|------|:-----:|
| Viewer | `opt2-viewer` | 4 | `OPT2_Sublime_Starter` | 72 |
| Owner | `opt2-owner` | 5 | `OPT2_Sublime_UserMgmt` | 123 |

---

## Directory Structure

```
.temp-02/
├── README.md                                    ← You are here
├── report/
│   └── opt2-test-results.md                     ← Full test results (70 tests)
└── roles-deployment/
    ├── sublime-roles-backup-option2.json         ← Role backup (72 + 123 permissions)
    └── test-role-permissions-option2.py           ← Automated test script
```

---

## Deployment Requirements

To deploy Option 2 on another Superset instance:

1. **Add the CustomSecurityManager** to `superset_config.py` (see `superset/config/superset_config.py` for the inline implementation)
2. **Restore roles** from `sublime-roles-backup-option2.json`
3. **Update the role name** in the CustomSecurityManager if using a different role name than `OPT2_Sublime_UserMgmt`
4. **Restart Superset** to load the custom security manager
5. **Update datasource-specific permissions** in the JSON to match target environment (same as Option 1)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| `all_datasource_access` grants access to ALL current and future datasets | Users see all data automatically | Acceptable for admin-like dataset role |
| CustomSecurityManager must be maintained across Superset upgrades | Override may break on major version change | Pin Superset version, test after upgrades |
| `can_write Dataset` includes delete (same as dashboards) | Users can delete any dataset | Intentional for Option 2 |
| Only works for the specific role name `OPT2_Sublime_UserMgmt` | Must update code if role is renamed | Document clearly |
