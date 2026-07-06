# Deferred Work

## From: background-tasks-infrastructure (2026-06-12)

- **datetime.now() vs UTC across worker**: All timestamps use naive `datetime.now()`. Pre-existing pattern in opengever (nightly jobs same). Consider switching to `datetime.utcnow()` uniformly to avoid TZ drift on DST changes. Low risk in practice since server and DB are usually in same timezone.

- **_task_registry test isolation**: Module-level `_task_registry` dict accumulates registrations across the test session. If two tests register conflicting type names, the last-imported wins silently. Add cleanup or use per-test override pattern.

- **register_task_type silent overwrite**: `register_task_type(name, cls)` silently replaces an existing entry. Consider raising `ValueError` on duplicate registration to catch accidental double-imports early.

- **Unknown task_type error type inconsistency**: `queue_task` raises `ValueError` for unknown types; `get_task_class` raises `KeyError`. A task whose type becomes unregistered after enqueue will fail with a `KeyError` — caught as a task failure but the error message gives no hint it's a code deployment issue vs data issue.

- **Checkpoint commit failure isolation**: If `commit_checkpoint` raises inside `execute()`, the outer `except Exception` catches it, aborts, and resets the task to the last committed state. The spec says "checkpoint abort only affects that commit" but in practice the abort rolls back to before the task was marked running. Acceptable but worth documenting.

- **Multi-site worker support**: `run_background_tasks_handler` uses `get_first_plone_site` because `run_forever` is an infinite loop. If opengever ever needs a multi-site worker, restructure so `run_forever` processes one task per call and the outer loop drives the forever behaviour.

## From: reindex-object-security-background-task (2026-06-23)

- **RUNNING task not cancelled during dedup**: Deduplication only cancels PENDING tasks for the same UID. If a task for the same object is already RUNNING (worker mid-execution), a second PENDING task is still enqueued. Both execute sequentially, which is safe (second is a no-op) but wasteful. A RUNNING check would require holding a lock or a different status model.

- **Transaction abort silently loses reindex**: If the calling transaction is aborted after `reindexObjectSecurity` returns (exception later in same request), both the dedup-delete and the new enqueue are rolled back. The security reindex is silently lost — no pending task, no error. Solving this properly requires after-commit hooks, which is a larger architectural change.

- **No synchronous fallback when queue_task fails**: If the SQL session is unavailable when `reindexObjectSecurity` is called, `queue_task` raises and the exception propagates to the caller. There is no fallback to running the reindex synchronously. This is intentional (avoids silent inconsistency) but worth revisiting if DB failures become a concern.

## From: background-tasks-kill-switch (2026-07-02)

- **Scheduling/priority/checkpoint semantics are no-ops when disabled**: When background tasks are disabled, `queue_task()` executes the handler immediately regardless of `run_at`, `priority`, or `max_retries`, and `commit_checkpoint` is a no-op. This is intentional per spec (no worker exists to honor them when disabled), but no current caller passes `run_at`/relies on checkpointing, so it's untested territory. Worth a second look if a future task handler starts relying on scheduled execution or checkpoint resumption.

## From: update-reference-prefixes-background-task (2026-07-06)

- **Stale child brain not guarded in `reindex_children_with_new_prefix`**: `child.getObject()` in the extracted loop is not checked for `None` before calling `.reindexObject()`. If a child is deleted/moved between the catalog path search and this call, it raises `AttributeError`. Pre-existing in the original inline implementation, unchanged by this story — but now runs with a longer queue-to-execution delay (worker mode) than the original in-request call, making the race window larger in practice.
- **`results[0]` assumes a single catalog match per UID, silently**: Both this task and the existing `ReindexObjectSecurityTask` pick `results[0]` without checking for or warning about duplicate/stale brains for the same UID. Shared pattern across `opengever.bgtasks`, not introduced here.
- **Fallback only triggers on `get_current_admin_unit() is None`, not on "is a worker actually consuming the queue"**: If the `bgtasks` feature is enabled but no worker process is deployed/running for an admin unit, tasks queue up and reference-prefix reindexing silently never happens (no error, no operator-facing warning). This is an architectural characteristic shared with `reindexObjectSecurity`'s task, not specific to this change.

## From: reindex-dossier-title-background-task (2026-07-06)

- **`get_current_admin_unit()` fallback runs the full synchronous Solr subtree walk with zero logging**: unchanged from `update_reference_prefixes`'s precedent — an operator has no way to tell that a given request fell back to synchronous reindexing instead of queuing. Same architectural characteristic as the prior two tasks; worth a shared fix (e.g. a single log line at the fallback site) across all three call sites rather than three one-off patches.
- **No de-duplication of pending `reindex-dossier-title` tasks for the same UID**: matches the precedent set by `update_reference_prefixes` (deliberately omitted per spec, title edits are not high-frequency). A bulk import/migration that rewrites many dossier titles would still queue one full-subtree Solr scan per edit; revisit if bulk title rewrites become common.
- **Dossier vs. subdossier dispatch decided at task-execution time, not at the original edit time**: if a dossier is moved to become/stop being a subdossier in the window between the title-change event firing and the queued task executing, the task updates whichever field matches its state at execution time, not necessarily the state at edit time. Deliberate spec tradeoff (recomputing is cheaper than risking staleness of a passed flag); the window is only relevant for the rare case of a dossier being reparented in the same instant its title changes.
- **`is_subdossier()`/reindex functions are not wrapped in the task's `try/except`**: only the initial `_unrestrictedGetObject()` catalog lookup is guarded (mirroring `UpdateReferencePrefixesTask`/`ReindexObjectSecurityTask`); any exception from the actual Solr reindex loop propagates uncaught to the worker's retry logic. Consistent with the two prior task implementations, not introduced here.
- **No test asserts the actual Solr payload/`sync_task` call** for the moved reindex functions — new tests only verify task queuing and dispatch (spying on the reindex functions), matching the test scope of `update_reference_prefixes`'s own test suite. Actual Solr-mutation coverage for this code path has never existed in the repo under any test module.
