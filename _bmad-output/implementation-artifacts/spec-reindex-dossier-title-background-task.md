---
title: 'Reindex Dossier Title Background Task'
type: 'feature'
created: '2026-07-06'
status: 'done'
baseline_commit: 'd51759a1bd385ed8fadb04d713258861981272fe'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `reindex_contained_objects` in `opengever.dossier.handlers` runs synchronously inside the `IObjectModifiedEvent` subscriber, walking every contained object via Solr and pushing a `containing_dossier`/`containing_subdossier` field update (plus a globalindex task sync) in-request whenever a dossier or subdossier's title changes — blocking the request on large dossiers.

**Approach:** Move the two existing reindex loops (`reindex_containing_subdossier_for_contained_objects`, `reindex_containing_dossier_for_contained_objects`) into a new `opengever.dossier.tasks` module as a `reindex-dossier-title` background task, and have `reindex_contained_objects` enqueue it via `queue_task()` instead of running inline, following the same enqueue/fallback pattern already established by `update_reference_prefixes`.

## Boundaries & Constraints

**Always:**
- Python 2.7 compatible — `u''` literals, `super(Cls, self)`, `%`-formatting.
- Preserve exact reindexing behavior (same Solr filters/fields, same `elevated_privileges()` wrapping, same globalindex `sync_task` call for contained tasks) — only the trigger mechanism (inline vs. queued) changes.
- Fall through to running the reindex synchronously when `get_current_admin_unit()` returns `None` (setup/test contexts where OGDS is not ready) — do not call `queue_task` in that case.
- Keep the early-return guards in `reindex_contained_objects` (`ILocalrolesModifiedEvent`, `IContainerModifiedEvent`, the `IOpenGeverBase.title` attribute check) exactly as-is in the subscriber — they gate whether a task is queued at all.
- Task handler resolves the dossier from `portal_catalog.unrestrictedSearchResults(UID=uid)` via `_unrestrictedGetObject()`, mirroring `UpdateReferencePrefixesTask`. Missing object at execution time → log a warning and return (task succeeds, no retry).
- The task re-derives `is_subdossier()` and the current title from the resolved object at execution time — do not pass title or subdossier-ness as task arguments, since they may lag between enqueue and execution.
- `sync_task(obj, event)` inside the dossier-branch loop only uses `event` for `IContainerModifiedEvent`/`IObjectMovedEvent` type checks (see `opengever/globalindex/handlers/task.py` and `opengever/base/sqlsyncer.py`); since the subscriber already guarantees the firing event is neither of those, the task handler must call it with `event=None` — `providedBy(None)` is `False` for both checks, so behavior is unchanged.
- The event handler stays registered for both `IDossierMarker` and `IDossierTemplateMarker` in `configure.zcml`, unchanged.

**Ask First:**
- Adding deduplication of pending tasks for the same UID (omitted here, matching the precedent set by `update_reference_prefixes`, since title edits are deliberate user actions, not high-frequency).

**Never:**
- Change the Solr filters, the set of reindexed fields, or the `TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX` branching logic.
- Alter `reindex_containing_subdossier_for_contained_objects`/`reindex_containing_dossier_for_contained_objects` beyond dropping the now-unused `event` param from the subdossier variant and defaulting it to `None` in the dossier variant's call site.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Normal enqueue (dossier) | Title changed on a top-level dossier, admin unit present | One `reindex-dossier-title` task queued with `{'uid': obj.UID()}` | — |
| Normal enqueue (subdossier) | Title changed on a subdossier, admin unit present | Same as above; task later resolves `is_subdossier()` True at execute time | — |
| No admin unit | `get_current_admin_unit()` returns `None` | Reindex runs synchronously in the current request, as before | — |
| Background tasks disabled (tests) | `is_background_tasks_enabled()` is `False` | `queue_task` executes the handler synchronously in-request — behavior identical to current tests | — |
| Object deleted before task runs | UID no longer in catalog at execution time | Log `WARNING`, task marked `succeeded`, no reindex performed | — |
| Task executes successfully | Object found in catalog | Same Solr fields updated for contained objects as today, including globalindex sync for contained tasks | Worker's existing retry/failure logic handles unexpected exceptions |

</frozen-after-approval>

## Code Map

- `opengever/dossier/tasks.py` — NEW: `TASK_TYPE = u'reindex-dossier-title'`; `reindex_containing_subdossier_for_contained_objects(dossier)` and `reindex_containing_dossier_for_contained_objects(dossier)` (moved verbatim from `handlers.py`, dossier variant calls `sync_task(obj, None)`); `ReindexDossierTitleTask(BaseBackgroundTask)`; `register_task_type(TASK_TYPE, ReindexDossierTitleTask)` at module level
- `opengever/dossier/handlers.py` — MODIFY: remove the two moved helper functions; `reindex_contained_objects` keeps its guard clauses, then calls `queue_task(TASK_TYPE, admin_unit.unit_id, arguments={u'uid': dossier.UID()})` or falls back to calling the (imported) reindex functions directly when `get_current_admin_unit()` is `None`
- `opengever/dossier/tests/test_tasks.py` — NEW: `IntegrationTestCase` covering enqueue-vs-fallback and the task handler's dossier/subdossier branching plus missing-object edge case

## Tasks & Acceptance

**Execution:**
- [x] `opengever/dossier/tasks.py` -- create -- defines the task type, the moved reindex functions, and the handler, following `opengever/repository/tasks.py`'s structure (catalog lookup by UID via `_unrestrictedGetObject()`, warn-and-return on missing object, dispatch on `is_subdossier()`)
- [x] `opengever/dossier/handlers.py` -- modify `reindex_contained_objects` -- replace the inline dispatch with an admin-unit check + `queue_task(...)` call or synchronous fallback; import `TASK_TYPE`, `reindex_containing_subdossier_for_contained_objects`, `reindex_containing_dossier_for_contained_objects` from `.tasks`, `queue_task` from `opengever.bgtasks.task`, `get_current_admin_unit` from `opengever.ogds.base.utils`; delete the two moved function definitions
- [x] `opengever/dossier/tests/test_tasks.py` -- create -- test: enqueues exactly one task when admin unit present (for both a dossier and a subdossier title change); test: falls back to synchronous execution when `get_current_admin_unit()` returns `None`; test: `ReindexDossierTitleTask.execute` dispatches to the subdossier reindex function when the resolved object `is_subdossier()`, and to the dossier reindex function otherwise; test: `execute` logs a warning and returns without error for a missing UID

**Acceptance Criteria:**
- Given a dossier's title changes and an admin unit is configured, when the `IObjectModifiedEvent` fires, then exactly one `reindex-dossier-title` task is queued with the dossier's UID and no reindexing happens inline in that request.
- Given a subdossier's title changes and an admin unit is configured, then the queued task, once executed, calls the subdossier reindex path (not the top-level dossier path).
- Given `get_current_admin_unit()` returns `None`, when the title changes, then the reindex runs synchronously exactly as it does today.
- Given a queued `reindex-dossier-title` task is executed and the UID is no longer present in the catalog, then the task completes successfully and a warning is logged.
- Given the existing dossier/subdossier/task browser and indexer tests, when run unmodified, then all tests still pass (bgtasks disabled in the fixture makes `queue_task` synchronous).

## Design Notes

**Extraction, not reinvention:** both reindex functions are straight lifts of the current bodies from `handlers.py`, unchanged except that `reindex_containing_dossier_for_contained_objects` now defaults `event=None` at its call site inside the task (its only use of `event` is the `sync_task(obj, event)` type checks, which are safe with `None`). This keeps behavior identical and the diff reviewable — the subscriber only decides *whether* to call the reindex inline or queue it.

**Dispatch lives in the task, not the subscriber:** unlike `update_reference_prefixes` (single reindex path), this handler has two paths (dossier vs. subdossier). Rather than passing a flag through `task_arguments`, the task handler calls `resolved_obj.is_subdossier()` itself after catalog lookup — cheaper to recompute than to risk it going stale between enqueue and execution.

## Verification

**Commands:**
- `bin/test opengever/dossier/tests/test_tasks.py` -- expected: all tests pass
- `python -c "from opengever.dossier.tasks import ReindexDossierTitleTask"` -- expected: no ImportError

**Manual checks (if no CLI):**
- After renaming a dossier's title with bgtasks enabled, verify a row appears in `background_tasks` with `task_type='reindex-dossier-title'` and the dossier's UID in `task_arguments`.

## Suggested Review Order

**Subscriber wiring — start here to grasp the design intent**

- `reindex_contained_objects`: admin-unit check gates queue-vs-inline fallback, mirroring `update_reference_prefixes`.
  [`handlers.py:89`](../../opengever/dossier/handlers.py#L89)

- Enqueue point: only `uid` is passed as an argument; dossier/subdossier dispatch is deliberately deferred to execution time.
  [`handlers.py:106`](../../opengever/dossier/handlers.py#L106)

**Task implementation**

- `ReindexDossierTitleTask.execute`: UID guard, catalog resolution with a defensive `try/except`, missing-object guard, then delegates to the shared dispatch helper.
  [`tasks.py:78`](../../opengever/dossier/tasks.py#L78)

- `reindex_dossier_title`: single shared dispatch point (used by both the task and the subscriber's synchronous fallback) — avoids duplicating the `is_subdossier()` branch.
  [`tasks.py:64`](../../opengever/dossier/tasks.py#L64)

- `reindex_containing_dossier_for_contained_objects`: moved verbatim from `handlers.py`, `sync_task(obj, None)` is safe since the firing event is always a plain `IObjectModifiedEvent`.
  [`tasks.py:43`](../../opengever/dossier/tasks.py#L43)

- `reindex_containing_subdossier_for_contained_objects`: moved verbatim, unchanged Solr filters and `elevated_privileges()` wrapping.
  [`tasks.py:20`](../../opengever/dossier/tasks.py#L20)

**Tests**

- Subscriber tests: enqueue-on-title-change for both a dossier and a subdossier.
  [`test_tasks.py:52`](../../opengever/dossier/tests/test_tasks.py#L52)

- No-admin-unit synchronous fallback, verified via a spy on `reindex_dossier_title` rather than just "no task queued".
  [`test_tasks.py:77`](../../opengever/dossier/tests/test_tasks.py#L77)

- Task handler tests: dispatch to the correct reindex function based on `is_subdossier()`, and the missing-UID no-op.
  [`test_tasks.py:139`](../../opengever/dossier/tests/test_tasks.py#L139)
