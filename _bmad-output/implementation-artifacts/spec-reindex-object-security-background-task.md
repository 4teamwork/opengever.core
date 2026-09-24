---
title: 'Reindex Object Security Background Task'
type: 'feature'
created: '2026-06-23'
status: 'done'
baseline_commit: '9d4d475569d488b807e75f11de8f561c6163b32f'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `CMFCatalogAware.reindexObjectSecurity` runs synchronously and recursively on every permission change, blocking the request when security cascades to large content trees. ftw.solr already replaces this method with an optimised `recursive_index_security` implementation, but it still runs in-request.

**Approach:** Patch `CMFCatalogAware.reindexObjectSecurity` (layering on top of ftw.solr's existing patch) to enqueue a `reindex-object-security` background task instead. The existing `BackgroundTaskWorker` consumes and executes the task out-of-band, calling the original (ftw.solr) implementation on the resolved object.

## Boundaries & Constraints

**Always:**
- Python 2.7 compatible — `u''` literals, `super(Cls, self)`, `%`-formatting throughout.
- Fall through to `_original_reindex_object_security(self, skip_self=skip_self)` when `get_current_admin_unit()` returns `None` (setup/test contexts where OGDS is not ready).
- Deduplication on enqueue: cancel any existing pending task for the same `uid` + `admin_unit_id` before inserting the new one. Delete + insert happen in the same SQLAlchemy session (committed at end of request).
- Task handler must NOT call `obj.reindexObjectSecurity()` — that would recurse into our own patch. Call `_original_reindex_object_security` via module-attribute late binding instead.
- Missing object at task-execution time → log a warning and return (task marks `succeeded`; do not retry).

**Ask First:**
- Adding a new column to `background_tasks` to make deduplication queryable in SQL (currently filtered in Python).
- Any change to how `_original_reindex_object_security` is resolved (e.g. explicit ftw.solr import).

**Never:**
- Import from `ftw.solr` internals directly (keeps ftw.solr version-independent).
- Apply the patch in ZCML; patch application belongs in `opengever/base/monkey/patches/__init__.py`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Normal enqueue | `obj.reindexObjectSecurity()` called, admin unit present | One pending `reindex-object-security` task inserted with `{'uid': uid, 'skip_self': False}` | — |
| Deduplication | Same object's `reindexObjectSecurity` called twice before worker runs | Old pending task deleted, new task inserted; only one row in DB | — |
| No admin unit | `get_current_admin_unit()` returns `None` | Falls through to `_original_reindex_object_security(self, skip_self=skip_self)` synchronously | — |
| `skip_self=True` | Called with `skip_self=True` | Stored in task arguments; passed to original on execution | — |
| Object deleted before task runs | UID no longer in catalog | Log `WARNING: object <uid> not found, skipping reindexObjectSecurity` — task succeeds | — |
| Task executes successfully | Object found in catalog | `_original_reindex_object_security(obj, skip_self=skip_self)` called; `task.status = 'succeeded'` | Worker's existing retry/failure logic handles exceptions |

</frozen-after-approval>

## Code Map

- `opengever/bgtasks/reindex_object_security.py` — NEW: `ReindexObjectSecurityTask(BaseBackgroundTask)` + module-level `register_task_type(TASK_TYPE, ...)` call; object lookup and execution logic
- `opengever/bgtasks/patches.py` — NEW: `PatchCMFCatalogAwareReindexObjectSecurity(MonkeyPatch)`; captures `_original_reindex_object_security` at patch time, exposes it at module level for the task handler
- `opengever/base/monkey/patches/__init__.py` — MODIFY: import task module (triggers `register_task_type`) + import + apply new patch class; follows the existing `opengever.debug` pattern for cross-package patches
- `opengever/bgtasks/tests/test_reindex_object_security.py` — NEW: `IntegrationTestCase` for patch behaviour; `MEMORY_DB_LAYER` unittest for task handler edge cases

## Tasks & Acceptance

**Execution:**
- [x] `opengever/bgtasks/reindex_object_security.py` — create: define `TASK_TYPE = u'reindex-object-security'`; define `ReindexObjectSecurityTask(BaseBackgroundTask)` with `task_type = TASK_TYPE`; `execute(self, task, commit_checkpoint)` looks up object via `portal_catalog.unrestrictedSearchResults(UID=uid)`, logs warning + returns if not found, otherwise calls `_patches._original_reindex_object_security(obj, skip_self=skip_self)` where `_patches` is `opengever.bgtasks.patches` imported as a module; call `register_task_type(TASK_TYPE, ReindexObjectSecurityTask)` at module level
- [x] `opengever/bgtasks/patches.py` — create: declare module-level `_original_reindex_object_security = None`; define `PatchCMFCatalogAwareReindexObjectSecurity(MonkeyPatch)` whose `__call__` captures `CMFCatalogAware.reindexObjectSecurity` into `_original_reindex_object_security`, defines the replacement function (gets UID + `skip_self`, calls `get_current_admin_unit()`, falls through if None, otherwise cancels existing pending same-UID tasks via session query + delete loop, then calls `queue_task(TASK_TYPE, admin_unit_id, arguments={u'uid': uid, u'skip_self': skip_self})`), and calls `self.patch_refs(CMFCatalogAware, 'reindexObjectSecurity', replacement)` with `locals()['__patch_refs__'] = False`
- [x] `opengever/base/monkey/patches/__init__.py` — add near the bottom (after all existing patches but before the conditional `readonly`/`debug` blocks): `from opengever.bgtasks.patches import PatchCMFCatalogAwareReindexObjectSecurity`, `import opengever.bgtasks.reindex_object_security  # noqa`, `PatchCMFCatalogAwareReindexObjectSecurity()()`
- [x] `opengever/bgtasks/tests/test_reindex_object_security.py` — create: `TestReindexObjectSecurityPatch(IntegrationTestCase)` tests covering: single enqueue, deduplication, `skip_self` propagation, fallback when no admin unit; `TestReindexObjectSecurityTask(unittest.TestCase)` with `layer = MEMORY_DB_LAYER` covering: successful execution calls original, missing object logs warning without retry

**Acceptance Criteria:**
- Given `obj.reindexObjectSecurity()` is called on a Dexterity content object with a configured admin unit, when the call returns, then exactly one pending `reindex-object-security` task exists in the `background_tasks` table for that object's UID.
- Given a pending task for UID `X` already exists, when `reindexObjectSecurity` is called again on the same object, then the old task is deleted and a single new pending task is present.
- Given `get_current_admin_unit()` returns `None`, when `reindexObjectSecurity` is called, then no task is enqueued and the original security reindexing runs synchronously.
- Given a `reindex-object-security` task is executed by the worker and the object no longer exists in the catalog, then the task completes with `status='succeeded'` and a warning is logged.
- Given a `reindex-object-security` task is executed by the worker and the object exists, then `_original_reindex_object_security` is called on the resolved object with the stored `skip_self` value.

## Design Notes

**Late-binding of `_original_reindex_object_security`:** The task handler accesses the original via `import opengever.bgtasks.patches as _patches_mod` and calls `_patches_mod._original_reindex_object_security(obj, ...)` at execute time (not at import time). This avoids circular imports and ensures the variable is set by the time any task actually runs.

**Patch ordering:** `_original_reindex_object_security` is captured from `CMFCatalogAware.reindexObjectSecurity` at the moment `PatchCMFCatalogAwareReindexObjectSecurity()()` runs. If ftw.solr has patched before us (typical), we capture ftw.solr's optimised version. If not, we capture the stock CMFCore version — both produce correct security reindexing.

**No new DB schema:** Deduplication is done by loading all pending `reindex-object-security` tasks for the admin unit and filtering by UID in Python. Task count is expected to be small at any point in time.

## Verification

**Commands:**
- `bin/test opengever/bgtasks/tests/test_reindex_object_security.py` -- expected: all tests pass
- `python -c "from opengever.bgtasks.reindex_object_security import ReindexObjectSecurityTask"` -- expected: no ImportError

**Manual checks (if no CLI):**
- After calling `obj.reindexObjectSecurity()` in a running instance, verify a row appears in `background_tasks` with `task_type='reindex-object-security'` and the object's UID in `task_arguments`.

## Suggested Review Order

**Patch wiring — start here to grasp the design intent**

- New patch class imported and applied after all existing patches, before conditional readonly/debug blocks.
  [`__init__.py:45`](../../opengever/base/monkey/patches/__init__.py#L45)

**Patch implementation**

- `__call__` captures the pre-existing method (ftw.solr's version), then replaces it; all dedup and enqueue logic lives in the inner closure.
  [`patches.py:24`](../../opengever/bgtasks/patches.py#L24)

- Module-level `_original_reindex_object_security = None` — set at patch time, read by the task handler at execute time to break the circular import.
  [`patches.py:13`](../../opengever/bgtasks/patches.py#L13)

- Inner replacement: guards for `IDisableCatalogIndexing`, `uid=None`, and missing admin unit; then dedup delete + enqueue.
  [`patches.py:30`](../../opengever/bgtasks/patches.py#L30)

**Task handler**

- `execute()`: lazy import of `patches` module to resolve `_original` at call time; uid/site/catalog/object guards before dispatching.
  [`reindex_object_security.py:17`](../../opengever/bgtasks/reindex_object_security.py#L17)

- Module-level `register_task_type` call — triggered on import via the `__init__.py` import chain.
  [`reindex_object_security.py:61`](../../opengever/bgtasks/reindex_object_security.py#L61)

**Tests**

- Patch-behaviour tests: enqueue, deduplication, `skip_self`, and admin-unit-absent fallback.
  [`test_reindex_object_security.py:13`](../../opengever/bgtasks/tests/test_reindex_object_security.py#L13)

- Task-handler tests: spy on `_original` to verify dispatch, `skip_self` pass-through, and missing-object no-op.
  [`test_reindex_object_security.py:83`](../../opengever/bgtasks/tests/test_reindex_object_security.py#L83)
