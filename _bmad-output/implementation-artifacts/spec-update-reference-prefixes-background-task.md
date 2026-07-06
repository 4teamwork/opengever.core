---
title: 'Update Reference Prefixes Background Task'
type: 'feature'
created: '2026-07-06'
status: 'done'
baseline_commit: '28a98f61cc857c199b2e37ada7ba243e66652131'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `update_reference_prefixes` in `opengever.repository.subscribers` runs synchronously inside the `IObjectModifiedEvent` subscriber, recursively reindexing every contained object's `reference`/`sortable_reference`/title indexes in-request when a repository folder's reference number prefix changes — blocking the request on large repository trees.

**Approach:** Move the reindexing loop into a new `opengever.bgtasks` task type (`update-reference-prefixes`) and have the subscriber enqueue it via `queue_task()` instead of executing inline, following the same enqueue/fallback pattern already established by `PatchCMFCatalogAwareReindexObjectSecurity`.

## Boundaries & Constraints

**Always:**
- Python 2.7 compatible — `u''` literals, `super(Cls, self)`, `%`-formatting.
- Preserve exact reindexing behavior (same idxs per content type, same `elevated_privileges()` wrapping) — only the trigger mechanism (inline vs. queued) changes.
- Fall through to running the reindex loop synchronously when `get_current_admin_unit()` returns `None` (setup/test contexts where OGDS is not ready) — do not call `queue_task` in that case.
- Task handler resolves the object from `portal_catalog.unrestrictedSearchResults(UID=uid)` using `_unrestrictedGetObject()`, mirroring `ReindexObjectSecurityTask`. Missing object at execution time → log a warning and return (task succeeds, no retry).
- Keep the early-return guards in `update_reference_prefixes` (`ILocalrolesModifiedEvent`, `IContainerModifiedEvent`) exactly as-is — only the body after `is_reference_number_prefix_changed` changes.

**Ask First:**
- Adding deduplication of pending tasks for the same UID (the existing `reindexObjectSecurity` task does this because it's called very frequently; this event fires only on deliberate prefix edits, so it is deliberately omitted here unless you want it).

**Never:**
- Import from `ftw.solr` internals — irrelevant here, no monkey-patch involved.
- Change the set of reindexed idxs or the `IBaseDocument`/`IRepositoryFolder` branching logic.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Normal enqueue | Prefix changed on a repository folder, admin unit present | One `update-reference-prefixes` task queued with `{'uid': obj.UID()}` | — |
| No admin unit | `get_current_admin_unit()` returns `None` | Reindex loop runs synchronously in the current request, as before | — |
| Background tasks disabled (tests) | `is_background_tasks_enabled()` is `False` | `queue_task` executes the handler synchronously in-request — behavior identical to current tests | — |
| Object deleted before task runs | UID no longer in catalog at execution time | Log `WARNING`, task marked `succeeded`, no reindex performed | — |
| Task executes successfully | Object found in catalog | Same idxs recomputed/reindexed for the object and all its contained children as today | Worker's existing retry/failure logic handles unexpected exceptions |

</frozen-after-approval>

## Code Map

- `opengever/repository/tasks.py` — NEW: `TASK_TYPE = u'update-reference-prefixes'`; `reindex_children_with_new_prefix(obj)` (extracted reindex loop, unchanged logic); `UpdateReferencePrefixesTask(BaseBackgroundTask)`; `register_task_type(TASK_TYPE, UpdateReferencePrefixesTask)` at module level
- `opengever/repository/subscribers.py` — MODIFY: `update_reference_prefixes` enqueues via `queue_task(TASK_TYPE, admin_unit.unit_id, arguments={u'uid': obj.UID()})`, falling back to calling `reindex_children_with_new_prefix(obj)` directly when `get_current_admin_unit()` is `None`
- `opengever/repository/tests/test_tasks.py` — NEW: `IntegrationTestCase` covering enqueue-vs-fallback and the task handler's missing-object edge case
- `opengever/repository/tests/test_subscribers.py` — unchanged; existing `SolrIntegrationTestCase` browser tests continue to pass because bgtasks are disabled by default in the test fixture (`queue_task` executes synchronously)

## Tasks & Acceptance

**Execution:**
- [x] `opengever/repository/tasks.py` -- create -- defines the task type, the extracted reindex logic, and the handler, following `opengever/bgtasks/reindex_object_security.py`'s structure (catalog lookup by UID via `_unrestrictedGetObject()`, warn-and-return on missing object)
- [x] `opengever/repository/subscribers.py` -- modify `update_reference_prefixes` -- replace the inline loop body with an admin-unit check + `queue_task(...)` call or synchronous fallback; import `TASK_TYPE` and `reindex_children_with_new_prefix` from `.tasks`, `queue_task` from `opengever.bgtasks.task`, `get_current_admin_unit` from `opengever.ogds.base.utils`
- [x] `opengever/repository/tests/test_tasks.py` -- create -- test: enqueues exactly one task when admin unit present; test: falls back to synchronous execution when `get_current_admin_unit()` returns `None`; test: `UpdateReferencePrefixesTask.execute` reindexes the resolved object's children; test: `execute` logs a warning and returns without error for a missing UID

**Acceptance Criteria:**
- Given a repository folder's `reference_number_prefix` changes and an admin unit is configured, when the `IObjectModifiedEvent` fires, then exactly one `update-reference-prefixes` task is queued with the folder's UID and no reindexing happens inline in that request.
- Given `get_current_admin_unit()` returns `None`, when the prefix changes, then the reindex loop runs synchronously exactly as it does today.
- Given a queued `update-reference-prefixes` task is executed and the UID is no longer present in the catalog, then the task completes successfully and a warning is logged.
- Given the existing `test_subscribers.py` `SolrIntegrationTestCase` suite, when run unmodified, then all tests still pass (bgtasks disabled in the fixture makes `queue_task` synchronous).

## Design Notes

**Extraction, not reinvention:** `reindex_children_with_new_prefix(obj)` is a straight lift of the current loop body from `update_reference_prefixes` (catalog path search + idxs branching + `elevated_privileges()`), unchanged. This keeps behavior identical and the diff reviewable — the subscriber only decides *whether* to call it inline or queue it.

**Why `elevated_privileges()` still matters here:** when bgtasks are disabled (all current tests), `queue_task` runs the handler synchronously in the editing user's own security context, not an elevated worker context — so the existing elevated-privileges wrapping around the children loop must be preserved inside the task handler, not dropped.

## Verification

**Commands:**
- `bin/test opengever/repository/tests/test_tasks.py opengever/repository/tests/test_subscribers.py` -- expected: all tests pass
- `python -c "from opengever.repository.tasks import UpdateReferencePrefixesTask"` -- expected: no ImportError

**Manual checks (if no CLI):**
- After changing a repository folder's reference number prefix with bgtasks enabled, verify a row appears in `background_tasks` with `task_type='update-reference-prefixes'` and the folder's UID in `task_arguments`.

## Suggested Review Order

**Subscriber wiring — start here to grasp the design intent**

- `update_reference_prefixes`: admin-unit check gates queue-vs-inline fallback, mirroring `PatchCMFCatalogAwareReindexObjectSecurity`.
  [`subscribers.py:25`](../../opengever/repository/subscribers.py#L25)

**Task implementation**

- `UpdateReferencePrefixesTask.execute`: UID guard, catalog resolution with a defensive `try/except` around `_unrestrictedGetObject()`, missing-object guard, then delegates to the extracted function.
  [`tasks.py:45`](../../opengever/repository/tasks.py#L45)

- `reindex_children_with_new_prefix`: extracted, unchanged loop body (idxs selection, `elevated_privileges()` wrapping) — behavior parity with the pre-refactor inline code.
  [`tasks.py:15`](../../opengever/repository/tasks.py#L15)

**Tests**

- Subscriber tests: enqueue-on-edit and the no-admin-unit synchronous fallback (verified via a spy on `reindex_children_with_new_prefix`, not just "no task queued").
  [`test_tasks.py:38`](../../opengever/repository/tests/test_tasks.py#L38)

- Task handler tests: successful execution delegates to the reindex function; missing UID is a no-op.
  [`test_tasks.py:114`](../../opengever/repository/tests/test_tasks.py#L114)

- Pre-existing `test_subscribers.py` Solr-backed assertions are unmodified and still pass because bgtasks are disabled by default in the test fixture, making `queue_task` synchronous.
  [`test_subscribers.py:10`](../../opengever/repository/tests/test_subscribers.py#L10)
