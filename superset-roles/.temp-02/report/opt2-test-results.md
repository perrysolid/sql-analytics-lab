# Option 2 — Superset Role Permission Test Results

**Scenario:** Admin-like dataset access for OPT2_Sublime_UserMgmt role
**Date:** 2026-03-05
**Total Tests:** 70
**Passed:** 68
**Failed:** 2

**Result: 2 FINDING(S) DETECTED**

## Option 2 vs Option 1 — What Changed

| Area | Option 1 (current) | Option 2 (this test) |
|------|-------------------|---------------------|
| Dashboards | Ownership-scoped edits | **Same** (no change) |
| Charts | Ownership-scoped edits | **Same** (no change) |
| **Datasets** | **No edits from UI** | **Admin-like: edit/delete/create ANY dataset** |
| SQL Lab | Full access for owner | **Same** (no change) |

## Extra Permissions Added (vs Option 1)

| Permission | View | Purpose |
|-----------|------|---------|
| `can_write` | Dataset | Edit/create/delete datasets |
| `can_save` | Datasource | Save datasource changes |
| `all_datasource_access` | all_datasource_access | Bypass per-dataset ownership — access ALL datasets |

## Test Environment

| Parameter | Value |
|-----------|-------|
| Dashboard Published+Owned | ID 5 |
| Dashboard Published+NotOwned | ID 2 |
| Dashboard Draft+Owned | ID 3 |
| Dashboard Draft+NotOwned | ID 4 |
| Chart Owned | ID 2 |
| Chart NotOwned | ID 6 |
| Datasets (all non-owned) | IDs [1, 2, 3, 4] |
| Database | ID 1 |

## Test Users (Option 2 specific)

| User | Username | Role | Permissions |
|------|----------|------|-------------|
| Viewer | opt2-viewer | OPT2_Sublime_Starter | 72 (same as Sublime Starter) |
| Owner | opt2-owner | OPT2_Sublime_UserMgmt | 123 (Sublime User Management + 3 dataset perms) |

## Detailed Results

### Dashboards

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 1.1.1 | PASS | viewer | one of [403, 422] | 403 | Non-owned: cannot edit (viewer) |
| 1.1.1 | PASS | owner | one of [403, 422] | 403 | Non-owned: cannot edit (owner) |
| 1.1.2 | PASS | viewer | one of [201, 200, 403] | 403 | Non-owned: copy (Save as) [viewer] |
| 1.1.2 | PASS | owner | one of [201, 200, 403] | 201 | Non-owned: copy (Save as) [owner] |
| 1.1.3 | PASS | viewer | one of [403, 404, 422] | 403 | Non-owned: cannot delete (viewer) |
| 1.1.3 | PASS | owner | one of [403, 404, 422] | 404 | Non-owned: cannot delete (owner) |
| 1.1.4 | PASS | viewer | 200 | 200 | Non-owned: can export (viewer) |
| 1.1.4 | PASS | owner | 200 | 200 | Non-owned: can export (owner) |
| 1.2.1 | PASS | viewer | one of [403, 422] | 403 | Owned: cannot edit (viewer) |
| 1.2.1 | PASS | owner | 200 | 200 | Owned: can edit (owner) |
| 1.2.2 | PASS | viewer | one of [403, 422] | 403 | Owned: cannot assign owner (viewer) |
| 1.2.2 | PASS | owner | 200 | 200 | Owned: can assign owner (owner) |
| 1.2.3 | PASS | viewer | one of [403, 422] | 403 | Owned: cannot delete (viewer) |
| 1.2.3 | **FAIL** | owner | one of [403, 422] | 200 | Owned: cannot delete (owner) |
| 1.2.4 | PASS | viewer | one of [403, 422] | 403 | Owned: cannot toggle published (viewer) |
| 1.2.4 | PASS | owner | 200 | 200 | Owned: can toggle published (owner) |
| 1.2.5 | PASS | viewer | one of [403, 422] | 403 | Non-owned: cannot toggle published (viewer) |
| 1.2.5 | PASS | owner | one of [403, 422] | 403 | Non-owned: cannot toggle published (owner) |

### Dashboard Visibility

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 1.3.1 | PASS | viewer | visible | visible | Published Owned dashboard visible (viewer) |
| 1.3.1 | PASS | viewer | visible | visible | Published NotOwned dashboard visible (viewer) |
| 1.3.1 | PASS | owner | visible | visible | Published Owned dashboard visible (owner) |
| 1.3.1 | PASS | owner | visible | visible | Published NotOwned dashboard visible (owner) |
| 1.3.2 | PASS | viewer | hidden | hidden | Owned Draft dashboard NOT visible (viewer) |
| 1.3.2 | PASS | owner | visible | visible | Owned Draft dashboard visible (owner) |
| 1.3.3 | PASS | viewer | hidden | hidden | Non-owned Draft dashboard NOT visible (viewer) |
| 1.3.3 | PASS | owner | hidden | hidden | Non-owned Draft dashboard NOT visible (owner) |
| 1.3.4 | PASS | owner | 200 | 200 | Owner can toggle owned Draft -> Published |
| 1.3.5 | PASS | owner | one of [403, 404, 422] | 404 | Owner cannot toggle non-owned Draft |
| 1.3.6 | PASS | owner | 200 | 200 | Revert owned Draft dashboard back to Draft |

### Datasets

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 2.1 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot edit non-owned dataset |
| 2.1 | PASS | owner | 200 | 200 | **Owner: CAN edit non-owned dataset (OPT2 NEW)** |
| 2.2 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot create datasets |
| 2.2 | PASS | owner | one of [200, 201] | 201 | **Owner: CAN create datasets (OPT2 NEW)** |
| 2.3 | PASS | viewer | 200 | 200 | Can read datasets (viewer) |
| 2.3 | PASS | owner | 200 | 200 | Can read datasets (owner) |
| 2.4 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot duplicate datasets |
| 2.4 | PASS | owner | one of [200, 201, 500] | 201 | Owner: can duplicate datasets |
| 2.5 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot export datasets |
| 2.5 | PASS | owner | 200 | 200 | Owner: can export datasets |
| 2.6 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot delete datasets |
| 2.6 | PASS | owner | one of [200, 204] | 200 | **Owner: CAN delete non-owned dataset (OPT2 NEW)** |
| 2.6 | PASS | owner | one of [200, 204] | 200 | **Owner: CAN delete owned dataset (OPT2 NEW)** |
| 2.7 | PASS | owner | 200 | 200 | **Owner: CAN set self as owner on non-owned dataset (OPT2 NEW)** |
| 2.7 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot set self as owner |

### Charts

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 3.1 | PASS | viewer | 200 | 200 | Can view charts (viewer) |
| 3.1 | PASS | owner | 200 | 200 | Can view charts (owner) |
| 3.3 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot create charts |
| 3.3 | PASS | owner | one of [200, 201] | 201 | Owner: can create charts |
| 3.4 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot edit owned charts |
| 3.4 | PASS | owner | 200 | 200 | Owner: can edit owned charts |
| 3.5 | PASS | viewer | one of [403, 422] | 403 | Cannot edit non-owned charts (viewer) |
| 3.5 | PASS | owner | one of [403, 422] | 403 | Cannot edit non-owned charts (owner) |
| 3.6 | PASS | viewer | one of [403, 422] | 403 | Cannot delete charts (viewer) |
| 3.6 | **FAIL** | owner | one of [403, 422] | 200 | Cannot delete charts (owner) |
| 3.7 | PASS | viewer | 200 | 200 | Can export charts (viewer) |
| 3.7 | PASS | owner | 200 | 200 | Can export charts (owner) |

### SQL Lab

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 4.1 | PASS | viewer | one of [403, 422, 400] | 403 | Viewer: cannot execute SQL |
| 4.1 | PASS | owner | one of [200, 201] | 200 | Owner: can execute SQL |
| 4.2 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot save queries |
| 4.2 | PASS | owner | one of [200, 201] | 201 | Owner: can save queries |
| 4.3 | PASS | viewer | 200 | 200 | Can read saved queries (viewer) |
| 4.3 | PASS | owner | 200 | 200 | Can read saved queries (owner) |

### Tags

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 5.1 | PASS | viewer | 200 | 200 | Can read tags (viewer) |
| 5.1 | PASS | owner | 200 | 200 | Can read tags (owner) |
| 5.2 | PASS | viewer | one of [403, 422] | 403 | Viewer: cannot create tags |
| 5.2 | PASS | owner | one of [200, 201] | 201 | Owner: can create tags |

### Databases

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 6.1 | PASS | viewer | 200 | 200 | Can read databases (viewer) |
| 6.1 | PASS | owner | 200 | 200 | Can read databases (owner) |
| 6.2 | PASS | viewer | one of [403, 422] | 403 | Cannot edit databases (viewer) |
| 6.2 | PASS | owner | one of [403, 422] | 403 | Cannot edit databases (owner) |

## Findings

### 1.2.3 - Owned: cannot delete (owner) (owner)
- **Expected:** one of [403, 422]
- **Actual:** 200
- **Detail:** `{"message":"OK"}
`

### 3.6 - Cannot delete charts (owner) (owner)
- **Expected:** one of [403, 422]
- **Actual:** 200
- **Detail:** `{"message":"OK"}
`
