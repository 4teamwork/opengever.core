---
title: 'REST API endpoint @backgroundtasks'
type: 'feature'
created: '2026-10-29'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Background tasks (`background_tasks` SQL table) can only be inspected via the Plone control panel. A Vue-based admin panel in a separate frontend repo needs a REST API to list them.

**Approach:** Add a `GET @backgroundtasks` service on the Plone site root, built on `OGDSListingBaseService` (batching, sorting, `b_start`/`b_size`, `items_total`) with a `BackgroundTask` summary serializer. Filters: `filters.status` (default: all except `succeeded`) and `filters.admin_unit` (default: current admin unit). Default sort `created` descending, unique tie-breaker `task_id`. Items carry `@id` (`<site>/@backgroundtasks/<task_id>`), `@type` (`virtual.ogds.backgroundtask`), `status`, `task_type`, `admin_unit`, `created`, `started`, `finished`, `retries`, `error_message`. Guarded by `cmf.ManagePortal`, like the control panel. Unknown `status` values raise `BadRequest`. Explicit `admin_unit` values replace the default (cross-unit access is intended). No single-item GET, no write actions.

</frozen-after-approval>

## Implementation Notes

- Added `opengever/api/backgroundtasks.py` (service, serializer), zcml registration, `opengever/api/tests/test_backgroundtasks.py`, `changes/backgroundtasks-api.feature`.
- Timestamps are stored naive server-local; serialized as UTC-aware.
- Tests could not be run (no buildout in checkout).
- Added `task_type` to items after review.

## Review Triage Log

- Dead `@id` (no single-item GET): low, matches requested response shape; rejected.
- Missing `task_type`: medium, real; patched.
- Timezone/DST fragility, test gaps (search, None unit, permission code): low; rejected.
- API docs: `docs/` not accessible in this session; not done.
- `as_list` public helper: low; rejected.
