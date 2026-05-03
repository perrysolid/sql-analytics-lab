# Superset Role Permission Test Results

**Date:** 2026-03-03
**Total Tests:** 65
**Passed:** 62
**Failed:** 3

**Result: 3 FINDING(S) DETECTED**

## Test Environment

| Parameter | Value |
|-----------|-------|
| Dashboard Published+Owned | ID 5 |
| Dashboard Published+NotOwned | ID 2 |
| Dashboard Draft+Owned | ID 3 |
| Dashboard Draft+NotOwned | ID 4 |
| Chart Owned | ID 2, 5 |
| Chart NotOwned | ID 3 |
| Dataset | ID 1 |
| Database | ID 1 |

## Test Users

| User | Username | Role |
|------|----------|------|
| Viewer (ID=2) | test-viewer | Sublime Starter (72 permissions) |
| Owner (ID=3) | test-owner | Sublime User Management (120 permissions) |

## Ownership Matrix

| Object | Admin (ID=1) | test-owner (ID=3) |
|--------|:-----:|:----------:|
| Dashboard 5 - Trip Patterns (Published) | Owner | Owner |
| Dashboard 2 - Revenue Analysis (Published) | Owner | - |
| Dashboard 3 - Trip Patterns Draft (Draft) | Owner | Owner |
| Dashboard 4 - Revenue Analysis Draft (Draft) | Owner | - |
| Chart 5 - Trips by Hour | Owner | Owner |
| Chart 2 - Trips by Borough | Owner | Owner |
| Chart 3 - Daily Trip Volume Trend | Owner | - |
| Chart 4 - Payment Type Analysis | Owner | - |

## Summary

| Category | Tests | Passed | Failed |
|----------|:-----:|:------:|:------:|
| Dashboards | 18 | 17 | 1 |
| Dashboard Visibility | 11 | 11 | 0 |
| Datasets | 10 | 9 | 1 |
| Charts | 12 | 11 | 1 |
| SQL Lab | 6 | 6 | 0 |
| Tags | 4 | 4 | 0 |
| Databases | 4 | 4 | 0 |
| **Total** | **65** | **62** | **3** |

## Detailed Results

### Dashboards

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 1.1.1 | PASS | viewer | 403 | 403 | Non-owned: cannot edit |
| 1.1.1 | PASS | owner | 403 | 403 | Non-owned: cannot edit |
| 1.1.2 | PASS | viewer | 201/200/403 | 403 | Non-owned: copy (Save as) [viewer] |
| 1.1.2 | PASS | owner | 201/200/403 | 201 | Non-owned: copy (Save as) [owner] |
| 1.1.3 | PASS | viewer | 403/404 | 403 | Non-owned: cannot delete |
| 1.1.3 | PASS | owner | 403/404 | 404 | Non-owned: cannot delete |
| 1.1.4 | PASS | viewer | 200 | 200 | Non-owned: can export |
| 1.1.4 | PASS | owner | 200 | 200 | Non-owned: can export |
| 1.2.1 | PASS | viewer | 403 | 403 | Owned: cannot edit (viewer) |
| 1.2.1 | PASS | owner | 200 | 200 | Owned: can edit (owner) |
| 1.2.2 | PASS | viewer | 403 | 403 | Owned: cannot assign owner (viewer) |
| 1.2.2 | PASS | owner | 200 | 200 | Owned: can assign owner (owner) |
| 1.2.3 | PASS | viewer | 403 | 403 | Owned: cannot delete (viewer) |
| 1.2.3 | **FAIL** | owner | 403 | 200 | Owned: cannot delete (owner) |
| 1.2.4 | PASS | viewer | 403 | 403 | Owned: cannot toggle published (viewer) |
| 1.2.4 | PASS | owner | 200 | 200 | Owned: can toggle published (owner) |
| 1.2.5 | PASS | viewer | 403 | 403 | Non-owned: cannot toggle published |
| 1.2.5 | PASS | owner | 403 | 403 | Non-owned: cannot toggle published |

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
| 1.3.5 | PASS | owner | 403/404 | 404 | Owner cannot toggle non-owned Draft |
| 1.3.6 | PASS | owner | 200 | 200 | Revert owned Draft dashboard back to Draft |

### Datasets

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 2.1 | PASS | viewer | 403 | 403 | Cannot edit datasets |
| 2.1 | PASS | owner | 403 | 403 | Cannot edit datasets |
| 2.2 | PASS | viewer | 403 | 403 | Cannot create datasets |
| 2.2 | PASS | owner | 403 | 403 | Cannot create datasets |
| 2.3 | PASS | viewer | 200 | 200 | Can read datasets |
| 2.3 | PASS | owner | 200 | 200 | Can read datasets |
| 2.4 | PASS | viewer | 403 | 403 | Viewer cannot duplicate datasets |
| 2.4 | **FAIL** | owner | 200/201 | 500 | Owner can duplicate datasets |
| 2.5 | PASS | viewer | 403 | 403 | Viewer cannot export datasets |
| 2.5 | PASS | owner | 200 | 200 | Owner can export datasets |

### Charts

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 3.1 | PASS | viewer | 200 | 200 | Can view charts |
| 3.1 | PASS | owner | 200 | 200 | Can view charts |
| 3.3 | PASS | viewer | 403 | 403 | Viewer cannot create charts |
| 3.3 | PASS | owner | 201 | 201 | Owner can create charts |
| 3.4 | PASS | viewer | 403 | 403 | Viewer cannot edit owned charts |
| 3.4 | PASS | owner | 200 | 200 | Owner can edit owned charts |
| 3.5 | PASS | viewer | 403 | 403 | Cannot edit non-owned charts |
| 3.5 | PASS | owner | 403 | 403 | Cannot edit non-owned charts |
| 3.6 | PASS | viewer | 403 | 403 | Cannot delete charts (viewer) |
| 3.6 | **FAIL** | owner | 403 | 200 | Cannot delete charts (owner) |
| 3.7 | PASS | viewer | 200 | 200 | Can export charts |
| 3.7 | PASS | owner | 200 | 200 | Can export charts |

### SQL Lab

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 4.1 | PASS | viewer | 403 | 403 | Viewer cannot execute SQL |
| 4.1 | PASS | owner | 200 | 200 | Owner can execute SQL |
| 4.2 | PASS | viewer | 403 | 403 | Viewer cannot save queries |
| 4.2 | PASS | owner | 201 | 201 | Owner can save queries |
| 4.3 | PASS | viewer | 200 | 200 | Can read saved queries |
| 4.3 | PASS | owner | 200 | 200 | Can read saved queries |

### Tags

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 5.1 | PASS | viewer | 200 | 200 | Can read tags |
| 5.1 | PASS | owner | 200 | 200 | Can read tags |
| 5.2 | PASS | viewer | 403 | 403 | Viewer cannot create tags |
| 5.2 | PASS | owner | 201 | 201 | Owner can create tags |

### Databases

| ID | Status | User | Expected | Actual | Description |
|:---|:------:|:-----|:---------|:-------|:------------|
| 6.1 | PASS | viewer | 200 | 200 | Can read databases |
| 6.1 | PASS | owner | 200 | 200 | Can read databases |
| 6.2 | PASS | viewer | 403 | 403 | Cannot edit databases |
| 6.2 | PASS | owner | 403 | 403 | Cannot edit databases |

## Findings

### Finding 1: Owner CAN Delete Owned Dashboards (1.2.3)

**Severity:** High
**Expected:** Owner role cannot delete dashboards (deletion handled by external "maszynka" notebook)
**Actual:** Owner role successfully deleted an owned dashboard (HTTP 200)

**Root Cause:** In Superset, `can_write Dashboard` permission includes create, update, AND delete for owned objects. There is no separate `can_delete Dashboard` permission that can be independently revoked.

**Impact:** Owner users can delete their own dashboards from the UI, bypassing the intended workflow where deletion is exclusively managed by the external Jupyter notebook automation.

**Mitigation Options:**
1. **Row Level Security (RLS):** Not applicable for delete operations
2. **Custom Security Manager:** Override `can_access` to intercept delete operations
3. **Frontend UI restriction:** Hide/disable delete buttons via custom CSS or Superset plugin
4. **Accept as design limitation:** Document that deletion is technically possible but organizationally controlled by policy ("don't delete from UI, use the notebook")

### Finding 2: Dataset Duplicate Returns 500 (2.4)

**Severity:** Medium
**Expected:** Owner role can duplicate datasets via `can_duplicate Dataset` permission
**Actual:** API returns HTTP 500 "Fatal error"

**Root Cause:** The `/api/v1/dataset/duplicate` endpoint likely requires additional parameters or has a Superset version-specific issue. The `can_duplicate Dataset` permission IS correctly assigned to the Owner role (verified by viewer getting 403), but the operation itself fails server-side.

**Impact:** Owner users cannot duplicate datasets via API. This may work differently through the UI.

**Mitigation:** Test dataset duplication via the Superset UI to verify if this is an API-only issue.

### Finding 3: Owner CAN Delete Owned Charts (3.6)

**Severity:** High
**Expected:** Owner role cannot delete charts (same as dashboard deletion policy)
**Actual:** Owner role successfully deleted an owned chart (HTTP 200)

**Root Cause:** Same as Finding 1 — `can_write Chart` includes delete for owned objects.

**Impact:** Same mitigation options apply as Finding 1.

## Notes

### Non-Destructive Testing

All delete tests used temporary objects created specifically for testing. No real dashboards or charts were destroyed during testing. Temporary objects are cleaned up automatically after test execution.

### Dashboard Visibility Behavior

Draft dashboards behave as expected:
- Non-owners receive HTTP 404 (not 403) when accessing non-owned draft dashboards
- This is correct behavior — the dashboard is hidden (not just forbidden)
- Owners see their own draft dashboards in the list view

### Viewer "Save as" for Dashboards

The viewer role (Sublime Starter) cannot copy dashboards via `POST /api/v1/dashboard/` (gets 403) because it lacks `can_write Dashboard`. The "Save as" feature in the Superset UI may work through a different mechanism (explore flow), which was not tested via API.
