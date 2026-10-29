---
title: 'Dedicated permission for @backgroundtasks'
type: 'feature'
created: '2026-10-29'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `@backgroundtasks` is guarded by the generic `cmf.ManagePortal`.

**Approach:** Introduce the permission "opengever.bgtasks: Manage background tasks" (zcml id `opengever.bgtasks.ManageBackgroundTasks`), use it for the endpoint, and grant it to Manager and Administrator in `rolemap.xml`.

</frozen-after-approval>

## Implementation Notes

- Added `opengever/bgtasks/permissions.zcml`, included via `opengever/bgtasks/configure.zcml`, which `opengever/api/configure.zcml` now includes.
- Updated `rolemap.xml`, `lawgiver.zcml` (ignored permissions) and the readonly permission-mapping test list.
- Upgrade step NOT created: writes to `opengever/core/upgrades/` were denied by the session's permission settings. Existing sites need one that applies the same `rolemap.xml` entry.
- Tests not run (no buildout in checkout).
